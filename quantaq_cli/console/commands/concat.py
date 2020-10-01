from pathlib import Path
import pandas as pd
import numpy as np
import re
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
            tmp = pd.read_csv(f, nrows=1, header=None)

            # hack to support new products with a different file format
            if tmp.iloc[0, 0] == 'deviceModel':
                tmp = pd.read_csv(f, skiprows=3)
            elif tmp.shape[1] == 2:
                tmp = pd.read_csv(f, skiprows=1)
            else:
                tmp = pd.read_csv(f)

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


def concat_logs_command(files, output, **kwargs):
    verbose = kwargs.pop("verbose", False)

    # make sure the extension is txt
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
            for line in open(f, "r"):
                items = line.split(":")
                pre, msg = items[0], items[1:]

                msg = ":".join(msg).strip("\n")

                try:
                    millis, location, level = re.split("[ ]", pre)
                except:
                    continue
                
                location = location[1:-1]

                data.append(dict(millis=int(millis), location=location, level=level, message=msg))
    
    # concat all results
    data = pd.DataFrame.from_dict(data)

    # group data
    data["group"] = (data.millis - data.millis.shift(1) < -1000).cumsum()
    data["timestamp"] = np.nan

    rv = []

    for i, grp in data.groupby("group"):
        t0 = None

        idx = grp[grp["message"].str.contains("Current time", regex=False)]
        if not idx.empty:
            t0 = pd.to_datetime(":".join(idx.message.values[0].split(":")[1:]))
        else:
            idx = grp[grp["message"].str.contains("Time from RTC", regex=False)]
            if not idx.empty:
                t0 = pd.to_datetime(idx.message.values[0][18:])
            
        if t0:
            millis0 = idx["millis"].values[0]

            grp.loc[:, "timestamp"] = grp["millis"].apply(lambda x: t0 + pd.Timedelta(x - millis0, unit='millis'))

            rv.append(grp)

    rv = pd.concat(rv)
    del rv["group"]

    # try sorting based on a time column
    if "timestamp" in rv.columns:
        rv = rv.sort_values(by='timestamp')

    if rv.empty:
        raise Exception("No data")

    # save the file
    if verbose:
        click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        rv.to_csv(output)
    else:
        rv.reset_index().to_feather(output)
