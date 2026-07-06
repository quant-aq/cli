import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd

from quantaq_tools.cli import concat_command
from quantaq_tools.utilities import safe_load

class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_concat_files_modulairx_rawsd(self):
        runner = CliRunner()
        result = runner.invoke(concat_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"),
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file2.csv"),
                    ], catch_exceptions=False
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")

        # are the number of lines correct?
        df1 = safe_load(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"))
        df2 = safe_load(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file2.csv"))
        df3 = safe_load(os.path.join(self.test_dir, "output.csv")) 

        self.assertEqual(df1.shape[0] + df2.shape[0], df3.shape[0])

    def test_concat_files_modulairpm_rawsd(self):
        runner = CliRunner()
        result = runner.invoke(concat_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"),
                        os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file2.csv"),
                    ], catch_exceptions=False
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")

        # are the number of lines correct?
        df1 = safe_load(os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"))
        df2 = safe_load(os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file2.csv"))
        df3 = safe_load(os.path.join(self.test_dir, "output.csv")) 

        self.assertEqual(df1.shape[0] + df2.shape[0], df3.shape[0])

    def test_concat_files_modulairx_cloudapi(self):
        runner = CliRunner()
        result = runner.invoke(concat_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"),
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file2.csv"),
                    ], catch_exceptions=False
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")

        # are the number of lines correct?
        df1 = safe_load(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"))
        df2 = safe_load(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file2.csv"))
        df3 = safe_load(os.path.join(self.test_dir, "output.csv")) 

        self.assertEqual(df1.shape[0] + df2.shape[0], df3.shape[0])

    def test_concat_files_modulair_db_parquet(self):
        runner = CliRunner()
        result = runner.invoke(concat_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.parquet"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair/MOD-00256-db-cleaned-file1.parquet"),
                        os.path.join(self.test_files_dir, "modulair/MOD-00256-db-cleaned-file2.parquet"),
                    ], catch_exceptions=False
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # make sure the file exists
        p = Path(self.test_dir + "/output.parquet")
        self.assertTrue(p.exists())
        
        # is it a parquet?
        self.assertEqual(p.suffix, ".parquet")

        # are the number of lines correct?
        df1 = safe_load(os.path.join(self.test_files_dir, "modulair/MOD-00256-db-cleaned-file1.parquet"))
        df2 = safe_load(os.path.join(self.test_files_dir, "modulair/MOD-00256-db-cleaned-file2.parquet"))
        df3 = safe_load(os.path.join(self.test_dir, "output.parquet")) 

        self.assertEqual(df1.shape[0] + df2.shape[0], df3.shape[0])
