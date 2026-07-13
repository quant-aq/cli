from loguru import logger
import pandera.pandas as pa

from quantaq_cli.schema import COLUMN_DEFINITIONS
from quantaq_cli.schema import standardize_columns, build_dtype_schema
from quantaq_cli.utilities import fix_timestamps, drop_unnamed


def clean_dataframe(df, coerce_dtypes=True):
    """Convert timestamps to sorted, timezone-aware, datetime objects; standardize 
    the schema and optionally coerce dtypes; drop rows where all 
    columns are NaN, remove unnamed columns.
    
    Args:
        df (pd.DataFrame): DataFrame to clean.
    """
    
    # Fix the timestamp columns -- only if needed
    df = fix_timestamps(df, set_index=False, sort_values=True, localize_tz=True)

    # standardize schema
    df = standardize_columns(df)
        
    # Force everything to be numeric
    # Check dtypes    
    schema_field_dtypes = build_dtype_schema(COLUMN_DEFINITIONS)
    try:
        # print all dtype errors instead of raising on the first error
        schema_field_dtypes.validate(df, lazy=True)
    except pa.errors.SchemaErrors as err:
        logger.error("Dtype validation failed.")
        logger.error("{}", err.failure_cases.to_string())
        if coerce_dtypes:
            logger.warning("Coercing dtypes to expected types.")
            dtype_map = {
                col: dtype for col, dtype in COLUMN_DEFINITIONS
                if col in df.columns
            }
            df = df.astype(dtype_map)

    # Drop the NaNs
    all_nan_mask = df.isnull().all(axis=1)
    if all_nan_mask.any():
        logger.warning("Dropping {} rows with all NaN values", all_nan_mask.sum())
        df = df.dropna(how='all') # drop rows if ALL columns are nan
    
    # Remove unnamed columns
    df = drop_unnamed(df)

    return df
