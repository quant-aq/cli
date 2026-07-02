from pathlib import Path

from loguru import logger
import pandas as pd
import rich
from rich.table import Table

from quantaq_py.variables import FLAG_DEFINITIONS, SUPPORTED_MODELS, SUPPORTED_SOURCES
from quantaq_py.variables import Range, Gap, flag_name_to_criteria
from quantaq_py.utilities import fix_timestamps, determine_timestamp_column
from quantaq_py.utilities import infer_data_source, infer_data_model


def _add_flag(df, flag_name, flag_value, criterion):
    """Add a specific flag to a DataFrame based on a given criterion.

    For each row that meets the specified criterion, this function modifies the 'flag' 
    column by applying a bitwise OR operation with the given flag value.

    Args:
        df (pd.DataFrame): DataFrame to which the flag will be added.
        flag_name (str): Name of the flag to be added.
        flag_value (int): Bitmask value of the flag to be added.
        criterion (Range or Gap): Logic based on which the flag will be added.
    
    Returns:
        pd.DataFrame: DataFrame with the flag added.
    """
    if isinstance(criterion, Range):
        if criterion.column in df.columns:
            col = df[criterion.column]
            mask = (col < criterion.lo) | (col > criterion.hi)
            if not mask.sum():
                return df
            df.loc[mask, "flag"] |= flag_value
            logger.info(
                f"Flagged: {flag_name} (flag {flag_value}) --> {mask.sum()} rows",
            )

    elif isinstance(criterion, Gap):
        # sort based on a time column
        df = fix_timestamps(df, sort_values=True)
        tscol = determine_timestamp_column(df)

        # Create a column to hold the time diff
        df["tdiff"] = df[tscol].diff().dt.total_seconds()

        # If we're missing enough data, apply the startup flag.
        startup_mask = df["tdiff"] > criterion.gap_in_seconds
        starts = df.loc[startup_mask]
        postgap_delta = pd.Timedelta(seconds=criterion.post_gap_flag_length_seconds)

        for _, row in starts.iterrows():
            # Flag everything between the startup flag's timestamp up to the gap.
            mask = (df[tscol] >= row[tscol]) & (
                df[tscol] <= (row[tscol] + postgap_delta)
            )
            df.loc[mask, "flag"] |= flag_value  
            logger.info(
                f"Flagged: {flag_name} (flag {flag_value}) --> {mask.sum()} rows",
            )

        # Delete the tdiff col
        del df["tdiff"]

    return df

def flag_summary(df):
    """Create a table with a summary of flags.

    Args:
        df (pd.DataFrame): DataFrame with flags to summarize.
    
    Returns:
        pd.DataFrame: A new DataFrame, suitable for human consumption.
    """

    # create flag column if it doesn't exist
    if "flag" not in df.columns:
        df["flag"] = 0

    # force the flag column to be an int
    df["flag"] = df["flag"].astype(int, errors='ignore')

    rows = []
    for name, value, cols in FLAG_DEFINITIONS:
        mask = df["flag"] & value
        num_naffected = mask.astype(bool).sum()
        percent_affected = f"{100 * num_naffected / df.shape[0]:.1f}"
        rows.append([name, int(value), num_naffected, percent_affected])

    explained_df = pd.DataFrame(
        rows,
        columns=["FLAG", "FLAG VALUE", "# OCCURENCES", "% DATA"],
    ).set_index("FLAG")
    return explained_df

def echo_flag_table(df):
    """Print a table of flag statistics for a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with flags to summarize.
    """
    explained_df = flag_summary(df)

    table = Table()
    for column in ["FLAG", *explained_df.columns]:
        table.add_column(
            column,
            justify="right" if column != "FLAG" else "left",
            style="bold",
        )
    for row in explained_df.itertuples():
        table.add_row(*map(str, row))
    rich.print(table)

def flag_dataframe(df):
    """Re-flags a DataFrame by iterating through the FLAG_DEFINITIONS and calling
    the _add_flag() function one-by-one.

    Args:
        df (pd.DataFrame): DataFrame to be flagged (or re-flagged).

    Returns:
        pd.DataFrame: The flagged DataFrame.
    """
    df = df.copy()

    model = infer_data_model(df)
    source = infer_data_source(df)

    # get flag criteria (this also checks if model and data source is valid)
    name_to_criteria = flag_name_to_criteria(source, model).items()

    # create flag column if it doesn't exist
    if "flag" not in df.columns:
        df["flag"] = 0

    # get the flag values for each flag name
    FLAG_VALUES = {flag.name: flag.value for flag in FLAG_DEFINITIONS}

    # set the flag for each flag_name and their respective crtieria 
    for flag_name, criteria in name_to_criteria:
        flag_value = FLAG_VALUES[flag_name]                      
        for criterion in criteria:              
            df = _add_flag(df, flag_name, flag_value, criterion)
    return df
