import base64
import datetime
import os
import osr
import re
import shutil
import urllib.request as urllib2

from http.cookiejar import CookieJar
from multiply_core.util import FileRef, get_mime_type, get_time_from_string
from multiply_core.observations import DataTypeConstants
from multiply_data_access.data_access import DataSetMetaInfo, FileSystemAccessor, MetaInfoProviderAccessor
from multiply_data_access.locally_wrapping_data_access import LocallyWrappingFileSystem, LocallyWrappingMetaInfoProvider
from shapely.geometry import Point, Polygon
from typing import List, Sequence

__author__ = 'Tonio Fincke (Brockmann Consult GmbH),' \
             'José Luis Gómez-Dans (University College London)'

_BASE_URL = 'http://e4ftl01.cr.usgs.gov/'
_PLATFORM = 'MOTA'
_FILE_SYSTEM_NAME = 'LpDaacFileSystem'
_META_INFO_PROVIDER_NAME = 'LpDaacMetaInfoProvider'
_X_STEP = -463.31271653 * 2400
_Y_STEP = 463.31271653 * 2400
_M_Y0 = -20015109.354
_M_X0 = 10007554.677


class LpDaacMetaInfoProvider(LocallyWrappingMetaInfoProvider):
    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    def _init_wrapped_meta_info_provider(self, parameters: dict) -> None:
        wgs84_srs = osr.SpatialReference()  # Define a SpatialReference object
        wgs84_srs.ImportFromEPSG(4326)  # And set it to WGS84 using the EPSG code
        modis_sinu_srs = osr.SpatialReference()  # define the SpatialReference object
        modis_sinu_srs.ImportFromProj4(
            "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs")
        self._wgs84_to_modis = osr.CoordinateTransformation(wgs84_srs, modis_sinu_srs)
        self._modis_to_wgs84 = osr.CoordinateTransformation(modis_sinu_srs, wgs84_srs)

    def _query_wrapped_meta_info_provider(self, query_string: str) -> List[DataSetMetaInfo]:
        data_types = self.get_data_types_from_query_string(query_string)
        if not DataTypeConstants.MODIS_MCD_43 in data_types:
            return []
        roi = self.get_roi_from_query_string(query_string)
        min_x, min_y, max_x, max_y = roi.bounds
        h_range, v_range = self._get_id_ranges(min_x, min_y, max_x, max_y)
        start_time = self.get_start_time_from_query_string(query_string)
        end_time = self.get_end_time_from_query_string(query_string)
        current_time = start_time
        data_set_meta_infos = []
        while (current_time < end_time):
            date_dir_url = '{}/{}/{}/{}.{:02d}.{:02d}/'.format(_BASE_URL, _PLATFORM, DataTypeConstants.MODIS_MCD_43,
                                                               current_time.year, current_time.month, current_time.day)
            date_page = urllib2.urlopen(date_dir_url).read().decode('utf-8')
            for h in h_range:
                for v in v_range:
                    file_regex = '.hdf">MCD43A1.A{}{:03d}.h{:02d}v{:02d}.006.*.hdf'. \
                        format(current_time.year, current_time.timetuple().tm_yday, h, v)
                    available_files = re.findall(file_regex, date_page)
                    # todo do this only once
                    tile_coverage = self._get_tile_coverage(h, v).wkt
                    for file in available_files:
                        data_set_meta_infos.append(DataSetMetaInfo(tile_coverage, current_time.strftime('%Y-%m-%d'),
                                                                   current_time.strftime('%Y-%m-%d'),
                                                                   DataTypeConstants.MODIS_MCD_43, file[6:]))
            current_time += datetime.timedelta(days=1)
        return data_set_meta_infos

    def _get_tile_coverage(self, h: int, v: int) -> Polygon:
        sinu_min_lat = h * _Y_STEP + _M_Y0
        sinu_max_lat = (h + 1) * _Y_STEP + _M_Y0
        sinu_min_lon = v * _X_STEP + _M_X0
        sinu_max_lon = (v + 1) * _X_STEP + _M_X0
        points = []
        lat0, lon0, z0 = self._modis_to_wgs84.TransformPoint(sinu_min_lat, sinu_min_lon)
        points.append(Point(lat0, lon0))
        lat1, lon1, z1 = self._modis_to_wgs84.TransformPoint(sinu_min_lat, sinu_max_lon)
        points.append(Point(lat1, lon1))
        lat2, lon2, z2 = self._modis_to_wgs84.TransformPoint(sinu_max_lat, sinu_min_lon)
        points.append(Point(lat2, lon2))
        lat3, lon3, z3 = self._modis_to_wgs84.TransformPoint(sinu_max_lat, sinu_max_lon)
        points.append(Point(lat3, lon3))
        polygon = Polygon([[p.x, p.y] for p in points])
        return polygon

    def _get_id_ranges(self, min_x: float, min_y: float, max_x: float, max_y: float) -> ([], []):
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

    def _get_h_v_tile_ids(self, min_x: float, min_y: float) -> (int, int):
        h, v, z = self._wgs84_to_modis.TransformPoint(min_x, min_y)
        h_id = int((h - _M_Y0) / _Y_STEP)
        v_id = int((v - _M_X0) / _X_STEP)
        return h_id, v_id

    def _get_wrapped_parameters_as_dict(self) -> dict:
        return {}

    def provides_data_type(self, data_type: str) -> bool:
        return data_type == DataTypeConstants.MODIS_MCD_43


class LpDaacMetaInfoProviderAccessor(MetaInfoProviderAccessor):
    @classmethod
    def name(cls) -> str:
        return _META_INFO_PROVIDER_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> LpDaacMetaInfoProvider:
        return LpDaacMetaInfoProvider(parameters)


class LpDaacFileSystem(LocallyWrappingFileSystem):
    @classmethod
    def name(cls) -> str:
        return _FILE_SYSTEM_NAME

    def _get_wrapped_parameters_as_dict(self) -> dict:
        return {}

    def _init_wrapped_file_system(self, parameters: dict) -> None:
        if 'temp_dir' not in parameters.keys() or not os.path.exists(parameters['temp_dir']):
            raise ValueError('No valid temporal directory provided for Lp Daac File System')
        self._temp_dir = parameters['temp_dir']
        if 'username' not in parameters.keys():
            raise ValueError('No username provided for Lp Daac File System')
        self._username = parameters['username']
        if 'password' not in parameters.keys():
            raise ValueError('No password provided for Lp Daac File System')
        self._password = parameters['password']
        cj = CookieJar()
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    def _get_from_wrapped(self, data_set_meta_info: DataSetMetaInfo) -> Sequence[FileRef]:
        file_refs = []
        time = get_time_from_string(data_set_meta_info.start_time)
        file_url = '{}/{}/{}/{}.{:02d}.{:02d}/{}'.format(_BASE_URL, _PLATFORM, DataTypeConstants.MODIS_MCD_43,
                                                         time.year, time.month, time.day, data_set_meta_info.identifier)
        request = urllib2.Request(file_url)
        authorization = base64.encodebytes(str.encode('{}:{}'.format(self._username, self._password))). \
            replace(b'\n', b'').decode()
        request.add_header('Authorization', 'Basic {}'.format(authorization))
        remote_file = self._opener.open(request)
        temp_url = '{}/{}'.format(self._temp_dir, data_set_meta_info.identifier)
        with open(temp_url, 'wb') as temp_file:
            shutil.copyfileobj(remote_file, temp_file)
        file_refs.append(FileRef(temp_url, data_set_meta_info.start_time, data_set_meta_info.end_time,
                                 get_mime_type(temp_url)))
        return file_refs

    def _notify_copied_to_local(self, data_set_meta_info: DataSetMetaInfo) -> None:
        pass


class LpDaacFileSystemAccessor(FileSystemAccessor):
    @classmethod
    def name(cls) -> str:
        return _FILE_SYSTEM_NAME

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> LpDaacFileSystem:
        return LpDaacFileSystem(parameters)
