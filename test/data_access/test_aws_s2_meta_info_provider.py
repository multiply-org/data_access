__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

from multiply_data_access.aws_s2_meta_info_provider import AwsS2MetaInfoProvider, AwsS2MetaInfoProviderAccessor, \
    _get_tile_stripes, _get_center_tile_identifiers

BARRAX_POLYGON = "POLYGON((-2.20397502663252 39.09868106889479,-1.9142106223355313 39.09868106889479," \
                 "-1.9142106223355313 38.94504502508093,-2.20397502663252 38.94504502508093," \
                 "-2.20397502663252 39.09868106889479))"
BARRAX_TILE = 'POLYGON((-3.00023345437724 39.7502679265611,-3.00023019602957 38.7608644567253,-1.73659678081167 ' \
              '38.7540360477761,-1.71871965133358 39.7431961916792,-3.00023345437724 39.7502679265611))'


def test_aws_s2_meta_info_provider_accessor_get_name():
    assert 'AwsS2MetaInfoProvider' == AwsS2MetaInfoProviderAccessor.name()


def test_aws_s2_meta_info_provider_accessor_create_from_parameters():
    aws_s2_meta_info_provider = AwsS2MetaInfoProviderAccessor.create_from_parameters({})
    assert type(aws_s2_meta_info_provider) == AwsS2MetaInfoProvider


def test_aws_s2_meta_info_provider_get_name():
    aws_s2_meta_info_provider = AwsS2MetaInfoProviderAccessor.create_from_parameters({})
    assert 'AwsS2MetaInfoProvider' == aws_s2_meta_info_provider.name()


def test_aws_s2_meta_info_provider_provides_data_type():
    aws_s2_meta_info_provider = AwsS2MetaInfoProviderAccessor.create_from_parameters({})

    assert not aws_s2_meta_info_provider.provides_data_type('AWS_S2_L2')
    assert not aws_s2_meta_info_provider.provides_data_type('hdtgbhhj')
    assert aws_s2_meta_info_provider.provides_data_type('AWS_S2_L1C')


def test_aws_s2_meta_info_provider_get_parameters_as_dict():
    aws_s2_meta_info_provider = AwsS2MetaInfoProviderAccessor.create_from_parameters({})
    parameters_as_dict = aws_s2_meta_info_provider._get_parameters_as_dict()

    assert 0 == len(parameters_as_dict.keys())


def test_get_center_tile_identifiers():
    assert ['S'] == _get_center_tile_identifiers(38.94504502508093, 39.09868106889479)
    assert ['R', 'S', 'T', 'U'] == _get_center_tile_identifiers(28.94, 52.43)
    assert ['C'] == _get_center_tile_identifiers(-84., -81.)
    assert ['C'] == _get_center_tile_identifiers(-78., -75.)
    assert ['X'] == _get_center_tile_identifiers(81., 84.)
    assert ['X'] == _get_center_tile_identifiers(75., 78.)


def test_get_tile_stripes():
    assert [30] == _get_tile_stripes(-5., -1.)
    assert [28, 29, 30, 31, 32] == _get_tile_stripes(-15., 10.)
    assert [1, 2] == _get_tile_stripes(-176., -170.)
    assert [59, 60] == _get_tile_stripes(170., 176.)
    assert [59, 60, 1, 2] == _get_tile_stripes(170., -170.)
    assert [60, 1] == _get_tile_stripes(176., -176.)


# def test_get_tile_coverage_as_wkt():
#     aws_s2_meta_info_provider = AwsS2MetaInfoProviderAccessor.create_from_parameters({})
#
#     tile_coverage_as_wkt = aws_s2_meta_info_provider._get_tile_coverage_as_wkt('30SWJ')
#
#     assert BARRAX_TILE == tile_coverage_as_wkt
#
#
def test_read_sub_lut():
    aws_s2_meta_info_provider = AwsS2MetaInfoProviderAccessor.create_from_parameters({})
    sub_lut = aws_s2_meta_info_provider._read_sub_lut('30', 'S')

    assert 1 == len(sub_lut.keys())
    assert 30 in sub_lut.keys()
    assert 1 == len(sub_lut[30].keys())
    assert 'S' in sub_lut[30].keys()
    assert '30SWJ' in sub_lut[30]['S'].keys()

# def test_get_military_grid_reference_system_tile():
#     aws_s2_meta_info_provider = AwsS2MetaInfoProviderAccessor.create_from_parameters({})
#
#     tile_id = aws_s2_meta_info_provider._get_military_grid_reference_system_tile(-2.20397502663252, 39.09868106889479)
#
#     assert tile_id == '30SWJ'

# def test_aws_s2_meta_info_provider_query():
#     aws_s2_meta_info_provider = AwsS2MetaInfoProviderAccessor.create_from_parameters({})
#     query_string = "{};2017-03-10;2017-03-10;AWS_S2_L1C".format(BARRAX_POLYGON)
#
#     data_set_meta_infos = aws_s2_meta_info_provider.query(query_string)
#     assert 1 == len(data_set_meta_infos)
