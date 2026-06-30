from pathlib import Path

import click
import pandas as pd
import numpy as np
from loguru import logger
from terminaltables import SingleTable

from quantaq_cli.variables import FLAGS, get_flag_criteria, SUPPORTED_MODELS, SUPPORTED_SOURCES
from quantaq_cli.variables import Range, Gap
from quantaq_cli.utilities import determine_timestamp_column, safe_load
from quantaq_cli.exceptions import InvalidFileExtension, InvalidArgument, InvalidDeviceModel


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

def flag_dataframe(df, model, source):
    """
    df = pandas dataframe to be flagged (or re-flagged)
    model = the sensor model (in SUPPORTED_MODELS)
    source = the data source (database or rawsd, eventually cloudAPI as well)
    """
    df = df.copy()

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
    flag_values = {flag.name: flag.value for flag in FLAGS[model]}

    # set the flag for each flag_name and their respective crtieria 
    for flag_name, criteria in get_flag_criteria(source, model).items():
        flag_value = flag_values[flag_name]                      
        for criterion in criteria:              
            df = add_flag(df, flag_name, flag_value, criterion)
    return df

def flag_command(file, output, model, source, **kwargs):
    verbose = kwargs.pop("verbose", False)

    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    if verbose:
        click.secho("File to read: {}".format(file), fg='green')

    # load the file
    df = safe_load(file)

    # flag the dataframe
    df = flag_dataframe(df, model, source)

    # save the file
    if verbose:
        click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        df.to_csv(output)
    else:
        df.reset_index().to_feather(output)
        