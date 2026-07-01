import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd

from quantaq_py.cli import concat_command
from quantaq_py.utilities import safe_load

class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_concat_files_csv_arisense_db(self):
        runner = CliRunner()
        result = runner.invoke(concat_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "arisense/SN000-063-db-file1.csv"), 
                        os.path.join(self.test_files_dir, "arisense/SN000-063-db-file2.csv"),
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
        df1 = safe_load(os.path.join(self.test_files_dir, "arisense/SN000-063-db-file1.csv"))
        df2 = safe_load(os.path.join(self.test_files_dir, "arisense/SN000-063-db-file2.csv"))
        df3 = safe_load(os.path.join(self.test_dir, "output.csv")).sort_values('timestamp')

        self.assertEqual(df1.shape[0] + df2.shape[0], df3.shape[0])

        # Are the timestamps correct?
        for i, (_, r) in enumerate(df2.sort_values('timestamp').head().iterrows()):
            self.assertEqual(r['timestamp'], df3.loc[i, "timestamp"])

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
