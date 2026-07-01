from loguru import logger
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_timedelta64_dtype

from quantaq_py.utilities import safe_load


def merge_files(files, tscol="timestamp"):
    """Merge multiple files on a timestamp column."""
    
    # create an array of timestamp column names to try
    tscols = [tscol, "timestamp", "timestamp_local"]

    df = pd.DataFrame()
    logger.info("Parsing {} files", len(files))
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
                
        # convert the timestamp column to a pandas datetime
        if not (is_datetime64_any_dtype(tmp[tscol]) or is_timedelta64_dtype(tmp[tscol])):
            tmp[tscol] = tmp[tscol].apply(lambda x: pd.to_datetime(x, errors='coerce'))

        # drop the bad rows
        tmp = tmp.dropna(how='any', subset=[tscol])

        # localize the timezone if needed
        tmp[tscol] = tmp[tscol].apply(lambda x: x.tz_localize("UTC") if not x.tzinfo else x)

        # set the index
        tmp.set_index(tscol, inplace=True)

        # merge with the other files
        df = pd.merge(df, tmp, left_index=True, right_index=True, how='outer')
    return df
