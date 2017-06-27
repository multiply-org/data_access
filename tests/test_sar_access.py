"""
Test for SAR data access provider
"""

import unittest

from multiply_data_access.sar_data_access import SARDataAccessProvider

class TestSAR(unittest.TestCase):
    def test_init(self):
        S = SARDataAccessProvider()
