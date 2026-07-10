import numpy as np
from loguru import logger

from quantaq_cli.utilities import determine_timestamp_column
from quantaq_cli.variables import FLAG_DEFINITIONS


def expunge_dataframe(df):
    """Expunge a DataFrame based on values in the flag column.
    
    Args:
        df (pd.DataFrame): DataFrame to expunge.
    """
    # get the flags (in the future, this will come from the file itself)
    list_of_flags = FLAG_DEFINITIONS

    # force the flag column to be an int
    df["flag"] = df["flag"].astype(int, errors='ignore')

    # Drop nan flags (should never happen)
    if df["flag"].isna().any():
        logger.warning("Dropping {} rows with NaN flags", df["flag"].isna().sum())
        df = df.dropna(how='any', subset=["flag"])

    for label, value, cols in list_of_flags:
        mask = df["flag"] & value == value
        if not mask.any() or cols is None:
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
