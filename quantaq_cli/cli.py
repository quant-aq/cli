from pathlib import Path
import pkg_resources

import rich_click as click
from loguru import logger

from quantaq_cli import concat_files, merge_files, resample_dataframe, clean_dataframe
from quantaq_cli import flag_dataframe, echo_flag_table, expunge_dataframe
from quantaq_cli.exceptions import InvalidFileExtension
from quantaq_cli.log import configure_logging, LOG_LEVELS
from quantaq_cli.toolkit.resample import WIND_COLUMNS
from quantaq_cli.toolkit.load import safe_load


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

__version__ = pkg_resources.get_distribution('quantaq_cli').version


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
@click.pass_context
def main(ctx):
    pass


def save_file(df, output):
    """Helper func to save a DataFrame to disk as CSV or parquet.

    Args:
        df (pd.DataFrame): DataFrame to save
        output (str): Destination filepath.
    """
    logger.info("Saving file to {}", output)
    output = Path(output)
    if output.suffix == ".csv":
        df.to_csv(output, index=False)
    else:
        df.to_parquet(output, index=False)

def check_extension(output):
    """Helper func to check if the output extension is either a csv or parquet
    format.
    
    Args:
        output (str): Destination filepath.
    """
    output = Path(output)
    if output.suffix not in (".csv", ".parquet"):
        error = InvalidFileExtension(f"Invalid file extension; got {output.suffix!r}")
        logger.error(error)
        raise error
    return output


@click.command("concat")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("--log-level", default="INFO",
              type=click.Choice(LOG_LEVELS, case_sensitive=False),
              help="loguru log level (default: INFO)")
def concat_command(files, output, log_level):
    """Concat FILES and save to OUTPUT."""
    configure_logging(log_level)

    # make sure the extension is either a csv or parquet format
    check_extension(output)
    
    # concat everything in filepath
    logger.info("Files to read: {}", files)

    df = concat_files(files)

    # save the file
    save_file(df, output)


@click.command("merge", short_help="merge two files together on their timestamp")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-ts", "--tscol", default="timestamp", help="The column by which to join the files", type=str)
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("--log-level", default="INFO",
              type=click.Choice(LOG_LEVELS, case_sensitive=False),
              help="loguru log level (default: INFO)")
def merge_command(files, output, tscol, log_level):
    """Merge FILES together and save to OUTPUT."""
    configure_logging(log_level)

    # make sure the extension is either a csv or parquet format
    check_extension(output)

    # merge everything in filepath
    logger.info("Files to read: {}", files)
    
    df = merge_files(files, tscol)
           
    # save the file
    save_file(df, output)


@click.command("resample", short_help="up/down sample data")
@click.argument("file", nargs=1, type=click.Path())
@click.argument("rule", nargs=1, type=str)
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("--on", default="timestamp", help="Name of the datetime column to resample over.", type=str)
@click.option("--by", default=None, help="Optional column(s) to group by first")
@click.option(
    "--wind",
    nargs=4,
    type=str,
    default=("wx_u", "wx_v", "wx_ws", "wx_wd"),
    help="(u, v, speed, direction) column names. The u/v columns don't need to be present in the dataframe, but the column names need to be specified.",
)
@click.option(
    "--flag-aware",
    is_flag=True,
    default=False,
    help=(
        "Whether to apply flag-aware row selection when resampling: bins "
        "with >1 good rows --> average only those rows; bins with no good "
        "rows -> average all rows and OR their flag values "
        "together. If False (default), all rows are averaged regardless "
        "of flags and the flag column is dropped."
    ),
)
@click.option("--numeric_how", default="mean", help="Aggregation for numeric columns.")
@click.option("--nonnumeric_how", default="first", help="Aggregation for non-numeric columns.")
@click.option("--log-level", default="INFO",
              type=click.Choice(LOG_LEVELS, case_sensitive=False),
              help="loguru log level (default: INFO)")
def resample_command(file, rule, output, log_level, **kwargs):
    """Resample FILE at INTERVAL and save to OUTPUT."""
    configure_logging(log_level)
    
    on = kwargs.pop("on", "timestamp")
    by = kwargs.pop("by", None)
    wind = kwargs.pop("wind", WIND_COLUMNS)
    flag_aware = kwargs.pop("flag_aware", False)
    numeric_how = kwargs.pop("numeric_how", "mean")
    nonnumeric_how = kwargs.pop("nonnumeric_how", "first")

    # make sure the extension is either a csv or parquet format
    check_extension(output)

    logger.info("File to read: {}", file)

    # load the file
    df = safe_load(file)

    # if column to resample over needs to be made a datetime obj, do so
    if on not in df.columns:
        error = ValueError(f"Invalid column name for the timestamp; got {on!r}")
        logger.error(error)
        raise error

    # resample
    df = resample_dataframe(
        df,
        rule,
        on=on,
        by=by,
        wind=wind,
        flag_aware=flag_aware,
        numeric_how=numeric_how,
        nonnumeric_how=nonnumeric_how,
    )

    # save the file
    save_file(df, output)


@click.command("flag")
@click.argument("file", nargs=1, type=click.Path())
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("--log-level", default="INFO",
              type=click.Choice(LOG_LEVELS, case_sensitive=False),
              help="loguru log level (default: INFO)")
def flag_command(file, output, log_level):
    """Flag FILE and save to OUTPUT."""
    configure_logging(log_level)

    # make sure the extension is either a csv or parquet format
    check_extension(output)

    logger.info("File to read: {}", file)

    # load the file
    df = safe_load(file)

    # flag the dataframe
    df = flag_dataframe(df)

    # save the file
    save_file(df, output)
        

@click.command("expunge")
@click.argument("file", nargs=1, type=click.Path())
@click.option("-d", "--dry-run", is_flag=True, help="Print table to screen and bypass file save")
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("--log-level", default="INFO",
              type=click.Choice(LOG_LEVELS, case_sensitive=False),
              help="loguru log level (default: INFO)")
def expunge_command(file, output, log_level, dry_run):
    """Expunge FILE and save to OUTPUT."""
    configure_logging(log_level)

    # make sure the extension is either a csv or parquet format
    check_extension(output)

    logger.info("Expunging data for {}", file)

    df = safe_load(file)
    show_summary = dry_run or log_level == "INFO"

    if show_summary:
        logger.info("Original flag summary:")
        echo_flag_table(df)

    df_expunged = expunge_dataframe(df)

    if show_summary:
        logger.info("New flag summary:")
        echo_flag_table(df_expunged)

    if not dry_run:
        save_file(df, output)


@click.command("clean")
@click.argument("file", nargs=1, type=click.Path())
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("--log-level", default="INFO",
              type=click.Choice(LOG_LEVELS, case_sensitive=False),
              help="loguru log level (default: INFO)")
def clean_command(file, output, log_level):
    """Clean FILE and save to OUTPUT."""
    configure_logging(log_level)

    # make sure the extension is either a csv or parquet format
    check_extension(output)
    
    logger.info("Cleaning data for {}", file)
    df = safe_load(file)
    df = clean_dataframe(df)
    # save the file
    save_file(df, output)

# add the commands one-by-one
main.add_command(concat_command)
main.add_command(merge_command)
main.add_command(resample_command)
main.add_command(expunge_command)
main.add_command(flag_command)
main.add_command(clean_command)
