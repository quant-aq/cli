from pathlib import Path
import pandas as pd
import click

from ...exceptions import InvalidFileExtension


def concat_command(files, output, **kwargs):
    verbose = kwargs.pop("verbose", False)

    # make sure the extension is csv
    output = Path(output)
    if output.suffix not in (".csv", ".feather"):
        raise InvalidFileExtension("Invalid file extension")

    save_as_csv = True if output.suffix == ".csv" else False

    # concat everything in filepath
    if verbose:
        click.secho("Files to read: {}".format(files), fg='green')

    # read all files
    data = []
    with click.progressbar(files, label="Parsing files") as bar:
        for f in bar:
            tmp = pd.read_csv(f)

            # hack: if the number of columns is 2, we need to skip a row
            if tmp.shape[1] == 2:
                click.secho("Invalid header line - skipping a row", fg="red")
                tmp = pd.read_csv(f, skiprows=1)

            data.append(tmp)

    # concat all of the files together
    df = pd.concat(data, sort=False)

    # try sorting based on a time column
    if "timestamp_iso" in df.columns:
        df = df.sort_values(by='timestamp_iso')
    elif "timestamp" in df.columns:
        df = df.sort_values(by='timestamp')

    if df.empty:
        raise Exception("No data")

    # save the file
    if verbose:
        click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        df.to_csv(output)
    else:
        df.reset_index().to_feather(output)

