__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

import os
import pytest
import shutil
from multiply_core.observations import DataTypeConstants
from multiply_data_access.aws_s2_file_system import AwsS2FileSystem, AwsS2FileSystemAccessor
from multiply_data_access.data_access import DataSetMetaInfo

OUTPUT_DIR = './test/test_data/aws_s2_download_dir/'
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)


def test_aws_s2_file_system_accessor_get_name():
    assert 'AwsS2FileSystem' == AwsS2FileSystemAccessor.name()


def test_aws_s2_file_system_accessor_create_from_parameters():
    aws_s2_file_system = AwsS2FileSystemAccessor.create_from_parameters({'temp_dir': OUTPUT_DIR})
    assert type(aws_s2_file_system) == AwsS2FileSystem
    with pytest.raises(ValueError):
        assert AwsS2FileSystemAccessor.create_from_parameters({})


def test_aws_s2_file_system_get_name():
    aws_s2_file_system = AwsS2FileSystemAccessor.create_from_parameters({'temp_dir': OUTPUT_DIR})
    assert 'AwsS2FileSystem' == aws_s2_file_system.name()
    assert 'AwsS2FileSystem' == AwsS2FileSystem.name()


def test_aws_s2_file_system_get_tile_name():
    aws_s2_file_system = AwsS2FileSystemAccessor.create_from_parameters({'temp_dir': OUTPUT_DIR})
    assert '30SWJ' == aws_s2_file_system._get_tile_name('30/S/WJ/2016/4/24/0')


def test_aws_s2_file_system_get_aws_index():
    aws_s2_file_system = AwsS2FileSystemAccessor.create_from_parameters({'temp_dir': OUTPUT_DIR})
    assert 0 == aws_s2_file_system._get_aws_index('30/S/WJ/2016/4/24/0')
    assert 25 == aws_s2_file_system._get_aws_index('30/S/WJ/2016/4/24/25')


def test_aws_s2_file_system_get_parameters_as_dict():
    aws_s2_file_system = AwsS2FileSystemAccessor.create_from_parameters({'temp_dir': OUTPUT_DIR})
    parameters_as_dict = aws_s2_file_system._get_parameters_as_dict()
    assert 1 == len(parameters_as_dict.keys())
    assert 'temp_dir' in parameters_as_dict.keys()
    assert OUTPUT_DIR == parameters_as_dict['temp_dir']


def test_aws_s2_file_system_is_valid_identifier():
    aws_s2_file_system = AwsS2FileSystemAccessor.create_from_parameters({'temp_dir': OUTPUT_DIR})
    assert aws_s2_file_system._is_valid_identifier('30/S/WJ/2016/4/1/0')
    assert not aws_s2_file_system._is_valid_identifier('dvghg')


def test_aws_s2_file_system_get():
    try:
        aws_s2_file_system = AwsS2FileSystemAccessor.create_from_parameters({'temp_dir': OUTPUT_DIR})
        data_set_meta_info = DataSetMetaInfo('doesnt matter here', '2016-04-01', '2016-04-01',
                                             DataTypeConstants.AWS_S2_L1C,
                                             '30/S/WJ/2016/4/1/0')
        file_ref = aws_s2_file_system._get_file_ref(data_set_meta_info, bands=[], metafiles=['tileInfo'])
        assert '{}/30SWJ,2016-04-01,0/'.format(OUTPUT_DIR) == file_ref.url
        assert '2016-04-01' == file_ref.start_time
        assert '2016-04-01' == file_ref.end_time
        assert 'application/x-directory' == file_ref.mime_type
    finally:
        shutil.rmtree('{}/30SWJ,2016-04-01,0/'.format(OUTPUT_DIR))
