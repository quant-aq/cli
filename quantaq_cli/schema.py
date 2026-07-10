import numpy as np
import pandera.pandas as pa

# Default dtypes from database / cloudAPI data
COLUMN_DEFINITIONS = [
    # --- OPC colunms ---
    ('bin0', np.float64),
    ('bin1', np.float64),
    ('bin2', np.float64),
    ('bin3', np.float64),
    ('bin4', np.float64),
    ('bin5', np.float64),
    ('bin6', np.float64),
    ('bin7', np.float64),
    ('bin8', np.float64),
    ('bin9', np.float64),
    ('bin10', np.float64),
    ('bin11', np.float64),
    ('bin12', np.float64),
    ('bin13', np.float64),
    ('bin14', np.float64),
    ('bin15', np.float64),
    ('bin16', np.float64),
    ('bin17', np.float64),
    ('bin18', np.float64),
    ('bin19', np.float64),
    ('bin20', np.float64),
    ('bin21', np.float64),
    ('bin22', np.float64),
    ('bin23', np.float64),
    ('opc.bin0', np.float64),
    ('opc.bin1', np.float64),
    ('opc.bin2', np.float64),
    ('opc.bin3', np.float64),
    ('opc.bin4', np.float64),
    ('opc.bin5', np.float64),
    ('opc.bin6', np.float64),
    ('opc.bin7', np.float64),
    ('opc.bin8', np.float64),
    ('opc.bin9', np.float64),
    ('opc.bin10', np.float64),
    ('opc.bin11', np.float64),
    ('opc.bin12', np.float64),
    ('opc.bin13', np.float64),
    ('opc.bin14', np.float64),
    ('opc.bin15', np.float64),
    ('opc.bin16', np.float64),
    ('opc.bin17', np.float64),
    ('opc.bin18', np.float64),
    ('opc.bin19', np.float64),
    ('opc.bin20', np.float64),
    ('opc.bin21', np.float64),
    ('opc.bin22', np.float64),
    ('opc.bin23', np.float64),
    ('bin1MToF', np.float64),
    ('bin3MToF', np.float64),
    ('bin5MToF', np.float64),
    ('bin7MToF', np.float64),
    ('opc_temp', np.float64),
    ('opc_rh', np.float64),
    ('opc_pm1', np.float64),
    ('opc_pm25', np.float64),
    ('opc_pm10', np.float64),
    ('opcn3_pm1', np.float64),
    ('opcn3_pm10', np.float64),
    ('opcn3_pm25', np.float64),
    ('opc.pm1', np.float64),
    ('opc.pm10', np.float64),
    ('opc.pm25', np.float64),
    ('sample_period', np.float64),
    ('opc_sample_period', np.float64),
    ('sample_flow', np.float64),
    ('opc_sample_flow', np.float64),
    ('laser_status', np.int64),
    ('opc_laser_status', np.int64),

    # --- Nephelometer columns ---
    ('pm1_std', np.float64),
    ('pm25_std', np.float64),
    ('pm10_std', np.float64),
    ('pm1_env', np.float64),
    ('pm25_env', np.float64),
    ('pm10_env', np.float64),
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
    ('neph.bin0', np.float64),
    ('neph.pm1', np.float64),
    ('neph.pm10', np.float64),
    ('neph.pm25', np.float64), 

    # --- RH / Temp / Pressure columns ---
    ('sample_rh', np.float64),
    ('sample_temp', np.float64),
    ('sample_pres', np.float64),
    ('rh', np.float64),
    ('temp', np.float64),

    # --- CO columns ---
    ('co', np.float64),
    ('co_we', np.float64),
    ('co_ae', np.float64),
    ('co_diff', np.float64),
    ('gases.co.we', np.float64),
    ('gases.co.ae', np.float64),
    ('gases.co.diff', np.float64),

    # --- NO columns ---
    ('no', np.float64),
    ('no_we', np.float64),
    ('no_ae', np.float64),
    ('no_diff', np.float64),
    ('gases.no.we', np.float64),
    ('gases.no.ae', np.float64),
    ('gases.no.diff', np.float64),

    # --- NO2 columns ---
    ('no2', np.float64),
    ('no2_we', np.float64),
    ('no2_ae', np.float64),
    ('no2_diff', np.float64),
    ('gases.no2.we', np.float64),
    ('gases.no2.ae', np.float64),
    ('gases.no2.diff', np.float64),

    # --- O3 columns ---
    ('o3', np.float64),
    ('ox_we', np.float64),
    ('ox_ae', np.float64),
    ('ox_diff', np.float64),
    ('o3_we', np.float64),
    ('o3_ae', np.float64),
    ('o3_diff', np.float64),
    ('gases.o3.we', np.float64),
    ('gases.o3.ae', np.float64),
    ('gases.o3.diff', np.float64),

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

def build_dtype_schema(column_definitions, nullable=True, required=False):
    """Build a Pandera DataFrameSchema from a list of column definitions.

    Args:
        column_definitions (list of tuples): A list of tuples where
            each tuple contains the column name and its
            corresponding data type.
        nullable (bool): Whether the columns are nullable. Default
            is True.
        required (bool): Whether the columns are required. Default
            is False.
        index_dtype (type, optional): The data type of the index.
            If None, no index is specified. Default is None.
    """
    columns = {
        name: pa.Column(dtype, nullable=nullable, required=required)
        for name, dtype in column_definitions
    }

    # index = None means no index is specified
    # strict = False allows missing and extra columns in the DataFrame
    schema = pa.DataFrameSchema(columns, index=None, strict=False)
    return schema
