from nose.tools import assert_equal
from multiply_data_access import DataUtils

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


def test_meta_info_provider_get_days_of_month():
    assert DataUtils.get_days_of_month(2017, 1) == 31
    assert DataUtils.get_days_of_month(2017, 2) == 28
    assert DataUtils.get_days_of_month(2017, 3) == 31
    assert DataUtils.get_days_of_month(2017, 4) == 30
    assert DataUtils.get_days_of_month(2017, 5) == 31
    assert DataUtils.get_days_of_month(2017, 6) == 30
    assert DataUtils.get_days_of_month(2017, 7) == 31
    assert DataUtils.get_days_of_month(2017, 8) == 31
    assert DataUtils.get_days_of_month(2017, 9) == 30
    assert DataUtils.get_days_of_month(2017, 10) == 31
    assert DataUtils.get_days_of_month(2017, 11) == 30
    assert DataUtils.get_days_of_month(2017, 12) == 31
    assert DataUtils.get_days_of_month(2016, 2) == 29
    assert DataUtils.get_days_of_month(2000, 2) == 29
    assert DataUtils.get_days_of_month(1900, 2) == 28
    assert DataUtils.get_days_of_month(1600, 2) == 29


def test_is_leap_year():
    assert_equal(True, DataUtils.is_leap_year(2004))
    assert_equal(False, DataUtils.is_leap_year(2003))
    assert_equal(True, DataUtils.is_leap_year(2000))
    assert_equal(False, DataUtils.is_leap_year(1900))


def test_get_mime_type():
    assert_equal('application/x-netcdf', DataUtils.get_mime_type('ctfthdbdr.nc'))
    assert_equal('application/zip', DataUtils.get_mime_type('ctfthdbdr.zip'))
    assert_equal('application/json', DataUtils.get_mime_type('ctfthdbdr.json'))
    assert_equal('unknown mime type', DataUtils.get_mime_type('ctfthdbdr'))
