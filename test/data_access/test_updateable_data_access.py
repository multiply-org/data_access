import os
import shutil

from multiply_data_access.local_file_system import LocalFileSystem
from multiply_data_access.json_meta_info_provider import JsonMetaInfoProvider
from multiply_data_access.updateable_data_access import WritableDataStore

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

AWS_S2_DATA_PATH = './test/test_data/aws_s2_data'
INCORRECT_AWS_S2_META_INFO_FILE = './test/test_data/non_existent_meta_info.json'

def test_update():
    # copy this so we don't mess up the original file
    path_to_incorrect_json_file = INCORRECT_AWS_S2_META_INFO_FILE + '_2'
    shutil.copyfile(INCORRECT_AWS_S2_META_INFO_FILE, path_to_incorrect_json_file)
    try:
        local_file_system = LocalFileSystem(AWS_S2_DATA_PATH, '')
        meta_info_provider = JsonMetaInfoProvider(path_to_incorrect_json_file)
        writable_data_store = WritableDataStore(local_file_system, meta_info_provider, 'test')

        writable_data_store.update()

        all_available_files = local_file_system.scan()
        assert 2 == len(all_available_files)
        assert 'AWS_S2_L1C' == all_available_files[0].data_type
        assert './test/test_data/aws_s2_data/15/F/ZX/2016/12/31/1' == all_available_files[0].identifier
        assert 'AWS_S2_L1C' == all_available_files[1].data_type
        assert './test/test_data/aws_s2_data/29/S/QB/2017/9/4/0' == all_available_files[1].identifier

        all_registered_files = meta_info_provider.get_all_data()
        assert 2 == len(all_registered_files)
        assert 'AWS_S2_L1C' == all_registered_files[0].data_type
        assert './test/test_data/aws_s2_data/15/F/ZX/2016/12/31/1' == all_registered_files[0].identifier
        assert '2017-09-04 11:18:25' == all_registered_files[0].start_time
        assert '2017-09-04 11:18:25' == all_registered_files[0].end_time
        assert 'POLYGON((-6.724926539250627 37.92559054724302, -5.4774490849610435 37.89483865860684, -5.5234456557459835 36.906971812661624, -6.754676710360797 36.93665039721959, -6.724926539250627 37.92559054724302))' == all_registered_files[0].coverage

        assert 'AWS_S2_L1C' == all_registered_files[1].data_type
        assert './test/test_data/aws_s2_data/29/S/QB/2017/9/4/0' == all_registered_files[1].identifier
        assert '2017-09-04 11:18:25' == all_registered_files[1].start_time
        assert '2017-09-04 11:18:25' == all_registered_files[1].end_time
        assert 'POLYGON((-6.724926539250627 37.92559054724302, -5.4774490849610435 37.89483865860684, -5.5234456557459835 36.906971812661624, -6.754676710360797 36.93665039721959, -6.724926539250627 37.92559054724302))' == all_registered_files[1].coverage


    finally:
        os.remove(path_to_incorrect_json_file)

