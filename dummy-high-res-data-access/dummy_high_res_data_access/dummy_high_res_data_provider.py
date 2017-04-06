import snappy

class dummy_high_res_data_provider:

    def get_data(self, temporal_location, spatial_location, constraints):
        print ('Retrieving high resolution data')
        return snappy.Product('high_res_l1', 'high_res_l1', 1, 1)
