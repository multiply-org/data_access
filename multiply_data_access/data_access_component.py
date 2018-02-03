from multiply_data_access import DataStore, FileSystem, MetaInfoProvider
from pathlib import Path
from typing import List
import os
import pkg_resources
import yaml

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


#: List of FileSystem implementations supported by the CLI.
# Entries are classes derived from :py:class:`FileSystem` class.
#: MULTIPLY plugins may extend this list by their implementations during plugin initialisation.
FILE_SYSTEM_REGISTRY = []


#: List of MetaInfoProvider implementations supported by the CLI.
# Entries are classes derived from :py:class:`MetaInfoProvider` class.
#: MULTIPLY plugins may extend this list by their implementations during plugin initialisation.
META_INFO_PROVIDER_REGISTRY = []
MULTIPLY_DIR_NAME = '.multiply'
DATA_STORES_FILE_NAME = 'data_stores.yml'


class DataAccessComponent(object):
    """
    The controlling component. The data access component is responsible for communicating with the various data stores
     and decides which data is used from which data store.
    """

    def __init__(self):
        self._set_file_system_registry()
        self._set_meta_info_provider_registry()
        self._data_stores = []
        self._read_registered_data_stores()

    def get_data_urls(self, roi: str, start_time: str, end_time: str, data_types: str) -> List[str]:
        """
        Builds a query from the given parameters and asks all data stores whether they contain data that match the
        query. If datasets are found, url's to their positions are returned.
        :return: a list of url's to locally stored files that match the conditions given by the query in the parameter.
        """
        query_string = DataAccessComponent._build_query_string(roi, start_time, end_time, data_types)
        urls = []
        print('Start retrieving urls')
        for data_store in self._data_stores:
            print('Retrieving url from data store')
            urls.append('x')
            query_results = data_store.query(query_string)
            for query_result in query_results:
                file_refs = data_store.get(query_result)
                for file_ref in file_refs:
                    urls.append(file_ref.url)
        return urls

    @staticmethod
    def _build_query_string(roi: str, start_time: str, end_time: str, data_types: str) -> str:
        """
        Builds a query string. In a future version, this will be an opensearch url.
        :param roi:
        :param start_time:
        :param end_time:
        :param data_types:
        :return:    A query string that may be passed on to a data store
        """
        return roi + ';' + start_time + ';' + end_time + ';' + data_types

    def _read_registered_data_stores(self) -> None:
        home_dir = str(Path.home())
        multiply_home_dir = '{0}/{1}'.format(home_dir, MULTIPLY_DIR_NAME)
        if not os.path.exists(multiply_home_dir):
            os.mkdir(multiply_home_dir)
        data_stores_file = '{0}/{1}'.format(multiply_home_dir, DATA_STORES_FILE_NAME)
        if not os.path.exists(data_stores_file):
            open(data_stores_file, 'w+')
        self.read_data_stores(data_stores_file)

    def read_data_stores(self, file: str) -> List[DataStore]:
        data_stores = []
        stream = open(file, 'r')
        data_store_lists = yaml.load(stream)
        if data_store_lists is None:
            return data_stores
        for index, data_store_entry in enumerate(data_store_lists['DataStores']):
            if 'FileSystem' not in data_store_entry.keys():
                raise UserWarning('DataStore is missing FileSystem: Cannot read DataStore')
            if 'MetaInfoProvider' not in data_store_entry.keys():
                raise UserWarning('DataStore is missing MetaInfoProvider: Cannot read DataStore')
            file_system = self._create_file_system_from_dict(data_store_entry['FileSystem'])
            meta_info_provider = self._create_meta_info_provider_from_dict(data_store_entry['MetaInfoProvider'])
            if 'Id' in data_store_entry.keys():
                id = data_store_entry['Id']
            else:
                id = index
            data_store = DataStore(file_system, meta_info_provider, id)
            data_stores.append(data_store)
        self._data_stores = self._data_stores + data_stores
        return data_stores

    def _create_file_system_from_dict(self, file_system_as_dict: dict) -> FileSystem:
        parameters = file_system_as_dict['parameters']
        for file_system_accessor in FILE_SYSTEM_REGISTRY:
            if file_system_accessor.name() == file_system_as_dict['type']:
                return file_system_accessor.create_from_parameters(parameters)
        raise UserWarning('Could not find file system of type {0}'.format(file_system_as_dict['type']))

    def _create_meta_info_provider_from_dict(self, meta_info_provider_as_dict: dict) -> MetaInfoProvider:
        parameters = meta_info_provider_as_dict['parameters']
        for meta_info_provider_accessor in META_INFO_PROVIDER_REGISTRY:
            if meta_info_provider_accessor.name() == meta_info_provider_as_dict['type']:
                return meta_info_provider_accessor.create_from_parameters(parameters)
        raise UserWarning('Could not find meta infor provider of type {0}'.format(meta_info_provider_as_dict['type']))

    @staticmethod
    def _set_file_system_registry():
        registered_file_systems = pkg_resources.iter_entry_points('file_system_plugins')
        for registered_file_system in registered_file_systems:
            FILE_SYSTEM_REGISTRY.append(registered_file_system.load())

    @staticmethod
    def _set_meta_info_provider_registry():
        registered_meta_info_providers = pkg_resources.iter_entry_points('meta_info_provider_plugins')
        for registered_meta_info_provider in registered_meta_info_providers:
            META_INFO_PROVIDER_REGISTRY.append(registered_meta_info_provider.load())
