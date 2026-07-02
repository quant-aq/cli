import os
import shutil
import tempfile
import unittest

import numpy as np

from quantaq_py.utilities import safe_load
from quantaq_py.utilities import sn_to_model, infer_data_model, infer_data_source

class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_sn_to_model(self):
        cases = [
            ("MOD-00246", "modulair"),
            ("MOD-PM-00933", "modulair-pm"),
            ("MOD-X-00993", "modulair-x"),
            ("MOD-X-PM-01685", "modulair-x-pm"),
            ("MOD-UFP-01685", "modulair-ufp"),
        ]
        for sn, expected in cases:
            with self.subTest(sn=sn):
                self.assertEqual(sn_to_model(sn), expected)

    def test_infer_data_model(self):
        df1 = safe_load(os.path.join(
            self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"))
        df2 = safe_load(os.path.join(
            self.test_files_dir, "modulair/MOD-00014-db-raw.csv"))
        df3 = safe_load(os.path.join(
            self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"))
        df4 = safe_load(os.path.join(
            self.test_files_dir, "modulair/MOD-00256-db-cleaned-file1.parquet"))
        df5 = safe_load(os.path.join(
            self.test_files_dir, "modulair-ufp/MOD-UFP-00002-rawsd.csv"))

        cases = [
            (df1, "modulair-pm"),
            (df2, "modulair"),
            (df3, "modulair-x"),
            (df4, "modulair"),
            (df5, "modulair-ufp"),
        ]

        for df, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(infer_data_model(df), expected)

    def test_infer_data_source(self):
        df1 = safe_load(os.path.join(
            self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"))
        df2 = safe_load(os.path.join(
            self.test_files_dir, "modulair/MOD-00014-db-raw.csv"))
        df3 = safe_load(os.path.join(
            self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"))
        df4 = safe_load(os.path.join(
            self.test_files_dir, "modulair/MOD-00256-db-cleaned-file1.parquet"))
        df5 = safe_load(os.path.join(
            self.test_files_dir, "modulair-ufp/MOD-UFP-00002-rawsd.csv"))
        df6 = safe_load(os.path.join(
            self.test_files_dir, "modulair-ufp/MOD-UFP-00002-rawsd-mixed-tdiffs.csv"))
        
        cases = [
            (df1, "rawsd"),
            (df2, "database"),
            (df3, "cloudapi"),
            (df4, "database"),
            (df5, "rawsd"),
            (df6, "rawsd"),
        ]

        for df, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(infer_data_source(df), expected)

