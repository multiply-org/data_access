import snappy

class coarse_res_data_provider:

    def get_data(self, constraints):
        return snappy.Product('coarse_res_l1c', 'coarse_res_l1_product', 1, 1)