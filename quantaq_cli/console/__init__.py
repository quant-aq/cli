import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


@click.command("concat")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("-o", "--output", default="output.csv", help="The filepath where you would like to save the file", type=str)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose mode (debugging)")
def concat(files, output, verbose, **kwargs):
    """Concatenate FILES together.

    Files should NOT have quotations around it if you are trying to use wildcards.
    """
    from .commands.concat import concat_command

    concat_command(files, output, verbose=verbose, **kwargs)


# add the commands one-by-one
main.add_command(concat)