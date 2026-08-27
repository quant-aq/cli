from __future__ import annotations

from loguru import logger
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype


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

def _min_required_count(timestamps, rule, threshold):
    """The minimum number of non-null samples needed in one resampling bin to 
    meet the data completeness threshold.

    We infer the native sampling interval from the median tdiff (spacing between
    consecutive timestamps in ``timestamps``), then compared to the resampling
    bin width to estimate how many native-resolution rows should fall in
    one bin. E.g. 1-min data resampled to "1hr" expects ~60 rows/bin;
    at ``threshold=0.75`` a bin needs >= 45 non-null rows to survive.

    Args:
        timestamps: The timestamp series (pre-resampling)
        rule: The pandas offset alias passed to ``resample_dataframe``.
        threshold: The required fraction of expected samples, e.g. ``0.75``.

    """
    bin_width = pd.Timedelta(pd.tseries.frequencies.to_offset(rule))
    median_tdiff = pd.to_datetime(timestamps).sort_values().diff().median()
    if pd.isna(median_tdiff) or median_tdiff <= pd.Timedelta(0):
        return 0
    expected_samples = bin_width / median_tdiff
    return int(np.ceil(threshold * expected_samples))

def _flag_aware_resample(df, rule, keys, agg):
    """Vectorized flag-aware resampling.

    For each resample bin: if any row has flag == 0, aggregate only those
    "clean" rows and set the output flag to 0. Otherwise aggregate all rows
    in the bin and set the output flag to the bitwise OR of every flag value
    present.

    Args:
        df (pd.DataFrame): the input dataframe to resample
        rule: Any pandas offset alias, e.g. ``"1min"``, ``"1h"``, ``"1D"``.
        keys (list[str]): Column(s) to group by before resampling (e.g.
            ``["sn"]``), so each device/location is resampled independently.
            Pass an empty list to resample the whole frame as one series
            of bins.
        agg (dict): Mapping of column name -> aggregation method, defined inside
                    resample_dataframe.
    """

    if "flag" not in df.columns:
        error = ValueError(
            "No 'flag' column found in dataframe! Cannot implement "
            "flag-aware resampling. Consider calling flag_dataframe() first."
        )
        logger.error(error)
        raise error

    def _resampler(frame):
        return frame.groupby(keys).resample(rule) if keys else frame.resample(rule)

    clean_agg = _resampler(df[df["flag"] == 0]).agg(agg)

    base_resampler = _resampler(df)
    all_agg = base_resampler.agg(agg)
    flag_col = base_resampler["flag"]
    has_clean = flag_col.agg(lambda s: bool((s == 0).any()))
    flag_or = flag_col.agg(lambda s: int(np.bitwise_or.reduce(s.to_numpy())) if len(s) else np.nan)

    clean_agg = clean_agg.reindex(all_agg.index)
    has_clean = has_clean.reindex(all_agg.index)
    flag_or = flag_or.reindex(all_agg.index)

    out = clean_agg.where(has_clean, all_agg)
    out["flag"] = np.where(has_clean, 0, flag_or)

    return out.reset_index()

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
    force_nonnumeric: str | list[str] | None = None,
    completeness_threshold: float | None = None,
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
        force_nonnumeric: Column name(s) to always aggregate with
            ``nonnumeric_how`` regardless of dtype, e.g. ``"fw"``,
            which is numeric but shouldn't be averaged.
        completeness_threshold: If given (e.g. ``0.75``), bins that don't
            meet the data-completeness requirement get every value column set
            to NaN. The definition of "complete" depends on ``flag_aware``:

              - If ``flag_aware=True``: the bin needs this fraction of its expected 
                native-resolution sample count to be clean (flag==0)
              - If ``flag_aware=False``: the bin needs this fraction of its expected 
                native-resolution sample count to be non-null

    Returns:
        A new frame with ``on`` (and any ``by`` keys) as columns.
    """
    if not is_datetime64_any_dtype(df[on]):
        df[on] = pd.to_datetime(df[on])

    keys = [by] if isinstance(by, str) else list(by or [])
    force_nonnumeric_set = (
        {force_nonnumeric}
        if isinstance(force_nonnumeric, str)
        else set(force_nonnumeric or [])
    )

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

    # hack for naming collision issue with "first" and "last" agg methods
    # (TypeError: NDFrame.first() missing 1 required positional argument: 'offset')
    agg = {
        c: (
            numeric_how if is_numeric_dtype(df[c]) and c not in force_nonnumeric_set
            else (lambda s: s.iloc[0] if len(s) else np.nan) if nonnumeric_how == "first"
            else (lambda s: s.iloc[-1] if len(s) else np.nan) if nonnumeric_how == "last"
            else nonnumeric_how
        )
        for c in value_cols
    }
    indexed = df.set_index(on)
    if flag_aware:
        out = _flag_aware_resample(indexed, rule, keys, agg)
    else:
        if keys:
            out = indexed.groupby(keys).resample(rule).agg(agg).reset_index()
        else:
            out = indexed.resample(rule).agg(agg).reset_index()

    if completeness_threshold is not None:
        merge_on = keys + [on]

        if flag_aware:
            # require >= completeness_threshold fraction of the expected
            # sample count to be clean (flag == 0)
            clean_indexed = indexed[indexed["flag"] == 0]
            if keys:
                clean_counts = (
                    clean_indexed.groupby(keys).resample(rule)["flag"]
                    .count().rename("_clean_count").reset_index()
                )
                min_count_by_group = (
                    df.groupby(keys)[on]
                    .apply(lambda s: _min_required_count(s, rule, completeness_threshold))
                    .rename("_min_count")
                )
                clean_counts = clean_counts.merge(min_count_by_group, on=keys, how="left")
            else:
                clean_counts = (
                    clean_indexed["flag"].resample(rule)
                    .count().rename("_clean_count").reset_index()
                )
                clean_counts["_min_count"] = _min_required_count(
                    df[on], rule, completeness_threshold
                )
            clean_counts["_clean_count"] = clean_counts["_clean_count"].fillna(0)

            merged = out[merge_on].merge(clean_counts, on=merge_on, how="left")
            fail_mask = merged["_clean_count"] < merged["_min_count"]

            for c in value_cols:
                if c not in out.columns:
                    continue
                out.loc[fail_mask.to_numpy(), c] = np.nan
        else:
            # require >= completeness_threshold fraction of the expected
            # sample count to be non-null, for each value column
            if keys:
                raw_counts = (
                    indexed.groupby(keys).resample(rule)[value_cols].count().reset_index()
                )
                min_count_by_group = (
                    df.groupby(keys)[on]
                    .apply(lambda s: _min_required_count(s, rule, completeness_threshold))
                    .rename("_min_count")
                )
                raw_counts = raw_counts.merge(min_count_by_group, on=keys, how="left")
            else:
                raw_counts = indexed[value_cols].resample(rule).count().reset_index()
                raw_counts["_min_count"] = _min_required_count(
                    df[on], rule, completeness_threshold
                )

            merged_counts = out[merge_on].merge(raw_counts, on=merge_on, how="left")
            for c in value_cols:
                if c not in out.columns:
                    continue
                short = merged_counts[c] < merged_counts["_min_count"]
                out.loc[short.to_numpy(), c] = np.nan

        logger.debug(
            "Applied {:.0%} completeness threshold to {} value column(s)",
            completeness_threshold, len(value_cols),
        )

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
