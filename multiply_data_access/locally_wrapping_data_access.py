"""
Description
===========

This module contains functionality for wrapping file systems or meta info providers with locally available file systems
or meta info providers. This is done with the objective to facilitate the handling of data that needs to be downloaded
(or is in another way hard to access) by putting it in a local data store.
by
"""

# from abc import ABCMeta, abstractmethod
# from typing import List, Sequence, Optional
# from datetime import datetime, timedelta
# from multiply_core.util import FileRef
# from shapely.wkt import loads
# from shapely.geometry import Polygon
# import os

from abc import abstractmethod
from multiply_core.util import FileRef
from multiply_data_access.data_access import DataSetMetaInfo, FileSystem, MetaInfoProvider
from multiply_data_access.local_file_system import LocalFileSystem
from multiply_data_access.json_meta_info_provider import JsonMetaInfoProvider
from typing import List, Sequence

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


class LocallyWrappingFileSystem(FileSystem):

    def __init__(self, parameters: dict):
        if not 'path' in parameters.keys():
            raise ValueError('Missing parameter \'path\'')
        if not 'pattern' in parameters.keys():
            raise ValueError('Missing parameter \'pattern\'')
        self._local_file_system = LocalFileSystem(parameters['path'], parameters['pattern'])
        self._init_wrapped_file_system(parameters)

    @abstractmethod
    def _init_wrapped_file_system(self, parameters: dict) -> None:
        """Initializes the file system wrapped by the LocallyWrappingFileSystem. To be called instead of __init__"""

    def get(self, data_set_meta_info: DataSetMetaInfo) -> Sequence[FileRef]:
        file_refs = self._local_file_system.get(data_set_meta_info)
        if len(file_refs) > 0:
            return file_refs
        # if on wrapped file system: access, add to local file system, retrieve it then

    def _get_parameters_as_dict(self) -> dict:
        local_parameters = self._local_file_system._get_parameters_as_dict()
        wrapped_parameters = self._get_wrapped_parameters_as_dict()
        local_parameters.update(wrapped_parameters)
        return local_parameters

    @abstractmethod
    def _get_wrapped_parameters_as_dict(self) -> dict:
        """
        :return: The parameters of this wrapped file system as dict
        """


class LocallyWrappingMetaInfoProvider(MetaInfoProvider):

    def __init__(self, parameters: dict):
        if not 'path_to_json_file' in parameters.keys():
            raise ValueError('Missing path to json file')
        self._json_meta_info_provider = JsonMetaInfoProvider(parameters['path_to_json_file'])
        self._init_wrapped_meta_info_provider(parameters)

    @abstractmethod
    def _init_wrapped_meta_info_provider(self, parameters: dict) -> None:
        """Initializes the meta info provider wrapped by the LocallyWrappingMetaInfoProvider.
        To be called instead of __init__"""

    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        local_data_meta_set_infos = self._json_meta_info_provider.query(query_string)
        wrapped_data_set_meta_infos = self._query_wrapped_file_system(query_string)
        for wrapped_data_set_meta_info in wrapped_data_set_meta_infos:
            for local_data_meta_set_info in local_data_meta_set_infos:
                if wrapped_data_set_meta_info.equals(local_data_meta_set_info):
                    break
            local_data_meta_set_infos.append(wrapped_data_set_meta_info)
        return local_data_meta_set_infos


    @abstractmethod
    def _query_wrapped_file_system(self, query_string: str) -> List[DataSetMetaInfo]:
        """Queries a wrapped file system."""

    # def provides_data_type(self, data_type: str) -> bool:
        # queries ONLY the wrapped meta info provider
        # pass

    def _get_parameters_as_dict(self) -> dict:
        local_parameters = self._json_meta_info_provider._get_parameters_as_dict()
        wrapped_parameters = self._get_wrapped_parameters_as_dict()
        local_parameters.update(wrapped_parameters)
        return local_parameters

    @abstractmethod
    def _get_wrapped_parameters_as_dict(self) -> dict:
        """
        :return: The parameters of this wrapped meta info provider as dict
        """
