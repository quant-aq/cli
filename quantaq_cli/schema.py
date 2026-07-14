import contextlib

from loguru import logger
import numpy as np
import pandera.pandas as pa


# Default dtypes
COLUMN_DEFINITIONS = [
    # --- OPC colunms ---
    ('opc_bin0', np.float64),
    ('opc_bin1', np.float64),
    ('opc_bin2', np.float64),
    ('opc_bin3', np.float64),
    ('opc_bin4', np.float64),
    ('opc_bin5', np.float64),
    ('opc_bin6', np.float64),
    ('opc_bin7', np.float64),
    ('opc_bin8', np.float64),
    ('opc_bin9', np.float64),
    ('opc_bin10', np.float64),
    ('opc_bin11', np.float64),
    ('opc_bin12', np.float64),
    ('opc_bin13', np.float64),
    ('opc_bin14', np.float64),
    ('opc_bin15', np.float64),
    ('opc_bin16', np.float64),
    ('opc_bin17', np.float64),
    ('opc_bin18', np.float64),
    ('opc_bin19', np.float64),
    ('opc_bin20', np.float64),
    ('opc_bin21', np.float64),
    ('opc_bin22', np.float64),
    ('opc_bin23', np.float64),
    ('opc_bin1MToF', np.float64),
    ('opc_bin3MToF', np.float64),
    ('opc_bin5MToF', np.float64),
    ('opc_bin7MToF', np.float64),
    ('opc_temp', np.float64),
    ('opc_rh', np.float64),
    ('opc_pm1', np.float64),
    ('opc_pm25', np.float64),
    ('opc_pm10', np.float64),
    ('opc_sample_period', np.float64),
    ('opc_sample_flow', np.float64),
    ('opc_laser_status', np.int64),

    # --- Nephelometer columns ---
    ('neph_pm1_std', np.float64),
    ('neph_pm25_std', np.float64),
    ('neph_pm10_std', np.float64),
    ('neph_pm1_env', np.float64),
    ('neph_pm25_env', np.float64),
    ('neph_pm10_env', np.float64),
    ('neph_bin0', np.float64),
    ('neph_bin1', np.float64),
    ('neph_bin2', np.float64),
    ('neph_bin3', np.float64),
    ('neph_bin4', np.float64),
    ('neph_bin5', np.float64),

    # --- RH / Temp / Pressure columns ---
    ('sample_rh', np.float64),
    ('sample_temp', np.float64),
    ('sample_pres', np.float64),

    # --- CO columns ---
    ('co', np.float64),
    ('co_we', np.float64),
    ('co_ae', np.float64),
    ('co_diff', np.float64),

    # --- NO columns ---
    ('no', np.float64),
    ('no_we', np.float64),
    ('no_ae', np.float64),
    ('no_diff', np.float64),

    # --- NO2 columns ---
    ('no2', np.float64),
    ('no2_we', np.float64),
    ('no2_ae', np.float64),
    ('no2_diff', np.float64),

    # --- O3 columns ---
    ('o3', np.float64),
    ('ox_diff', np.float64),
    ('o3_we', np.float64),
    ('o3_ae', np.float64),

    # --- CO2 columns ---
    ('co2_raw', np.float64),
    ('co2', np.float64),

    # --- SO2 columns ---
    ('so2_we', np.float64),
    ('so2_ae', np.float64),
    ('so2_diff', np.float64),
    ('so2', np.float64),

    # --- H2S columns ---
    ('h2s_we', np.float64),
    ('h2s_ae', np.float64),
    ('h2s_diff', np.float64),
    ('h2s', np.float64),

    # --- Battery columns ---
    ('bat_voltage', np.float64),
    ('soc', np.float64),
    ('vbat', np.float64),

    # --- Device / metadata columns ---
    ('fw', np.int64),
    ('flag', np.int64),
    ('connection_status', np.int16),
    ('iteration', np.int16),
    ('dd_measurement_state', np.int64),
    ('dd_operating_state', np.int64),
]

STATIC_COLUMN_RENAMES = {
    # --- OPC colunms --- 
    "opc.pm1": "opc_pm1",
    "opc.pm25": "opc_pm25",
    "opc.pm10": "opc_pm10",
    "opcn3_pm1": "opc_pm1",
    "opcn3_pm25": "opc_pm25",
    "opcn3_pm10": "opc_pm10",
    "sample_period": "opc_sample_period",
    "sample_flow": "opc_sample_flow",
    "laser_status": "opc_laser_status",

    # --- Nephelometer columns ---
    "neph.bin0": "neph_bin0",  # MODULAIR-PM's name
    "neph.cscat": "neph_bin0",  # MODULAIR's name
    "neph.pm1": "neph_pm1_env",
    "neph.pm25": "neph_pm25_env",
    "neph.pm10": "neph_pm10_env",
    "pm1_env": "neph_pm1_env",
    "pm25_env": "neph_pm25_env",
    "pm10_env": "neph_pm10_env",
    "pm1_std": "neph_pm1_std",
    "pm25_std": "neph_pm25_std",
    "pm10_std": "neph_pm10_std",

    # --- O3 columns ---
    "o3_diff": "ox_diff", 
    "ox_we": "o3_we",
    "ox_ae": "o3_ae",
 
    # --- RHT columns ---
    "temp": "sample_temp",
    "rh": "sample_rh",
}

# Prefixes for unstandardized column names
COLUMN_RENAME_PREFIXES = ("bin", "opc.bin", "met.", "gases.", "geo.")


def validate_schema(df, nullable=True, required=False, coerce_dtypes=True, coerce_rename=True):
    """Validate a DataFrame's dtypes and column names.

    Checks that columns match their expected dtypes and that no
    unstandardized column names remain.

    Args:
        nullable (bool): Whether the columns are nullable. Default is True.
        required (bool): Whether the columns are required. Default is False.
        coerce_dtypes (bool): Whether to coerce dtypes to expected types if
            dtype validation fails. Default is True.
        coerce_rename (bool): Whether to run `standardize_columns` on the
            DataFrame if unstandardized column names are found. Default is True.

    Returns:
        df (pd.DataFrame): the DataFrame with validated dtypes and column names
    """
    df = df.copy()

    columns = {
        name: pa.Column(dtype, nullable=nullable, required=required)
        for name, dtype in COLUMN_DEFINITIONS
    }

    legacy_names = set(STATIC_COLUMN_RENAMES.keys())
    prefix_patterns = COLUMN_RENAME_PREFIXES

    def _has_legacy_column_names(df):
        """Return True if any legacy names/prefixes remain."""
        has_legacy_name = bool(legacy_names.intersection(df.columns))
        has_legacy_prefix = any(
            col.startswith(p) for col in df.columns for p in prefix_patterns
        )
        return has_legacy_name or has_legacy_prefix

    def _no_legacy_column_names(df):
        """Pandera check: True if no legacy names/prefixes remain."""
        return not _has_legacy_column_names(df)

    # index = None means no index is specified
    # strict = False allows missing and extra columns in the DataFrame
    schema = pa.DataFrameSchema(
        columns,
        checks=pa.Check(
            _no_legacy_column_names,
            error="dataframe contains unstandardized column names",
        ),
        index=None,
        strict=False,
    )

    try:
        # print all schema errors instead of raising on the first error
        schema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as err:
        logger.error("Schema validation failed.")
        logger.error("{}", err.failure_cases.to_string())

        # Check the actual condition directly rather than parsing
        # failure_cases["check"], since pandera's naming of anonymous
        # check functions in that column isn't a stable contract.
        if coerce_rename and _has_legacy_column_names(df):
            logger.warning("Standardizing unstandardized column names.")
            df = standardize_columns(df)

        if coerce_dtypes:
            logger.warning("Coercing dtypes to expected types.")
            dtype_map = {
                col: dtype for col, dtype in COLUMN_DEFINITIONS
                if col in df.columns
            }
            df = df.astype(dtype_map)

        if coerce_rename or coerce_dtypes:
            try:
                schema.validate(df, lazy=True)
                logger.info("Schema validation passed after coercion.")
            except pa.errors.SchemaErrors as second_err:
                logger.error("Schema validation still failing after coercion.")
                logger.error("{}", second_err.failure_cases.to_string())

    return df

def drop_unnamed(df):
    """Drop unnamed columns.
    
    Args:
        df (pd.DataFrame): DataFrame to prune columns of.
    """

    unnamed = [c for c in df.columns if str(c).startswith("Unnamed:")]
    if unnamed:
        df.drop(columns=unnamed, inplace=True)
    return df

def standardize_columns(df):
    """Standardize column names.

    Note that this doesn't remove any columns, it simply adds diff columns if
    they don't exist and standardizes naming.

    Args:
        df (pd.DataFrame): the dataframe to be standardized
    """

    df = df.copy()

    # copy so the dynamic renames below don't mutate the module-level
    # STATIC_COLUMN_RENAMES dict used by validate_schema
    column_renames = dict(STATIC_COLUMN_RENAMES)

    # bin0 --> opc_bin0, etc..
    for column in df.columns:
        if column.startswith("bin"):  # opc_bin0, opc_bin23
            column_renames[column] = column.replace("bin", "opc_bin")

    # Add diff columns (we minus ae) if they don't already exist
    if not any('diff' in col for col in df.columns):
        for pollutant in ("co", "no", "no2"):
            with contextlib.suppress(KeyError):
                df[f"{pollutant}_diff"] = (
                    df[f"{pollutant}_we"] - df[f"{pollutant}_ae"]
                )
        with contextlib.suppress(KeyError):
            df["ox_diff"] = df["ox_we"] - df["no2_we"]
            df["ox_diff"] = df["o3_we"] - df["no2_we"]

    # CloudAPI schema to database schema
    for column in df.columns:
        if column.startswith("opc.bin"):  # opc_bin0, opc_bin23
            column_renames[column] = column.replace(".", "_")
        elif column.startswith("met."):
            column_renames[column] = column.replace("met.", "")
        elif column.startswith("gases."):
            if column != 'gases.o3.diff':
                new_column = column.removeprefix("gases.").replace(".", "_")
            else:
                new_column = 'ox_diff'
            column_renames[column] = new_column
        elif column.startswith("geo."):
            column_renames[column] = column.removeprefix("geo.")

    df = df.rename(columns=column_renames)
    df = drop_unnamed(df)
    return df
