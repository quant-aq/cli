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
        ]
        for sn, expected in cases:
            with self.subTest(sn=sn):
                self.assertEqual(sn_to_model(sn), expected)

    def test_infer_data_model(self):
        file = os.path.join(
            self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"
        )
        expected = "modulair-x"
        df = safe_load(file, add_sn_column=True)
        result = infer_data_model(df)

        self.assertEqual(result, expected)

    def test_infer_data_source(self):
        df1 = safe_load(os.path.join(
            self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"))
        df2 = safe_load(os.path.join(
            self.test_files_dir, "modulair/MOD-00014-db-raw.csv"))
        df3 = safe_load(os.path.join(
            self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"))

        cases = [
            (df1, "rawsd"),
            (df2, "database"),
            (df3, "cloudapi"),
        ]

        for df, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(infer_data_source(df), expected)

