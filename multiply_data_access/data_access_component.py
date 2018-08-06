from multiply_data_access import DataStore, FileSystem, MetaInfoProvider, WritableDataStore
from .aws_s2_file_system import AwsS2FileSystem
from .aws_s2_meta_info_provider import AwsS2MetaInfoProvider
from .json_meta_info_provider import JsonMetaInfoProvider
from .local_file_system import LocalFileSystem
from pathlib import Path
from typing import List, Optional
import os
import json
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
DATA_FOLDER_NAME = 'data'


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
        for data_store in self._data_stores:
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
        data_stores_file = self._get_default_data_stores_file()
        self.read_data_stores(data_stores_file)

    def _get_default_data_stores_file(self) -> str:
        multiply_home_dir = self._get_multiply_home_dir()
        data_stores_file = '{0}/{1}'.format(multiply_home_dir, DATA_STORES_FILE_NAME)
        if not os.path.exists(data_stores_file):
            open(data_stores_file, 'w+')
            self._add_default_stores()
        return data_stores_file

    def _add_default_stores(self):
        """Will add the default stores to the data stores file when it is created."""
        # todo remove this from here
        multiply_home_dir = self._get_multiply_home_dir()
        aws_s2_path = '{}/aws_s2_l1c/'.format(multiply_home_dir)
        if not os.path.exists(aws_s2_path):
            os.mkdir(aws_s2_path)
        file_system_parameters = {'temp_dir': aws_s2_path, 'path': aws_s2_path, 'pattern': '/dt/yy/mm/dd/'}
        path_to_json_file = '{}/aws_s2_l1c/aws_s2_store.json'.format(multiply_home_dir)
        if not os.path.exists(path_to_json_file):
            with open(path_to_json_file, "w") as json_file:
                json_dict = {'data_sets': []}
                json.dump(json_dict, json_file, indent=2)
        meta_info_parameters = {'path_to_json_file': path_to_json_file}
        aws_s2_data_store = DataStore(AwsS2FileSystem(file_system_parameters),
                                      AwsS2MetaInfoProvider(meta_info_parameters), 'aws_s2')
        self._put_data_store(aws_s2_data_store)

    def _get_multiply_home_dir(self) -> str:
        home_dir = str(Path.home())
        multiply_home_dir = '{0}/{1}'.format(home_dir, MULTIPLY_DIR_NAME)
        if not os.path.exists(multiply_home_dir):
            os.mkdir(multiply_home_dir)
        return multiply_home_dir

    def read_data_stores(self, file: str) -> List[DataStore]:
        data_stores = []
        stream = open(file, 'r')
        data_store_lists = yaml.safe_load(stream)
        if data_store_lists is None:
            return data_stores
        for index, data_store_entry in enumerate(data_store_lists):
            if 'DataStore' not in data_store_entry.keys():
                raise UserWarning('Cannot read DataStore')
            if 'FileSystem' not in data_store_entry['DataStore'].keys():
                raise UserWarning('DataStore is missing FileSystem: Cannot read DataStore')
            if 'MetaInfoProvider' not in data_store_entry['DataStore'].keys():
                raise UserWarning('DataStore is missing MetaInfoProvider: Cannot read DataStore')
            file_system = self.create_file_system_from_dict(data_store_entry['DataStore']['FileSystem'])
            meta_info_provider = self.create_meta_info_provider_from_dict(data_store_entry['DataStore']['MetaInfoProvider'])
            if 'Id' in data_store_entry['DataStore'].keys():
                id = data_store_entry['DataStore']['Id']
            else:
                id = index
            data_store = DataStore(file_system, meta_info_provider, id)
            data_stores.append(data_store)
        self._data_stores = self._data_stores + data_stores
        return data_stores

    def _put_data_store(self, data_store: DataStore, file: Optional[str] = None) -> None:
        if file is None:
            file = self._get_default_data_stores_file()
        data_store_as_dict = data_store.get_as_dict()
        self._write_data_store_as_dict(data_store_as_dict, file)

    def _write_data_store_as_dict(self, data_store_as_dict: dict, file: str) -> None:
        with open(file, 'r') as infile:
            data_stores = yaml.safe_load(infile)
            if data_stores is None:
                data_stores = []
            data_stores.append(data_store_as_dict)
            with open(file, 'w') as outfile:
                yaml.safe_dump(data_stores, outfile, default_flow_style=False)

    # def _remove_data_store(self, data_store: DataStore):
    #

    def create_local_data_store(self, base_dir: Optional[str] = None, meta_info_file: Optional[str] = None,
                                base_pattern: Optional[str]='/dt/yy/mm/dd/', id: Optional[str] = None) -> DataStore:
        multiply_home_dir = self._get_multiply_home_dir()
        if base_dir is None:
            base_dir = '{0}/{1}'.format(multiply_home_dir, DATA_FOLDER_NAME)
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        if meta_info_file is None:
            meta_info_file = '{0}/meta_info.json'.format(base_dir)
            count = 1
            while os.path.exists(meta_info_file):
                meta_info_file = '{0}/meta_info_{1}.json'.format(base_dir, count)
                count += 1
            with open(meta_info_file, "w") as json_file:
                empty_dict = dict(data_sets=())
                json.dump(empty_dict, json_file, indent=2)
        local_file_system = LocalFileSystem(base_dir, base_pattern)
        json_meta_info_provider = JsonMetaInfoProvider(meta_info_file)
        if id is None:
            i = 0
            is_contained = True
            while is_contained:
                is_contained = False
                id = 'data_store_{}'.format(i)
                for data_store in self._data_stores:
                    if data_store.id == id:
                        is_contained = True
                        i += 1
                        break
        writable_data_store = WritableDataStore(local_file_system, json_meta_info_provider, id)
        writable_data_store.update()
        self._data_stores.append(writable_data_store)
        return writable_data_store

    def create_file_system_from_dict(self, file_system_as_dict: dict) -> FileSystem:
        parameters = file_system_as_dict['parameters']
        for file_system_accessor in FILE_SYSTEM_REGISTRY:
            if file_system_accessor.name() == file_system_as_dict['type']:
                return file_system_accessor.create_from_parameters(parameters)
        raise UserWarning('Could not find file system of type {0}'.format(file_system_as_dict['type']))

    def create_meta_info_provider_from_dict(self, meta_info_provider_as_dict: dict) -> MetaInfoProvider:
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
