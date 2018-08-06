"""
Description
===========

This module contains the functionality to access data that is encapsulated in the form of a single file in the .vrt
format that is globally an.
"""

import gdal
import os

from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import cascaded_union
from shapely.wkt import loads
from typing import List, Optional, Sequence
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
        if 'path_to_vrt_file' not in parameters:
            raise ValueError('No vrt file provided')
        self._path_to_vrt_file = parameters['path_to_vrt_file']
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
        roi = self.get_roi_from_query_string(query_string)
        if not os.path.exists(self._path_to_vrt_file):
            coverages = self._get_coverages_from_wrapped_meta_info_provider(query_string)
            coverage = cascaded_union(coverages)
        else:
            vrt_data_set = gdal.Open(self._path_to_vrt_file)
            vrt_coverage = loads(vrt_data_set.GetMetadataItem('COVERAGE'))
            if roi.within(vrt_coverage):
                coverage = vrt_coverage
            else:
                coverages = self._get_coverages_from_wrapped_meta_info_provider(query_string)
                coverages.append(vrt_coverage)
                coverage = cascaded_union(coverages)
        data_set_meta_info = DataSetMetaInfo(coverage.wkt, None, None, 'VRT', self._path_to_vrt_file)
        return [data_set_meta_info]

    def _get_coverages_from_wrapped_meta_info_provider(self, query_string:str) -> List[Polygon]:
        split_string = query_string.split(';')
        split_string[-1] = self._encapsulated_data_type
        new_query_string = ';'.join(split_string)
        encapsulated_data_meta_set_infos = self._wrapped_meta_info_provider.query(new_query_string)
        coverages = []
        for data_set_meta_info in encapsulated_data_meta_set_infos:
            coverages.append(loads(data_set_meta_info.coverage))
        return coverages

    def provides_data_type(self, data_type: str) -> bool:
        return data_type == 'VRT'

    def _get_parameters_as_dict(self) -> dict:
        parameters = {'vrt_file_name': self._path_to_vrt_file, 'provided_data_type': self._encapsulated_data_type}
        return parameters

class VrtMetaInfoProviderAccessor(MetaInfoProviderAccessor):

    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> VrtMetaInfoProvider:
        return VrtMetaInfoProvider(parameters)