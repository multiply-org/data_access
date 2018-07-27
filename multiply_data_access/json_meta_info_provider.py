from .data_access import DataSetMetaInfo, DataUtils, MetaInfoProviderAccessor
from .updateable_data_access import UpdateableMetaInfoProvider
from typing import List, Sequence
from shapely.wkt import loads
import json

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

_NAME = 'JsonMetaInfoProvider'


class JsonMetaInfoProvider(UpdateableMetaInfoProvider):
    """
    A MetaInfoProvider that retrieves its meta information from a JSON file.
    """

    def __init__(self, path_to_json_file: str):
        self.path_to_json_file = path_to_json_file
        with open(path_to_json_file, "r") as json_file:
            self.data_set_infos = json.load(json_file)
            self._update_provided_data_sets()

    @classmethod
    def name(cls) -> str:
        """The name of the file system implementation."""
        return _NAME

    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        roi = self.get_roi_from_query_string(query_string)
        query_start_time = self.get_start_time_from_query_string(query_string)
        query_end_time = self.get_end_time_from_query_string(query_string)
        data_types = self.get_data_types_from_query_string(query_string)
        data_set_meta_infos = []
        for data_set_info in self.data_set_infos['data_sets']:
            if data_set_info.get('coverage') is not None and roi is not None:
                data_set_coverage = loads(data_set_info.get('coverage'))
                if not roi.intersects(data_set_coverage):
                    continue
            if data_set_info.get('start_time') is not None:
                data_set_start_time = DataUtils.get_time_from_string(data_set_info.get('start_time'), False)
                if query_end_time < data_set_start_time:
                    continue
            if data_set_info.get('end_time') is not None:
                data_set_end_time = DataUtils.get_time_from_string(data_set_info.get('end_time'), True)
                if data_set_end_time < query_start_time:
                    continue
            if data_set_info.get('data_type') in data_types:
                data_set_meta_info = DataSetMetaInfo(coverage=data_set_info.get('coverage'),
                                                     start_time=data_set_info.get('start_time'),
                                                     end_time=data_set_info.get('end_time'),
                                                     data_type=data_set_info.get('data_type'),
                                                     identifier=data_set_info.get('name'))
                data_set_meta_infos.append(data_set_meta_info)
        return data_set_meta_infos

    def provides_data_type(self, data_type: str):
        return data_type in self.provided_data_types

    def update(self, data_set_meta_info: DataSetMetaInfo):
        if self._contains(data_set_meta_info):
            return
        data_set_info = {}
        if data_set_meta_info.coverage is not None and loads(data_set_meta_info.coverage) is not None:
            data_set_info['coverage'] = data_set_meta_info.coverage
        data_set_start_time = None
        if data_set_meta_info.start_time is not None:
            data_set_start_time = DataUtils.get_time_from_string(data_set_meta_info.start_time, False)
        data_set_end_time = None
        if data_set_meta_info.end_time is not None:
            data_set_end_time = DataUtils.get_time_from_string(data_set_meta_info.start_time, True)
        if data_set_start_time is not None and data_set_end_time is not None and data_set_start_time > data_set_end_time:
            raise ValueError('start time must not be later than end time')
        if data_set_start_time is not None:
            data_set_info['start_time'] = data_set_meta_info.start_time
        if data_set_end_time is not None:
            data_set_info['end_time'] = data_set_meta_info.end_time
        if data_set_meta_info.data_type is not None:
            data_set_info['data_type'] = data_set_meta_info.data_type
        data_set_info['name'] = data_set_meta_info.identifier
        self.data_set_infos['data_sets'].append(data_set_info)
        self._update_json_file()
        self._update_provided_data_sets()

    def _contains(self, data_set_meta_info: DataSetMetaInfo):
        #todo consider making this an interface function
        for data_set_info in self.data_set_infos['data_sets']:
            if data_set_info.get('coverage') != data_set_meta_info.coverage:
                continue
            if data_set_info.get('start_time') != data_set_meta_info.start_time:
                continue
            if data_set_info.get('end_time') != data_set_meta_info.end_time:
                continue
            if data_set_info.get('data_type') != data_set_meta_info.data_type:
                continue
            if data_set_info.get('name') != data_set_meta_info.identifier:
                continue
            return True
        return False

    def remove(self, data_set_meta_info: DataSetMetaInfo):
        for data_set_info in self.data_set_infos['data_sets']:
            if data_set_info.get('coverage') != data_set_meta_info.coverage:
                continue
            if data_set_info.get('start_time') != data_set_meta_info.start_time:
                continue
            if data_set_info.get('end_time') != data_set_meta_info.end_time:
                continue
            if data_set_info.get('data_type') != data_set_meta_info.data_type:
                continue
            if data_set_info.get('name') != data_set_meta_info.identifier:
                continue
            self.data_set_infos['data_sets'].remove(data_set_info)
        self._update_json_file()
        self._update_provided_data_sets()

    def _update_json_file(self):
        with open(self.path_to_json_file, "w") as json_file:
            json.dump(self.data_set_infos, json_file, indent=2)

    def _update_provided_data_sets(self):
        self.provided_data_types = []
        for data_set_info in self.data_set_infos['data_sets']:
            if data_set_info.get('data_type') not in self.provided_data_types:
                self.provided_data_types.append(data_set_info.get('data_type'))

    def get_all_data(self) -> Sequence[DataSetMetaInfo]:
        data_set_meta_infos = []
        for data_set_info in self.data_set_infos['data_sets']:
            data_set_meta_info = DataSetMetaInfo(coverage=data_set_info.get('coverage'),
                                                 start_time=data_set_info.get('start_time'),
                                                 end_time=data_set_info.get('end_time'),
                                                 data_type=data_set_info.get('data_type'),
                                                 identifier=data_set_info.get('name'))
            data_set_meta_infos.append(data_set_meta_info)
        return data_set_meta_infos

    def _get_parameters_as_dict(self):
        return {'path_to_json_file': self.path_to_json_file}


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