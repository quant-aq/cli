from loguru import logger

from quantaq_cli.schema import validate_schema
from quantaq_cli.utilities import fix_timestamps


def clean_dataframe(df, coerce_dtypes=True, coerce_rename=True):
    """Convert timestamps to sorted, timezone-aware, datetime objects; standardize 
    the schema and optionally coerce dtypes; drop rows where all 
    columns are NaN, remove unnamed columns.
    
    Args:
        df (pd.DataFrame): DataFrame to clean.
    """
    
    # Fix the timestamp columns -- only if needed
    df = fix_timestamps(df, set_index=False, sort_values=True, localize_tz=True)

    # Drop the NaNs
    all_nan_mask = df.isnull().all(axis=1)
    if all_nan_mask.any():
        logger.warning("Dropping {} rows with all NaN values", all_nan_mask.sum())
        df = df.dropna(how='all') # drop rows if ALL columns are nan
    
    # Validate the schema
    # by default this also coerces dtypes and column names, but that can be overrided
    df = validate_schema(df, coerce_dtypes=coerce_dtypes, coerce_rename=coerce_rename)

    return df
