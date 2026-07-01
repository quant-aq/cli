from loguru import logger
import pandas as pd

from quantaq_py.utilities import safe_load, determine_timestamp_column

def concat_files(files):
    # read all files
    data = []
    logger.info("Parsing {} files", len(files))
    for f in files:
        
        logger.debug("Parsing {}", f)
        tmp = safe_load(f)
        data.append(tmp)

    # concat all of the files together
    df = pd.concat(data, sort=False)

    # sort based on a time column
    tscol = determine_timestamp_column(df)
    df = df.sort_values(by=tscol)
    
    if df.empty:
        raise Exception("No data")
    
    return df
