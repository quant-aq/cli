from pathlib import Path

from loguru import logger
import pandas as pd
import pandera.pandas as pa

from quantaq_tools.exceptions import InvalidFileExtension
from quantaq_tools.schema import build_dtype_schema, COLUMN_DEFINITIONS

def drop_unnamed(df):
    """Drop unnamed columns.
    
    Args:
        df (pd.DataFrame): DataFrame to prune columns of.
    """

    unnamed = [c for c in df.columns if str(c).startswith("Unnamed:")]
    if unnamed:
        df.drop(columns=unnamed, inplace=True)
    return df 

def infer_data_source(df, tscol=None):
    """Determine the data source (rawSD, cloudAPI, or database) from the 
    sampling frequency in the dataframe.

    Args:
        df (pd.DataFrame): DataFrame to check.
        tscol (str): the timestamp column used to infer the sampling frequency.

    Returns:
        str: the data source (i.e. "rawsd", "cloudapi", or "database")
    """

    df = fix_timestamps(df, sort_values=True)
    tscol = tscol if tscol is not None else determine_timestamp_column(df)

    # Grab the tdiff between consecutive rows
    df["tdiff"] = df[tscol].diff().dt.total_seconds()

    # normalize=True converts counts to fraction of non-nan entries
    tdiffs = df["tdiff"].dropna()
    tdiff_counts = tdiffs.value_counts(normalize=True)

    # if multiple tdiffs are found, log them and their frequencies
    if len(tdiffs.unique()) > 1:
        breakdown = ", ".join(f"{frac:.1%}: {tdiff}s" for tdiff, frac in tdiff_counts.items())
        logger.warning("Found mixed sampling frequencies: [{}]", breakdown)

    dominant_tdiff = tdiff_counts.idxmax()

    mostly_1min = dominant_tdiff == 60.0
    mostly_5sec = dominant_tdiff == 5.0
    mostly_10sec = dominant_tdiff == 10.0

    if mostly_1min:
        logger.info(f"Reading mostly {dominant_tdiff}s data --> inferring database or cloud API")
        if "api_received_at" in df.columns:
            return "cloudapi"
        else:
            return "database"
    elif mostly_5sec:
        logger.info(f"Reading mostly {dominant_tdiff}s data --> inferring rawSD")
        return "rawsd"
    elif mostly_10sec:
        logger.info(f"Reading mostly {dominant_tdiff}s data --> inferring rawSD for modulair-ufp")
        return "rawsd"
    else:
        error = NotImplementedError(f"Unrecognized dominant sampling intervals: {dominant_tdiff}")
        logger.error(error)
        raise error

def infer_data_model(df):
    """Infers the device model from the serial number in a dataframe.

    Args:
        df (pd.DataFrame): DataFrame to check.
    
    Returns:
        str: the device model / data model
    """
    if "sn" not in df.columns:
        error = ValueError("No serial number column found in dataframe, set `add_sn_column=True` when calling `safe_load`.")
        logger.error(error)
        raise error
    sn_array = df['sn'].unique()
    if len(sn_array) > 1:
        error = ValueError(f"Found {len(sn_array)} unique serial numbers: {sn_array}")
        logger.error(error)
        raise error
    device_sn = sn_array.item()
    device_model = sn_to_model(device_sn)
    return device_model

def sn_to_model(device_sn):
    """Map a device serial number to its model string.

    MOD-00246      -> modulair
    MOD-PM-00933   -> modulair-pm
    MOD-X-00993    -> modulair-x
    MOD-X-PM-01685 -> modulair-x-pm
    MOD-UFP-01685  -> modulair-ufp

    Args:
        device_sn (str): a device serial number (i.e. 'MOD-X-PM-01685')
    
    Returns:
        str: name of the device model / data model (i.e. 'modulair-x-pm')
    """
    prefix, _, _ = device_sn.rpartition("-")
    return prefix.lower().replace("mod", "modulair", 1)

def safe_load(fpath, coerce_dtypes=True):
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

    # Check dtypes    
    schema_field_dtypes = build_dtype_schema(COLUMN_DEFINITIONS)
    try:
        # print all dtype errors instead of raising on the first error
        schema_field_dtypes.validate(tmp, lazy=True)
    except pa.errors.SchemaErrors as err:
        logger.error("Dtype validation failed for file {}.", fpath)
        logger.error("{}", err.failure_cases.to_string())
        if coerce_dtypes:
            logger.warning("Coercing dtypes to expected types for file {}.", fpath)
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

    error = ValueError(f"Couldn't find a timestamp column: {df.columns}")
    logger.error(error)
    raise error 

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

    # localize the timezone if needed (should not do for timestamp_local)
    if localize_tz and tscol in ("timestamp", "timestamp_iso"):
        df[tscol] = df[tscol].apply(lambda x: x.tz_localize("UTC") if not x.tzinfo else x)

    # Drop rows with NaN/NaT datetime indices
    df = df.dropna(how='any', subset=[tscol])

    if set_index:
        if df.index.name != tscol:
            df = df.set_index(tscol)

    return df
