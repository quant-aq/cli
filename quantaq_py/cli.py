from pathlib import Path
import click

from loguru import logger

from quantaq_py import concat_files, merge_files
from quantaq_py.exceptions import InvalidFileExtension
from quantaq_py.log import configure_logging, LOG_LEVELS


@click.command("concat")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("--log-level", default="INFO",
              type=click.Choice(LOG_LEVELS, case_sensitive=False),
              help="loguru log level (default: INFO)")
def concat_command(files, output, log_level):
    configure_logging(log_level)

    # make sure the extension is valid
    output = Path(output)
    if output.suffix not in (".csv", ".parquet"):
        raise InvalidFileExtension("Invalid file extension")

    # concat everything in filepath
    logger.info("Files to read: {}", files)

    df = concat_files(files)

    # save the file
    logger.info("Saving file to {}", output)

    if output.suffix == ".csv":
        df.to_csv(output, index=False)
    else:
        df.to_parquet(output, index=False)


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
    output = Path(output)
    if output.suffix not in (".csv", ".parquet"):
        raise InvalidFileExtension("Invalid file extension")

    # merge everything in filepath
    logger.info("Files to read: {}", files)
    
    df = merge_files(files, tscol)
           
    # save the file
    logger.info("Saving file to {}", output)
    if output.suffix == ".csv":
        # index=True is needed to preserve the timestamp column after merge
        df.to_csv(output, index=True)
    else:
         # index=True is needed to preserve the timestamp column after merge
        df.to_parquet(output, index=True)
        