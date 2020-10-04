from pathlib import Path
import pandas as pd
import numpy as np
import click

from ...exceptions import InvalidFileExtension
from ...utilities import safe_load


def merge_command(files, output, **kwargs):
    verbose = kwargs.pop("verbose", False)
    tscol   = kwargs.pop("tscol", "timestamp")

    # make sure the extension is either a csv or feather format
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    # concat everything in filepath
    if verbose:
        click.secho("Files to read: {}".format(files), fg='green')

    df = pd.DataFrame()
    with click.progressbar(files, label="Parsing files") as bar:
        for f in bar:
            if verbose:
                click.secho("Now reading {}".format(f), fg='green')

            tmp = safe_load(f)

            # check for the column name
            if not tscol in tmp.columns:
                click.secho("Time tscol was not found in the file.", fg='red')
                continue
                
            # convert the timestamp column to a pandas datetime
            if type(tmp[tscol]) != np.datetime64:
                tmp[tscol] = tmp[tscol].map(pd.to_datetime)

            # set the index
            tmp.set_index(tscol, inplace=True)
            
            # force to UTC
            if tscol == "timestamp":
                try:
                    tmp.index = tmp.index.tz_localize("UTC")
                except TypeError:
                    pass
            
            # merge with the other files
            df = pd.merge(df, tmp, left_index=True, right_index=True, how='outer')       

    # save the file
    if verbose:
        click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        df.to_csv(output)
    else:
        df.reset_index().to_feather(output)

