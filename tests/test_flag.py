import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd

from quantaq_cli.console import flag

class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_flag_files(self):
        runner = CliRunner()
        result = runner.invoke(flag, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
                        os.path.join(self.test_files_dir, "lcs-1.csv"), 
                        "co_we",
                        "lt",
                        "205.0"
                    ]
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("File to read" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")

    def test_flag_files_feather(self):
        runner = CliRunner()
        result = runner.invoke(flag, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.feather"),
                        "-v",
                        os.path.join(self.test_files_dir, "lcs-1.csv"), 
                        "co_we",
                        "gt",
                        "505.0"
                    ]
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("File to read" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.feather")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".feather")
