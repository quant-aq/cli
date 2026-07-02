from pathlib import Path

from loguru import logger
import pandas as pd
import pandera.pandas as pa

from quantaq_py.exceptions import InvalidFileExtension
from quantaq_py.schema import build_dtype_schema, COLUMN_DEFINITIONS

def infer_data_source(df):
    """Determine the data source (rawSD, cloudAPI, or database) from the 
    sampling frequency in the dataframe.

    Args:
        df (pd.DataFrame): DataFrame to check.

    Returns:
        str: the data source (i.e. "rawsd", "cloudapi", or "database")
    """

    df = fix_timestamps(df, sort_values=True)
    tscol = determine_timestamp_column(df)

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
    """Infers the device model from the serial number in a dataframe.

    Args:
        df (pd.DataFrame): DataFrame to check.
    
    Returns:
        str: the device model / data model
    """
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

    Args:
        device_sn (str): a device serial number (i.e. 'MOD-X-PM-01685')
    
    Returns:
        str: name of the device model / data model (i.e. 'modulair-x-pm')
    """
    prefix, _, _ = device_sn.rpartition("-")
    return prefix.lower().replace("mod", "modulair", 1)

def safe_load(fpath, coerce_dtypes=False):
    """Load a CSV or parquet file.
    
    Args:
        fpath (str or Path): Path to the CSV or parquet file.
        coerce_dtypes (bool): Whether to coerce dtypes to expected types.

    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    
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
    unnamed = [c for c in tmp.columns if str(c).startswith("Unnamed:")]
    if unnamed:
        tmp.drop(columns=unnamed, inplace=True)

    # Check dtypes    
    schema_field_dtypes = build_dtype_schema(COLUMN_DEFINITIONS)
    try:
        # print all dtype errors instead of raising on the first error
        schema_field_dtypes.validate(tmp, lazy=True)
    except pa.errors.SchemaErrors as err:
        logger.error("Dtype validation failed for file {}.", fpath)
        logger.debug("{}", err.failure_cases.to_string())
        if coerce_dtypes:
            logger.warning("Coercing dtypes to expected types.")
            dtype_map = {
                col: dtype for col, dtype in COLUMN_DEFINITIONS
                if col in tmp.columns
            }
            tmp = tmp.astype(dtype_map)

    return tmp

def determine_timestamp_column(df):
    """Find the best column to use for timestamps.

    Args:
        df (pd.DataFrame): DataFrame to check. 
    
    Returns:
        str: Name of the timestamp column.
    """
    for col in ("timestamp_iso", "timestamp", "timestamp_local"):
        if col in df.columns:
            return col

    raise ValueError(f"Couldn't find a timestamp column: {df.columns}")

def fix_timestamps(df, set_index=False, sort_values=False, localize_tz=False):
    """Fix the timestamps (convert to datetime index, sort by 
    timestamp, drop nans.)
        
    Args:
        df (pd.DataFrame): DataFrame to fix.
        set_index (bool): Whether to set the best timestamp column
            as the DataFrame's index. Default is False.
        sort_values (bool): Whether to sort the DataFrame by the
            best timestamp column. Default is False.
        localize_tz (bool): Whether to localize naive timestamps
            to UTC. Default is False.
    """
    # Convert timestamp columns to datetime, if needed
    for c in ('timestamp', 'timestamp_local', 'timestamp_iso'):
        if c in df.columns and not pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = pd.to_datetime(df[c], errors='coerce')

    # Set index to best timestamp column, if not already set
    tscol = determine_timestamp_column(df)

    # Sort the dataframe by the best timestamp column
    if sort_values:
        df = df.sort_values(by=tscol)

    # localize the timezone if needed
    if localize_tz:
        df[tscol] = df[tscol].apply(lambda x: x.tz_localize("UTC") if not x.tzinfo else x)

    # Drop rows with NaN/NaT datetime indices
    df = df.dropna(how='any', subset=[tscol])

    if set_index:
        if df.index.name != tscol:
            df = df.set_index(tscol)

    return df
