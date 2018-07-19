__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

from multiply_data_access.aws_s2_meta_info_provider import AwsS2MetaInfoProvider, AwsS2MetaInfoProviderAccessor, \
    _get_tile_stripes, _get_center_tile_identifiers, TileDescription
from multiply_data_access.data_access import DataUtils
from shapely.wkt import loads

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


def test_read_sub_lut():
    aws_s2_meta_info_provider = AwsS2MetaInfoProviderAccessor.create_from_parameters({})
    sub_lut = aws_s2_meta_info_provider._read_sub_lut('30', 'S')

    for key in sub_lut.keys():
        assert key.startswith('30S')


def test_get_affected_tile_descriptions():
    aws_s2_meta_info_provider = AwsS2MetaInfoProviderAccessor.create_from_parameters({})
    barrax_geometry = loads(BARRAX_POLYGON)
    affected_tile_ids = aws_s2_meta_info_provider.get_affected_tile_descriptions(barrax_geometry)

    assert 1 == len(affected_tile_ids)
    assert '30SWJ' == affected_tile_ids[0].tile_id
    assert BARRAX_TILE == affected_tile_ids[0].coverage

    large_polygon = loads("POLYGON((-15. 52.43,10. 52.43, 10. 28.94,-15. 28.94,-15. 52.43))")
    affected_tile_ids = aws_s2_meta_info_provider.get_affected_tile_descriptions(large_polygon)

    for tile_description in affected_tile_ids:
        assert tile_description.tile_id.startswith('28R') or tile_description.tile_id.startswith('29R') or \
               tile_description.tile_id.startswith('30R') or tile_description.tile_id.startswith('31R') or \
               tile_description.tile_id.startswith('32R') or tile_description.tile_id.startswith('28S') or \
               tile_description.tile_id.startswith('29S') or tile_description.tile_id.startswith('30S') or \
               tile_description.tile_id.startswith('31S') or tile_description.tile_id.startswith('32S') or \
               tile_description.tile_id.startswith('28T') or tile_description.tile_id.startswith('29T') or \
               tile_description.tile_id.startswith('30T') or tile_description.tile_id.startswith('31T') or \
               tile_description.tile_id.startswith('32T') or tile_description.tile_id.startswith('28U') or \
               tile_description.tile_id.startswith('29U') or tile_description.tile_id.startswith('30U') or \
               tile_description.tile_id.startswith('31U') or tile_description.tile_id.startswith('32U')


def test_get_data_set_meta_infos_for_tile_description():
    aws_s2_meta_info_provider = AwsS2MetaInfoProviderAccessor.create_from_parameters({})
    tile_description = TileDescription('30SWJ', BARRAX_TILE)
    start_time = DataUtils.get_time_from_string('2016-04-01')
    end_time = DataUtils.get_time_from_string('2016-04-30')
    data_set_meta_infos = aws_s2_meta_info_provider.get_data_set_meta_infos_for_tile_description(tile_description,
                                                                                                 start_time,
                                                                                                 end_time)
    assert 6 == len(data_set_meta_infos)
    assert '2016-04-01' == data_set_meta_infos[0].start_time
    assert '0' == data_set_meta_infos[0].identifier
    assert '2016-04-04' == data_set_meta_infos[1].start_time
    assert '0' == data_set_meta_infos[1].identifier
    assert '2016-04-11' == data_set_meta_infos[2].start_time
    assert '0' == data_set_meta_infos[2].identifier
    assert '2016-04-14' == data_set_meta_infos[3].start_time
    assert '0' == data_set_meta_infos[3].identifier
    assert '2016-04-21' == data_set_meta_infos[4].start_time
    assert '0' == data_set_meta_infos[4].identifier
    assert '2016-04-24' == data_set_meta_infos[5].start_time
    assert '0' == data_set_meta_infos[5].identifier
