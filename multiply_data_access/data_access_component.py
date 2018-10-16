from multiply_core.observations import get_valid_type
from multiply_data_access import DataSetMetaInfo, DataStore, create_file_system_from_dict, \
    create_meta_info_provider_from_dict
from .aws_s2_file_system import AwsS2FileSystem
from .aws_s2_meta_info_provider import AwsS2MetaInfoProvider
from .json_meta_info_provider import JsonMetaInfoProvider
from .local_file_system import LocalFileSystem
from pathlib import Path
from typing import List, Optional
import logging
import os
import json
import pkg_resources
import yaml

MULTIPLY_DIR_NAME = '.multiply'
DATA_STORES_FILE_NAME = 'data_stores.yml'
DATA_FOLDER_NAME = 'data'
PATH_TO_DEFAULT_DATA_STORES_FILE = pkg_resources.resource_filename(__name__, 'default_data_stores.yaml')

logging.getLogger().setLevel(logging.INFO)


class DataAccessComponent(object):
    """
    The controlling component. The data access component is responsible for communicating with the various data stores
    and decides which data is used from which data store.
    """

    def __init__(self):
        self._data_stores = []
        self._read_registered_data_stores()
        for data_store in self._data_stores:
            data_store.update()

    def show_stores(self):
        """
        Prints out a list of all registered data stores.
        """
        for data_store in self._data_stores:
            print(data_store)

    def query(self, roi: str, start_time: str, end_time: str, data_types: str) -> List[DataSetMetaInfo]:
        """
        Distributes the query on all registered data stores and returns meta information on all data sets that meet
        the conditions of the query.
        :param roi: The region of interest, given in the form of a wkt-string.
        :param start_time: The start time of the query, given as a string in UTC time format
        :param end_time: The end time of the query, given as a string in UTC time format
        :param data_types: A list of data types to be queried for.
        :return: A list of DataSetMetaInfos that meet the conditions of the query.
        """
        query_string = DataAccessComponent._build_query_string(roi, start_time, end_time, data_types)
        meta_data_infos = []
        for data_store in self._data_stores:
            query_results = data_store.query(query_string)
            meta_data_infos.extend(query_results)
        return meta_data_infos

    def put(self, path: str, data_store_id: Optional[str]=None) -> None:
        """
        Puts data into the data access component. If the id to a data store is provided, the data access component
        will attempt to put the data into the store. If data cannot be added to that particular store, it will not be
        attempted to put it into another one. If no store id is provided, the data access component will on its own
        try to determine an apt data store. A data store is considered apt if it already holds data of the same type.
        :param path: A path to the data that shall be added to the Data Access Component.
        :param data_store_id: The id of a data store. Can be None.
        """
        data_type = get_valid_type(path)
        if data_type is '':
            logging.info('Could not determine data type of data at {}. Will not add it to Data Access Component.'
                         .format(path))
            return
        for data_store in self._data_stores:
            if data_store_id is not None and data_store.id == data_store_id:
                if not data_store.provides_data_type(data_type):
                    logging.info(
                        'Data Store {} is not apt for data of type {}. Will not add it to Data Access Component.'
                            .format(data_store_id, data_type))
                    return
                elif not data_store.can_put():
                    logging.info('Cannot put data into data store {}. Will not add it to Data Access Component.'.
                                 format(data_store.id))
                data_store.put(path)
                return
            elif data_store_id is None:
                if data_store.provides_data_type(data_type) and data_store.can_put():
                    data_store.put(path)
                    logging.info('Added data to data store {}.'.format(data_store.id))
                    return
        # TODO consider to create local data store for these cases
        logging.info('Could not determine apt data store for data at {}. Did not add to Data Access Component.'.
                     format(path))

    def get_provided_data_types(self) -> List[str]:
        """
        :return: A list of all data types that are provided by the Data Access Component.
        """
        provided_types = []
        for data_store in self._data_stores:
            provided_data_types = data_store.get_provided_data_types()
            for provided_data_type in provided_data_types:
                if provided_data_type not in provided_types:
                    provided_types.append(provided_data_type)
        return provided_types

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

    def get_data_urls_from_data_set_meta_infos(self, data_set_meta_infos: List[DataSetMetaInfo]) -> List[str]:
        """
        Builds a query from the given parameters and asks all data stores whether they contain data that match the
        query. If datasets are found, url's to their positions are returned.
        :return: a list of url's to locally stored files that match the conditions given by the query in the parameter.
        """
        urls = []
        for data_store in self._data_stores:
            for data_set_meta_info in data_set_meta_infos:
                if data_store.provides_data_type(data_set_meta_info.data_type):
                    file_refs = data_store.get(data_set_meta_info)
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
        self._read_data_stores(data_stores_file)

    def _get_default_data_stores_file(self) -> str:
        multiply_home_dir = self._get_multiply_home_dir()
        data_stores_file = '{0}/{1}'.format(multiply_home_dir, DATA_STORES_FILE_NAME)
        if not os.path.exists(data_stores_file):
            open(data_stores_file, 'w+')
            self._add_default_stores()
        return data_stores_file

    def _add_default_stores(self):
        """Will add the default stores to the data stores file when it is created."""
        multiply_home_dir = self._get_multiply_home_dir()
        with open(PATH_TO_DEFAULT_DATA_STORES_FILE, 'r') as stream:
            default_data_store_lists = yaml.safe_load(stream)
            if default_data_store_lists is None:
                return
            for index, data_store_entry in enumerate(default_data_store_lists):
                if 'DataStore' not in data_store_entry.keys() or \
                        'FileSystem' not in data_store_entry['DataStore'].keys() or \
                        'MetaInfoProvider' not in data_store_entry['DataStore'].keys():
                    continue
                for key, value in data_store_entry['DataStore']['FileSystem']['parameters'].items():
                    if value is not None and 'user_dir' in value:
                        file = value.replace('user_dir', multiply_home_dir)
                        if not os.path.exists(file) and file.endswith('/'):
                            os.makedirs(file)
                        data_store_entry['DataStore']['FileSystem']['parameters'][key] = file
                file_system = create_file_system_from_dict(data_store_entry['DataStore']['FileSystem'])
                for key, value in data_store_entry['DataStore']['MetaInfoProvider']['parameters'].items():
                    data_store_entry['DataStore']['MetaInfoProvider']['parameters'][key] = \
                        value.replace('user_dir', multiply_home_dir)
                meta_info_provider = create_meta_info_provider_from_dict(
                    data_store_entry['DataStore']['MetaInfoProvider'])
                if 'Id' in data_store_entry['DataStore'].keys():
                    id = data_store_entry['DataStore']['Id']
                else:
                    id = index
                data_store = DataStore(file_system, meta_info_provider, id)
                self._put_data_store(data_store)

    def _get_multiply_home_dir(self) -> str:
        home_dir = str(Path.home())
        multiply_home_dir = '{0}/{1}'.format(home_dir, MULTIPLY_DIR_NAME)
        if not os.path.exists(multiply_home_dir):
            os.mkdir(multiply_home_dir)
        return multiply_home_dir

    def _read_data_stores(self, file: str) -> List[DataStore]:
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
            file_system = create_file_system_from_dict(data_store_entry['DataStore']['FileSystem'])
            meta_info_provider = create_meta_info_provider_from_dict(data_store_entry['DataStore']['MetaInfoProvider'])
            if 'Id' in data_store_entry['DataStore'].keys():
                id = data_store_entry['DataStore']['Id']
            else:
                id = index
            data_store = DataStore(file_system, meta_info_provider, id)
            data_stores.append(data_store)
            logging.info('Read data store {}'.format(data_store.id))
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
                                base_pattern: Optional[str]='/dt/yy/mm/dd/', id: Optional[str] = None):
        """
        Adds a a new local data store and saves it permanently. It will consist of a LocalFileSystem and a
        JsonMetaInfoProvider.
        :param base_dir: The base directory to which the data shall be written.
        :param meta_info_file: A JSON file that already contains meta information about the data that is present in the
        folder. If not provided, an empty file will be created and filled with the data that match the base directory
        and the base pattern.
        :param base_pattern: A pattern that allows to create an order in the base directory. Available options are 'dt'
        for the data type, 'yy' for the year, 'mm' for the month, and 'dd' for the day, arrangeable in any oder. If no
        pattern is given, all data will simply be written into the base directory.
        :param id: An identifier for the Data Store. If there already exists a Data Store with the name, an additional
        number will be added to the name.
        :return: The newly created Data Store.
        """
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
        data_store = DataStore(local_file_system, json_meta_info_provider, id)
        data_store.update()
        self._data_stores.append(data_store)
