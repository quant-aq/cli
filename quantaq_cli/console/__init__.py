import click
import pkg_resources
from ..variables import SUPPORTED_MODELS

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

__version__ = pkg_resources.get_distribution('quantaq_cli').version


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
@click.pass_context
def main(ctx):
    pass


@click.command("concat", short_help="concatenate files together")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
@click.option("-l", "--logs", is_flag=True, help="Parse and save locally-saved log files.")
def concat(files, output, verbose, logs, **kwargs):
    """Concatenate FILES together and save to OUTPUT.

    FILES is the collection or list of files that you are concatenating together. They 
    can be provided as a list or by using a wildcard and providing the path with wildcard.
    """
    from .commands.concat import concat_command, concat_logs_command

    if not logs:
        concat_command(files, output, verbose=verbose, **kwargs)
    else:
        concat_logs_command(files, output, verbose=verbose, **kwargs)


@click.command("merge", short_help="merge two files together on their timestamp")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-ts", "--tscol", default="timestamp", help="The column by which to join the files", type=str)
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
def merge(files, tscol, output, verbose, **kwargs):
    """Merge FILES together and save to OUTPUT.
    """
    from .commands.merge import merge_command

    merge_command(files, output, tscol=tscol, verbose=verbose, **kwargs)


@click.command("resample", short_help="up/down sample data")
@click.argument("file", nargs=1, type=click.Path())
@click.argument("interval", nargs=1, type=str)
@click.option("-ts", "--tscol", default="timestamp", help="The column by which to join the files", type=str)
@click.option("-m", "--method", default="mean", help="One of [mean, median, sum, min, max]")
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
def resample(file, interval, tscol, method, output, verbose, **kwargs):
    """Resample FILE at INTERVAL and save to OUTPUT.
    """
    from .commands.resample import resample_command

    resample_command(file, interval, output, method=method, tscol=tscol, verbose=verbose, **kwargs)


@click.command("expunge", short_help="NaN flagged values")
@click.argument("file", nargs=1, type=click.Path())
@click.option("-d", "--dry-run", is_flag=True, help="Print table to screen and bypass file save")
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-f", "--flag", default="flag", help="The name of the flag column", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
@click.option("-m", "--model", default="modulair_pm", help="The device model type. One of {}".format(SUPPORTED_MODELS))
def expunge(file, dry_run, output, flag, verbose, model, **kwargs):
    """Expunge (NaN flagged values) FILE and save to OUTPUT.
    """
    from .commands.expunge import expunge_command

    expunge_command(file, output, flagcol=flag, dry_run=dry_run, verbose=verbose, model=model, **kwargs)


@click.command("flag", short_help="flag data based on specific criteria")
@click.argument("file", nargs=1, type=click.Path())
@click.argument("column", nargs=1, type=str)
@click.argument("comparator", nargs=1, type=str)
@click.argument("value", nargs=1, type=float)
@click.option("-f", "--flag", default="FLAG_ROW", help="One of [FLAG_OPC, FLAG_CO, FLAG_NO, FLAG_NO2, FLAG_O3, FLAG_CO2, FLAG_ROW]")
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
@click.option("-m", "--model", default="modulair_pm", help="The device model type. One of {}".format(SUPPORTED_MODELS))
def flag(file, column, comparator, value, flag, output, verbose, model, **kwargs):
    """Set a FLAG based on user input or statistical method.

    Four arguments are required:
      1. FILE -> the path to the file of interest
      2. COLUMN -> the exact name of the column
      3. COMPARATOR -> one of ['lt', 'gt', 'eq', 'le', 'ge']
      4. VALUE -> the value by which to filter
    """
    from .commands.flag import flag_command

    flag_command(file, column, comparator, value, output, flag=flag, verbose=verbose, model=model)


# add the commands one-by-one
main.add_command(concat)
main.add_command(merge)
main.add_command(resample)
main.add_command(expunge)
main.add_command(flag)