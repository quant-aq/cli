import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd

from quantaq_cli.console import merge, concat


class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_merge_files_csv(self):
        runner = CliRunner()
        result = runner.invoke(merge, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
                        os.path.join(self.test_files_dir, "modulair/MOD-raw.csv"), 
                        os.path.join(self.test_files_dir, "modulair/MOD-final.csv"),
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
        df1 = pd.read_csv(os.path.join(self.test_files_dir, "modulair/MOD-raw.csv"), index_col=0)
        df2 = pd.read_csv(os.path.join(self.test_files_dir, "modulair/MOD-final.csv"), index_col=0)
        df3 = pd.read_csv(os.path.join(self.test_dir, "output.csv")) 

        self.assertEqual(df1.shape[1] + df2.shape[1] - 1, df3.shape[1])
      
    def test_merge_files_feather(self):
        runner = CliRunner()
        result = runner.invoke(merge, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.feather"),
                        "-v",
                        os.path.join(self.test_files_dir, "lcs-1.csv"), 
                        os.path.join(self.test_files_dir, "ref.csv"),
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

    def test_concat_then_merge(self):
        runner = CliRunner()
        res1 = runner.invoke(concat,
            [
                "-o",
                os.path.join(self.test_dir, "concat1.csv"),
                os.path.join(self.test_files_dir, "modulair-pm/file1.csv"),
                os.path.join(self.test_files_dir, "modulair-pm/file2.csv"),
            ]
        )

        self.assertEqual(res1.exit_code, 0)

        res2 = runner.invoke(concat,
            [
                "-o",
                os.path.join(self.test_dir, "concat2.csv"),
                "-l",
                os.path.join(self.test_files_dir, "modulair-pm/logs/000001.txt"),
                os.path.join(self.test_files_dir, "modulair-pm/logs/000002.txt"),
            ]
        )

        self.assertEqual(res2.exit_code, 0)

        res3 = runner.invoke(merge,
            [
                "-o",
                os.path.join(self.test_dir, "final.csv"),
                os.path.join(self.test_dir, "concat1.csv"), 
                os.path.join(self.test_dir, "concat2.csv"),
            ],
            catch_exceptions=False
        )

        self.assertEqual(res3.exit_code, 0)