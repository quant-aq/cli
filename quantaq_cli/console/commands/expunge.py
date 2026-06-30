from pathlib import Path

import click
import numpy as np
import pandas as pd
import rich
from rich.table import Table

from quantaq_cli.exceptions import InvalidFileExtension, InvalidDeviceModel
from quantaq_cli.utilities import safe_load
from quantaq_cli.variables import FLAG_DEFINITIONS, SUPPORTED_MODELS


def expunge_dataframe(df):

    # get the flags (in the future, this will come from the file itself)
    list_of_flags = FLAG_DEFINITIONS

    # force the flag column to be an int
    df["flag"] = df["flag"].astype(int, errors='ignore')

    # Drop NaNs
    df = df.dropna(how='any', subset=["flag"])

    for label, value, cols in list_of_flags:
        mask = df["flag"] & value == value
        n_affected = mask.sum()
        pct_affected = round((n_affected / df.shape[0]) * 100.0, 2)

        # NaN the necessary columns
        if cols is None:
            cols = df.columns
        elif len(cols) > 0:
            cols = [c for c in cols if c in df.columns]
    
        # set the mask
        df.loc[mask, cols] = np.nan

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
