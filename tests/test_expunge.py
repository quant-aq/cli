import os
import shutil
import tempfile
import unittest
from os import path
from pathlib import Path

from click.testing import CliRunner
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from quantaq_tools import expunge_dataframe, flag_summary
from quantaq_tools.cli import expunge_command

class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_expunge_csv_modulairpm_rawsd(self):
        runner = CliRunner()
        result = runner.invoke(expunge_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"), 
                    ], catch_exceptions=False
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

    def test_expunge_csv_modulair_db(self):
        runner = CliRunner()
        result = runner.invoke(expunge_command, 
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
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")

    def test_expunge_csv_modulairx_rawsd(self):
        runner = CliRunner()
        result = runner.invoke(expunge_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"), 
                    ], catch_exceptions=False
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

    def test_expunge_csv_modulairx_cloudapi(self):
        runner = CliRunner()
        result = runner.invoke(expunge_command, 
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
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.csv")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".csv")

def test_expunge_dataframe_noop():
    """Ensure expunge_dataframe doesn't change data that doesn't meet new flags."""
    sample_df = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2023-03-10T17:41:24Z"),
                "rh": 77.6,
                "temp": -10.4,
                "pm1_env": 10.6,
                "pm25_env": 25.0,
                "pm10_env": 32.4,
                "neph_bin0": 1590.375,
                "co_we": 758.8,
                "co_ae": 656.8,
                "co_diff": 102.0,
                "flag": 0,
                "sn" : 'MOD-00001',
            },
        ],
    )

    flagged = expunge_dataframe(sample_df)

    assert_frame_equal(flagged, sample_df)


def test_expunge_dataframe_irrelevant_flag():
    """Ensure expunge_dataframe doesn't change data with irrelevant flags.

    In this case, the flags don't apply to the current columns.
    """
    sample_df = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2023-03-10T17:41:24Z"),
                "rh": 77.6,
                "temp": -10.4,
                "pm1_env": 10.6,
                "pm25_env": 25.0,
                "pm10_env": 32.4,
                "neph_bin0": 1590.375,
                "co_we": 758.8,
                "co_ae": 656.8,
                "co_diff": 102.0,
                "flag": 128,  # FLAG_O3 -- doesn't change any current values
                "sn" : 'MOD-00001',
            },
        ],
    )

    flagged = expunge_dataframe(sample_df)

    assert_frame_equal(flagged, sample_df)


def test_expunge_dataframe_expunges_rht():
    """Ensure expunge_dataframe expunges values correctly for FLAG_RHT."""
    sample_df = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2023-03-10T17:41:24Z"),
                "rh": 20000,  # too high!
                "temp": -10.4,
                "pm1_env": 10.6,
                "pm25_env": 25.0,
                "pm10_env": 32.4,
                "neph_bin0": 1590.375,
                "co_we": 758.8,
                "co_ae": 656.8,
                "co_diff": 102.0,
                "flag": 8,  # FLAG_RHT
                "sn" : 'MOD-00001',
            },
        ],
    )

    flagged = expunge_dataframe(sample_df)

    # Ensure rh and temp are expunged.
    expected = sample_df.copy().assign(rh=np.nan, temp=np.nan)
    assert_frame_equal(flagged, expected, check_dtype=False)


def test_expunge_dataframe_expunges_startup():
    """Ensure expunge_dataframe expunges all columns correctly for FLAG_STARTUP."""
    sample_df = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2023-03-10T17:41:24Z"),
                "sn": "MOD-12345",
                "rh": 20000.,  # too high!
                "temp": -10.4,
                "pm1_env": 10.6,
                "pm25_env": 25.0,
                "pm10_env": 32.4,
                "neph_bin0": 1590.375,
                "co_we": 758.8,
                "co_ae": 656.8,
                "co_diff": 102.0,
                "flag": 1,  # FLAG_STARTUP
            },
        ],
    )

    flagged = expunge_dataframe(sample_df)

    # Ensure most columns are expunged but key metadata is unaffected.
    expected = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime("2023-03-10T17:41:24Z"),
                "sn": "MOD-12345",
                "rh": np.nan,
                "temp": np.nan,
                "pm1_env": np.nan,
                "pm25_env": np.nan,
                "pm10_env": np.nan,
                "neph_bin0": np.nan,
                "co_we": np.nan,
                "co_ae": np.nan,
                "co_diff": np.nan,
                "flag": 1,  # FLAG_STARTUP
            },
        ],
    )
    assert_frame_equal(flagged, expected)


def test_flag_summary_basic():
    """Simple check to confirm flag_summary correctness."""
    sample_df = pd.DataFrame(
        [
            {
                "flag": 1 | 4,  # FLAG_STARTUP | FLAG_NEPH
            },
            {
                "flag": 1 | 32 | 64,  # FLAG_STARTUP | FLAG_NO | FLAG_NO2,
            },
            {
                "flag": 0,
            },
        ],
    )
    summary = flag_summary(sample_df)

    expected = pd.DataFrame(
        {
            "FLAG VALUE": {
                "FLAG_BAT": 2048,
                "FLAG_CO": 16,
                "FLAG_CO2": 256,
                "FLAG_H2S": 1024,
                "FLAG_NEPH": 4,
                "FLAG_NO": 32,
                "FLAG_NO2": 64,
                "FLAG_O3": 128,
                "FLAG_OPC": 2,
                "FLAG_RHTP": 8,
                "FLAG_SO2": 512,
                "FLAG_STARTUP": 1,
            },
            "# OCCURENCES": {
                "FLAG_BAT": 0,
                "FLAG_CO": 0,
                "FLAG_CO2": 0,
                "FLAG_H2S": 0,
                "FLAG_NEPH": 1,
                "FLAG_NO": 1,
                "FLAG_NO2": 1,
                "FLAG_O3": 0,
                "FLAG_OPC": 0,
                "FLAG_RHTP": 0,
                "FLAG_SO2": 0,
                "FLAG_STARTUP": 2,
            },
            "% DATA": {
                "FLAG_BAT": "0.0",
                "FLAG_CO": "0.0",
                "FLAG_CO2": "0.0",
                "FLAG_H2S": "0.0",
                "FLAG_NEPH": "33.3",
                "FLAG_NO": "33.3",
                "FLAG_NO2": "33.3",
                "FLAG_O3": "0.0",
                "FLAG_OPC": "0.0",
                "FLAG_RHTP": "0.0",
                "FLAG_SO2": "0.0",
                "FLAG_STARTUP": "66.7",
            },
        },
    )
    expected.index.name = "FLAG"

    assert_frame_equal(summary.sort_index(), expected.sort_index())

    def test_expunge_modulair_db_parquet(self):
        runner = CliRunner()
        result = runner.invoke(expunge_command, 
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
        self.assertTrue("Saving file" in result.output)

        # make sure the file exists
        p = Path(self.test_dir + "/output.parquet")
        self.assertTrue(p.exists())
        
        # is it a csv?
        self.assertEqual(p.suffix, ".parquet")
