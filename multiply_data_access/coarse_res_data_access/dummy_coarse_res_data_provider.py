# import snappy

class DummyCoarseResDataProvider:

    def get_data(self, temporal_location, spatial_location, constraints):
        print ('Retrieving coarse resolution data')
        # return snappy.Product('coarse_res_l1c', 'coarse_res_l1_product', 1, 1)
        return 'coarse_res_product'