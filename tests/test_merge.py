import os
from os import path
from pathlib import Path
import shutil
import tempfile
import unittest

from click.testing import CliRunner
import pandas as pd

from quantaq_tools.cli import concat_command, merge_command
from quantaq_tools.utilities import safe_load


class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_merge_files_modulair_db(self):
        runner = CliRunner()
        result = runner.invoke(merge_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair/MOD-00014-db-raw.csv"), 
                        os.path.join(self.test_files_dir, "modulair/MOD-00014-db-final.csv"),
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
        df1 = safe_load(os.path.join(self.test_files_dir, "modulair/MOD-00014-db-raw.csv"))
        df2 = safe_load(os.path.join(self.test_files_dir, "modulair/MOD-00014-db-final.csv"))
        df3 = safe_load(os.path.join(self.test_dir, "output.csv"))

        self.assertEqual(df1.shape[1] + df2.shape[1] - 1, df3.shape[1])

    def test_merge_files_modulair_db_parquet(self):
        runner = CliRunner()
        result = runner.invoke(merge_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.parquet"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair/MOD-00256-db-cleaned-file1.parquet"), 
                        os.path.join(self.test_files_dir, "modulair/ref/bos_roxbury-cleaned.parquet"),
                    ],
                    catch_exceptions=False
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)

        # did it output the correct text?
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.parquet")
        self.assertTrue(p.exists())
        
        # is it a parquet?
        self.assertEqual(p.suffix, ".parquet")

        # are the number of lines correct?
        df1 = safe_load(os.path.join(self.test_files_dir, "modulair/MOD-00256-db-cleaned-file1.parquet"))
        df2 = safe_load(os.path.join(self.test_files_dir, "modulair/ref/bos_roxbury-cleaned.parquet"))
        df3 = safe_load(os.path.join(self.test_dir, "output.parquet"))
        
        self.assertEqual(df1.shape[1] + df2.shape[1] - 1, df3.shape[1])

    #def test_concat_then_merge(self):
    #    runner = CliRunner()
    #    res1 = runner.invoke(concat_command,
    #        [
    #            "-o",
    #            os.path.join(self.test_dir, "concat1.csv"),
    #            os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"),
    #            os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file2.csv"),
    #        ], catch_exceptions=False
    #    )

    #    self.assertEqual(res1.exit_code, 0)

    #    res2 = runner.invoke(concat_command,
    #        [
    #            "-o",
    #            os.path.join(self.test_dir, "concat2.csv"),
    #            "-l",
    #            os.path.join(self.test_files_dir, "modulair-pm/logs/000001.txt"),
    #            os.path.join(self.test_files_dir, "modulair-pm/logs/000002.txt"),
    #        ], catch_exceptions=False
    #    )

    #    self.assertEqual(res2.exit_code, 0)

    #    res3 = runner.invoke(merge_command,
    #        [
    #            "-o",
    #            os.path.join(self.test_dir, "final.csv"),
    #            os.path.join(self.test_dir, "concat1.csv"), 
    #            os.path.join(self.test_dir, "concat2.csv"),
    #        ],
    #        catch_exceptions=False
    #    )

    #    self.assertEqual(res3.exit_code, 0)

    def test_merge_files_modulairx_rawsd(self):
            runner = CliRunner()
            result = runner.invoke(merge_command, 
                        [
                            "-o",
                            os.path.join(self.test_dir, "output.csv"),
                            "--log-level",
                            "DEBUG",
                            os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"), 
                            os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file2.csv"),
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
            df1 = safe_load(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"))
            df2 = safe_load(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file2.csv"))
            df3 = safe_load(os.path.join(self.test_dir, "output.csv"))

            self.assertEqual(df1.shape[1] + df2.shape[1] - 1, df3.shape[1])

    def test_merge_files_modulairx_cloudapi(self):
            runner = CliRunner()
            result = runner.invoke(merge_command, 
                        [
                            "-o",
                            os.path.join(self.test_dir, "output.csv"),
                            "--log-level",
                            "DEBUG",
                            os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"), 
                            os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file2.csv"),
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
            df1 = safe_load(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"))
            df2 = safe_load(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file2.csv"))
            df3 = safe_load(os.path.join(self.test_dir, "output.csv"))

            self.assertEqual(df1.shape[1] + df2.shape[1] - 1, df3.shape[1])
            