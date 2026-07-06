from loguru import logger
import pandas as pd

from quantaq_tools.utilities import safe_load, fix_timestamps

def concat_files(files):
    """Concatenate multiple files into a single DataFrame and sort based on a 
    timestamp column.

    Args:
        files (list): List of file paths to concatenate.

    Returns:
        pd.DataFrame: Concatenated and sorted DataFrame.
    """
    data = []
    logger.info("Parsing {} files", len(files))
    for f in files:
        logger.debug("Parsing {}", f)
        tmp = safe_load(f)
        data.append(tmp)

    # concat all of the files together
    df = pd.concat(data, sort=False)
    
    if df.empty:
        error = ValueError(f"No data found after parsing {len(files)} files: {files}")
        logger.error(error)
        raise error
    
    # sort based on a time column
    df = fix_timestamps(df, sort_values=True)

    return df
