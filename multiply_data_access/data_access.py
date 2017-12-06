"""
Description
===========

This module contains the MULTIPLY data access API.
"""

from abc import ABCMeta, abstractmethod
from typing import List
from datetime import datetime, timedelta
from shapely.wkt import loads
from shapely.geometry import Polygon

__author__ = 'Alexander Löw (Ludwig Maximilians-Universität München), ' \
             'Tonio Fincke (Brockmann Consult GmbH)'


class DataSetMetaInfo:
    """
    A representation of meta information about a data set. To be retrieved from a query on a MetaInfProvider.
    """

    def __init__(self, coverage: str, start_time: str, end_time: str, data_type: str, identifier: str):
        self._coverage = coverage
        self._start_time = start_time
        self._end_time = end_time
        self._data_type = data_type
        self._identifier = identifier

    @property
    def start_time(self) -> str:
        """The dataset's start time."""
        return self._start_time

    @property
    def end_time(self) -> str:
        """The dataset's end time."""
        return self._end_time

    @property
    def coverage(self) -> str:
        """The dataset's spatial coverage, given as WKT string."""
        return self._coverage

    @property
    def data_type(self) -> str:
        """The type of the dataset."""
        return self._data_type

    @property
    def identifier(self) -> str:
        """An identifier so that the data set can be found on the Data Store's File System."""
        return self._identifier


class FileRef:
    """
    A reference to the physical location of a file.
    """

    def __init__(self, url: str, mime_type: str):
        self._url = url
        self._mime_type = mime_type

    @property
    def url(self) -> str:
        """The URL indicating where the file is physically located."""
        return self._url

    @property
    def mime_type(self):
        """The mime type of the file in question."""
        return self._mime_type


class FileSystem(metaclass=ABCMeta):
    """
    An abstraction of a file system on which data sets are physically stored
    """

    @abstractmethod
    def get(self, data_set_meta_info: DataSetMetaInfo) -> FileRef:
        """Retrieves a sequence of 'FileRef's."""


class MetaInfoProvider(metaclass=ABCMeta):
    """
    An abstraction of a provider that contains meta information about the files provided by a data store.
    """

    @abstractmethod
    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        """
        Processes a query and retrieves a result. The result will consist of all the data sets that satisfy the query.
        :return: A list of meta information about data sets that fulfill the query.
        """

    @staticmethod
    def get_roi_from_query_string(query_string: str) -> Polygon:
        roi_as_wkt = query_string.split(';')[0]
        roi = loads(roi_as_wkt)
        if not isinstance(roi, Polygon):
            raise ValueError('ROI must be a polygon')
        return roi

    @staticmethod
    def get_start_time_from_query_string(query_string: str):
        start_time_as_string = query_string.split(';')[1]
        return DataUtils.get_time_from_string(start_time_as_string, False)

    @staticmethod
    def get_end_time_from_query_string(query_string: str):
        end_time_as_string = query_string.split(';')[2]
        return DataUtils.get_time_from_string(end_time_as_string, True)

    @staticmethod
    def get_data_types_from_query_string(query_string: str) -> List[str]:
        data_types = query_string.split(';')[3].split(',')
        if len(data_types) == 1 and data_types[0] == '':
            return []
        for i, data_type in enumerate(data_types):
            data_types[i] = data_type.strip()
        return data_types


class DataUtils:

    @staticmethod
    def get_time_from_string(time_string: str, upper_bound: bool = False) -> datetime:
        # note: This an excerpt of a method in cate_core
        format_to_timedelta = [("%Y-%m-%dT%H:%M:%S", timedelta(), False),
                               ("%Y-%m-%d %H:%M:%S", timedelta(), False),
                               ("%Y-%m-%d", timedelta(hours=24, seconds=-1), False),
                               ("%Y-%m", timedelta(), True),
                               ("%Y", timedelta(days=365, seconds=-1), False)]
        for f, td, adjust in format_to_timedelta:
            try:
                dt = datetime.strptime(time_string, f)
                if adjust:
                    td = timedelta(days=DataUtils.get_days_of_month(dt.year, dt.month), seconds=-1)
                return dt + td if upper_bound else dt
            except ValueError:
                pass
        raise ValueError('Invalid date/time value: "%s"' % time_string)

    @staticmethod
    # not private so it can be tested
    def get_days_of_month(year: int, month: int) -> int:
        if month < 1 or month > 12:
            raise ValueError('Invalid month: %', month)
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        if month in [4, 6, 9, 11]:
            return 30
        if DataUtils.is_leap_year(year):
            return 29
        return 28

    @staticmethod
    def is_leap_year(year: int) -> bool:
        if year % 4 > 0:
            return False
        if year % 400 == 0:
            return True
        if year % 100 == 0:
            return False
        return True

    @staticmethod
    def get_mime_type(file_name: str):
        if file_name.endswith('.nc'):
            return 'application/x-netcdf'
        elif file_name.endswith('.zip'):
            return 'application/zip'
        elif file_name.endswith('.json'):
            return 'application/json'
        return 'unknown mime type'


class DataStore(object):
    """
    A store which provides access to data sets and information about these.
    """

    def __init__(self, file_system: FileSystem, meta_info_provider: MetaInfoProvider, identifier: str):
        self._file_system = file_system
        self._meta_info_provider = meta_info_provider
        self._id = identifier

    @property
    def id(self):
        """The identifier of the data store."""
        return self._id

    def get(self, data_set_meta_info: DataSetMetaInfo):
        """
        Retrieves data
        :return:
        """
        self._file_system.get(data_set_meta_info)

    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        """
        Evaluates a query and retrieves a result set for it.
        :return:
        """
        return self._meta_info_provider.query(query_string)


class WritableDataStore(DataStore):
    """
    An extension of the DataStore that additionally allows to put data sets.
    """

    def __init__(self, file_system: FileSystem, meta_info_provider: MetaInfoProvider, identifier: str):
        if not isinstance(file_system, WritableFileSystem):
            raise TypeError('Writable Data Store cannot be instantiated with a non-writable File System.')
        super().__init__(file_system, meta_info_provider, identifier)
        self._writable_file_system = file_system

    @abstractmethod
    def put(self):
        """
        Puts a data set into the data store.
        :return:
        """
        self._writable_file_system.put()


class WritableFileSystem(FileSystem):
    """
    An extension of a file system that allows to put files.
    """

    @abstractmethod
    def put(self, from_url: str, data_set_meta_info: DataSetMetaInfo):
        """Adds a data set to the file system by copying it from the given url to the expected location within
        the file system."""

    @abstractmethod
    def remove(self, data_set_meta_info: DataSetMetaInfo):
        """Removes all data sets from the file system that are described by the data set meta info"""
