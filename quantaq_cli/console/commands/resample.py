from pathlib import Path
import pandas as pd
import numpy as np
import click

from ...exceptions import InvalidFileExtension
from ...utilities import safe_load


def resample_command(file, interval, output, **kwargs):
    verbose = kwargs.pop("verbose", False)
    tscol   = kwargs.pop("tscol", "timestamp")
    method  = kwargs.pop("method", "mean")

    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    # concat everything in filepath
    if verbose:
        click.secho("Files to read: {}".format(file), fg='green')

    # load the file
    df = safe_load(file)

    # if tscol needs to be made a datetime obj, do so
    if tscol not in df.columns:
        raise Exception("Invalid column name for the timestamp")

    # resample
    if type(df[tscol]) != np.datetime64:
        df[tscol] = df[tscol].map(pd.to_datetime)

    df = df.resample(interval, on=tscol)

    if method == "mean":
        df = df.mean()
    elif method == "median":
        df = df.median()
    elif method == "max":
        df = df.max()
    elif method == "min":
        df = df.min()
    elif method == "sum":
        df = df.sum()
    else:
        raise Exception("Invalid argument for INTERVAL")

    # save the file
    if verbose:
        click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        df.to_csv(output)
    else:
        df.reset_index().to_feather(output)
