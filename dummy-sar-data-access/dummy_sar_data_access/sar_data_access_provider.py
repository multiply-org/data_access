import snappy

class sar_data_access_provider:

    def get_data(self, temporal_location, spatial_location, constraints):
        print ('Retrieving SAR data')
        return snappy.Product('sar_data', 'sar_data', 1, 1)