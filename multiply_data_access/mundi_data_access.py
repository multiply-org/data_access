"""
Description
===========

This module contains the functionality to access data from the MUNDI DIAS.
"""
from datetime import datetime
from lxml.etree import XML
import requests
from shapely.geometry import Polygon
from shapely.wkt import dumps
from typing import List, Sequence
import urllib.request as urllib2

from multiply_core.observations import DataTypeConstants
from multiply_core.util import FileRef, get_time_from_string
from multiply_data_access.data_access import DataSetMetaInfo, FileSystem, FileSystemAccessor, MetaInfoProvider, \
    MetaInfoProviderAccessor

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

_META_INFO_PROVIDER_NAME = 'MundiMetaInfoProvider'
_FILE_SYSTEM_NAME = 'MundiFileSystem'

_BASE_URL = 'https://mundiwebservices.com/acdc/catalog/proxy/search/'
_COLLECTIONS_DESCRIPTIONS_ADDITION = 'collections/opensearch/description.xml'
_COLLECTION_DESCRIPTION_ADDITION = '{}/opensearch/description.xml'
_BASE_CATALOGUE_URL = "https://mundiwebservices.com/acdc/catalog/proxy/search/{}/opensearch?q=({})"
_POLYGON_FORMAT = 'POLYGON(({1} {0}, {3} {2}, {5} {4}, {7} {6}, {9} {8}))'
_DATA_TYPE_PARAMETER_DICTS = {
    DataTypeConstants.S1_SLC:
        {'platform': 'Sentinel1', 'processingLevel': 'L1_', 'instrument': 'SAR', 'productType': 'SLC',
         'baseBucket': 's1-l1-slc', 'storageStructure': 'YYYY/MM/DD/mm/pp/',
         'placeholders': {'mm': {'start': 4, 'end': 6}, 'pp': {'start': 14, 'end': 16}}},
    DataTypeConstants.S2_L1C:
        {'platform': 'Sentinel2', 'processingLevel': 'L1C', 'instrument': 'MSI', 'productType': 'IMAGE',
         'baseBucket': 's2-l1c', 'storageStructure': 'UU/L/SS/YYYY/MM/DD/',
         'placeholders': {'UU': {'start': 39, 'end': 41}, 'L': {'start': 41, 'end': 42},
                          'SS': {'start': 42, 'end': 44}}},
    DataTypeConstants.S3_L1_OLCI_RR:
        {'platform': 'Sentinel3', 'processingLevel': 'L1_', 'instrument': 'OLCI', 'productType': 'OL_1_ERR___',
         'baseBucket': 's3-olci', 'storageStructure': 'LRR/YYYY/MM/DD/', 'placeholders': {}},
    DataTypeConstants.S3_L1_OLCI_FR:
        {'platform': 'Sentinel3', 'processingLevel': 'L1_', 'instrument': 'OLCI', 'productType': 'OL_1_EFR___',
         'baseBucket': 's3-olci', 'storageStructure': 'LFR/YYYY/MM/DD/', 'placeholders': {}}
}
_MUNDI_SERVER = 'obs.otc.t-systems.com'


class MundiMetaInfoProvider(MetaInfoProvider):

    def __init__(self, parameters: dict):
        collections_description_url = '{}{}'.format(_BASE_URL, _COLLECTIONS_DESCRIPTIONS_ADDITION)
        descriptions = urllib2.urlopen(collections_description_url).read()
        descriptions_root = XML(descriptions)
        platforms = []
        # todo make this more sophisticated
        for child in descriptions_root:
            if child.tag == '{http://a9.com/-/spec/opensearch/1.1/}Url':
                if child.get('rel') == 'search':
                    for child2 in child:
                        if child2.tag == '{http://a9.com/-/spec/opensearch/extensions/parameters/1.0/}Parameter':
                            for child3 in child2:
                                platforms.append(child3.get('value'))
        self._provided_data_types = []
        for data_type in _DATA_TYPE_PARAMETER_DICTS:
            data_type_dict = _DATA_TYPE_PARAMETER_DICTS[data_type]
            instruments = []
            processing_levels = []
            product_types = []
            if data_type_dict['platform'] in platforms:
                platform_url = '{}{}'.format(_BASE_URL, _COLLECTION_DESCRIPTION_ADDITION.format(data_type_dict['platform']))
                description = urllib2.urlopen(platform_url).read()
                platform_description_root = XML(description)
                for child in platform_description_root:
                    if child.tag == '{http://a9.com/-/spec/opensearch/1.1/}Url':
                        for child2 in child:
                            if child2.tag == '{http://a9.com/-/spec/opensearch/extensions/parameters/1.0/}Parameter':
                                if child2.get('name') == 'instrument':
                                    for child3 in child2:
                                        instruments.append(child3.get('value'))
                                elif child2.get('name') == 'processingLevel':
                                    for child3 in child2:
                                        processing_levels.append(child3.get('value'))
                                elif child2.get('name') == 'productType':
                                    for child3 in child2:
                                        product_types.append(child3.get('value'))
            if data_type_dict['instrument'] in instruments and \
                    data_type_dict['processingLevel'] in processing_levels and \
                    data_type_dict['productType'] in product_types:
                self._provided_data_types.append(data_type)

    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        roi = dumps(self.get_roi_from_query_string(query_string))
        data_types = self.get_data_types_from_query_string(query_string)
        start_time = datetime.strftime(self.get_start_time_from_query_string(query_string), "%Y-%m-%dT%H:%M:%SZ")
        end_time = datetime.strftime(self.get_end_time_from_query_string(query_string), "%Y-%m-%dT%H:%M:%SZ")
        data_set_meta_infos = []
        for data_type in data_types:
            if self.provides_data_type(data_type):
                mundi_query = self._create_mundi_query(roi, data_type, start_time, end_time)
                response = requests.get(mundi_query)
                response_xml = XML(response.content)
                for child in response_xml:
                    if child.tag == '{http://www.w3.org/2005/Atom}entry':
                        data_set_meta_info_id = ""
                        data_set_meta_info_time = ""
                        data_set_meta_info_coverage = ""
                        for child2 in child:
                            if child2.tag == '{http://www.w3.org/2005/Atom}id':
                                data_set_meta_info_id = child2.text
                            elif child2.tag == '{http://www.georss.org/georss}polygon':
                                data_set_meta_info_coverage = self._convert_mundi_coverage(child2.text)
                            elif child2.tag == '{http://tas/DIAS}sensingStartDate':
                                data_set_meta_info_time = child2.text
                        data_set_meta_info = DataSetMetaInfo(data_set_meta_info_coverage, data_set_meta_info_time,
                                                             data_set_meta_info_time, data_type, data_set_meta_info_id)
                        data_set_meta_infos.append(data_set_meta_info)
        return data_set_meta_infos

    @staticmethod
    def _create_mundi_query(roi: str, data_type: str, start_time: str, end_time: str) -> str:
        data_type_dict = _DATA_TYPE_PARAMETER_DICTS[data_type]
        query_part = "(sensingStartDate:[{} TO {}]AND footprint:\"Intersects({})\")&processingLevel={}&instrument={}" \
                     "&productType={}"
        query_part = query_part.format(start_time, end_time, roi, data_type_dict['processingLevel'],
                                       data_type_dict['instrument'], data_type_dict['productType'])
        return _BASE_CATALOGUE_URL.format(data_type_dict['platform'], query_part)

    @staticmethod
    def _convert_mundi_coverage(mundi_coverage_string: str):
        coords = mundi_coverage_string.split(" ")
        coord_list = []
        for i in range(0, len(coords), 2):
            coord_list.append((float(coords[i + 1]), float(coords[i])))
        coverage = Polygon(coord_list)
        return dumps(coverage)

    def provides_data_type(self, data_type: str) -> bool:
        return data_type in self._provided_data_types

    def get_provided_data_types(self) -> List[str]:
        return self._provided_data_types

    def encapsulates_data_type(self, data_type: str) -> bool:
        return False

    def _get_parameters_as_dict(self) -> dict:
        return {}

    def can_update(self) -> bool:
        return False

    def update(self, data_set_meta_info: DataSetMetaInfo):
        # todo raise exception
        pass

    def remove(self, data_set_meta_info: DataSetMetaInfo):
        # todo raise exception
        pass

    def get_all_data(self) -> Sequence[DataSetMetaInfo]:
        # todo raise exception
        return []


class MundiMetaInfoProviderAccessor(MetaInfoProviderAccessor):

    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> MundiMetaInfoProvider:
        return MundiMetaInfoProvider(parameters)


class MundiFileSystem(FileSystem):

    def __init__(self, parameters: dict):
        pass

    @classmethod
    def name(cls) -> str:
        return _FILE_SYSTEM_NAME

    def get(self, data_set_meta_info: DataSetMetaInfo) -> Sequence[FileRef]:
        pass

    def get_parameters_as_dict(self) -> dict:
        pass

    def can_put(self) -> bool:
        pass

    def put(self, from_url: str, data_set_meta_info: DataSetMetaInfo) -> DataSetMetaInfo:
        pass

    def remove(self, data_set_meta_info: DataSetMetaInfo):
        pass

    def scan(self) -> Sequence[DataSetMetaInfo]:
        return []


class MundiFileSystemAccessor(FileSystemAccessor):

    @classmethod
    def name(cls) -> str:
        return _FILE_SYSTEM_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> FileSystem:
        return MundiFileSystem(parameters)
