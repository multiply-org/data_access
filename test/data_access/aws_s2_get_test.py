# test script that actually downloads S2 data. Execute with care

from multiply_data_access import DataAccessComponent

data_access_component = DataAccessComponent()
BARRAX_POLYGON = "POLYGON((-2.20397502663252 39.09868106889479,-1.9142106223355313 39.09868106889479," \
                 "-1.9142106223355313 38.94504502508093,-2.20397502663252 38.94504502508093," \
                 "-2.20397502663252 39.09868106889479))"
# uncomment these lines
# file_refs = data_access_component.get_data_urls(BARRAX_POLYGON, '2017-04-01', '2017-04-08', 'AWS_S2_L1C')
# print(file_refs)
