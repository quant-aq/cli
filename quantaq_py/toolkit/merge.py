from loguru import logger
import pandas as pd

from quantaq_py.utilities import safe_load, fix_timestamps


def merge_files(files, tscol="timestamp"):
    """Merge multiple files on a timestamp column.

    Args:
        files (list): List of file paths to merge.
        tscol (str, optional): Name of the timestamp column. Default is "timestamp".    

    Returns:
        pd.DataFrame: the merged DataFrame
    """
    
    # create an array of timestamp column names to try
    tscols = [tscol, "timestamp", "timestamp_local"]

    df = pd.DataFrame()
    logger.info("Parsing {} files", len(files))

    # Find the best timestamp column from the first file, and use it for merging
    # if found in subsequent files.
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
        df = pd.merge(df, tmp, left_index=True, right_index=True, how='outer')
        
    df = df.reset_index()  # bring timestamp back as a column named `tscol`

    return df
