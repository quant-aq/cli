import os
import shutil
import tempfile
import unittest
from os import path
from pathlib import Path

import numpy as np
import pandas as pd
from click.testing import CliRunner
from loguru import logger

from quantaq_py.resample import resample_dataframe
from quantaq_py.cli import resample_command
from quantaq_py.utilities import safe_load


class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_resample_files_csv(self):
        runner = CliRunner()
        result = runner.invoke(resample_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "arisense/ref/ref.csv"), 
                        "10min",
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

        # are the number of lines correct?
        df = pd.read_csv(os.path.join(self.test_dir, "output.csv"))
        df['timestamp'] = df['timestamp'].map(pd.to_datetime)
       
        idx = df.timestamp.values

        self.assertEqual((idx[1] - idx[0]) / np.timedelta64(1, 's'), 600.0)

    def test_resample_modulair_db(self):
        runner = CliRunner()
        result = runner.invoke(resample_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair/MOD-00014-db-raw.csv"), 
                        "1h",
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

        # are the number of lines correct?
        df = pd.read_csv(os.path.join(self.test_dir, "output.csv"))
        df['timestamp'] = df['timestamp'].map(pd.to_datetime)
       
        idx = df.timestamp.values

        self.assertEqual((idx[1] - idx[0]) / np.timedelta64(1, 's'), 3600.0)

    def test_resample_modulairpm_rawsd(self):
        runner = CliRunner()
        result = runner.invoke(resample_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"), 
                        "10min",
                        "--on",
                        "timestamp_iso"
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

        # are the number of lines correct?
        df = pd.read_csv(os.path.join(self.test_dir, "output.csv"))
        df['timestamp_iso'] = df['timestamp_iso'].map(pd.to_datetime)
       
        idx = df.timestamp_iso.values

        self.assertEqual((idx[1] - idx[0]) / np.timedelta64(1, 's'), 600.0)

    def test_resample_modulairx_rawsd(self):
        runner = CliRunner()
        result = runner.invoke(resample_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"), 
                        "10min",
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

        # are the number of lines correct?
        df = pd.read_csv(os.path.join(self.test_dir, "output.csv"))
        df['timestamp'] = df['timestamp'].map(pd.to_datetime)
       
        idx = df.timestamp.values

        self.assertEqual((idx[1] - idx[0]) / np.timedelta64(1, 's'), 600.0)

    def test_resample_modulairx_cloudapi(self):
        runner = CliRunner()
        result = runner.invoke(resample_command, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "--log-level",
                        "DEBUG",
                        os.path.join(self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"), 
                        "10min",
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

        # are the number of lines correct?
        df = pd.read_csv(os.path.join(self.test_dir, "output.csv"))
        df['timestamp'] = df['timestamp'].map(pd.to_datetime)
       
        idx = df.timestamp.values

        self.assertEqual((idx[1] - idx[0]) / np.timedelta64(1, 's'), 600.0)

    def test_resample_dataframe_nan_winds(self):
        """Test for edge case in case u/v cols exist but have nans.
        """
        file = os.path.join(
            self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"
        )

        expected = pd.DataFrame(
            {"wx_wd": [171.0000, 187.9838],
             "wx_ws": [1.53998, 0.49199]},
        )
        atol = 1e-3

        # case 1: all u/v rows are nan
        df1 = safe_load(file)
        df1["wx_u"] = np.nan
        df1["wx_v"] = np.nan

        df1_resampled = resample_dataframe(df1, "10min")
        np.testing.assert_allclose(
            df1_resampled[["wx_wd", "wx_ws"]].to_numpy(),
            expected.to_numpy(),
            atol=atol, equal_nan=True,
        )

        # case 2: some u/v rows are nan
        df2 = safe_load(file) # has 1 row where wx_u and wx_v are nan

        df2_resampled = resample_dataframe(df2, "10min")
        np.testing.assert_allclose(
            df2_resampled[["wx_wd", "wx_ws"]].to_numpy(),
            expected.to_numpy(),
            atol=atol, equal_nan=True,
        )
