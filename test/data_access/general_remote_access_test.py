# test script that actually downloads data. Execute with care

from multiply_data_access import DataSetMetaInfo
from multiply_data_access.general_remote_access import HttpFileSystemAccessor

BARRAX_POLYGON = "POLYGON((-2.20397502663252 39.09868106889479,-1.9142106223355313 39.09868106889479," \
                 "-1.9142106223355313 38.94504502508093,-2.20397502663252 38.94504502508093," \
                 "-2.20397502663252 39.09868106889479))"

cams_parameters = {'url': 'http://www2.geog.ucl.ac.uk/~ucfafyi/cams/', 'temp_dir': './test/test_data_2/cams_temp_dir',
                   'path': './test/test_data_2/cams_main_dir', 'pattern': 'dt/yy'}
data_set_meta_info = DataSetMetaInfo(BARRAX_POLYGON, '2017-09-04', '2017-09-04', 'CAMS', '2017-09-04.nc')
# cams_file_system = HttpFileSystemAccessor.create_from_parameters(cams_parameters)
# uncomment these lines
# file_refs = cams_file_system.get(data_set_meta_info)

# print(file_refs)
