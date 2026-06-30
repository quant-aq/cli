import os
import shutil
import tempfile
import unittest

import numpy as np

from quantaq_cli.utilities import sn_to_model, safe_load, infer_data_model

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
        for serial, expected in cases:
            with self.subTest(serial=serial):
                self.assertEqual(sn_to_model(serial), expected)

    def test_infer_data_model(self):
        file = os.path.join(
            self.test_files_dir, "modulair-x/MOD-X-00891-rawsd-file1.csv"
        )
        expected = "modulair-x"
        df = safe_load(file)
        result = infer_data_model(df)

        self.assertEqual(result, expected)
