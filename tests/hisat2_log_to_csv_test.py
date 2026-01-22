import unittest
import os
import pandas as pd
import numpy as np
import sys

# Add the test directory to path so we can import base
test_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(test_dir)

from base import TestBase

LOG_CONTENTS = \
"""10000 reads; of these:
  1000 (10.00%) aligned 0 times
  6000 (60.00%) aligned exactly 1 time
  3000 (30.00%) aligned >1 times
90.00% overall alignment rate"""

class TestHisat2Log(TestBase):
    
    def setUp(self):
        self.log_file = "hisat2_log.txt"
        self.output_file = "hisat2_log.csv"
        
        self.files = [self.log_file, self.output_file]
        
        with open(self.log_file, "w") as output_stream:
            print(LOG_CONTENTS, file=output_stream)
        
    def test_convert_log(self):
        
        command = ["rfc", "hisat2-log-to-csv",
                   "--log", self.log_file,
                   "--out", self.output_file,
                   "-n", "Sample1",
                   "-p", "genome"]
        
        output, error = self.run_command(command)
        
        # Check if the command ran successfully
        if error and "Error" in error:
            self.fail(f"Command failed with error: {error}")
            
        result_df = pd.read_csv(self.output_file, index_col=0)
        
        self.assertTrue("Sample1" in result_df.keys())
        
        # Expected order based on write_csv in hisat2_log_to_csv.py:
        # aligned_once, aligned_once_%, aligned_many, aligned_many_%,
        # total_aligned, total_aligned_%, unaligned, unaligned_%
        expected_values = [
            6000,   # aligned_once
            60.00,  # aligned_once_%
            3000,   # aligned_many
            30.00,  # aligned_many_%
            9000,   # total_aligned
            90.00,  # total_aligned_%
            1000,   # unaligned
            10.00   # unaligned_%
        ]
        
        self.assertTrue(np.allclose(result_df["Sample1"], expected_values))

if __name__ == '__main__':
    unittest.main()
