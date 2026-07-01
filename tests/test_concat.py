import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd

from quantaq_py.console import concat


class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_concat_files_csv_arisense_db(self):
        runner = CliRunner()
        result = runner.invoke(concat, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
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
        df1 = pd.read_csv(os.path.join(self.test_files_dir, "arisense/SN000-063-db-file1.csv"))
        df2 = pd.read_csv(os.path.join(self.test_files_dir, "arisense/SN000-063-db-file2.csv"), skiprows=1)
        df3 = pd.read_csv(os.path.join(self.test_dir, "output.csv")).sort_values('timestamp')

        self.assertEqual(df1.shape[0] + df2.shape[0], df3.shape[0])

        # Are the timestamps correct?
        for i, (_, r) in enumerate(df2.sort_values('timestamp').head().iterrows()):
            self.assertEqual(r['timestamp'], df3.loc[i, "timestamp"])

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

    def test_concat_files_feather_arisense_db(self):
        runner = CliRunner()
        result = runner.invoke(concat, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.feather"),
                        "-v",
                        os.path.join(self.test_files_dir, "arisense/SN000-063-db-file1.csv"), 
                        os.path.join(self.test_files_dir, "arisense/SN000-063-db-file2.csv"),
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

    def test_concat_files_modulairx_rawsd(self):
        runner = CliRunner()
        result = runner.invoke(concat, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"),
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file2.csv"),
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
        df1 = pd.read_csv(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"), skiprows=3)
        df2 = pd.read_csv(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file2.csv"), skiprows=3)
        df3 = pd.read_csv(os.path.join(self.test_dir, "output.csv")) 

        self.assertEqual(df1.shape[0] + df2.shape[0], df3.shape[0])

    def test_concat_files_modulairpm_rawsd(self):
        runner = CliRunner()
        result = runner.invoke(concat, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
                        os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"),
                        os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file2.csv"),
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
        df1 = pd.read_csv(os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"), skiprows=3)
        df2 = pd.read_csv(os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file2.csv"), skiprows=3)
        df3 = pd.read_csv(os.path.join(self.test_dir, "output.csv")) 

        self.assertEqual(df1.shape[0] + df2.shape[0], df3.shape[0])

    def test_concat_files_modulairx_cloudapi(self):
        runner = CliRunner()
        result = runner.invoke(concat, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"),
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file2.csv"),
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
        df1 = pd.read_csv(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"))
        df2 = pd.read_csv(os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file2.csv"))
        df3 = pd.read_csv(os.path.join(self.test_dir, "output.csv")) 

        self.assertEqual(df1.shape[0] + df2.shape[0], df3.shape[0])
