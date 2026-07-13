from pathlib import Path

from loguru import logger
import pandas as pd

from quantaq_cli.exceptions import InvalidFileExtension
from quantaq_cli.utilities import drop_unnamed
from quantaq_cli.toolkit.munge import clean_dataframe


def safe_load(fpath, standardize_schema=True):
    """Load a CSV or parquet file.
    
    Args:
        fpath (str or Path): Path to the CSV or parquet file.
        coerce_dtypes (bool): Whether to coerce dtypes to expected types. 
        Default is True.

    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    
    p = Path(fpath)

    if p.suffix == ".csv":
        as_csv = True
    elif p.suffix == ".parquet":
        as_csv = False
    else:
        error = InvalidFileExtension(f"Invalid file extension; got {p.suffix!r}")
        logger.error(error)
        raise error

    tmp = pd.read_csv(fpath, nrows=1, header=None) if as_csv else pd.read_parquet(fpath)

    if as_csv and tmp.iloc[0, 0] == "deviceModel": # hack to deal with modulair format
        logger.info("Reading rawSD card data {}", fpath)
        
        tmp = pd.read_csv(fpath, skiprows=3)

        # Always add the sn as a column for rawSD data
        tmp2 = pd.read_csv(fpath, nrows=3, header=None)
        serial_number = tmp2.iloc[2, 1]
        tmp['sn'] = serial_number
        logger.info("Added serial number {} to column `sn` ", serial_number)
        
    elif as_csv and tmp.shape[1] == 2: # hack to deal with bad header format
        tmp = pd.read_csv(fpath, skiprows=1)
    elif as_csv:
        tmp = pd.read_csv(fpath)

    # drop the extra column if it was added
    tmp = drop_unnamed(tmp)

    if standardize_schema:
        tmp = clean_dataframe(tmp)

    return tmp
