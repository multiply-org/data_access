__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

from multiply_data_access.lpdaac_data_access import LpDaacMetaInfoProvider


path_to_json_file = './test/test_data/modis_store.json'


def test_lpdaac_meta_info_provider_create():
    parameters = {'path_to_json_file': path_to_json_file}
    provider = LpDaacMetaInfoProvider(parameters)

    assert provider is not None


def test_lpdaac_meta_info_provider_name():
    parameters = {'path_to_json_file': path_to_json_file}
    provider = LpDaacMetaInfoProvider(parameters)

    assert 'LpDaacMetaInfoProvider' == provider.name()
    assert 'LpDaacMetaInfoProvider' == LpDaacMetaInfoProvider.name()

def test_lpdaac_meta_info_provider_provides_data_type():
    parameters = {'path_to_json_file': path_to_json_file}
    provider = LpDaacMetaInfoProvider(parameters)

    assert provider.provides_data_type('MCD43A1.006')
    assert not provider.provides_data_type('AWS_S2_L1C')
    assert not provider.provides_data_type('Mrtftgeftt')


def test_lpdaac_meta_info_provider_get_h_v_tile_ids():
    parameters = {'path_to_json_file': path_to_json_file}
    provider = LpDaacMetaInfoProvider(parameters)

    h_id_0, v_id_0 = provider._get_h_v_tile_ids(-6., 35.)
    assert 17 == h_id_0
    assert 5 == v_id_0
    h_id_1, v_id_1 = provider._get_h_v_tile_ids(-39., -25.)
    assert 14 == h_id_1
    assert 11 == v_id_1


def test_lpdaac_meta_info_provider_get_id_ranges():
    parameters = {'path_to_json_file': path_to_json_file}
    provider = LpDaacMetaInfoProvider(parameters)

    h_range_0, v_range_0 = provider._get_id_ranges(-6., 35., -6., 35)
    assert [17] == h_range_0
    assert [5] == v_range_0
    h_range_1, v_range_1 = provider._get_id_ranges(-39., -25., -6., 35)
    assert [14, 15, 16, 17] == h_range_1
    assert [5, 6, 7, 8, 9, 10, 11] == v_range_1
    h_range_2, v_range_2 = provider._get_id_ranges(-20., 25., -6., 35)
    assert [16, 17] == h_range_2
    assert [5, 6] == v_range_2
