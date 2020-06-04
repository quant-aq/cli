import unittest
from os import path
import shutil, tempfile
import pandas as pd

def create_fake_file(fpath, **kwargs):
    header = kwargs.pop("header", False)
    nrows  = kwargs.pop("nrows", 25)

    cols = ["timestamp", "id", "temp_box", "bin0", "bin1", "bin2", "bin3", "co_we", "co_ae", "flag"]

    # create the times
    timestamps = pd.date_range("2020-01-01", periods=nrows, freq='min')

    # open a file for writing
    with open(fpath, "a") as f:
        if header:
            f.write("deviceID,12703192301\n")
        
        # write the real header column
        f.write(",".join(cols) + "\n")

        for i, r in enumerate(range(nrows)):
            f.write(str(timestamps[i]) + ",")
            f.write("\n")


class SetupTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_something(self):
        fpath = path.join(self.test_dir, "test.csv")
        
        create_fake_file(fpath, header=True, nrows=10)

        with open(fpath, "r") as f:
            content = f.readlines()
        
        for line in [x.strip() for x in content]:
            print (line)