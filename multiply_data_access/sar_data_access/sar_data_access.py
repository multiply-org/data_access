"""
SAR data access
"""


from .. data_access import DataAccessProvider


class SARDataAccessProvider(DataAccessProvider):
    def __init__(self, **kwargs):
        super(SARDataAccessProvider, self).__init__(**kwargs)

    def get_data(self):
        """
        Parameters
        ----------

        Returns
        -------
        d : str
            directory where downloaded unprocessed data can be found
        """

        return self.output_dir
