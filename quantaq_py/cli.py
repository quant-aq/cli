from pathlib import Path
import click

from loguru import logger

from quantaq_py import concat_files
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
