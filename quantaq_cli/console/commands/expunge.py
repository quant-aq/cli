from pathlib import Path
import pandas as pd
import numpy as np
import click
from terminaltables import SingleTable

from ...exceptions import InvalidFileExtension, InvalidDeviceModel
from ...utilities import safe_load
from ...variables import FLAGS, SUPPORTED_MODELS


def expunge_command(file, output, **kwargs):
    verbose = kwargs.pop("verbose", False)
    dry_run = kwargs.pop("dry_run", False)
    flagcol = kwargs.pop("flagcol", "flag")
    model   = kwargs.pop("model", "modulair_pm")

    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid file extension")

    # ensure the model is valid
    if model not in SUPPORTED_MODELS:
        raise InvalidDeviceModel("Invalid device model. Must be one of {}".format(SUPPORTED_MODELS))

    save_as_csv = True if output.suffix == ".csv" else False

    # concat everything in filepath
    if verbose:
        click.secho("File to read: {}".format(file), fg='green')

    # load the file
    df = safe_load(file)

    if verbose:
        click.echo("Expunging data for {}".format(model))

    # init an array to hold the table data
    data = []
    data.append(["FLAG", "FLAG VALUE", "# OCCURENCES", "% DATA"])

    # get the flags (in the future, this will come from the file itself)
    list_of_flags = FLAGS.get(model)

    # force the flag column to be an int
    df[flagcol] = df[flagcol].astype(int)

    for label, value, cols in list_of_flags:
        mask = df[flagcol] & value == value
        n_affected = mask.sum()
        pct_affected = round((n_affected / df.shape[0]) * 100.0, 2)

        # NaN the necessary columns
        if cols is None:
            cols = df.columns
        elif len(cols) > 0:
            cols = [c for c in cols if c in df.columns]
    
        # set the mask
        df.loc[mask, cols] = np.nan

        # add a row to the output table
        data.append([label, value, n_affected, pct_affected])

    if dry_run or verbose:
        table = SingleTable(data)
        table.title = "Flag Breakdown".upper()

        click.echo(table.table)
    
    # save the file (if not a dry run)
    if not dry_run:
        if verbose:
            click.secho("Saving file to {}".format(output), fg='green')

        if save_as_csv:
            df.to_csv(output)
        else:
            df.reset_index().to_feather(output)
