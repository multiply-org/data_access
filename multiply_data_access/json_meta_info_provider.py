from .data_access import DataSetMetaInfo, DataUtils, MetaInfoProvider, MetaInfoProviderAccessor
from typing import List
from shapely.wkt import loads
import json

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

_NAME = 'JsonMetaInfoProvider'


class JsonMetaInfoProvider(MetaInfoProvider):
    """
    A MetaInfoProvider that retrieves its meta information from a JSON file.
    """

    def __init__(self, path_to_json_file: str):
        json_file = open(path_to_json_file)
        self.data_set_infos = json.load(json_file)

    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        roi = self.get_roi_from_query_string(query_string)
        query_start_time = self.get_start_time_from_query_string(query_string)
        query_end_time = self.get_end_time_from_query_string(query_string)
        data_types = self.get_data_types_from_query_string(query_string)
        data_set_meta_infos = []
        print('start examining data sets')
        print(self.data_set_infos['data_sets'])
        for data_set_info in self.data_set_infos['data_sets']:
            if data_set_info.get('coverage') is not None and roi is not None:
                data_set_coverage = loads(data_set_info.get('coverage'))
                if not roi.intersects(data_set_coverage):
                    print('roi does not intersect coverage')
                    continue
            if data_set_info.get('start_time') is not None:
                data_set_start_time = DataUtils.get_time_from_string(data_set_info.get('start_time'), False)
                if query_end_time < data_set_start_time:
                    print('query end time is before data set start time')
                    continue
            if data_set_info.get('end_time') is not None:
                data_set_end_time = DataUtils.get_time_from_string(data_set_info.get('end_time'), True)
                if data_set_end_time < query_start_time:
                    print('query start time is after data set end time')
                    continue
            if data_set_info.get('data_type') in data_types:
                data_set_meta_info = DataSetMetaInfo(coverage=data_set_info.get('coverage'),
                                                     start_time=data_set_info.get('start_time'),
                                                     end_time=data_set_info.get('end_time'),
                                                     data_type=data_set_info.get('data_type'),
                                                     identifier=data_set_info.get('name'))
                data_set_meta_infos.append(data_set_meta_info)
        return data_set_meta_infos


class JsonMetaInfoProviderAccessor(MetaInfoProviderAccessor):

    @classmethod
    def name(cls) -> str:
        """The name of the file system implementation."""
        return _NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> JsonMetaInfoProvider:
        if 'path_to_json_file' not in parameters.keys():
            raise ValueError('Required parameter path_to_json_file is missing')
        return JsonMetaInfoProvider(path_to_json_file=parameters['path_to_json_file'])