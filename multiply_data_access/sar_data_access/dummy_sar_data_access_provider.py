# import snappy

import tempfile

class DummySARDataAccessProvider:

    def get_data(self, temporal_location, spatial_location, constraints):
        print ('Retrieving SAR data')
        # return snappy.Product('sar_data', 'sar_data', 1, 1)
        # returns a directory
        return tempfile.mkdtemp()
