from nose.tools import assert_equal
from multiply_data_access.data_access_component import DataAccessComponent

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

path_to_json_file = './test/test_data/test_data_stores.yml'


def test_data_access_read_data_stores():
    data_access_component = DataAccessComponent()
    data_stores = data_access_component.read_data_stores(path_to_json_file)
    assert_equal(2, len(data_stores))
