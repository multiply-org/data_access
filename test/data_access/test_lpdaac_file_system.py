__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

from multiply_data_access.lpdaac_data_access import DataSetMetaInfo, LpDaacFileSystem, LpDaacFileSystemAccessor
from shapely.wkt import loads


H17_V05_COVERAGE = 'POLYGON ((-13.05407289035348 39.99999999616804, -11.54700538146705 29.9999999970181, ' \
                '1.127072786096139e-09 39.99999999616804, 9.96954409223065e-10 29.9999999970181, ' \
                '-13.05407289035348 39.99999999616804))'
H17_V04_COVERAGE = 'POLYGON ((-15.55723826442343 49.99999999531797, -13.05407289035348 39.99999999616804, ' \
                   '1.343193041889809e-09 49.99999999531797, 1.127072786096139e-09 39.99999999616804, ' \
                   '-15.55723826442343 49.99999999531797))'


def test_lpdaac_file_system_creation():
    parameters = {'path': './test/test_data/', 'pattern': '', 'temp_dir': './test/test_data/', 'username': 'dummy',
                  'password': 'dummy'}
    file_system = LpDaacFileSystemAccessor.create_from_parameters(parameters)

    assert file_system is not None

def test_lpdaac_file_system_name():
    parameters = {'path': './test/test_data/', 'pattern': '', 'temp_dir': './test/test_data/', 'username': 'dummy',
                  'password': 'dummy'}
    file_system = LpDaacFileSystemAccessor.create_from_parameters(parameters)

    assert 'LpDaacFileSystem' == file_system.name()
    assert 'LpDaacFileSystem' == LpDaacFileSystem.name()
    assert 'LpDaacFileSystem' == LpDaacFileSystemAccessor.name()
