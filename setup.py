#!/usr/bin/env python

from setuptools import setup

setup(name='multiply-data-access',
      version='0.1',
      description='MULTIPLY Data Access',
      author='MULTIPLY Team',
      packages=['multiply_data_access',
                'multiply_data_access.aux_data_access',
                'multiply_data_access.brdf_access',
                'multiply_data_access.coarse_res_data_access',
                'multiply_data_access.high_res_data_access',
                'multiply_data_access.sar_data_access'],
     )