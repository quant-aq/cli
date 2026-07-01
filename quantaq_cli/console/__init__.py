import pkg_resources
import rich_click as click
from quantaq_cli.variables import SUPPORTED_MODELS, SUPPORTED_SOURCES

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
@click.option("-ts", "--tscol", default="timestamp_iso", help="The column by which to join the files", type=str)
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
def merge(files, tscol, output, verbose, **kwargs):
    """Merge FILES together and save to OUTPUT.
    """
    from .commands.merge import merge_command

    merge_command(files, output, tscol=tscol, verbose=verbose, **kwargs)


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
    help="(u, v, speed, direction) column names",
)
@click.option("--numeric_how", default="mean", help="Aggregation for numeric columns.")
@click.option("--nonnumeric_how", default="first", help="Aggregation for non-numeric columns.")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
def resample(file, rule, output, verbose, **kwargs):
    """Resample FILE at INTERVAL and save to OUTPUT.
    """
    from .commands.resample import resample_command

    resample_command(file, rule, output, verbose=verbose, **kwargs)


@click.command("expunge", short_help="NaN flagged values")
@click.argument("file", nargs=1, type=click.Path())
@click.option("-d", "--dry-run", is_flag=True, help="Print table to screen and bypass file save")
@click.option("-t", "--table", is_flag=True, help="Print as a dict instead of as a table")
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-f", "--flag", default="flag", help="The name of the flag column", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
@click.option("-m", "--model", default="modulair_pm", help="The device model type. One of {}".format(SUPPORTED_MODELS))
def expunge(file, dry_run, table, output, flag, verbose, model, **kwargs):
    """Expunge (NaN flagged values) FILE and save to OUTPUT.
    """
    from .commands.expunge import expunge_command

    expunge_command(file, output, flagcol=flag, dry_run=dry_run, verbose=verbose, model=model, table=table, **kwargs)


@click.command("flag", short_help="flag data based on specific criteria")
@click.argument("file", nargs=1, type=click.Path())
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
def flag(file, output, verbose, model, source, **kwargs):
    """Reflag a data file"""
    from .commands.flag import flag_command

    flag_command(file, output, verbose=verbose)


@click.command("clean")
@click.argument("filepath", nargs=1, type=click.Path())
@click.argument("savepath", nargs=1, type=click.Path())
def clean(filepath, savepath, **kwargs):
    """Clean FILEPATH and save to SAVEPATH.
    
    Remove corrupt data and force columns to be the 
    desired column type based on the specific column.
    """
    from .commands.munge import clean_file
    
    clean_file(filepath, savepath, **kwargs)


# add the commands one-by-one
main.add_command(concat)
main.add_command(merge)
main.add_command(resample)
main.add_command(expunge)
main.add_command(flag)
main.add_command(clean)