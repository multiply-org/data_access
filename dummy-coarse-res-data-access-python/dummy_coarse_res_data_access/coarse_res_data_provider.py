import snappy

class coarse_res_data_provider:

    def get_data(self, temporal_location, spatial_location, constraints):
        print ('Retrieving coarse resolution data')
        return snappy.Product('coarse_res_l1c', 'coarse_res_l1_product', 1, 1)