#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np
# import re
import click

from ...exceptions import InvalidFileExtension


COLUMN_DEFINITIONS = [
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
    ('bin1MToF', np.float32),
    ('bin3MToF', np.float32),
    ('bin5MToF', np.float32),
    ('bin7MToF', np.float32),
    ('sample_period', np.float32),
    ('sample_flow', np.float32),
    ('opc_temp', np.float32),
    ('opc_rh', np.float32),
    ('opc_pm1', np.float32),
    ('opc_pm25', np.float32),
    ('opc_pm10', np.float32),
    ('laser_status', np.int16),
    ('pm1_std', np.float32),
    ('pm25_std', np.float32),
    ('pm10_std', np.float32),
    ('pm1_env', np.float32),
    ('pm25_env', np.float32),
    ('pm10_env', np.float32),
    ('neph_bin0', np.float32),
    ('neph_bin1', np.float32),
    ('neph_bin2', np.float32),
    ('neph_bin3', np.float32),
    ('neph_bin4', np.float32),
    ('neph_bin5', np.float32),
    ('sample_rh', np.float32),
    ('sample_temp', np.float32),
    ('sample_pres', np.float32),
    ('fw', np.int16),
    ('flag', np.int16),
    ('connection_status', np.int16),
    ('iteration', np.int16),
]


def clean_file(filepath, savepath, **kwargs):
    """_summary_
    """
    # make sure the extension is csv
    output = Path(savepath)
    if output.suffix not in (".csv"):
        raise InvalidFileExtension("Invalid file extension")
    
    # Load the data
    df = pd.read_csv(filepath, on_bad_lines='skip', encoding='unicode_escape', low_memory=False)
    
    # Fix the timestamp column(s)
    for c in ('timestamp', 'timestamp_local', 'timestamp_iso'):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')
    
    # Set the index
    for c in ('timestamp', 'timestamp_iso'):
        if c in df.columns:
            df = df.set_index(c)
            break
        
    # Force everything to be numeric
    df = df.apply(pd.to_numeric, errors='coerce')
    
    # Drop the NaNs
    df = df.dropna(how='any')
    
    # Clean up any unneeded columns
    for c in df.columns:
        if "Unnamed" in c:
            del df[c]
            
    # Reduce memory use by cleaning up all the column types
    for cname, ctype in COLUMN_DEFINITIONS:
        if cname in df.columns:
            df[cname] = df[cname].astype(ctype)
            
    # Save the file
    df.to_csv(savepath)
