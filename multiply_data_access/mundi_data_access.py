"""
Description
===========

This module contains the functionality to access data from the MUNDI DIAS.
"""
from lxml.etree import XML
from typing import Sequence, List
import urllib.request as urllib2

from multiply_core.observations import DataTypeConstants
from multiply_core.util import FileRef
from multiply_data_access.data_access import DataSetMetaInfo, FileSystem, FileSystemAccessor, MetaInfoProvider, \
    MetaInfoProviderAccessor

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

_META_INFO_PROVIDER_NAME = 'MundiMetaInfoProvider'
_FILE_SYSTEM_NAME = 'MundiFileSystem'

_BASE_URL = 'https://mundiwebservices.com/acdc/catalog/proxy/search/'
_COLLECTIONS_DESCRIPTIONS_ADDITION = 'collections/opensearch/description.xml'
_COLLECTION_DESCRIPTION_ADDITION = '{}/opensearch/description.xml'


class MundiMetaInfoProvider(MetaInfoProvider):

    def __init__(self, parameters: dict):
        collections_description_url = '{}{}'.format(_BASE_URL, _COLLECTIONS_DESCRIPTIONS_ADDITION)
        # collections_request = requests.get(collections_description_url, stream=True)
        descriptions = urllib2.urlopen(collections_description_url).read()
        descriptions_root = XML(descriptions)
        platforms = []
        for child in descriptions_root:
            if child.tag == '{http://a9.com/-/spec/opensearch/1.1/}Url':
                if child.get('rel') == 'search':
                    for child2 in child:
                        if child2.tag == '{http://a9.com/-/spec/opensearch/extensions/parameters/1.0/}Parameter':
                            for child3 in child2:
                                platforms.append(child3.get('value'))
        # collections_request.close()
        instruments = []
        processing_levels = []
        if 'Sentinel2' in platforms:
            platform_url = '{}{}'.format(_BASE_URL, _COLLECTION_DESCRIPTION_ADDITION.format('Sentinel2'))
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
        self._provided_data_types = []
        if 'MSI' in instruments and 'L1C' in processing_levels:
            self._provided_data_types.append(DataTypeConstants.S2_L1C)

    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        pass

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
        pass

    def remove(self, data_set_meta_info: DataSetMetaInfo):
        pass

    def get_all_data(self) -> Sequence[DataSetMetaInfo]:
        pass


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
        pass


class MundiFileSystemAccessor(FileSystemAccessor):

    @classmethod
    def name(cls) -> str:
        return _FILE_SYSTEM_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> FileSystem:
        return MundiFileSystem(parameters)
