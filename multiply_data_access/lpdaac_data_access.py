import osr

from multiply_core.observations import DataTypeConstants
from multiply_data_access.data_access import DataSetMetaInfo, MetaInfoProviderAccessor
from multiply_data_access.locally_wrapping_data_access import LocallyWrappingMetaInfoProvider
from shapely.geometry import Polygon
from typing import List

__author__ = 'Tonio Fincke (Brockmann Consult GmbH),' \
             'José Luis Gómez-Dans (University College London)'

_NAME = 'LpDaacMetaInfoProvider'
_X_STEP = -463.31271653
_Y_STEP = 463.31271653
_M_Y0 = -20015109.354
_M_X0 = 10007554.677


class LpDaacMetaInfoProvider(LocallyWrappingMetaInfoProvider):

    @classmethod
    def name(cls) -> str:
        return _NAME

    def _init_wrapped_meta_info_provider(self, parameters: dict) -> None:
        wgs84_srs = osr.SpatialReference()  # Define a SpatialReference object
        wgs84_srs.ImportFromEPSG(4326)  # And set it to WGS84 using the EPSG code
        modis_sinu_srs = osr.SpatialReference()  # define the SpatialReference object
        modis_sinu_srs.ImportFromProj4("+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs")
        self._transformation = osr.CoordinateTransformation(wgs84_srs, modis_sinu_srs)  # from wgs84 to modis

    def _query_wrapped_meta_info_provider(self, query_string: str) -> List[DataSetMetaInfo]:
        data_types = self.get_data_types_from_query_string(query_string)
        if not DataTypeConstants.MODIS_MCD_43 in data_types:
            return []
        roi = self.get_roi_from_query_string(query_string)
        min_x, min_y, max_x, max_y = roi.bounds
        h_range, v_range = self._get_id_ranges(min_x, min_y, max_x, max_y)

        start_time = self.get_start_time_from_query_string(query_string)
        end_time = self.get_end_time_from_query_string(query_string)
        return []

    def _get_id_ranges(self, min_x: float, min_y:float, max_x: float, max_y:float) -> ([], []):
        h0, v0 = self._get_h_v_tile_ids(min_x, min_y)
        h1, v1 = self._get_h_v_tile_ids(min_x, max_y)
        h2, v2 = self._get_h_v_tile_ids(max_x, min_y)
        h3, v3 = self._get_h_v_tile_ids(max_x, max_y)
        min_h_id = min([h0, h1, h2, h3])
        max_h_id = max([h0, h1, h2, h3]) + 1
        h_id_range = list(range(min_h_id, max_h_id))
        min_v_id = min([v0, v1, v2, v3])
        max_v_id = max([v0, v1, v2, v3]) + 1
        v_id_range = list(range(min_v_id, max_v_id))
        return h_id_range, v_id_range

    def _get_h_v_tile_ids(self, min_x: float, min_y:float) -> (int, int):
        h, v, z = self._transformation.TransformPoint(min_x, min_y)
        h_id = self._get_horizontal_tile_id(h)
        v_id = self._get_vertical_tile_id(v)
        return h_id, v_id

    @staticmethod
    def _get_horizontal_tile_id(h: float) -> int:
        return int((h - _M_Y0) / (2400 * _Y_STEP))

    @staticmethod
    def _get_vertical_tile_id(v: float) -> int:
        return int((v - _M_X0) / (2400 * _X_STEP))

    def _get_wrapped_parameters_as_dict(self) -> dict:
        return {}

    def provides_data_type(self, data_type: str) -> bool:
        return data_type == DataTypeConstants.MODIS_MCD_43


class LpDaacMetaInfoProviderAccessor(MetaInfoProviderAccessor):

    @classmethod
    def name(cls) -> str:
        return _NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> LpDaacMetaInfoProvider:
        return LpDaacMetaInfoProvider(parameters)
