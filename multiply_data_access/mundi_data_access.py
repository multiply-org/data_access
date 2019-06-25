"""
Description
===========

This module contains the functionality to access data from the MUNDI DIAS.
"""
from datetime import datetime
from lxml.etree import XML
import logging
import os
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
         'baseBucket': 's1-l1-slc-{YYYY}-q{q}', 'storageStructure': 'YYYY/MM/DD/mm/pp/',
         'placeholders': {'mm': {'start': 4, 'end': 6}, 'pp': {'start': 14, 'end': 16}}},
    DataTypeConstants.S2_L1C:
        {'platform': 'Sentinel2', 'processingLevel': 'L1C', 'instrument': 'MSI', 'productType': 'IMAGE',
         'baseBucket': 's2-l1c-{YYYY}-q{q}', 'storageStructure': 'UU/L/SS/YYYY/MM/DD/',
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
        if 'access_key_id' not in parameters.keys():
            logging.warning('No access key id set. Will not be able to download data from MUNDI DIAS')
        else:
            self._access_key_id = parameters['access_key_id']
        if 'secret_access_key' not in parameters.keys():
            logging.warning('No secret access key set. Will not be able to download data from MUNDI DIAS')
        else:
            self._secret_access_key = parameters['secret_access_key']
        if 'path' not in parameters.keys():
            raise ValueError('Missing parameter \'path\'')
        self._path = self._get_validated_path(parameters['path'])

    @staticmethod
    def _get_validated_path(path: str) -> str:
        if not os.path.exists(path):
            os.makedirs(path)
        if not path.endswith('/'):
            path += '/'
        return path

    @classmethod
    def name(cls) -> str:
        return _FILE_SYSTEM_NAME

    def get(self, data_set_meta_info: DataSetMetaInfo) -> Sequence[FileRef]:
        from com.obs.client.obs_client import ObsClient
        if data_set_meta_info.data_type not in _DATA_TYPE_PARAMETER_DICTS:
            logging.warning(f'Data Type {data_set_meta_info.data_type} not supported by MUNDI DIAS File System '
                            f'implementation.')
            return []
        bucket = self._get_bucket_name(data_set_meta_info)
        prefix = self._get_prefix(data_set_meta_info)
        obs_client = ObsClient(access_key_id=self._access_key_id,
                               secret_access_key=self._secret_access_key,
                               server=_MUNDI_SERVER)
        objects = obs_client.listObjects(bucketName=bucket, prefix=prefix)
        keys = []
        if objects.status < 300:
            for content in objects.body.contents:
                keys.append(content.key)
        else:
            logging.error(objects.errorCode)
        for key in keys:
            relative_path_to_file = key.split(data_set_meta_info.identifier)[1]
            resp = obs_client.getObject(bucket, key, downloadPath=f'{self._path}/{relative_path_to_file}')
            if resp.status >= 300:
                logging.error(objects.errorCode)
        obs_client.close()

    @staticmethod
    def _get_bucket_name(data_set_meta_info: DataSetMetaInfo):
        start_time = get_time_from_string(data_set_meta_info.start_time)
        base_bucket_name = _DATA_TYPE_PARAMETER_DICTS[data_set_meta_info.data_type]['baseBucket']
        quarter = int(int(start_time.month - 1) / 3) + 1
        bucket_name = base_bucket_name.replace('{YYYY}', str(start_time.year))
        bucket_name = bucket_name.replace('{q}', str(quarter))
        return bucket_name

    @staticmethod
    def _get_prefix(data_set_meta_info: DataSetMetaInfo):
        data_type_dict = _DATA_TYPE_PARAMETER_DICTS[data_set_meta_info.data_type]
        storage_structure = data_type_dict['storageStructure']
        data_time = get_time_from_string(data_set_meta_info.start_time)
        prefix = storage_structure.replace('{}'.format('YYYY'), '{:04d}'.format(data_time.year))
        prefix = prefix.replace('{}'.format('MM'), '{:02d}'.format(data_time.month))
        prefix = prefix.replace('{}'.format('DD'), '{:02d}'.format(data_time.day))
        for placeholder in data_type_dict['placeholders'].keys():
            start = data_type_dict['placeholders'][placeholder]['start']
            end = data_type_dict['placeholders'][placeholder]['end']
            prefix = prefix.replace(placeholder, data_set_meta_info.identifier[start:end])
        return prefix

    def get_parameters_as_dict(self) -> dict:
        return {'access_key_id': self._access_key_id, 'secret_access_key': self._secret_access_key, 'path': self._path}

    def can_put(self) -> bool:
        return False

    def put(self, from_url: str, data_set_meta_info: DataSetMetaInfo) -> DataSetMetaInfo:
        raise UserWarning('Method not supported')

    def remove(self, data_set_meta_info: DataSetMetaInfo):
        raise UserWarning('Method not supported')

    def scan(self) -> Sequence[DataSetMetaInfo]:
        logging.info('Skip scanning of MUNDI DIAS file system')
        return []


class MundiFileSystemAccessor(FileSystemAccessor):

    @classmethod
    def name(cls) -> str:
        return _FILE_SYSTEM_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> FileSystem:
        return MundiFileSystem(parameters)
