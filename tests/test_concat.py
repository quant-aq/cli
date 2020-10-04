import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd

from quantaq_cli.console import concat


class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_concat_files_csv(self):
        runner = CliRunner()
        result = runner.invoke(concat, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
                        os.path.join(self.test_files_dir, "lcs-1.csv"), 
                        os.path.join(self.test_files_dir, "lcs-2.csv"),
                    ],
                    catch_exceptions=False
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

        # are the number of lines correct?
        df1 = pd.read_csv(os.path.join(self.test_files_dir, "lcs-1.csv"))
        df2 = pd.read_csv(os.path.join(self.test_files_dir, "lcs-2.csv"), skiprows=1)
        df3 = pd.read_csv(os.path.join(self.test_dir, "output.csv")) 

        self.assertEqual(df1.shape[0] + df2.shape[0], df3.shape[0])

    def test_concat_logfiles(self):
        runner = CliRunner()
        result = runner.invoke(concat, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-l",
                        os.path.join(self.test_files_dir, "modulair-pm/logs/000001.txt"), 
                        os.path.join(self.test_files_dir, "modulair-pm/logs/000002.txt"),
                    ],
                    catch_exceptions=False
                )
        
        # did it succeed?
        print (result.stdout)
        self.assertEqual(result.exit_code, 0)


    def test_concat_files_feather(self):
        runner = CliRunner()
        result = runner.invoke(concat, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.feather"),
                        "-v",
                        os.path.join(self.test_files_dir, "lcs-1.csv"), 
                        os.path.join(self.test_files_dir, "lcs-2.csv"),
                    ]
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.feather")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".feather")

    def test_concat_files_modulair(self):
        runner = CliRunner()
        result = runner.invoke(concat, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
                        os.path.join(self.test_files_dir, "modulair-pm/file1.csv"), 
                        os.path.join(self.test_files_dir, "modulair-pm/file2.csv"),
                    ]
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")

        # are the number of lines correct?
        df1 = pd.read_csv(os.path.join(self.test_files_dir, "modulair-pm/file1.csv"), skiprows=3)
        df2 = pd.read_csv(os.path.join(self.test_files_dir, "modulair-pm/file2.csv"), skiprows=3)
        df3 = pd.read_csv(os.path.join(self.test_dir, "output.csv")) 

        self.assertEqual(df1.shape[0] + df2.shape[0], df3.shape[0])

