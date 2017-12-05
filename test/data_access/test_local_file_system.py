from multiply_data_access import DataSetMetaInfo, LocalFileSystem
import os
import shutil

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


def test_get_one_file():
    local_file_system = LocalFileSystem('./test/test_data/', '/dt/yy/mm/dd/')
    data_set_meta_info = DataSetMetaInfo('doesn\'t matter', '2017-08-21', '2017-08-21', 'my_data_type', '')
    file_refs = local_file_system.get(data_set_meta_info)
    assert 1, len(file_refs)
    assert 'small_product.nc', file_refs[0].url
    assert 'application/x-netcdf', file_refs[0].mime_type


def test_get_two_files():
    local_file_system = LocalFileSystem('./test/test_data/', '/dt/yy/mm/dd/')
    data_set_meta_info = DataSetMetaInfo('doesn\'t matter', '2017-08-21', '2017-08-25', 'my_data_type', '')
    file_refs = local_file_system.get(data_set_meta_info)
    assert 2, len(file_refs)
    assert 'small_product.nc', file_refs[0].url
    assert 'application/x-netcdf', file_refs[0].mime_type
    assert 'other_small_product.nc', file_refs[1].url
    assert 'application/x-netcdf', file_refs[1].mime_type


def test_get_invalid_time():
    local_file_system = LocalFileSystem('./test/test_data/', '/dt/yy/mm/dd/')
    data_set_meta_info = DataSetMetaInfo('doesn\'t matter', '2017-07-19', '2017-07-20', 'my_data_type', '')
    file_refs = local_file_system.get(data_set_meta_info)
    assert 0 == len(file_refs)


def test_get_invalid_data_type():
    local_file_system = LocalFileSystem('./test/test_data/', '/dt/yy/mm/dd/')
    data_set_meta_info = DataSetMetaInfo('doesn\'t matter', '2017-08-21', '2017-08-21', 'my_other_data_type', '')
    file_refs = local_file_system.get(data_set_meta_info)
    assert 0 == len(file_refs)


def test_get_invalid_identifier():
    local_file_system = LocalFileSystem('./test/test_data/', '/dt/yy/mm/dd/')
    data_set_meta_info = DataSetMetaInfo('doesn\'t matter', '2017-08-21', '2017-08-21', 'my_data_type', ' rtfghnmchfj')
    file_refs = local_file_system.get(data_set_meta_info)
    assert 0 == len(file_refs)


def test_get_weird_pattern():
    local_file_system = LocalFileSystem('./test/test_data/', '/mm/')
    data_set_meta_info = DataSetMetaInfo('doesn\'t matter', '2017-06-21', '2017-06-21', 'doesn\'t matter', '')
    file_refs = local_file_system.get(data_set_meta_info)
    assert 1, len(file_refs)
    assert 'vfbzf.json', file_refs[0].url
    assert 'application/json', file_refs[0].mime_type


def test_put():
    local_file_system = LocalFileSystem('./test/test_data/', '/dt/yy/mm/dd/')
    url = open('gfhnfd.nc', 'w+').name
    try:
        data_set_meta_info = DataSetMetaInfo('doesn\'t matter', '2016-12-15', '2016-12-16', 'my_data_type',
                                             'doesn\'t matter')
        local_file_system.put(url, data_set_meta_info)
        assert os.path.exists('./test/test_data/my_data_type/2016/12/15/gfhnfd.nc')
    finally:
        os.remove(url)
        if os.path.exists('./test/test_data/my_data_type/2016/'):
            shutil.rmtree('./test/test_data/my_data_type/2016/')
