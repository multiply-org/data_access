"""
"""

class DataAccessProvider(object):
    def __init__(self, **kwargs):
        self.config = kwargs.get('config', None)
        self._check()

    def _check(self):
        assert self.config is not None, 'ERROR: configuration needs to be provided'
