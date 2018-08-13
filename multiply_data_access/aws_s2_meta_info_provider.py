from multiply_data_access.data_access import DataSetMetaInfo, MetaInfoProviderAccessor
from multiply_data_access.locally_wrapping_data_access import LocallyWrappingMetaInfoProvider
from datetime import datetime, timedelta
from multiply_core.observations import DataTypeConstants
from typing import List, Optional
from shapely.wkt import loads
from shapely.geometry import Polygon
import math
import pkg_resources
import requests

__author__ = 'Tonio Fincke (Brockmann Consult GmbH),' \
             'José Luis Gómez-Dans (University College London)'

_NAME = 'AwsS2MetaInfoProvider'
_AWS_BASE_TILE_INFO_URL = 'https://roda.sentinel-hub.com/sentinel-s2-l1c/tiles/{}/tileInfo.json'
_ID_PATTERN = '{0}/{1}/{2}/{3}/{4}/{5}/{6}'

TILE_LAT_IDENTIFIERS = \
    ['C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X']
PATH_TO_TILE_LOOKUP_TABLE = pkg_resources.resource_filename(__name__, 'tile_lookup_table.yaml')


def _get_tile_stripes(min_lon: float, max_lon: float) -> List[int]:
    start_index = int(math.ceil((min_lon + 180.) / 6.))
    end_index = int(math.ceil((max_lon + 180.) / 6.)) + 1
    if start_index > end_index:  # i.e., if we pass the anti-meridian:
        return list(range(start_index, 61)) + list(range(1, end_index))
    return list(range(start_index, end_index))


def _get_center_tile_identifiers(min_lat: float, max_lat: float) -> List[str]:
    start_index = int(math.floor((min(79., max(-80., min_lat)) + 80) / 8.))
    end_index = int(math.ceil((min(79., max(-80., max_lat)) + 80) / 8.))
    if start_index == end_index:
        end_index += 1
    return TILE_LAT_IDENTIFIERS[start_index:end_index]


class TileDescription(object):

    def __init__(self, tile_id: str, coverage: str):
        self._tile_id = tile_id
        self._coverage = coverage

    @property
    def tile_id(self) -> str:
        return self._tile_id

    @property
    def coverage(self):
        return self._coverage


class AwsS2MetaInfoProvider(LocallyWrappingMetaInfoProvider):

    def _init_wrapped_meta_info_provider(self, parameters: dict):
        self._lut = {}

    @classmethod
    def name(cls) -> str:
        return _NAME

    def _query_wrapped_meta_info_provider(self, query_string: str) -> List[DataSetMetaInfo]:
        data_types = self.get_data_types_from_query_string(query_string)
        if DataTypeConstants.AWS_S2_L1C not in data_types:
            return []
        roi = self.get_roi_from_query_string(query_string)
        tile_descriptions = self.get_affected_tile_descriptions(roi)
        start_time = self.get_start_time_from_query_string(query_string)
        end_time = self.get_end_time_from_query_string(query_string)
        data_set_meta_infos = []
        for tile_description in tile_descriptions:
            data_set_meta_infos += self._get_data_set_meta_infos_for_tile_description(tile_description, start_time,
                                                                                      end_time)
        return data_set_meta_infos

    def _get_data_set_meta_infos_for_tile_description(self, tile_description: TileDescription, start_time: datetime,
                                                      end_time: datetime) -> List[DataSetMetaInfo]:
        data_set_meta_infos = []
        current_time = start_time
        while current_time < end_time:
            current_time_as_string = datetime.strftime(current_time, '%Y-%m-%d')
            aws_index = 0
            while aws_index >= 0:
                id = _ID_PATTERN.format(tile_description.tile_id[0:2], tile_description.tile_id[2:3],
                                        tile_description.tile_id[3:5], current_time.year, current_time.month,
                                        current_time.day, aws_index)
                tile_info_url = _AWS_BASE_TILE_INFO_URL.format(id)
                request = requests.get(tile_info_url)
                if request.status_code == 200:
                    data_set_meta_infos.append(DataSetMetaInfo(tile_description.coverage, current_time_as_string,
                                                               current_time_as_string, DataTypeConstants.AWS_S2_L1C,
                                                               id))
                    aws_index += 1
                else:
                    aws_index = -1
                    current_time += timedelta(days=1)
        return data_set_meta_infos

    def get_affected_tile_descriptions(self, roi: Polygon) -> List[TileDescription]:
        min_lon, min_lat, max_lon, max_lat = roi.bounds

        tile_stripes = _get_tile_stripes(min_lon, max_lon)
        center_tile_identifiers = _get_center_tile_identifiers(min_lat, max_lat)
        tile_descriptions = []
        for tile_stripe in tile_stripes:
            for center_tile_identifier in center_tile_identifiers:
                sub_lut = self._get_sub_lut(tile_stripe, center_tile_identifier)
                for tile_id in sub_lut:
                    if roi.intersects(loads(sub_lut[tile_id])):
                        tile_descriptions.append(TileDescription(tile_id, sub_lut[tile_id]))
        return tile_descriptions

    def _get_sub_lut(self, tile_stripe: int, center_tile_identifier: str):
        if tile_stripe not in self._lut.keys() or center_tile_identifier not in self._lut[tile_stripe].keys():
            if tile_stripe not in self._lut.keys():
                self._lut[tile_stripe] = {}
            self._lut[tile_stripe][center_tile_identifier] = self._read_sub_lut(str(tile_stripe),
                                                                                center_tile_identifier)
        return self._lut[tile_stripe][center_tile_identifier]

    def _read_sub_lut(self, tile_stripe: str, center_tile_identifier: str) -> dict:
        with open(PATH_TO_TILE_LOOKUP_TABLE, 'r') as stream:
            sub_lut = {}
            part_of_sub_lut = 0
            for line in stream:
                if line.startswith(tile_stripe):
                    part_of_sub_lut = 1
                elif part_of_sub_lut > 0 and line.strip().startswith(center_tile_identifier):
                    part_of_sub_lut = 2
                elif part_of_sub_lut == 2:
                    if not line.startswith('    '):
                        break
                    split_line = line.split(':')
                    sub_lut[split_line[0].strip()] = split_line[1].strip()
            return sub_lut

    def _get_tile_coverage_as_wkt(self, tile_id: str) -> Optional[str]:
        start = int(tile_id[0:2])
        sub_lut = self._read_sub_lut(tile_id)
        if tile_id in sub_lut[start].keys():
            return sub_lut[start][tile_id]

    def _get_tile_coverage(self, tile_id: str) -> Optional[Polygon]:
        coverage_as_wkt = self._get_tile_coverage_as_wkt(tile_id)
        if coverage_as_wkt is not None:
            return loads(coverage_as_wkt)

    def provides_data_type(self, data_type: str) -> bool:
        return data_type == DataTypeConstants.AWS_S2_L1C

    def get_provided_data_types(self) -> List[str]:
        return [DataTypeConstants.AWS_S2_L1C]

    def _get_wrapped_parameters_as_dict(self) -> dict:
        return {}


class AwsS2MetaInfoProviderAccessor(MetaInfoProviderAccessor):

    @classmethod
    def name(cls) -> str:
        return _NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> AwsS2MetaInfoProvider:
        return AwsS2MetaInfoProvider(parameters)
