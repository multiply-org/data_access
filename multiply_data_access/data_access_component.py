from typing import List, NewType, Sequence

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


class DataAccessComponent(object):
    """
    The controlling component. The data access component is responsible for communicating with the various data stores
     and decides which data is used from which data store.
    """

    def __init__(self):
        # todo read data stores here
        self._data_stores = []

    def get_data_urls(self, roi: str, start_time: str, end_time: str, data_types: str) -> List[str]:
        """
        Builds a query from the given parameters and asks all data stores whether they contain data that match the
        query. If datasets are found, url's to their positions are returned.
        :return: a list of url's to locally stored files that match the conditions given by the query in the parameter.
        """
        query_string = DataAccessComponent._build_query_string(roi, start_time, end_time, data_types)
        urls = []
        for data_store in self._data_stores:
            query_results = data_store.query(query_string)
            for query_result in query_results:
                file_ref = data_store.get(query_result)
                urls.append(file_ref.url)
        return urls

    @staticmethod
    def _build_query_string(roi: str, start_time: str, end_time: str, data_types: str) -> str:
        """
        Builds a query string. In a future version, this will be an opensearch url.
        :param roi:
        :param start_time:
        :param end_time:
        :param data_types:
        :return:    A query string that may be passed on to a data store
        """
        return roi + ';' + start_time + ';' + end_time + ';' + data_types
