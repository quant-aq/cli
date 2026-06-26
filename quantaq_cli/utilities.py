import pandas as pd
from pathlib import Path

from quantaq_cli.exceptions import InvalidFileExtension


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

    tmp = pd.read_csv(fpath, nrows=1, header=None) if as_csv else pd.read_feather(fpath)

    if tmp.iloc[0, 0] == "deviceModel": # hack to deal with modulair format
        tmp = pd.read_csv(fpath, skiprows=3) if as_csv else pd.read_feather(fpath, skiprows=3)
    elif tmp.shape[1] == 2: # hack to deal with bad header format
        tmp = pd.read_csv(fpath, skiprows=1) if as_csv else pd.read_feather(fpath, skiprows=1)
    else:
        tmp = pd.read_csv(fpath) if as_csv else pd.read_feather(fpath)

    # drop the extra column if it was added
    unnamed = [c for c in tmp.columns if str(c).startswith("Unnamed:")]
    if unnamed:
        tmp.drop(columns=unnamed, inplace=True)

    return tmp

def determine_timestamp_column(sensor_df: pd.DataFrame) -> str:
    """Find the best column to use for timestamps."""
    for col in ("timestamp_iso", "timestamp", "timestamp_local"):
        if col in sensor_df.columns:
            return col

    raise ValueError(f"Couldn't find a timestamp column: {sensor_df.columns}")
