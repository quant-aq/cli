from pathlib import Path

import click
import numpy as np
import pandas as pd

from quantaq_py.exceptions import InvalidFileExtension, InvalidDeviceModel
from quantaq_py.utilities import safe_load, determine_timestamp_column
from quantaq_py.variables import FLAG_DEFINITIONS, SUPPORTED_MODELS
from quantaq_py.console.commands.flag import (
    echo_flag_table
)


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

def expunge_command(file, output, **kwargs):
    verbose = kwargs.pop("verbose", False)
    dry_run = kwargs.pop("dry_run", False)
    table   = kwargs.pop("table", False)

    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    # concat everything in filepath
    if verbose:
        click.secho("File to read: {}".format(file), fg='green')

    # load the file
    df = safe_load(file)

    # expunge
    if verbose:
        click.echo("Expunging data for {}".format(file))

    df = expunge_dataframe(df)

    if dry_run or verbose:
        echo_flag_table(df)
                
    # save the file (if not a dry run)
    if not dry_run:
        if verbose:
            click.secho("Saving file to {}".format(output), fg='green')

        if save_as_csv:
            df.to_csv(output)
        else:
            df.reset_index().to_feather(output)
