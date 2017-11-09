from multiply.data_access import JsonMetaInfoProvider
from multiply_data_access.data_access import DataSetMetaInfo

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

path_to_json_file = '../test_data/test_meta_info.json'


def test_json_meta_info_provider_query_for_region():
    provider = JsonMetaInfoProvider(path_to_json_file)
    query_string = "POLYGON((5 5, 20 5, 20 20, 5 20, 5 5));2017-03-01;2017-03-31;TYPE_A, TYPE_B, TYPE_C"
    meta_data_infos = provider.query(query_string)
    assert len(meta_data_infos) == 2
    ensure_first_data_set(meta_data_infos[0])
    ensure_second_data_set(meta_data_infos[1])

    query_string = "POLYGON((5 20, 35 20, 35 40, 5 40, 5 20));2017-03-01;2017-03-31;TYPE_A, TYPE_B, TYPE_C"
    meta_data_infos = provider.query(query_string)
    assert len(meta_data_infos) == 3
    ensure_second_data_set(meta_data_infos[0])
    ensure_third_data_set(meta_data_infos[1])
    ensure_fourth_data_set(meta_data_infos[2])

    query_string = "POLYGON((35 0, 45 0, 45 10, 35 10, 35 0));2017-03-01;2017-03-31;TYPE_A, TYPE_B, TYPE_C"
    meta_data_infos = provider.query(query_string)
    assert len(meta_data_infos) == 0


def test_json_meta_info_provider_query_for_times():
    provider = JsonMetaInfoProvider(path_to_json_file)
    query_string = "POLYGON((5 5, 35 5, 35 35, 5 35, 5 5));2017-03-24;2017-03-26;TYPE_A, TYPE_B, TYPE_C"
    meta_data_infos = provider.query(query_string)
    assert len(meta_data_infos) == 2
    ensure_first_data_set(meta_data_infos[0])
    ensure_fourth_data_set(meta_data_infos[1])

    query_string = "POLYGON((5 5, 35 5, 35 35, 5 35, 5 5));2017-03-19;2017-03-20;TYPE_A, TYPE_B, TYPE_C"
    meta_data_infos = provider.query(query_string)
    assert len(meta_data_infos) == 3
    ensure_second_data_set(meta_data_infos[0])
    ensure_third_data_set(meta_data_infos[1])
    ensure_fourth_data_set(meta_data_infos[2])

    query_string = "POLYGON((5 5, 35 5, 35 35, 5 35, 5 5));2017-03-10;2017-03-10;TYPE_A, TYPE_B, TYPE_C"
    meta_data_infos = provider.query(query_string)
    assert len(meta_data_infos) == 1
    ensure_fourth_data_set(meta_data_infos[0])

    query_string = "POLYGON((5 5, 35 5, 35 35, 5 35, 5 5));2017-03;2017-03;TYPE_A, TYPE_B, TYPE_C"
    meta_data_infos = provider.query(query_string)
    assert len(meta_data_infos) == 4
    ensure_first_data_set(meta_data_infos[0])
    ensure_second_data_set(meta_data_infos[1])
    ensure_third_data_set(meta_data_infos[2])
    ensure_fourth_data_set(meta_data_infos[3])

    query_string = "POLYGON((5 5, 35 5, 35 35, 5 35, 5 5));2016-03;2016-03;TYPE_A, TYPE_B, TYPE_C"
    meta_data_infos = provider.query(query_string)
    assert len(meta_data_infos) == 0


def test_json_meta_info_provider_query_for_data_type():
    provider = JsonMetaInfoProvider(path_to_json_file)
    query_string = "POLYGON((5 5, 35 5, 35 35, 5 35, 5 5));2017-03;2017-03;TYPE_A, TYPE_C"
    meta_data_infos = provider.query(query_string)
    assert len(meta_data_infos) == 3
    ensure_first_data_set(meta_data_infos[0])
    ensure_second_data_set(meta_data_infos[1])
    ensure_fourth_data_set(meta_data_infos[2])

    query_string = "POLYGON((5 5, 35 5, 35 35, 5 35, 5 5));2017-03;2017-03;TYPE_B"
    meta_data_infos = provider.query(query_string)
    assert len(meta_data_infos) == 1
    ensure_third_data_set(meta_data_infos[0])

    query_string = "POLYGON((5 5, 35 5, 35 35, 5 35, 5 5));2017-03;2017-03;"
    meta_data_infos = provider.query(query_string)
    assert len(meta_data_infos) == 0


def ensure_first_data_set(data_set:DataSetMetaInfo):
    assert data_set.coverage == 'POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))'
    assert data_set.start_time == '2017-03-25 12:30:00'
    assert data_set.end_time == '2017-03-25 12:40:00'
    assert data_set.data_type == 'TYPE_A'
    assert data_set.identifier == 'dvgbvjn'


def ensure_second_data_set(data_set:DataSetMetaInfo):
    assert data_set.coverage == 'POLYGON((15 15, 25 15, 25 25, 15 25, 15 15))'
    assert data_set.start_time == '2017-03-20 14:30:00'
    assert data_set.end_time == '2017-03-20 14:40:00'
    assert data_set.data_type == 'TYPE_A'
    assert data_set.identifier == 'nkhmjzh'


def ensure_third_data_set(data_set:DataSetMetaInfo):
    assert data_set.coverage == 'POLYGON((35 35, 45 35, 45 35, 35 45, 35 35))'
    assert data_set.start_time == '2017-03-20'
    assert data_set.end_time == '2017-03-20'
    assert data_set.data_type == 'TYPE_B'
    assert data_set.identifier == 'rtwgtnj'


def ensure_fourth_data_set(data_set:DataSetMetaInfo):
    assert data_set.coverage == 'POLYGON((0 35, 10 35, 10 35, 0 45, 0 35))'
    assert data_set.start_time == '2017-03'
    assert data_set.end_time == '2017-03'
    assert data_set.data_type == 'TYPE_C'
    assert data_set.identifier == 'vgfbhngf'
