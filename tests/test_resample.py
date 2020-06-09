import unittest
from click.testing import CliRunner
from os import path
from pathlib import Path
import os
import shutil, tempfile
import pandas as pd
import numpy as np

from quantaq_cli.console import resample


class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_resample_files_csv(self):
        runner = CliRunner()
        result = runner.invoke(resample, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.csv"),
                        "-v",
                        os.path.join(self.test_files_dir, "ref.csv"), 
                        "10min",
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

        # are the number of lines correct?
        df = pd.read_csv(os.path.join(self.test_dir, "output.csv"))
        df['timestamp'] = df['timestamp'].map(pd.to_datetime)
       
        idx = df.timestamp.values

        self.assertEqual((idx[1] - idx[0]) / np.timedelta64(1, 's'), 600.0)

    def test_resample_files_feather(self):
        runner = CliRunner()
        result = runner.invoke(resample, 
                    [
                        "-o",
                        os.path.join(self.test_dir, "output.feather"),
                        "-v",
                        os.path.join(self.test_files_dir, "ref.csv"), 
                        "10min",
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

        # are the number of lines correct?
        df = pd.read_feather(os.path.join(self.test_dir, "output.feather"))

        idx = df.timestamp.values

        self.assertEqual((idx[1] - idx[0]) / np.timedelta64(1, 's'), 600.0)