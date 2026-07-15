import os
import shutil
import tempfile
import unittest

import numpy as np

from quantaq_cli.toolkit.load import safe_load
from quantaq_cli.schema import standardize_columns 

class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_files_dir = os.path.join(os.getcwd(), "tests/files")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_schema_migration_modpm_rawsd(self):
        df1 = safe_load(os.path.join(
            self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"), validate_dataframe_schema=False)
        df2 = safe_load(os.path.join(
            self.test_files_dir, "modulair-pm/MOD-PM-00001-rawsd-file1.csv"), validate_dataframe_schema=True)

        df1_expected_columns = [
            'timestamp_iso',
            'sample_rh',
            'sample_temp',
            'sample_pres',
            'bin0',
            'bin1',
            'bin2',
            'bin3',
            'bin4',
            'bin5',
            'bin6',
            'bin7',
            'bin8',
            'bin9',
            'bin10',
            'bin11',
            'bin12',
            'bin13',
            'bin14',
            'bin15',
            'bin16',
            'bin17',
            'bin18',
            'bin19',
            'bin20',
            'bin21',
            'bin22',
            'bin23',
            'bin1MToF',
            'bin3MToF',
            'bin5MToF',
            'bin7MToF',
            'sample_period',
            'sample_flow',
            'opc_temp',
            'opc_rh',
            'opc_pm1',
            'opc_pm25',
            'opc_pm10',
            'laser_status',
            'pm1_std',
            'pm25_std',
            'pm10_std',
            'pm1_env',
            'pm25_env',
            'pm10_env',
            'neph_bin0',
            'neph_bin1',
            'neph_bin2',
            'neph_bin3',
            'neph_bin4',
            'neph_bin5',
            'flag',
            'fw',
            'sn'
        ]

        df2_expected_columns = [
            'timestamp_iso',
            'sample_rh',
            'sample_temp',
            'sample_pres',
            'opc_bin0',
            'opc_bin1',
            'opc_bin2',
            'opc_bin3',
            'opc_bin4',
            'opc_bin5',
            'opc_bin6',
            'opc_bin7',
            'opc_bin8',
            'opc_bin9',
            'opc_bin10',
            'opc_bin11',
            'opc_bin12',
            'opc_bin13',
            'opc_bin14',
            'opc_bin15',
            'opc_bin16',
            'opc_bin17',
            'opc_bin18',
            'opc_bin19',
            'opc_bin20',
            'opc_bin21',
            'opc_bin22',
            'opc_bin23',
            'opc_bin1MToF',
            'opc_bin3MToF',
            'opc_bin5MToF',
            'opc_bin7MToF',
            'opc_sample_period',
            'opc_sample_flow',
            'opc_temp',
            'opc_rh',
            'opc_pm1',
            'opc_pm25',
            'opc_pm10',
            'opc_laser_status',
            'neph_pm1_std',
            'neph_pm25_std',
            'neph_pm10_std',
            'neph_pm1_env',
            'neph_pm25_env',
            'neph_pm10_env',
            'neph_bin0',
            'neph_bin1',
            'neph_bin2',
            'neph_bin3',
            'neph_bin4',
            'neph_bin5',
            'flag',
            'fw',
            'sn'
        ]
        
        cases = [
            (list(df1.columns), df1_expected_columns),
            (list(df2.columns), df2_expected_columns),
        ]

        for actual, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(actual, expected)

    def test_schema_migration_modx_api(self):
        df1 = safe_load(os.path.join(
            self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"), validate_dataframe_schema=False)
        df2 = safe_load(os.path.join(
            self.test_files_dir, "modulair-x/MOD-X-00993-cloudapi-file1.csv"), validate_dataframe_schema=True)

        df1_expected_columns =[
            'dd_operating_state',
            'flag',
            'sample_rh',
            'sample_temp',
            'sn',
            'timestamp',
            'timestamp_local',
            'url',
            'gases.co.ae',
            'gases.co.diff',
            'gases.co.we',
            'gases.no.ae',
            'gases.no.diff',
            'gases.no.we',
            'gases.no2.ae',
            'gases.no2.diff',
            'gases.no2.we',
            'gases.o3.ae',
            'gases.o3.diff',
            'gases.o3.we',
            'geo.lat',
            'geo.lon',
            'neph.bin0',
            'neph.pm1',
            'neph.pm10',
            'neph.pm25',
            'opc.bin0',
            'opc.bin1',
            'opc.bin10',
            'opc.bin11',
            'opc.bin12',
            'opc.bin13',
            'opc.bin14',
            'opc.bin15',
            'opc.bin16',
            'opc.bin17',
            'opc.bin18',
            'opc.bin19',
            'opc.bin2',
            'opc.bin20',
            'opc.bin21',
            'opc.bin22',
            'opc.bin23',
            'opc.bin3',
            'opc.bin4',
            'opc.bin5',
            'opc.bin6',
            'opc.bin7',
            'opc.bin8',
            'opc.bin9',
            'opc.pm1',
            'opc.pm10',
            'opc.pm25'
            ]

        df2_expected_columns = [
            'dd_operating_state',
            'flag',
            'sample_rh',
            'sample_temp',
            'sn',
            'timestamp',
            'timestamp_local',
            'url',
            'co_ae',
            'co_diff',
            'co_we',
            'no_ae',
            'no_diff',
            'no_we',
            'no2_ae',
            'no2_diff',
            'no2_we',
            'o3_ae',
            'ox_diff',
            'o3_we',
            'lat',
            'lon',
            'neph_bin0',
            'neph_pm1_env',
            'neph_pm10_env',
            'neph_pm25_env',
            'opc_bin0',
            'opc_bin1',
            'opc_bin10',
            'opc_bin11',
            'opc_bin12',
            'opc_bin13',
            'opc_bin14',
            'opc_bin15',
            'opc_bin16',
            'opc_bin17',
            'opc_bin18',
            'opc_bin19',
            'opc_bin2',
            'opc_bin20',
            'opc_bin21',
            'opc_bin22',
            'opc_bin23',
            'opc_bin3',
            'opc_bin4',
            'opc_bin5',
            'opc_bin6',
            'opc_bin7',
            'opc_bin8',
            'opc_bin9',
            'opc_pm1',
            'opc_pm10',
            'opc_pm25'
        ]
        
        cases = [
            (list(df1.columns), df1_expected_columns),
            (list(df2.columns), df2_expected_columns),
        ]

        for actual, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(actual, expected)
