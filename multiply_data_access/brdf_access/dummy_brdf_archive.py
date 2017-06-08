import snappy

class DummyBRDFArchive:

    def has_brdf_descriptor(self, temporal_information, spatial_information):
        print ('Checking whether a brdf descriptor is present')
        return True


    def get_brdf_descriptor(self, temporal_information, spatial_information):
        print ('Retrieving a brdf descriptor from the archive')
        return snappy.Product('brdf_descriptor', 'brdf_descriptor', 1, 1)