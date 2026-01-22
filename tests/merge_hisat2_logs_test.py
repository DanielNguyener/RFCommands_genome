import unittest
import os
import sys

# Add the test directory to path so we can import base
test_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(test_dir)

from base import TestBase

LOG_1 = \
"""10000 reads; of these:
  1000 (10.00%) aligned 0 times
  6000 (60.00%) aligned exactly 1 time
  3000 (30.00%) aligned >1 times
90.00% overall alignment rate"""

LOG_2 = \
"""20000 reads; of these:
  2000 (10.00%) aligned 0 times
  12000 (60.00%) aligned exactly 1 time
  6000 (30.00%) aligned >1 times
90.00% overall alignment rate"""

class TestMergeHisat2Logs(TestBase):
    
    def setUp(self):
        self.log1_file = "hisat2_log_1.txt"
        self.log2_file = "hisat2_log_2.txt"
        self.output_log = "hisat2_merged_log.txt"
        
        self.files = [self.log1_file, self.log2_file, self.output_log]
        
        with open(self.log1_file, "w") as output_stream:
            print(LOG_1, file=output_stream)
            
        with open(self.log2_file, "w") as output_stream:
            print(LOG_2, file=output_stream)
        
    def test_merge_logs(self):
        command = ["rfc", "merge-hisat2-logs",
                   "--output", self.output_log,
                   self.log1_file, self.log2_file]
        
        output, error = self.run_command(command)
        
        if error and "Error" in error:
            self.fail(f"Command failed with error: {error}")
            
        with open(self.output_log) as read_stream:
            output_lines = read_stream.readlines()
            
        # Parse the merged log to verify values
        # Format:
        # <total> reads; of these:
        #   <total> (100.00%) were unpaired; of these:
        #     <unaligned> (<pct>%) aligned 0 times
        #     <aligned_once> (<pct>%) aligned exactly 1 time
        #     <aligned_many> (<pct>%) aligned >1 times
        # <overall>% overall alignment rate
        
        self.assertTrue(len(output_lines) >= 6)
        
        total_reads_line = output_lines[0]
        self.assertTrue(total_reads_line.startswith("30000 reads"))
        
        unaligned_line = output_lines[2]
        self.assertTrue("3000" in unaligned_line and "aligned 0 times" in unaligned_line)
        
        aligned_once_line = output_lines[3]
        self.assertTrue("18000" in aligned_once_line and "aligned exactly 1 time" in aligned_once_line)
        
        aligned_many_line = output_lines[4]
        self.assertTrue("9000" in aligned_many_line and "aligned >1 times" in aligned_many_line)
        
        overall_line = output_lines[5]
        self.assertTrue("90.00%" in overall_line and "overall alignment rate" in overall_line)

if __name__ == '__main__':
    unittest.main()
