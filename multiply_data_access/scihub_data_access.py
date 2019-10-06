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
import shutil
from shapely.geometry import Polygon
from shapely.wkt import dumps
from typing import List, Sequence
import urllib.request as urllib2

from multiply_core.observations import DataTypeConstants
from multiply_core.util import FileRef, get_mime_type, get_time_from_string
from multiply_data_access.data_access import DataSetMetaInfo, FileSystemAccessor, MetaInfoProviderAccessor
from multiply_data_access.locally_wrapped_data_access import LocallyWrappedFileSystem, LocallyWrappedMetaInfoProvider

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

_META_INFO_PROVIDER_NAME = 'SciHubMetaInfoProvider'
_FILE_SYSTEM_NAME = 'SciHubFileSystem'

_BASE_URL = 'https://mundiwebservices.com/acdc/catalog/proxy/search/'
_COLLECTIONS_DESCRIPTIONS_ADDITION = 'collections/opensearch/description.xml'
_COLLECTION_DESCRIPTION_ADDITION = '{}/opensearch/description.xml'

_BASE_CATALOGUE_URL = "https://scihub.copernicus.eu/dhus/search?start={}&rows=50&q=({})"
_POLYGON_FORMAT = 'POLYGON(({1} {0}, {3} {2}, {5} {4}, {7} {6}, {9} {8}))'
_DATA_TYPE_PARAMETER_DICTS = {
    DataTypeConstants.S1_SLC: {'platformname': 'Sentinel-1', 'productType': 'SLC'}
}
_MUNDI_SERVER = 'obs.otc.t-systems.com'


class SciHubMetaInfoProvider(LocallyWrappedMetaInfoProvider):

    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    def _init_wrapped_meta_info_provider(self, parameters: dict) -> None:
        if 'username' not in parameters.keys():
            raise ValueError('No username provided for Lp Daac File System')
        self._username = parameters['username']
        if 'password' not in parameters.keys():
            raise ValueError('No password provided for Lp Daac File System')
        self._password = parameters['password']

    def _query_wrapped_meta_info_provider(self, query_string: str,
                                          local_data_set_meta_infos: List[DataSetMetaInfo]) -> List[DataSetMetaInfo]:
        roi = dumps(self.get_roi_from_query_string(query_string))
        data_types = self.get_data_types_from_query_string(query_string)
        start_time = datetime.strftime(self.get_start_time_from_query_string(query_string), "%Y-%m-%dT%H:%M:%SZ")
        end_time = datetime.strftime(self.get_end_time_from_query_string(query_string), "%Y-%m-%dT%H:%M:%SZ")
        data_set_meta_infos = []
        for data_type in data_types:
            if self.provides_data_type(data_type):
                run = 0
                continue_checking_for_data_sets = True
                while continue_checking_for_data_sets:
                    scihub_query = self._create_scihub_query(roi, data_type, start_time, end_time, run)
                    run += 1
                    response = requests.get(scihub_query, auth=(self._username, self._password))
                    response_xml = XML(response.content)
                    continue_checking_for_data_sets = False
                    for child in response_xml:
                        if child.tag == '{http://www.w3.org/2005/Atom}entry':
                            data_set_meta_info_id = ""
                            data_set_meta_info_start_time = ""
                            data_set_meta_info_end_time = ""
                            data_set_meta_info_coverage = ""
                            data_set_meta_info_reference = ""
                            for child2 in child:
                                if child2.tag == '{http://www.w3.org/2005/Atom}id':
                                    data_set_meta_info_reference = child2.text
                                elif child2.tag == '{http://www.w3.org/2005/Atom}title':
                                    data_set_meta_info_id = child2.text
                                elif child2.tag == '{http://www.w3.org/2005/Atom}date' and 'name' in child2.attrib \
                                        and child2.attrib['name'] == 'beginposition':
                                    data_set_meta_info_start_time = child2.text
                                elif child2.tag == '{http://www.w3.org/2005/Atom}date' and 'name' in child2.attrib \
                                        and child2.attrib['name'] == 'endposition':
                                    data_set_meta_info_end_time = child2.text
                                elif child2.tag == '{http://www.w3.org/2005/Atom}str' and 'name' in child2.attrib \
                                        and child2.attrib['name'] == 'footprint':
                                    data_set_meta_info_coverage = child2.text
                            data_set_meta_info = \
                                DataSetMetaInfo(data_set_meta_info_coverage, data_set_meta_info_start_time,
                                                data_set_meta_info_end_time, data_type, data_set_meta_info_id,
                                                data_set_meta_info_reference)
                            data_set_meta_infos.append(data_set_meta_info)
                            continue_checking_for_data_sets = True
        return data_set_meta_infos

    @staticmethod
    def _convert_mundi_coverage(mundi_coverage_string: str):
        coords = mundi_coverage_string.split(" ")
        coord_list = []
        for i in range(0, len(coords), 2):
            coord_list.append((float(coords[i + 1]), float(coords[i])))
        coverage = Polygon(coord_list)
        return dumps(coverage)

    @staticmethod
    def _create_scihub_query(roi: str, data_type: str, start_time: str, end_time: str, run: int) -> str:
        data_type_dict = _DATA_TYPE_PARAMETER_DICTS[data_type]
        query_part = "(beginPosition:[{} TO {}] AND endPosition:[{} TO {}]) " \
                     "AND (footprint:\"Intersects({})\") " \
                     "AND (platformname:{} AND producttype:{})"
        query_part = query_part.format(start_time, end_time, start_time, end_time, roi,
                                       data_type_dict['platformname'], data_type_dict['productType'])
        return _BASE_CATALOGUE_URL.format((50 * run), query_part)

    def _get_wrapped_parameters_as_dict(self) -> dict:
        return {'username': self._username, 'password': self._password}

    def provides_data_type(self, data_type: str) -> bool:
        return data_type == DataTypeConstants.S1_SLC

    def get_provided_data_types(self) -> List[str]:
        return [DataTypeConstants.S1_SLC]

    def encapsulates_data_type(self, data_type: str) -> bool:
        return False


class SciHubMetaInfoProviderAccessor(MetaInfoProviderAccessor):

    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> SciHubMetaInfoProvider:
        return SciHubMetaInfoProvider(parameters)


class SciHubFileSystem(LocallyWrappedFileSystem):

    def _init_wrapped_file_system(self, parameters: dict) -> None:
        if 'access_key_id' not in parameters.keys():
            self._access_key_id = ''
            logging.warning('No access key id set. Will not be able to download data from MUNDI DIAS')
        else:
            self._access_key_id = parameters['access_key_id']
        if 'secret_access_key' not in parameters.keys():
            logging.warning('No secret access key set. Will not be able to download data from MUNDI DIAS')
            self._secret_access_key = ''
        else:
            self._secret_access_key = parameters['secret_access_key']
        if 'temp_dir' not in parameters.keys():
            raise ValueError('No valid temporal directory provided for AWS S2 File System')
        if not os.path.exists(parameters['temp_dir']):
            os.makedirs(parameters['temp_dir'])
        self._temp_dir = parameters['temp_dir']

    @classmethod
    def name(cls) -> str:
        return _FILE_SYSTEM_NAME

    def _get_from_wrapped(self, data_set_meta_info: DataSetMetaInfo) -> Sequence[FileRef]:
        from com.obs.client.obs_client import ObsClient
        if data_set_meta_info.data_type not in _DATA_TYPE_PARAMETER_DICTS:
            logging.warning(f'Data Type {data_set_meta_info.data_type} not supported by MUNDI DIAS File System '
                            f'implementation.')
            return []
        buckets = self._get_bucket_names(data_set_meta_info)
        prefix = self._get_prefix(data_set_meta_info)
        obs_client = ObsClient(access_key_id=self._access_key_id,
                               secret_access_key=self._secret_access_key,
                               server=_MUNDI_SERVER)
        keys = []
        right_bucket = None
        for bucket in buckets:
            right_bucket = bucket
            objects = obs_client.listObjects(bucketName=bucket, prefix=prefix)
            if objects.status < 300:
                for content in objects.body.contents:
                    keys.append(content.key)
                if len(keys) > 0:
                    break
            else:
                logging.error(objects.errorCode)
        if len(keys) == 0:
            return []
        for key in keys:
            relative_path_to_file = key.split(data_set_meta_info.identifier)[1]
            resp = obs_client.getObject(right_bucket, key, downloadPath=
            f'{self._temp_dir}/{data_set_meta_info.identifier}/{relative_path_to_file}')
            if resp.status >= 300:
                logging.error(resp.errorCode)
                return []
        obs_client.close()
        file_ref = FileRef(f'{self._temp_dir}/{data_set_meta_info.identifier}',
                           data_set_meta_info.start_time, data_set_meta_info.end_time,
                           get_mime_type(data_set_meta_info.identifier))
        return [file_ref]

    @staticmethod
    def _get_bucket_names(data_set_meta_info: DataSetMetaInfo) -> List[str]:
        start_time = get_time_from_string(data_set_meta_info.start_time)
        base_bucket_names = _DATA_TYPE_PARAMETER_DICTS[data_set_meta_info.data_type]['baseBuckets']
        bucket_names = []
        for base_bucket_name in base_bucket_names:
            quarter = int(int(start_time.month - 1) / 3) + 1
            bucket_name = base_bucket_name.replace('{YYYY}', str(start_time.year))
            bucket_name = bucket_name.replace('{q}', str(quarter))
            bucket_names.append(bucket_name)
        return bucket_names

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

    def _get_wrapped_parameters_as_dict(self) -> dict:
        return {'access_key_id': self._access_key_id, 'secret_access_key': self._secret_access_key,
                'temp_dir': self._temp_dir}

    def _notify_copied_to_local(self, data_set_meta_info: DataSetMetaInfo) -> None:
        full_path = '{}/{}'.format(self._temp_dir, data_set_meta_info.identifier)
        if os.path.exists(full_path):
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)


class SciHubFileSystemAccessor(FileSystemAccessor):

    @classmethod
    def name(cls) -> str:
        return _FILE_SYSTEM_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> SciHubFileSystem:
        return SciHubFileSystem(parameters)
