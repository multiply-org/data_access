__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

from multiply_data_access.lpdaac_data_access import DataSetMetaInfo, LpDaacFileSystem, LpDaacFileSystemAccessor
import os

from multiply_core.observations import DataTypeConstants
from multiply_data_access.vrt_data_access import VrtMetaInfoProvider, VrtMetaInfoProviderAccessor
from shapely.wkt import loads

H17_V05_COVERAGE = 'POLYGON ((-13.05407289035348 39.99999999616804, -11.54700538146705 29.9999999970181, ' \
                '1.127072786096139e-09 39.99999999616804, 9.96954409223065e-10 29.9999999970181, ' \
                '-13.05407289035348 39.99999999616804))'
H17_V04_COVERAGE = 'POLYGON ((-15.55723826442343 49.99999999531797, -13.05407289035348 39.99999999616804, ' \
                   '1.343193041889809e-09 49.99999999531797, 1.127072786096139e-09 39.99999999616804, ' \
                   '-15.55723826442343 49.99999999531797))'
PATH_TO_VRT_FILE = './test/test_data/global_dem.vrt'
PATH_TO_JSON_FILE = './test/test_data/aster_meta_info.json'
ASTER_POLYGON = "POLYGON ((-5. 37., -4. 37., -4. 36., -5. 36., -5. 37.))"

def test_vrt_meta_info_provider_create():
    parameters = {'path_to_vrt_file': PATH_TO_VRT_FILE, 'encapsulated_data_type': DataTypeConstants.ASTER,
                  'accessed_meta_info_provider': 'JsonMetaInfoProvider', 'path_to_json_file': PATH_TO_JSON_FILE}
    provider = VrtMetaInfoProviderAccessor.create_from_parameters(parameters)

    assert provider is not None


def test_vrt_meta_info_provider_name():
    parameters = {'path_to_vrt_file': PATH_TO_VRT_FILE, 'encapsulated_data_type': DataTypeConstants.ASTER,
                  'accessed_meta_info_provider': 'JsonMetaInfoProvider', 'path_to_json_file': PATH_TO_JSON_FILE}
    provider = VrtMetaInfoProviderAccessor.create_from_parameters(parameters)

    assert 'VrtMetaInfoProvider' == provider.name()
    assert 'VrtMetaInfoProvider' == VrtMetaInfoProvider.name()
    assert 'VrtMetaInfoProvider' == VrtMetaInfoProviderAccessor.name()


def test_vrt_meta_info_provider_query_vrt_file_does_not_exist_yet():
    parameters = {'path_to_vrt_file': 'a_non_existing_file', 'encapsulated_data_type': DataTypeConstants.ASTER,
                    'accessed_meta_info_provider': 'JsonMetaInfoProvider', 'path_to_json_file': PATH_TO_JSON_FILE}
    provider = VrtMetaInfoProviderAccessor.create_from_parameters(parameters)

    query_string = 'POLYGON ((-4.6 36.8, -4. 36.8, -4. 36.2, -4.6 36.2, -4.6 36.8));2017-09-01;2017-09-12;VRT'
    data_set_meta_infos = provider.query(query_string)

    assert 1 == len(data_set_meta_infos)
    aster_polygon = loads(ASTER_POLYGON)
    covered_geometry = loads(data_set_meta_infos[0].coverage)
    assert covered_geometry.almost_equals(aster_polygon)
    assert data_set_meta_infos[0].start_time is None
    assert data_set_meta_infos[0].end_time is None
    assert 'VRT' == data_set_meta_infos[0].data_type
    assert 'a_non_existing_file' == data_set_meta_infos[0].identifier


def test_vrt_meta_info_provider_query_existing_vrt_file_can_use_existing_vrt():
    parameters = {'path_to_vrt_file': PATH_TO_VRT_FILE, 'encapsulated_data_type': DataTypeConstants.ASTER,
                  'accessed_meta_info_provider': 'JsonMetaInfoProvider', 'path_to_json_file': PATH_TO_JSON_FILE}
    provider = VrtMetaInfoProviderAccessor.create_from_parameters(parameters)

    query_string = 'POLYGON ((-4.6 36.8, -4. 36.8, -4. 36.2, -4.6 36.2, -4.6 36.8));2017-09-01;2017-09-12;VRT'
    data_set_meta_infos = provider.query(query_string)

    assert 1 == len(data_set_meta_infos)
    aster_polygon = loads(ASTER_POLYGON)
    covered_geometry = loads(data_set_meta_infos[0].coverage)
    assert covered_geometry.almost_equals(aster_polygon)
    assert data_set_meta_infos[0].start_time is None
    assert data_set_meta_infos[0].end_time is None
    assert 'VRT' == data_set_meta_infos[0].data_type
    assert PATH_TO_VRT_FILE == data_set_meta_infos[0].identifier


def test_vrt_meta_info_provider_query_existing_vrt_file_new_vrt():
    parameters = {'path_to_vrt_file': PATH_TO_VRT_FILE, 'encapsulated_data_type': DataTypeConstants.ASTER,
                  'accessed_meta_info_provider': 'JsonMetaInfoProvider', 'path_to_json_file': PATH_TO_JSON_FILE}
    provider = VrtMetaInfoProviderAccessor.create_from_parameters(parameters)

    query_string = 'POLYGON ((-5.2 36.8, -4.2 36.8, -4.2 36.2, -5.2 36.2, -5.2 36.8));2017-09-01;2017-09-12;VRT'
    data_set_meta_infos = provider.query(query_string)

    assert 1 == len(data_set_meta_infos)
    aster_polygon = loads('POLYGON ((-5. 37., -4. 37., -4. 36., -5. 36., -6. 36., -6. 37., -5. 37.))')
    covered_geometry = loads(data_set_meta_infos[0].coverage)
    assert covered_geometry.almost_equals(aster_polygon)
    assert data_set_meta_infos[0].start_time is None
    assert data_set_meta_infos[0].end_time is None
    assert 'VRT' == data_set_meta_infos[0].data_type
    assert PATH_TO_VRT_FILE == data_set_meta_infos[0].identifier


def test_vrt_meta_info_provider_query_existing_vrt_file_new_vrt_with_multipolygon():
    parameters = {'path_to_vrt_file': PATH_TO_VRT_FILE, 'encapsulated_data_type': DataTypeConstants.ASTER,
                  'accessed_meta_info_provider': 'JsonMetaInfoProvider', 'path_to_json_file': PATH_TO_JSON_FILE}
    provider = VrtMetaInfoProviderAccessor.create_from_parameters(parameters)

    query_string = 'POLYGON ((-6.8 38.8, -6.2 38.8, -6.2 38.2, -6.8 38.2, -6.8 38.8));2017-09-01;2017-09-12;VRT'
    data_set_meta_infos = provider.query(query_string)

    assert 1 == len(data_set_meta_infos)
    multi_polygon = loads('MULTIPOLYGON (((-5 37, -4 37, -4 36, -5 36, -5 37)), ((-7 39, -6 39, -6 38, -7 38, -7 39)))')
    covered_geometry = loads(data_set_meta_infos[0].coverage)
    assert covered_geometry.almost_equals(multi_polygon)
    assert data_set_meta_infos[0].start_time is None
    assert data_set_meta_infos[0].end_time is None
    assert 'VRT' == data_set_meta_infos[0].data_type
    assert PATH_TO_VRT_FILE == data_set_meta_infos[0].identifier
