from multiply_data_access.data_access_component import DataAccessComponent
from multiply_data_access.json_meta_info_provider import JsonMetaInfoProvider
from multiply_data_access.local_file_system import LocalFileSystem
from multiply_data_access.data_store import DataStore

import os
import shutil

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

PATH_TO_YAML_FILE = './test/test_data/test_data_stores.yml'


def test_data_access_read_data_stores():
    data_access_component = DataAccessComponent()
    data_stores = data_access_component._read_data_stores(PATH_TO_YAML_FILE)
    assert 2 == len(data_stores)

    assert 'Default' == data_stores[0].id
    assert 'Fallback' == data_stores[1].id


def test_put_data_store():
    path_to_yaml_file_2 = './test/test_data/test_data_stores_2.yml'
    shutil.copyfile(PATH_TO_YAML_FILE, path_to_yaml_file_2)
    try:
        data_access_component = DataAccessComponent()
        local_file_system = LocalFileSystem('./test/test_data/', '/yy/dt/dd/')
        json_meta_info_provider = JsonMetaInfoProvider('./test/test_data/test_meta_info.json', 'TYPE_A,TYPE_B,TYPE_C')
        data_store = DataStore(local_file_system, json_meta_info_provider, 'a_test')
        data_access_component._put_data_store(data_store, path_to_yaml_file_2)

        data_stores = data_access_component._read_data_stores(path_to_yaml_file_2)
        assert 3 == len(data_stores)
        assert 'Default' == data_stores[0].id
        assert 'Fallback' == data_stores[1].id
        assert 'a_test' == data_stores[2].id
    finally:
        os.remove(path_to_yaml_file_2)


def test_write_data_store_as_dict():
    path_to_yaml_file_2 = './test/test_data/test_data_stores_3.yml'
    shutil.copyfile(PATH_TO_YAML_FILE, path_to_yaml_file_2)
    try:
        data_access_component = DataAccessComponent()
        file_system_parameters = {'path': './test/test_data/', 'pattern': '/yy/dt/dd/'}
        file_system_as_dict = {'type': 'LocalFileSystem', 'parameters': file_system_parameters}
        meta_info_provider_parameters = {'path_to_json_file': './test/test_data/test_meta_info.json'}
        meta_info_provider_as_dict = {'type': 'JsonMetaInfoProvider', 'parameters': meta_info_provider_parameters}
        data_store_as_dict = {'FileSystem': file_system_as_dict, 'MetaInfoProvider': meta_info_provider_as_dict,
                              'Id': 'for_testing'}
        data_store = {'DataStore': data_store_as_dict}
        data_access_component._write_data_store_as_dict(data_store, path_to_yaml_file_2)

        data_stores = data_access_component._read_data_stores(path_to_yaml_file_2)
        assert 3 == len(data_stores)

        assert 'Default' == data_stores[0].id
        assert 'Fallback' == data_stores[1].id
        assert 'for_testing' == data_stores[2].id
    finally:
        os.remove(path_to_yaml_file_2)


def test_write_data_store_as_dict_to_empty_file():
    path_to_empty_yaml_file = './test/test_data/test_data_stores_4.yml'
    open(path_to_empty_yaml_file, 'w')
    try:
        data_access_component = DataAccessComponent()
        file_system_parameters = {'path': './test/test_data/', 'pattern': '/yy/dt/dd/'}
        file_system_as_dict = {'type': 'LocalFileSystem', 'parameters': file_system_parameters}
        meta_info_provider_parameters = {'path_to_json_file': './test/test_data/test_meta_info.json'}
        meta_info_provider_as_dict = {'type': 'JsonMetaInfoProvider', 'parameters': meta_info_provider_parameters}
        data_store_as_dict = {'FileSystem': file_system_as_dict, 'MetaInfoProvider': meta_info_provider_as_dict,
                              'Id': 'for_testing'}
        data_store = {'DataStore': data_store_as_dict}
        data_access_component._write_data_store_as_dict(data_store, path_to_empty_yaml_file)

        data_stores = data_access_component._read_data_stores(path_to_empty_yaml_file)
        assert 1 == len(data_stores)

        assert 'for_testing' == data_stores[0].id
    finally:
        os.remove(path_to_empty_yaml_file)


def test_create_local_data_store():
    data_access_component = DataAccessComponent()
    data_access_component.create_local_data_store(base_dir='./test/test_data/',
                                                  meta_info_file='./test/test_data/meta_store.json',
                                                  base_pattern='mm/dt/', id='cgfsvt',
                                                  supported_data_types='TYPE_A,TYPE_B')
