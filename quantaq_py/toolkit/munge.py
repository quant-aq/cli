import numpy as np
from pathlib import Path
import pandas as pd
from loguru import logger

from quantaq_py.exceptions import InvalidFileExtension
from quantaq_py.utilities import fix_timestamps, drop_unnamed


def clean_dataframe(df):
    """Load a dataframe, set timestamp to sorted, timezone-aware datetime index,
    drop rows where all columns are NaN, remove unnamed columns.
    
    Args:
        df (pd.DataFrame): DataFrame to clean.
    """
    
    # Fix the timestamp columns -- only if needed
    df = fix_timestamps(df, set_index=True, sort_values=True, localize_tz=True)
        
    # Force everything to be numeric
    #df = df.apply(pd.to_numeric, errors='coerce') # is this necessary?
    
    # Drop the NaNs
    #df = df.dropna(how='any') # drop rows if ANY column is nan
    all_nan_mask = df.isnull().all(axis=1)
    if all_nan_mask.any():
        logger.warning("Dropping {} rows with all NaN values", all_nan_mask.sum())
        df = df.dropna(how='all') # drop rows if ALL columns are nan
    
    # Remove unnamed columns
    df = drop_unnamed(df)

    return df
