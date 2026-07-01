from pathlib import Path

import click
import pandas as pd
import numpy as np
from loguru import logger
import rich
from rich.table import Table
from terminaltables import SingleTable

from quantaq_py.exceptions import InvalidFileExtension, InvalidArgument, InvalidDeviceModel
from quantaq_py.variables import FLAG_DEFINITIONS, SUPPORTED_MODELS, SUPPORTED_SOURCES
from quantaq_py.variables import Range, Gap, get_flag_criteria
from quantaq_py.utilities import determine_timestamp_column, safe_load
from quantaq_py.utilities import infer_data_source, infer_data_model


def add_flag(df, flag_name, flag_value, criterion):
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
        # Find best timestamp column.
        tscol = determine_timestamp_column(df)

        # Force timestamp type
        df[tscol] = df[tscol].map(pd.to_datetime)

        # Sort by timestamp
        df = df.sort_values(tscol)

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

    Parameters
    ----------
    sensor_df
        DataFrame with flags to summarize.

    Returns
    -------
        A new DataFrame, suitable for human consumption.

    TO DO: move this to flag.py after merging sc-20242
    """
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

    Parameters
    ----------
    sensor_df
        DataFrame to describe.

    TO DO: move this to flag.py after merging sc-20242
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
    """
    df = pandas dataframe to be flagged (or re-flagged)
    model = the sensor model (in SUPPORTED_MODELS)
    source = the data source (database or rawsd, eventually cloudAPI as well)
    """
    df = df.copy()

    model = infer_data_model(df)
    source = infer_data_source(df)

    # ensure the model is valid
    if model not in SUPPORTED_MODELS:
        raise InvalidDeviceModel("Invalid device model. Must be one of {}".format(SUPPORTED_MODELS))
    
    # ensure the data source is valid
    if source not in SUPPORTED_SOURCES:
        raise NotImplementedError # add this to exceptions

    # create flag column if it doesn't exist
    if "flag" not in df.columns:
        df["flag"] = 0

    # get the flag values for each flag name
    FLAG_VALUES = {flag.name: flag.value for flag in FLAG_DEFINITIONS}

    # set the flag for each flag_name and their respective crtieria 
    for flag_name, criteria in get_flag_criteria(source, model).items():
        flag_value = FLAG_VALUES[flag_name]                      
        for criterion in criteria:              
            df = add_flag(df, flag_name, flag_value, criterion)
    return df
