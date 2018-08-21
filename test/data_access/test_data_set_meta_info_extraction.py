from multiply_data_access.data_set_meta_info_extraction import DataSetMetaInfoExtractor, AwsS2MetaInfoExtractor, \
    S2L2MetaInfoExtractor

from shapely import wkt

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

path_to_s2_dir = './test/test_data/aws_s2_data/29/S/QB/2017/9/4/0/'
path_to_s2_l2_dir = './test/test_data/s2_l2_dir/'

def test_aws_s2_meta_info_extractor():
    provider = AwsS2MetaInfoExtractor()
    assert 'AWS_S2_L1C' == provider.name()
    data_set_meta_info = provider.extract_meta_info(path_to_s2_dir)
    assert 'AWS_S2_L1C' == data_set_meta_info.data_type
    assert path_to_s2_dir == data_set_meta_info.identifier
    assert '2017-09-04 11:18:25' == data_set_meta_info.start_time
    assert '2017-09-04 11:18:25' == data_set_meta_info.end_time
    geometry_bounds = wkt.loads(data_set_meta_info.coverage).bounds
    assert 4 == len(geometry_bounds)
    assert -6.754676710360797 in geometry_bounds
    assert 36.906971812661624 in geometry_bounds
    assert -5.4774490849610435 in geometry_bounds
    assert 37.92559054724302 in geometry_bounds


def test_s2_l2_meta_info_extractor():
    provider = S2L2MetaInfoExtractor()
    assert 'AWS_S2_L2' == provider.name()
    data_set_meta_info = provider.extract_meta_info(path_to_s2_l2_dir)
    assert 'AWS_S2_L2' == data_set_meta_info.data_type
    assert path_to_s2_l2_dir == data_set_meta_info.identifier
    assert '2017-01-19 11:05:33' == data_set_meta_info.start_time
    assert '2017-01-19 11:05:33' == data_set_meta_info.end_time
    geometry_bounds = wkt.loads(data_set_meta_info.coverage).bounds
    assert 4 == len(geometry_bounds)
    assert -3.000233454377241 in geometry_bounds
    assert 38.754036047778804 in geometry_bounds
    assert -1.7187196513335372 in geometry_bounds
    assert 39.75026792656397 in geometry_bounds
