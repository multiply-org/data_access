"""
Description
===========

This module contains the functionality to access data from a remote directory accessible via http.
"""
import os
import re
import requests

from typing import List, Sequence
import urllib.request as urllib2

from multiply_core.observations import get_file_pattern, is_valid_for
from multiply_core.util import FileRef, get_mime_type
from multiply_data_access.data_access import DataSetMetaInfo, FileSystemAccessor, MetaInfoProviderAccessor
from multiply_data_access.data_set_meta_info_extraction import DataSetMetaInfoProvision

__author__ = 'Tonio Fincke (Brockmann Consult GmbH),' \
             'José Luis Gómez-Dans (University College London)'

from multiply_data_access.locally_wrapped_data_access import LocallyWrappedFileSystem, LocallyWrappedMetaInfoProvider

_FILE_SYSTEM_NAME = 'HttpFileSystem'
_META_INFO_PROVIDER_NAME = 'HttpMetaInfoProvider'


class HttpMetaInfoProvider(LocallyWrappedMetaInfoProvider):

    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    def _init_wrapped_meta_info_provider(self, parameters: dict) -> None:
        if 'url' not in parameters.keys():
            raise ValueError('No url provided for Http MetaInfoProvider')
        if requests.get(parameters['url']).status_code != 200:
            raise ValueError('Invalid url provided for Http MetaInfoProvider')
        self._url = parameters['url']
        if 'data_types' not in parameters.keys():
            raise ValueError('HttpMetaInfoProvider must receive data types as parameter')
        self._data_types = parameters['data_types'].replace(' ', '').split(',')
        self._data_set_meta_info_provision = DataSetMetaInfoProvision()

    def provides_data_type(self, data_type: str) -> bool:
        for provided_data_type in self._data_types:
            if data_type == provided_data_type:
                return True
        return False

    def get_provided_data_types(self) -> List[str]:
        return self._data_types

    def _query_wrapped_meta_info_provider(self, query_string: str) -> List[DataSetMetaInfo]:
        data_set_meta_infos = []
        queried_data_types = self.get_data_types_from_query_string(query_string)
        may_continue = False
        for data_type in queried_data_types:
            if data_type in self._data_types:
                may_continue = True
                break
        if not may_continue:
            return data_set_meta_infos
        page = urllib2.urlopen(self._url).read().decode('utf-8')
        roi = self.get_roi_from_query_string(query_string)
        start_time = self.get_start_time_from_query_string(query_string)
        end_time = self.get_end_time_from_query_string(query_string)
        for data_type in queried_data_types:
            if data_type not in self._data_types:
                continue
            file_pattern = get_file_pattern(data_type)
            available_files = re.findall('>{}<'.format(file_pattern), page)
            for file in available_files:
                if is_valid_for(file[1:-1], data_type, roi, start_time, end_time):
                    data_set_meta_info = self._data_set_meta_info_provision.get_data_set_meta_info(data_type, file[1:-1])
                    data_set_meta_infos.append(data_set_meta_info)
        return data_set_meta_infos

    def _get_wrapped_parameters_as_dict(self) -> dict:
        parameters = {'url': self._url, 'data_types': ','.join(self._data_types)}
        return parameters


class HttpMetaInfoProviderAccessor(MetaInfoProviderAccessor):

    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> HttpMetaInfoProvider:
        return HttpMetaInfoProvider(parameters)


class HttpFileSystem(LocallyWrappedFileSystem):

    @classmethod
    def name(cls) -> str:
        return _FILE_SYSTEM_NAME

    def _init_wrapped_file_system(self, parameters: dict) -> None:
        if 'url' not in parameters.keys():
            raise ValueError('No url provided for HttpFileSystem')
        if requests.get(parameters['url']).status_code != 200:
            raise ValueError('Invalid url provided for HttpFileSystem')
        self._url = parameters['url']
        if 'temp_dir' not in parameters.keys():
            raise ValueError('No valid temporal directory provided Http File System')
        if not os.path.exists(parameters['temp_dir']):
            os.makedirs(parameters['temp_dir'])
        self._temp_dir = parameters['temp_dir']

    def _get_from_wrapped(self, data_set_meta_info: DataSetMetaInfo) -> Sequence[FileRef]:
        file_refs = []
        download_url = '{}/{}'.format(self._url, data_set_meta_info.identifier)
        request = requests.get(download_url, stream=True)
        if request.ok:
            temp_path = os.path.join(self._temp_dir, data_set_meta_info.identifier)
            with open(temp_path, 'wb') as fp:
                for chunk in request.iter_content(chunk_size=1024):
                    if chunk:
                        fp.write(chunk)
            file_refs.append(FileRef(temp_path, data_set_meta_info.start_time, data_set_meta_info.end_time,
                                     get_mime_type(data_set_meta_info.identifier)))
        return file_refs

    def _notify_copied_to_local(self, data_set_meta_info: DataSetMetaInfo) -> None:
        full_path = '{}/{}'.format(self._temp_dir, data_set_meta_info.identifier)
        if os.path.exists(full_path):
            os.remove(full_path)

    def _get_wrapped_parameters_as_dict(self) -> dict:
        parameters = {'url': self._url, 'temp_dir': self._temp_dir}
        return parameters


class HttpFileSystemAccessor(FileSystemAccessor):

    @classmethod
    def name(cls) -> str:
        return _FILE_SYSTEM_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> HttpFileSystem:
        return HttpFileSystem(parameters)
