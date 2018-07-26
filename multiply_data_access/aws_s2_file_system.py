"""
Description
===========

This module contains an implementation of a file system that allows to access and download S2 L1C data from Amazon Web
Services (AWS).
"""
from multiply_core.util import FileRef, get_mime_type
from .data_access import DataSetMetaInfo, FileSystemAccessor, FileSystem
from sentinelhub import AwsTileRequest
from typing import Optional, Sequence
import os
import re

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

BASIC_AWS_S2_PATTERN = '[0-9]{1,2}/[A-Z]/[A-Z]{2}/20[0-9][0-9]/[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}'
BASIC_AWS_S2_MATCHER = re.compile(BASIC_AWS_S2_PATTERN)

_NAME = 'AwsS2FileSystem'


class AwsS2FileSystem(FileSystem):

    def __init__(self, temp_dir: str):
        if temp_dir is None or not os.path.exists(temp_dir):
            raise ValueError('No valid temporal directory provided for AWS S2 File System')
        self._temp_dir = temp_dir

    @classmethod
    def name(cls) -> str:
        return _NAME

    def get(self, data_set_meta_info: DataSetMetaInfo) -> Sequence[FileRef]:
        file_refs = []
        retrieved_file_ref = self._get_file_ref(data_set_meta_info)
        if retrieved_file_ref is not None:
            file_refs.append(retrieved_file_ref)
        return file_refs

    def _get_file_ref(self, data_set_meta_info: DataSetMetaInfo, bands=None, metafiles=None) -> Optional[FileRef]:
        """auxiliary method to delimit the number of downloaded files for testing"""
        if not self._is_valid_identifier(data_set_meta_info.identifier):
            # consider throwing an exception
            return None
        tile_name = self._get_tile_name(data_set_meta_info.identifier)
        aws_index = self._get_aws_index(data_set_meta_info.identifier)
        start_time = data_set_meta_info.start_time
        request = AwsTileRequest(tile=tile_name, time=start_time, aws_index=aws_index,
                                 bands=bands, metafiles=metafiles, data_folder=self._temp_dir)
        request.save_data()
        saved_dir = '{0}/{1},{2},{3}/'.format(self._temp_dir, tile_name, start_time, aws_index)
        return FileRef(saved_dir, start_time, data_set_meta_info.end_time, get_mime_type(saved_dir))

    def _is_valid_identifier(self, path: str) -> bool:
        return BASIC_AWS_S2_MATCHER.match(path) is not None

    def _get_tile_name(self, id: str) -> str:
        split_id = id.split('/')
        return '{0}{1}{2}'.format(split_id[0], split_id[1], split_id[2])

    def _get_aws_index(self, id: str) -> int:
        return int(id.split('/')[-1])

    def get_parameters_as_dict(self) -> dict:
        parameters = {'temp_dir': self._temp_dir}
        return parameters


class AwsS2FileSystemAccessor(FileSystemAccessor):

    @classmethod
    def name(cls) -> str:
        return _NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> AwsS2FileSystem:
        if 'temp_dir' not in parameters.keys():
            raise ValueError('No valid temporal directory provided for AWS S2 File System')
        return AwsS2FileSystem(temp_dir=parameters['temp_dir'])
