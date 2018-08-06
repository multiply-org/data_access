"""
Description
===========

This module contains the functionality to access data that is encapsulated in the form of a single file in the .vrt
format that is globally an.
"""

import os
import re
import requests

from typing import List, Sequence
import urllib.request as urllib2

from multiply_core.observations import get_file_pattern, is_valid_for
from multiply_core.util import FileRef, get_mime_type
from multiply_data_access.data_access import DataSetMetaInfo, FileSystemAccessor, MetaInfoProvider, \
    MetaInfoProviderAccessor
from multiply_data_access.data_access_component import DataAccessComponent
from multiply_data_access.data_set_meta_info_extraction import DataSetMetaInfoProvision

_META_INFO_PROVIDER_NAME = 'VrtMetaInfoProvider'


class VrtMetaInfoProvider(MetaInfoProvider):

    def __init__(self, parameters: dict):
        if 'vrt_file_name' not in parameters:
            raise ValueError('No name for vrt file provided')
        self._vrt_file_name = parameters['vrt_file_name']
        if 'encapsulated_data_type' not in parameters:
            raise ValueError('Vrt meta info provider must know encapsulated data type')
        self._encapsulated_data_type = parameters['encapsulated_data_type']
        if 'accessed_meta_info_provider' not in parameters:
            raise ValueError('Vrt meta info provider must access other meta info provider')
        data_access_component = DataAccessComponent()
        meta_info_provider_as_dict = {'type': parameters['accessed_meta_info_provider'], 'parameters': parameters}
        self._wrapped_meta_info_provider = \
            data_access_component.create_meta_info_provider_from_dict(meta_info_provider_as_dict)

    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        split_string = query_string.split(';')
        split_string[-1] = self._encapsulated_data_type
        new_query_string = ';'.join(split_string)
        encapsulated_data_meta_set_infos = self._wrapped_meta_info_provider.query(new_query_string)


    def provides_data_type(self, data_type: str) -> bool:
        # return data_type == self._provided_data_type
        return data_type == '.vrt'

    def _get_parameters_as_dict(self) -> dict:
        parameters = {'vrt_file_name': self._vrt_file_name, 'provided_data_type': self._encapsulated_data_type}
        return parameters

class VrtMetaInfoProviderAccessor(MetaInfoProviderAccessor):

    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> VrtMetaInfoProvider:
        return VrtMetaInfoProvider(parameters)