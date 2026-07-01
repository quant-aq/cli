import numpy as np

from quantaq_py.utilities import determine_timestamp_column
from quantaq_py.variables import FLAG_DEFINITIONS


def expunge_dataframe(df):

    # get the flags (in the future, this will come from the file itself)
    list_of_flags = FLAG_DEFINITIONS

    # force the flag column to be an int
    df["flag"] = df["flag"].astype(int, errors='ignore')

    # Drop NaNs
    df = df.dropna(how='any', subset=["flag"])

    for label, value, cols in list_of_flags:
        mask = df["flag"] & value == value
        if not mask.any():
            continue

        # NaN the necessary columns
        if cols == "all_columns":
            tscol = determine_timestamp_column(df)
            cols_to_keep = {tscol, "sn", "flag"}
            cols = [c for c in df.columns if c not in cols_to_keep]
        elif len(cols) > 0:
            cols = [c for c in cols if c in df.columns]
    
        # set the mask
        df.loc[mask, cols] = np.nan

    return df
