import pandas as pd
from pathlib import Path

from .exceptions import InvalidFileExtension

def safe_load(fpath, **kwargs):
    """Load and return a file
    """
    p = Path(fpath)

    if p.suffix == ".csv":
        as_csv = True
    elif p.suffix == ".feather":
        as_csv = False
    else:
        raise InvalidFileExtension

    tmp = pd.read_csv(fpath) if as_csv else pd.read_feather(fpath)
    if tmp.shape[1] == 2:
        tmp = pd.read_csv(fpath, skiprows=1) if as_csv else pd.read_feather(fpath, skiprows=1)

    # drop the extra column if it was added
    if "Unnamed: 0" in tmp.columns:
        del tmp["Unnamed: 0"]
    
    return tmp