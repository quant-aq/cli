import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


@click.command("concat", short_help="concatenate files together")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
def concat(files, output, verbose, **kwargs):
    """Concatenate *FILES* together and save to *OUTPUT*.

    *FILES* is the collection or list of files that you are concatenating together. They 
    can be provided as a list or by using a wildcard and providing the path with wildcard.
    """
    from .commands.concat import concat_command

    concat_command(files, output, verbose=verbose, **kwargs)


@click.command("merge", short_help="merge two files together on their timestamp")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-t", "--tscol", default="timestamp", help="The column by which to join the files", type=str)
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
def merge(files, tscol, output, verbose, **kwargs):
    """Merge *FILES* together and save to *OUTPUT*.
    """
    from .commands.merge import merge_command

    merge_command(files, output, tscol=tscol, verbose=verbose, **kwargs)


# flag (pop out table?)

# expunge (nan)

# 

# add the commands one-by-one
main.add_command(concat)
main.add_command(merge)