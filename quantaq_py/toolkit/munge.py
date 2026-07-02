import numpy as np
from pathlib import Path
import pandas as pd

from quantaq_py.exceptions import InvalidFileExtension
from quantaq_py.utilities import determine_timestamp_column


def clean_dataframe(df):
    """Load a dataframe, clean it, and save to csv. 

    Removes corrupt data and force columns to be the 
    desired column type based on the specific column.
    """
    
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
            
    return df
