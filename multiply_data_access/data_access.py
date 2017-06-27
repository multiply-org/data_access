"""
"""
import os

class DataAccessProvider(object):
    def __init__(self, **kwargs):
        self.config = kwargs.get('config', None)
        self.output_dir = kwargs.get('output_dir', None)

        self._check()
        self._set_output_dir()

    def _set_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if self.output_dir[-1] != os.sep:
            self.output_dir += os.sep


    def _check(self):
        assert self.config is not None, 'ERROR: configuration needs to be provided'
        assert self.output_dir is not None, 'ERROR: output directory not specified'
