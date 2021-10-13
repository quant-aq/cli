import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd
import numpy as np

from quantaq_cli.console import expunge


class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_expunge_csv(self):
        runner = CliRunner()
        result = runner.invoke(expunge, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
                        os.path.join(self.test_files_dir, "lcs-1.csv"), 
                    ]
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")

    def test_expunge_dryrun(self):
        runner = CliRunner()
        result = runner.invoke(expunge, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.feather"),
                        "--dry-run",
                        "--table",
                        os.path.join(self.test_files_dir, "lcs-1.csv"),
                    ]
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("FLAG BREAKDOWN" in result.output)

        # make sure the file does not exist
        p = Path(self.test_dir + "/output.feather")
        self.assertFalse(p.exists())

    def test_expunge_dict(self):
        runner = CliRunner()
        result = runner.invoke(expunge, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.feather"),
                        "--dry-run",
                        os.path.join(self.test_files_dir, "lcs-1.csv"),
                    ]
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertFalse("FLAG BREAKDOWN" in result.output)

    def test_expunge_feather(self):
        runner = CliRunner()
        result = runner.invoke(expunge, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.feather"),
                        os.path.join(self.test_files_dir, "lcs-1.csv"),
                    ]
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)
        

        # did it output the correct text?
        self.assertFalse("FLAG BREAKDOWN" in result.output)

        # make sure the file does not exist
        p = Path(self.test_dir + "/output.feather")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".feather")

    def test_expunge_csv_modulair_pm(self):
        runner = CliRunner()
        result = runner.invoke(expunge, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
                        os.path.join(self.test_files_dir, "modulair-pm/file1.csv"), 
                    ]
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")

    def test_expunge_csv_modulair(self):
        runner = CliRunner()
        result = runner.invoke(expunge, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
                        os.path.join(self.test_files_dir, "modulair/MOD-raw.csv"), 
                    ]
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")
