import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd

from quantaq_tools.cli import clean_command


class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_clean_file_modulairpm_rawsd(self):
        runner = CliRunner()
        result = runner.invoke(clean_command, 
                    [
                        os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"), 
                        "-o",
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

    def test_clean_file_modulairx_cloudapi(self):
        runner = CliRunner()
        result = runner.invoke(clean_command, 
                    [
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"), 
                        "-o",
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

    def test_clean_file_modulair_db_parquet(self):
        runner = CliRunner()
        result = runner.invoke(clean_command, 
                    [
                        os.path.join(self.test_files_dir, "modulair/MOD-00256-db-raw.parquet"), 
                        "-o",
                        os.path.join(self.test_dir, "output.parquet"),
                    ],
                    catch_exceptions=False
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # make sure the file exists
        p = Path(self.test_dir + "/output.parquet")
        self.assertTrue(p.exists())
        
        # is it a parquet?
        self.assertEqual(p.suffix, ".parquet")
