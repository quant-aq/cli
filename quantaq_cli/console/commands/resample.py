from __future__ import annotations
from pathlib import Path

import click
from loguru import logger
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from ...exceptions import InvalidFileExtension
from ...utilities import safe_load


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

def resample_dataframe(
    df: pd.DataFrame,
    rule: str,
    *,
    on: str = "timestamp",
    by: str | list[str] | None = None,
    wind: tuple[str, str, str, str] | None = WIND_COLUMNS,
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
        wind: ``(u, v, speed, direction)`` column names. When the u/v columns
            are present, the speed/direction columns are NOT scalar-averaged;
            they are derived from the averaged u/v components instead (see
            ``_vector_wind``). If only speed/direction are present, the u/v
            components are first created from them (see ``_components_from_polar``).
            Pass ``None`` to skip.
        numeric_how: Aggregation for numeric columns.
        nonnumeric_how: Aggregation for non-numeric columns.

    Returns:
        A new frame with ``on`` (and any ``by`` keys) as columns.
    """
    if type(df[on]) != np.datetime64:
        df[on] = df[on].map(pd.to_datetime)

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
        c for c in df.columns if c != on and c not in keys and c not in derived
    ]
    agg = {
        c: (numeric_how if is_numeric_dtype(df[c]) else nonnumeric_how)
        for c in value_cols
    }

    indexed = df.set_index(on)
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

def resample_command(file, rule, output, **kwargs):
    verbose = kwargs.pop("verbose", False)
    on = kwargs.pop("on", "timestamp")
    by = kwargs.pop("by", None)
    wind = kwargs.pop("wind", WIND_COLUMNS)
    numeric_how = kwargs.pop("numeric_how", "mean")
    nonnumeric_how = kwargs.pop("nonnumeric_how", "first")

    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    # concat everything in filepath
    if verbose:
        click.secho("Files to read: {}".format(file), fg='green')

    # load the file
    df = safe_load(file)

    # if column to resample over needs to be made a datetime obj, do so
    if on not in df.columns:
        raise Exception("Invalid column name for the timestamp")

    # resample
    df = resample_dataframe(
        df,
        rule,
        on=on,
        by=by,
        wind=wind,
        numeric_how=numeric_how,
        nonnumeric_how=nonnumeric_how,
    )

    # save the file
    if verbose:
        click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        df.to_csv(output)
    else:
        df.reset_index().to_feather(output)
