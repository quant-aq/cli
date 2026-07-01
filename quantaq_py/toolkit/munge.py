import numpy as np
from pathlib import Path
import pandas as pd

from quantaq_py.exceptions import InvalidFileExtension
from quantaq_py.utilities import safe_load, determine_timestamp_column


COLUMN_DEFINITIONS = [
    # --- OPC colunms ---
    ('bin0', np.float32),
    ('bin1', np.float32),
    ('bin2', np.float32),
    ('bin3', np.float32),
    ('bin4', np.float32),
    ('bin5', np.float32),
    ('bin6', np.float32),
    ('bin7', np.float32),
    ('bin8', np.float32),
    ('bin9', np.float32),
    ('bin10', np.float32),
    ('bin11', np.float32),
    ('bin12', np.float32),
    ('bin13', np.float32),
    ('bin14', np.float32),
    ('bin15', np.float32),
    ('bin16', np.float32),
    ('bin17', np.float32),
    ('bin18', np.float32),
    ('bin19', np.float32),
    ('bin20', np.float32),
    ('bin21', np.float32),
    ('bin22', np.float32),
    ('bin23', np.float32),
    ('opc.bin0', np.float32),
    ('opc.bin1', np.float32),
    ('opc.bin2', np.float32),
    ('opc.bin3', np.float32),
    ('opc.bin4', np.float32),
    ('opc.bin5', np.float32),
    ('opc.bin6', np.float32),
    ('opc.bin7', np.float32),
    ('opc.bin8', np.float32),
    ('opc.bin9', np.float32),
    ('opc.bin10', np.float32),
    ('opc.bin11', np.float32),
    ('opc.bin12', np.float32),
    ('opc.bin13', np.float32),
    ('opc.bin14', np.float32),
    ('opc.bin15', np.float32),
    ('opc.bin16', np.float32),
    ('opc.bin17', np.float32),
    ('opc.bin18', np.float32),
    ('opc.bin19', np.float32),
    ('opc.bin20', np.float32),
    ('opc.bin21', np.float32),
    ('opc.bin22', np.float32),
    ('opc.bin23', np.float32),
    ('bin1MToF', np.float32),
    ('bin3MToF', np.float32),
    ('bin5MToF', np.float32),
    ('bin7MToF', np.float32),
    ('sample_period', np.float32),
    ('opc_sample_period', np.float32),
    ('sample_flow', np.float32),
    ('opc_sample_flow', np.float32),
    ('opc_temp', np.float32),
    ('opc_rh', np.float32),
    ('opc_pm1', np.float32),
    ('opc_pm25', np.float32),
    ('opc_pm10', np.float32),
    ('opcn3_pm1', np.float32),
    ('opcn3_pm25', np.float32),
    ('opcn3_pm10', np.float32),
    ('laser_status', np.int16),
    ('opc_laser_status', np.int16),

    # --- Nephelometer columns ---
    ('pm1_std', np.float32),
    ('pm25_std', np.float32),
    ('pm10_std', np.float32),
    ('pm1_env', np.float32),
    ('pm25_env', np.float32),
    ('pm10_env', np.float32),
    ('neph_pm1_std', np.float32),
    ('neph_pm25_std', np.float32),
    ('neph_pm10_std', np.float32),
    ('neph_pm1_env', np.float32),
    ('neph_pm25_env', np.float32),
    ('neph_pm10_env', np.float32),
    ('neph_bin0', np.float32),
    ('neph_bin1', np.float32),
    ('neph_bin2', np.float32),
    ('neph_bin3', np.float32),
    ('neph_bin4', np.float32),
    ('neph_bin5', np.float32),

    # --- RH / Temp / Pressure columns ---
    ('sample_rh', np.float32),
    ('sample_temp', np.float32),
    ('sample_pres', np.float32),
    ('rh', np.float32),
    ('temp', np.float32),

    # --- CO columns ---
    ('co', np.float32),
    ('co_we', np.float32),
    ('co_ae', np.float32),
    ('co_diff', np.float32),
    ('gases.co.we', np.float32),
    ('gases.co.ae', np.float32),
    ('gases.co.diff', np.float32),

    # --- NO columns ---
    ('no', np.float32),
    ('no_we', np.float32),
    ('no_ae', np.float32),
    ('no_diff', np.float32),
    ('gases.no.we', np.float32),
    ('gases.no.ae', np.float32),
    ('gases.no.diff', np.float32),

    # --- NO2 columns ---
    ('no2', np.float32),
    ('no2_we', np.float32),
    ('no2_ae', np.float32),
    ('no2_diff', np.float32),
    ('gases.no2.we', np.float32),
    ('gases.no2.ae', np.float32),
    ('gases.no2.diff', np.float32),

    # --- O3 columns ---
    ('o3', np.float32),
    ('ox_we', np.float32),
    ('ox_ae', np.float32),
    ('ox_diff', np.float32),
    ('o3_we', np.float32),
    ('o3_ae', np.float32),
    ('o3_diff', np.float32),
    ('gases.o3.we', np.float32),
    ('gases.o3.ae', np.float32),
    ('gases.o3.diff', np.float32),

    # --- CO2 columns ---
    ('co2_raw', np.float32),
    ('co2', np.float32),

    # --- SO2 columns ---
    ('so2_we', np.float32),
    ('so2_ae', np.float32),
    ('so2_diff', np.float32),
    ('so2', np.float32),

    # --- H2S columns ---
    ('h2s_we', np.float32),
    ('h2s_ae', np.float32),
    ('h2s_diff', np.float32),
    ('h2s', np.float32),

    # --- Battery columns ---
    ('bat_voltage', np.float32),
    ('soc', np.float32),
    ('vbat', np.float32),

    # --- Device / metadata columns ---
    ('fw', np.int16),
    ('flag', np.int16),
    ('connection_status', np.int16),
    ('iteration', np.int16),
]


def clean_file(filepath):
    """Load a file, clean it, and save to csv. 

    Removes corrupt data and force columns to be the 
    desired column type based on the specific column.
    """
    # Load the data
    df = safe_load(filepath)
    
    # Fix the timestamp column(s)
    for c in ('timestamp', 'timestamp_local', 'timestamp_iso'):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')
    
    # Set the index
    tscol = determine_timestamp_column(df)
    df = df.set_index(tscol)
        
    # Force everything to be numeric
    df = df.apply(pd.to_numeric, errors='coerce')
    
    # Drop the NaNs
    #df = df.dropna(how='any') # drop rows if ANY column is nan
    df = df.dropna(how='all') # drop rows if EVERY column is nan
            
    # Reduce memory use by cleaning up all the column types
    for cname, ctype in COLUMN_DEFINITIONS:
        if cname in df.columns:
            df[cname] = df[cname].astype(ctype)
            
    return df
