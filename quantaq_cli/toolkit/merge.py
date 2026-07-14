from loguru import logger
import pandas as pd

from quantaq_cli.utilities import fix_timestamps
from quantaq_cli.toolkit.load import safe_load

def merge_files(files, tscol="timestamp", suffixes=None, keep="both"):
    """Merge two files on a timestamp column.
    Args:
        files (list): List of file paths to merge.
        tscol (str, optional): Name of the timestamp column. Default is "timestamp".
        suffixes (tuple or str, optional): Suffix(es) to apply to overlapping
            column names.
            - If keep="both": must be a length-2 tuple, where each element is
              the suffix applied to the left and right DataFrame's version of
              an overlapping column, respectively.  Defaults to
              ("_left", "_right") if not specified.
            - If keep="left" or keep="right": must be a single string which is 
              applied only to the kept side's column name. Defaults to "" 
              (kept column keeps its original name) if not specified.
        keep (str, optional): Which side to keep for columns that overlap
            between files: "both" keeps both suffixed columns, "left" keeps
            only the left/earlier file's version, "right" keeps only the
            right/later file's version. Default is "both". 

    Returns:
        pd.DataFrame: the merged DataFrame
    """
    if len(files)>2:
        error = ValueError("Attempting to merge >2 files at a time.")
        logger.error(error)
        raise error
    
    if suffixes is None:
        suffixes = ('_left', '_right') if keep == "both" else ""

    if keep == "both":
        if not (isinstance(suffixes, tuple) and len(suffixes) == 2):
            error = ValueError(
                "suffixes must be a length-2 tuple when keep='both', got "
                f"{suffixes!r}"
            )
            logger.error(error)
            raise error
    elif keep in ("left", "right"):
        if isinstance(suffixes, str):
            # Single suffix applies only to the kept side; the dropped
            # side's column name is temporarily named _drop
            suffixes = (
                (suffixes, "_drop") if keep == "left" else ("_drop", suffixes)
            )
        else: 
            invalid_suffixes = suffixes
            suffixes = (
                ("", "_drop") if keep == "left" else ("_drop", "")
            )
            logger.warning(
                "suffixes must be a single string when "
                f"keep={keep!r}; got {invalid_suffixes!r}. Defaulting to ""."
            )
    else:
        error = ValueError(f"keep must be 'both', 'left', or 'right', got {keep!r}")
        logger.error(error)
        raise error
    
    # create an array of timestamp column names to try
    tscols = [tscol, "timestamp", "timestamp_local"]

    df = pd.DataFrame()
    logger.info("Parsing {} files", len(files))

    # Find the best timestamp column from the first file, and use it for merging with the second file.
    for f in files:
        logger.debug("Parsing {}", f)
        tmp = safe_load(f)

        # check for the column name and set to best guess
        for c in tscols:
            if c in tmp.columns:
                tscol = c
                break

        if not tscol in tmp.columns:
            logger.debug("Time {} was not found in the file; skipping file.", tscol)
            continue

        # Fix timestamps, if needed
        tmp = fix_timestamps(tmp, set_index=True, sort_values=True, localize_tz=True)

        # merge with the other files
        df = pd.merge(df, tmp, left_index=True, right_index=True, how='outer', suffixes=suffixes)

        # resolve overlapping columns down to one side, if desired
        if keep != "both":
            left_suffix, right_suffix = suffixes
            drop_suffix, _ = (
                (right_suffix, left_suffix) if keep == "left" else (left_suffix, right_suffix)
            )
            df = df.loc[:, ~df.columns.str.endswith(drop_suffix)]

    df = df.reset_index()  # bring timestamp back as a column named `tscol`

    return df
