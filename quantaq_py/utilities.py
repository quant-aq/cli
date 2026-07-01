from pathlib import Path

from loguru import logger
import pandas as pd

from quantaq_py.exceptions import InvalidFileExtension


def infer_data_source(df):
    # Determine the best timestamp column and sort
    tscol = determine_timestamp_column(df)
    df[tscol] = pd.to_datetime(df[tscol])
    df = df.sort_values(tscol)

    # Grab the tdiff between consecutive rows
    df["tdiff"] = df[tscol].diff().dt.total_seconds()
    tdiffs = set(df["tdiff"].dropna().unique())

    has_1min = 60.0 in tdiffs
    has_5sec = 5.0 in tdiffs

    if has_1min and has_5sec:
        logger.debug("Mixed 1-min and 5-sec sampling not supported")
        raise NotImplementedError
    elif has_1min:
        logger.info("Reading 1-min data --> inferring database or cloud API")
        if "api_received_at" in df.columns:
            return "cloudapi"
        else:
            return "database"
    elif has_5sec:
        logger.info("Reading 5-sec data --> inferring rawSD")
        return "rawsd"
    else:
        logger.error(f"Unrecognized sampling intervals: {sorted(tdiffs)}")
        raise NotImplementedError

def infer_data_model(df):
    if "sn" not in df.columns:
        logger.error("No serial number column found in dataframe, set `add_sn_column=True` when calling `safe_load`.")
        raise ValueError
    sn_array = df['sn'].unique()
    if len(sn_array) > 1:
        logger.error(f"Found {len(sn_array)} unique serial numbers: {sn_array}")
        raise ValueError
    device_sn = sn_array.item()
    device_model = sn_to_model(device_sn)
    return device_model

def sn_to_model(device_sn):
    """Map a device serial number to its model string.
    MOD-00246      -> modulair
    MOD-PM-00933   -> modulair-pm
    MOD-X-00993    -> modulair-x
    MOD-X-PM-01685 -> modulair-x-pm
    """
    prefix, _, _ = device_sn.rpartition("-")
    return prefix.lower().replace("mod", "modulair", 1)

def safe_load(fpath, add_sn_column=False):
    """Load a CSV or parquet file"""
    
    p = Path(fpath)

    if p.suffix == ".csv":
        as_csv = True
    elif p.suffix == ".parquet":
        as_csv = False
    else:
        raise InvalidFileExtension

    tmp = pd.read_csv(fpath, nrows=1, header=None) if as_csv else pd.read_parquet(fpath)

    if as_csv and tmp.iloc[0, 0] == "deviceModel": # hack to deal with modulair format
        logger.info("Reading rawSD card data {}", fpath)
        
        tmp = pd.read_csv(fpath, skiprows=3)

        # Optionally add the sn as a column (required for flagging rawSD data)
        if add_sn_column:
            # Grab the serial number from the header
            tmp2 = pd.read_csv(fpath, nrows=3, header=None)
            serial_number = tmp2.iloc[2, 1]
            tmp['sn'] = serial_number
            logger.info("Added serial number {} to column `sn` ", serial_number)
        
    elif as_csv and tmp.shape[1] == 2: # hack to deal with bad header format
        tmp = pd.read_csv(fpath, skiprows=1)
    elif as_csv:
        tmp = pd.read_csv(fpath)

    # drop the extra column if it was added
    unnamed = [c for c in tmp.columns if str(c).startswith("Unnamed:")]
    if unnamed:
        tmp.drop(columns=unnamed, inplace=True)

    return tmp

def determine_timestamp_column(sensor_df: pd.DataFrame) -> str:
    """Find the best column to use for timestamps."""
    for col in ("timestamp_iso", "timestamp", "timestamp_local"):
        if col in sensor_df.columns:
            return col

    raise ValueError(f"Couldn't find a timestamp column: {sensor_df.columns}")
