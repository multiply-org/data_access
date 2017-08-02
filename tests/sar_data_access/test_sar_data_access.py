"""
Test for SAR data access provider
"""

import unittest

from multiply_dummy.configuration import Configuration
from multiply_dummy.state import TargetState

from multiply_data_access.sar_data_access import SARDataAccessProvider
import datetime

import os
import tempfile


class TestSAR(unittest.TestCase):
    
    def setUp(self):
        self.output_dir = tempfile.mkdtemp() + os.sep
        t1 = datetime.datetime(2000, 1, 1)
        t2 = datetime.datetime(2002, 12, 31)
        t_state = TargetState(state={'lai': True, 'sm': False})
        r = {}
        r.update({'lr': {'lat': 45., 'lon': 11.2}})
        r.update({'ul': {'lat': 47., 'lon': 10.2}})
        self.c = Configuration(region=r, time_start=t1, time_stop=t2, tstate=t_state)

    def test_init(self):
        output_dir = self.output_dir + 'xyz'
        s = SARDataAccessProvider(config=self.c, output_dir=output_dir)
        self.assertTrue(os.path.exists(s.output_dir))
        self.assertTrue(s.output_dir[-1] == os.sep)

    def test_get_data(self):
        s = SARDataAccessProvider(config=self.c, output_dir=self.output_dir)
        r = s.get_data()
        self.assertTrue(isinstance(r, str))
