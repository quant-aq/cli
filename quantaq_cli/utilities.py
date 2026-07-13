from pathlib import Path

from loguru import logger
import pandas as pd
import pandera.pandas as pa

from quantaq_cli.exceptions import InvalidFileExtension
from quantaq_cli.schema import COLUMN_DEFINITIONS
from quantaq_cli.schema import standardize_columns, build_dtype_schema


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
    """Determine the data source (rawSD or database) from the 
    sampling frequency in the dataframe.

    NOTE: data from the cloudAPI will be identical to data from the database 
    if the column names are standardized (by calling either standardize_columns()
    or clean_dataframe())

    Args:
        df (pd.DataFrame): DataFrame to check.
        tscol (str): the timestamp column used to infer the sampling frequency.

    Returns:
        str: the data source (i.e. "rawsd", "database")
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
        logger.info(f"Reading mostly {dominant_tdiff}s data --> inferring database")
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
        error = ValueError("No serial number column found in dataframe. Use `safe_load` to read the file.")
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
