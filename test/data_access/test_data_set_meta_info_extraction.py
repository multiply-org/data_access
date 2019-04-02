from multiply_data_access.data_set_meta_info_extraction import AwsS2MetaInfoExtractor, S2L1CMetaInfoExtractor, \
    S2L2MetaInfoExtractor, MODISMCD43MetaInfoExtractor, MODISMCD15A2MetaInfoExtractor

from shapely import wkt

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

path_to_s2_dir = './test/test_data/aws_s2_data/29/S/QB/2017/9/4/0/'
path_to_s2_l1c_dir = './test/test_data/S2B_MSIL1C_20180819T100019_N0206_R122_T32TQR_20180819T141300'
path_to_s2_l2_dir = './test/test_data/s2_l2_dir/'


def test_aws_s2_meta_info_extractor():
    provider = AwsS2MetaInfoExtractor()
    assert 'AWS_S2_L1C' == provider.name()
    data_set_meta_info = provider.extract_meta_info(path_to_s2_dir)
    assert 'AWS_S2_L1C' == data_set_meta_info.data_type
    assert path_to_s2_dir == data_set_meta_info.identifier
    assert '2017-09-04 11:18:25' == data_set_meta_info.start_time
    assert '2017-09-04 11:18:25' == data_set_meta_info.end_time
    coverage = wkt.loads(data_set_meta_info.coverage)
    expected_coverage = wkt.loads('POLYGON((-6.724926539250627 37.92559054724302, '
                                  '-5.477449084961044 37.89483865860684, -5.523445655745983 36.90697181266162,'
                                  '-6.754676710360797 36.93665039721959, -6.724926539250627 37.92559054724302))')
    assert coverage.almost_equals(expected_coverage)


def test_s2_l1c_meta_info_extractor():
    provider = S2L1CMetaInfoExtractor()
    assert 'S2_L1C' == provider.name()
    data_set_meta_info = provider.extract_meta_info(path_to_s2_l1c_dir)
    assert 'S2_L1C' == data_set_meta_info.data_type
    assert path_to_s2_l1c_dir == data_set_meta_info.identifier
    assert '2017-09-10T10:40:21' == data_set_meta_info.start_time
    assert '2017-09-10T10:40:21' == data_set_meta_info.end_time
    assert 'POLYGON((7.434601639013215 55.03692054207882, 9.152753273727466 55.04689020612033, ' \
           '9.149109963691934 54.06011138907911, 7.471920122716345 54.050496442234184, ' \
           '7.434601639013215 55.03692054207882))' == data_set_meta_info.coverage


def test_s2_l2_meta_info_extractor():
    provider = S2L2MetaInfoExtractor()
    assert 'AWS_S2_L2' == provider.name()
    data_set_meta_info = provider.extract_meta_info(path_to_s2_l2_dir)
    assert 'AWS_S2_L2' == data_set_meta_info.data_type
    assert path_to_s2_l2_dir == data_set_meta_info.identifier
    assert '2017-01-19 11:05:33' == data_set_meta_info.start_time
    assert '2017-01-19 11:05:33' == data_set_meta_info.end_time
    expected_wkt_coverage = wkt.loads('POLYGON((-3.000233454377241 39.75026792656398, '
                                      '-1.718719651333537 39.74319619168243, -1.736596780811647 38.7540360477788, '
                                      '-3.00023019602957 38.76086445672779, -3.000233454377241 39.75026792656398))')
    coverage = wkt.loads(data_set_meta_info.coverage)
    assert coverage.almost_equals(expected_wkt_coverage)


def test_modis_mcd43a1_extractor():
    extractor = MODISMCD43MetaInfoExtractor()
    assert 'MCD43A1.006' == extractor.name()
    data_set_meta_info = extractor.extract_meta_info('/some/thing/MCD43A1.A2017015.h17v05.006.2017024094450.hdf')
    assert 'MCD43A1.006' == data_set_meta_info.data_type
    assert 'MCD43A1.A2017015.h17v05.006.2017024094450.hdf' == data_set_meta_info.identifier
    assert '2017-01-15 00:00:00' == data_set_meta_info.start_time
    assert '2017-01-15 23:59:59' == data_set_meta_info.end_time
    coverage = wkt.loads(data_set_meta_info.coverage)
    expected_coverage = wkt.loads('POLYGON ((-13.05407289035348 39.99999999616804, '
                                  '1.127072786096139e-09 39.99999999616804, 9.96954409223065e-10 29.9999999970181, '
                                  '-11.54700538146705 29.9999999970181, -13.05407289035348 39.99999999616804))')
    assert coverage.almost_equals(expected_coverage)


def test_modis_mcd15a2_extractor():
    extractor = MODISMCD15A2MetaInfoExtractor()
    assert 'MCD15A2H.006' == extractor.name()
    data_set_meta_info = extractor.extract_meta_info('/some/thing/MCD15A2H.A2018313.h17v05.006.2018323214613.hdf')
    assert 'MCD15A2H.006' == data_set_meta_info.data_type
    assert 'MCD15A2H.A2018313.h17v05.006.2018323214613.hdf' == data_set_meta_info.identifier
    assert '2018-11-09 00:00:00' == data_set_meta_info.start_time
    assert '2018-11-16 23:59:59' == data_set_meta_info.end_time
    coverage = wkt.loads(data_set_meta_info.coverage)
    expected_coverage = wkt.loads('POLYGON ((-13.05407289035348 39.99999999616804, '
                                  '1.127072786096139e-09 39.99999999616804, 9.96954409223065e-10 29.9999999970181, '
                                  '-11.54700538146705 29.9999999970181, -13.05407289035348 39.99999999616804))')
    assert coverage.almost_equals(expected_coverage)
