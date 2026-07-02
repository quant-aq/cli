import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from click.testing import CliRunner

from quantaq_py.cli import flag_command

class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_flag_files_modulair_db(self):
        runner = CliRunner()
        result = runner.invoke(flag_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair/MOD-00014-db-raw.csv"), 
                    ], catch_exceptions=False
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

    #def test_flag_files_modulairx_rawsd(self):
    #    NOTE: not currently implemented
    #    runner = CliRunner()
    #    result = runner.invoke(flag_command, 
    #                [
    #                    "-o",
    #                    os.path.join(self.test_dir, "output.csv"),
    #                    "-v",
    #                    os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"), 
    #                ], catch_exceptions=False
    #            )
        
        # did it succeed?
    #    self.assertEqual(result.exit_code, 0)#

    #    # did it output the correct text?
    #    self.assertTrue("File to read" in result.output)

    #    # make sure the file exists
    #    p = Path(self.test_dir + "/output.csv")
    #    self.assertTrue(p.exists())
        
    #    # is it a csv?
    #    self.assertEqual(p.suffix, ".csv")

    def test_flag_files_modulairx_cloudapi(self):
        runner = CliRunner()
        result = runner.invoke(flag_command, 
                   [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"), 
                    ], catch_exceptions=False
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

    def test_flag_files_modulair_db_parquet(self):
        runner = CliRunner()
        result = runner.invoke(flag_command, 
                   [
                        "-o",
                        os.path.join(self.test_dir, "output.parquet"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair/MOD-00256-db-raw.parquet"), 
                    ], catch_exceptions=False
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("File to read" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.parquet")
        self.assertTrue(p.exists())
        
        # is it a parquet?
        self.assertEqual(p.suffix, ".parquet")
