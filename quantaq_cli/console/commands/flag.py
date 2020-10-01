from pathlib import Path
import pandas as pd
import numpy as np
import click
from terminaltables import SingleTable

from ...exceptions import InvalidFileExtension, InvalidArgument, InvalidDeviceModel
from ...utilities import safe_load
from ...variables import FLAGS, SUPPORTED_MODELS

import operator

ops = {
    'eq': operator.eq, 
    'lt': operator.lt, 
    'le': operator.le, 
    'gt': operator.gt, 
    'ge': operator.ge
    }


def flag_command(file, column, comparator, value, output, **kwargs):
    verbose = kwargs.pop("verbose", False)
    flag    = kwargs.pop("flag", "FLAG_ROW")
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

    # is the <column> in df.columns?
    if not column in df.columns:
        raise InvalidArgument("Bad column name")

    # is the comparator valid?
    if not comparator in ops.keys():
        raise InvalidArgument("Bad comparator")

    # create flag column if it doesn't exist
    if "flag" not in df.columns:
        df["flag"] = 0

    # get the flag value
    flag_value = 0
    flag_list = FLAGS.get(model)
    for label, v, _ in flag_list:
        if label == flag:
            flag_value = v
            break

    # create a mask and set the flag accordingly
    mask = ops[comparator](df[column], value)
    df.loc[mask, "flag"] = df[mask]["flag"] | flag_value

    # save the file
    if verbose:
        click.secho("Saving file to {}".format(output), fg='green')

    if save_as_csv:
        df.to_csv(output)
    else:
        df.reset_index().to_feather(output)