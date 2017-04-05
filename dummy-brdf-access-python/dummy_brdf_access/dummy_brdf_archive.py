import snappy

class dummy_brdf_archive:

    def has_brdf_descriptor(self, temporal_information, spatial_information):
        return True


    def get_brdf_descriptor(self, temporal_information, spatial_information):
        return snappy.Product('brdf_descriptor', 'brdf_descriptor', 1, 1)