import clikit
from cleo import Command
import pandas as pd
from pathlib import Path

DEFAULT_GLOB_EXT = "*.csv"
DEFAULT_OUTPUT   = "output.csv"

class InvalidPathException(Exception):
    pass

class ConcatCommand(Command):
    """
    Concatenate multiple files together

    concat
        {filepath : Which files do you want to concatenate?}
        {output? : Where should the output file be saved?}
    """
    def handle(self):
        fpath = self.argument("filepath")
        output = self.argument("output")

        # print an empty line
        self.line("", verbosity=clikit.api.io.flags.VERBOSE)

        # check to see if the path is valid
        fpath = Path(fpath)

        if not fpath.is_dir():
            path = fpath.parent
            ext = fpath.name
        else:
            path = fpath
            ext = DEFAULT_GLOB_EXT

        # output some debugging info
        self.line("File Path: <info>{}</info>".format(path), verbosity=clikit.api.io.flags.VERBOSE)
        self.line("Glob Extension: <info>{}</info>".format(ext), verbosity=clikit.api.io.flags.VERBOSE)

        # make sure the directory is valid
        if not path.is_dir():
            raise InvalidPathException("")

        if not output:
            output = DEFAULT_OUTPUT

        # check the extension of the output
        parts_of_output = output.split(".")
        if parts_of_output[-1] != "csv":
            parts_of_output[-1] = "csv"
            self.line("<comment>Forcing the file output extension to be a csv.</comment>")

        # rejoin the output
        output = ".".join(parts_of_output)

        # gather a list of all files to be concatenated together
        files_to_concat = list(path.glob(ext))

        if len(files_to_concat) == 0:
            raise Exception("No files were found to concatenate.")
        
        self.line("<info>{}</info> files were found to concatenate together".format(len(files_to_concat)), verbosity=clikit.api.io.flags.VERBOSE)
        self.line("Files to concatenate:", verbosity=clikit.api.io.flags.VERY_VERBOSE)
        for f in files_to_concat:
            self.line("\t<info>{}</info>".format(f), verbosity=clikit.api.io.flags.VERY_VERBOSE)

        # gather all files in the path
        self.line("\nLoading files:")
        progress = self.progress_bar(len(files_to_concat))

        dataframes = []
        for each in files_to_concat:
            tmp = pd.read_csv(each)

            # hack: if the number of columns is 2, then we should have skipped a line
            if len(tmp.columns) == 2:
                tmp = pd.read_csv(each, skiprows=1)

            dataframes.append(tmp)
            progress.advance()
        
        progress.finish()
        self.line("\n")

        # concatenate the files
        df = pd.concat(dataframes, sort=False)

        # try sorting by the timestamp
        if "timestamp_iso" in df.columns:
            df = df.sort_values(by="timestamp_iso")
        elif "timestamp" in df.columns:
            df = df.sort_values(by="timestamp")

        # save the file
        if not df.empty and output:
            self.line("Saving data to <info>{}</info>".format(output), verbosity=clikit.api.io.flags.VERBOSE)
            df.to_csv(output)
