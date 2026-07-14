import os
import shutil
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from quantaq_cli import flag_dataframe
from quantaq_cli.cli import flag_command

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

    def test_flag_files_modulairx_rawsd(self):
        runner = CliRunner()
        result = runner.invoke(flag_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"), 
                    ], catch_exceptions=False
                )
        
        # did it succeed?
        self.assertEqual(result.exit_code, 0)#

        # did it output the correct text?
        self.assertTrue("File to read" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")

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

    def test_flag_files_modulairx_db(self):
        runner = CliRunner()
        result = runner.invoke(flag_command, 
                   [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-db-file1.csv"), 
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

def test_flag_dataframe_nanflag():
    sample_df = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2023-03-10T17:41:24Z"),
                "sample_rh": 77.6,
                "sample_temp": -10.4,
                "neph_pm1_env": 10.6,
                "neph_pm25_env": 25.0,
                "neph_pm10_env": 32.4,
                "neph_bin0": 1590.375,
                "co_we": 758.8,
                "co_ae": 656.8,
                "co_diff": 102.0,
                "flag": np.nan,  # this row should be dropped
                "sn": "MOD-00001",
            },
            {
                "timestamp": pd.to_datetime("2023-03-10T17:42:24Z"),
                "sample_rh": 77.9,
                "sample_temp": -10.3,
                "neph_pm1_env": 10.4,
                "neph_pm25_env": 24.8,
                "neph_pm10_env": 32.1,
                "neph_bin0": 1588.0,
                "co_we": 759.1,
                "co_ae": 657.0,
                "co_diff": 102.1,
                "flag": 0.,  # this row should survive
                "sn": "MOD-00001",
            },
            {
                "timestamp": pd.to_datetime("2023-03-10T17:43:24Z"),
                "sample_rh": 78.1,
                "sample_temp": -10.2,
                "neph_pm1_env": 10.5,
                "neph_pm25_env": 24.9,
                "neph_pm10_env": 32.0,
                "neph_bin0": 1589.0,
                "co_we": 759.3,
                "co_ae": 657.2,
                "co_diff": 102.0,
                "flag": 0.,  # this row should survive
                "sn": "MOD-00001",
            },
        ],
    )

    expected = sample_df.dropna(how="any")
    
    flagged = flag_dataframe(sample_df)

    assert_frame_equal(flagged, expected, check_dtype=False)
