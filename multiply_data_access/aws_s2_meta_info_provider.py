from .data_access import DataSetMetaInfo, DataUtils, MetaInfoProvider, MetaInfoProviderAccessor
from multiply_core.observations import DataTypeConstants
from typing import List, Optional
from shapely.wkt import loads
from shapely.geometry import Polygon
import json
import math
import numpy as np
import requests
import yaml

__author__ = 'Tonio Fincke (Brockmann Consult GmbH),' \
             'José Luis Gómez-Dans (University College London)'

_NAME = 'AwsS2MetaInfoProvider'
LAND_CONVERTER_BASE_URL = "http://legallandconverter.com/cgi-bin/shopmgrs3.cgi"
TILE_LAT_IDENTIFIERS = \
    ['C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X']
PATH_TO_TILE_LOOKUP_TABLE = './aux_data/tile_lookup_table.yaml'


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


#
# def _get_all_tiles(min_lon: float, min_lat_float, max_lon:float, max_lat: float) -> :


class AwsS2MetaInfoProvider(MetaInfoProvider):

    def __init__(self):
        self._lut = {}

    @classmethod
    def name(cls) -> str:
        return _NAME

    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        roi = self.get_roi_from_query_string(query_string)

        start_time = self.get_start_time_from_query_string(query_string)
        end_time = self.get_end_time_from_query_string(query_string)
        data_types = self.get_data_types_from_query_string(query_string)

        return []

    def get_affected_tile_ids(self, roi: Polygon) -> List[TileDescription]:
        min_lon, min_lat, max_lon, max_lat = roi.bounds
        tile_stripes = _get_tile_stripes(min_lon, max_lon)
        center_tile_identifiers = _get_center_tile_identifiers(min_lat, max_lat)
        for tile_stripe in tile_stripes:
            for center_tile_identifier in center_tile_identifiers:
                sub_lut = self._read_sub_lut(str(tile_stripe), center_tile_identifier)
                for lut_entry in sub_lut[tile_stripe][center_tile_identifier]:
                    pass
        return []

    def _get_sub_lut(self, tile_stripe: str, center_tile_identifier: str):
        if tile_stripe not in self._lut.keys() and \
                center_tile_identifier not in self._lut[tile_stripe][center_tile_identifier]:
            pass
        return self._lut[tile_stripe][center_tile_identifier]

    # def _ensure_lut_is_read(self):
    #     if not self._tile_lut:
    #         with open(PATH_TO_TILE_LOOKUP_TABLE, 'r') as infile:
    #             self._tile_lut = yaml.safe_load(infile)

    def _read_sub_lut(self, tile_stripe: str, center_tile_identifier: str) -> dict:
        with open(PATH_TO_TILE_LOOKUP_TABLE, 'r') as stream:
            # tile_strip_as_int = t(tile_stripe)
            # next_tile_strip = int(tile_stripe)
            part_of_sub_lut = 0
            data = []
            for line in stream:
                # if line.startswith(next_tile_strip):
                #     break
                if line.startswith(tile_stripe):
                    part_of_sub_lut = 1
                    data.append(line)
                elif part_of_sub_lut > 0 and line.strip().startswith(center_tile_identifier):
                    part_of_sub_lut = 2
                    data.append(line)
                elif part_of_sub_lut == 2:
                    if not line.startswith('    '):
                        break
                    data.append(line)
            return yaml.load(''.join(data))

    # def _read_sub_lut(self, tile_id: str) -> dict:
    #     start = '{}:'.format(tile_id[0:2])
    #     end = '{}:'.format(int(tile_id[0:2]) + 1)
    #     with open(PATH_TO_TILE_LOOKUP_TABLE, 'r') as stream:
    #         part_of_doc = False
    #         data = []
    #         for line in stream:
    #             if line.startswith(end):
    #                 break
    #             if line.startswith(start):
    #                 part_of_doc = True
    #             if part_of_doc:
    #                 data.append(line)
    #         return yaml.load(''.join(data))

    def _get_tile_coverage_as_wkt(self, tile_id: str) -> Optional[str]:
        start = int(tile_id[0:2])
        sub_lut = self._read_sub_lut(tile_id)
        if tile_id in sub_lut[start].keys():
            return sub_lut[start][tile_id]

    def _get_tile_coverage(self, tile_id: str) -> Optional[Polygon]:
        coverage_as_wkt = self._get_tile_coverage_as_wkt(tile_id)
        if coverage_as_wkt is not None:
            return loads(coverage_as_wkt)

    @classmethod
    def _get_military_grid_reference_system_tile(cls, longitude: float, latitude: float) -> str:
        """
        A method that uses a website to infer the Military Grid Reference System tile that is used by the
        Amazon data buckets from the latitude/longitude
        :param latitude: The latitude in decimal degrees
        :param longitude: The longitude in decimal degrees
        :return: The MGRS tile (e.g. 29TNJ)
        """
        response = requests.post(LAND_CONVERTER_BASE_URL, data=dict(latitude=latitude, longitude=longitude,
                                                                    xcmd="Calc", cmd="gps"))
        tile = None
        for response_line in response.text.split("\n"):
            if response_line.find("<title>") >= 0:
                tile = response_line.replace("<title>", "").replace("</title>", "")
                tile = tile.replace(" ", "")
        if tile is None:
            raise UserWarning('Could not determine tile id')
        try:
            return tile[:5]
        except NameError:
            return ''

    def provides_data_type(self, data_type: str) -> bool:
        return data_type == DataTypeConstants.AWS_S2_L1C

    def _get_parameters_as_dict(self) -> dict:
        return {}


class AwsS2MetaInfoProviderAccessor(MetaInfoProviderAccessor):

    @classmethod
    def name(cls) -> str:
        return _NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> AwsS2MetaInfoProvider:
        return AwsS2MetaInfoProvider()
