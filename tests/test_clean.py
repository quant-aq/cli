import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd

from quantaq_cli.console import clean


class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_clean_file(self):
        runner = CliRunner()
        result = runner.invoke(clean, 
                    [
                        os.path.join(self.test_files_dir, "lcs-1.csv"), 
                        os.path.join(self.test_dir, "output.csv"),
                    ],
                    catch_exceptions=False
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")
