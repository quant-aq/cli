from __future__ import annotations
from pathlib import Path

import click
from loguru import logger
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype

from quantaq_cli.exceptions import InvalidFileExtension
from quantaq_cli.utilities import safe_load


# Default (u, v, speed, direction) column names for vector wind averaging.
WIND_COLUMNS = ("wx_u", "wx_v", "wx_ws", "wx_wd")

def _vector_wind(
    df: pd.DataFrame, u_col: str, v_col: str, ws_col: str, wd_col: str
) -> pd.DataFrame:
    """Derive vector-averaged speed/direction from averaged u/v components.

    Wind speed and direction cannot be scalar-averaged (350 deg and 10 deg
    average to 180 deg, not 0). Instead the Cartesian u/v components are
    averaged and converted back to polar form. This mirrors the reference
    C++ implementation::

        ws = sqrt(mean_u**2 + mean_v**2)
        wd = atan2(mean_u, mean_v)  in degrees, wrapped to [0, 360)

    ``df`` already holds the per-bin averaged components, so ``ws`` is the
    magnitude of the *mean* vector (the divide-by-count is baked in), not the
    raw vector sum.
    """
    u, v = df[u_col], df[v_col]
    df[ws_col] = np.sqrt(u**2 + v**2)
    df[wd_col] = np.degrees(np.arctan2(u, v)) % 360.0
    return df

def _components_from_polar(
    df: pd.DataFrame, u_col: str, v_col: str, ws_col: str, wd_col: str
) -> pd.DataFrame:
    """Create u/v wind components from speed/direction.

    The exact inverse of ``_vector_wind``'s recovery, so the two round-trip::

        u = ws * sin(radians(wd))
        v = ws * cos(radians(wd))

    Used when the input has wind speed/direction but not the Cartesian
    components, which must exist before wind can be vector-averaged.
    """
    wd_rad = np.radians(df[wd_col])
    df[u_col] = df[ws_col] * np.sin(wd_rad)
    df[v_col] = df[ws_col] * np.cos(wd_rad)
    return df

def _aggregate_group(group, agg):
    """Aggregate a single resample bin using flag-aware row selection.

    This attempts to mirror the averaging logic in the firmware:
    If the bin has at least one good row (flag == 0), only those rows
    are aggregated and the resulting flag is 0. If there are no good rows (every 
    row in the bin is flagged), all rows are aggregated instead, and the resulting flag is the
    bitwise OR of every flag value that was present in the bin.

    Args:
        group (pd.DataFrame): All rows falling in one resample bin
        agg (dict): Mapping of column name -> aggregation method, defined inside
            resample_dataframe.

    Returns:
        pd.Series: One aggregated row for this bin.
    """
    # resample can produce empty bins so we also check len(group)
    if 'flag' in group.columns and len(group): 
        clean_mask = group['flag'] == 0 # true for every good row

        # there's at least 1 good row --> aggregate only the good rows, and set the new flag to 0
        if clean_mask.any():
            subset = group.loc[clean_mask]
            group_flag = 0 

        # there are no good rows --> aggregate all rows, and combine flags using bitwise OR
        else:
            subset = group 
            group_flag = int(np.bitwise_or.reduce(group['flag'].to_numpy()))
    else:
        # empty bin (produced by resampe) --> all columns will be nan, include the flag
        subset = group
        group_flag = np.nan

    # hack for naming collision issue with "first" and "last" agg methods
    # (TypeError: NDFrame.first() missing 1 required positional argument: 'offset')
    values = {}
    for col, how in agg.items():
        if how == "first":
            values[col] = subset[col].iloc[0] if len(subset) else np.nan
        elif how == "last":
            values[col] = subset[col].iloc[-1] if len(subset) else np.nan
        else:
            values[col] = subset[col].agg(how)

    values['flag'] = group_flag

    return pd.Series(values)

def resample_dataframe(
    df: pd.DataFrame,
    rule: str,
    *,
    on: str = "timestamp",
    by: str | list[str] | None = None,
    wind: tuple[str, str, str, str] | None = WIND_COLUMNS,
    flag_aware: bool = False,
    numeric_how: str = "mean",
    nonnumeric_how: str = "first",
) -> pd.DataFrame:
    """Resample a time-indexed frame, handling mixed dtypes safely.

    A drop-in improvement over ``df.resample(rule).mean()``: numeric columns
    are aggregated with ``numeric_how`` (default ``"mean"``) while non-numeric
    columns (strings, categoricals) use ``nonnumeric_how`` (default
    ``"first"``) instead of being silently dropped.

    Args:
        df: Input frame containing a datetime column ``on``.
        rule: Any pandas offset alias, e.g. ``"1min"``, ``"1h"``, ``"1D"``.
        on: Name of the datetime column to resample over.
        by: Optional column(s) to group by first (e.g. ``"sn"``), so each
            device/location is resampled independently.
        wind: ``(u, v, speed, direction)`` column names. The u/v columns don't 
            need to be present in the dataframe, but the column names still need to be
            specified here. When the u/v columns are present in the dataframe, 
            the speed/direction columns are NOT scalar-averaged;
            they are derived from the averaged u/v components instead (see
            ``_vector_wind``). If only speed/direction are present, the u/v
            components are first created from them (see ``_components_from_polar``).
            Pass ``None`` to skip.        
        flag_aware: Whether to apply flag-aware row selection when resampling.
            If True, each resample bin is aggregated as follows:
              - If the bin has one or more good rows (non-flagged rows, flag == 0),
                only those rows are aggregated, and the resulting flag is 0.
              - If there are no good rows (every row in the bin is flagged), all
                rows are aggregated, and the resulting flag is the bitwise OR of every
                flag value present in the bin.
            If False (default), all rows in a bin are aggregated together regardless
            of flag values, and the `flag` column is dropped from the
            output.
        numeric_how: Aggregation for numeric columns.
        nonnumeric_how: Aggregation for non-numeric columns.

    Returns:
        A new frame with ``on`` (and any ``by`` keys) as columns.
    """
    if not is_datetime64_any_dtype(df[on]):
        df[on] = pd.to_datetime(df[on])

    keys = [by] if isinstance(by, str) else list(by or [])

    # When vector-averaging wind, the speed/direction columns must never be
    # scalar-aggregated -- drop them from the agg pass and derive them from the
    # averaged u/v components afterwards.
    do_wind = False
    derived: set[str] = set()
    if wind is not None:
        u_col, v_col, ws_col, wd_col = wind
        have_uv = {u_col, v_col}.issubset(df.columns)
        if have_uv and (df[u_col].isna().all() or df[v_col].isna().all()):
            logger.debug(
                    "All wind components contain NaNs ({}: {}, {}: {}); "
                    "Deriving them from the averaged u/v components",
                    u_col, int(df[u_col].isna().sum()),
                    v_col, int(df[v_col].isna().sum()),
                )
            have_uv = False
        elif have_uv and (df[u_col].isna().any() or df[v_col].isna().any()):
            logger.debug(
                    "Some wind components contain NaNs ({}: {}, {}: {}); "
                    "affected bins might produce NaN wind",
                    u_col, int(df[u_col].isna().sum()),
                    v_col, int(df[v_col].isna().sum()),
                )
        have_polar = {ws_col, wd_col}.issubset(df.columns)
        if not have_uv and have_polar:
            # Create the u/v components from speed/direction before resampling.
            logger.debug(
                "Deriving {}/{} from {}/{} before resampling",
                u_col, v_col, ws_col, wd_col,
            )
            df = _components_from_polar(df.copy(), u_col, v_col, ws_col, wd_col)
            have_uv = True
        do_wind = have_uv
        if do_wind:
            derived = {ws_col, wd_col}

    value_cols = [
        c for c in df.columns if c != on and c != 'flag' and c not in keys and c not in derived
    ]
    agg = {
        c: (numeric_how if is_numeric_dtype(df[c]) else nonnumeric_how)
        for c in value_cols
    }

    indexed = df.set_index(on)
    if flag_aware:
        if keys:
            out = (
                indexed.groupby(keys)
                .resample(rule)
                .apply(_aggregate_group, agg=agg)
                .reset_index()
            )
        else:
            out = (
                indexed.resample(rule)
                .apply(_aggregate_group, agg=agg)
                .reset_index()
            )
    else:
        if keys:
            out = indexed.groupby(keys).resample(rule).agg(agg).reset_index()
        else:
            out = indexed.resample(rule).agg(agg).reset_index()

    if do_wind:
        out = _vector_wind(out, *wind)
    elif wind is not None:
        logger.trace("wind columns {} absent; skipping vector average", wind)

    # Preserve the input column order; append any derived columns that were not
    # present in the input (e.g. speed/direction created from u/v alone).
    ordered = [c for c in df.columns if c in out.columns]
    extra = [c for c in out.columns if c not in df.columns]
    out = out[ordered + extra]

    logger.debug(
        "Resampled {} -> {} rows at '{}'{}",
        len(df), len(out), rule, f" grouped by {keys}" if keys else "",
    )
    return out
