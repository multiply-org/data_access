"""
Description
===========

This module contains the MULTIPLY data access API.
"""

from abc import ABCMeta, abstractmethod
from typing import List, Sequence, Optional
from datetime import datetime, timedelta
from multiply_core.util import FileRef
from shapely.wkt import loads
from shapely.geometry import Polygon
import os

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


class FileSystem(metaclass=ABCMeta):
    """
    An abstraction of a file system on which data sets are physically stored
    """

    @abstractmethod
    def get(self, data_set_meta_info: DataSetMetaInfo) -> Sequence[FileRef]:
        """Retrieves a sequence of 'FileRef's."""


class FileSystemAccessor(metaclass=ABCMeta):

    @classmethod
    def name(cls) -> str:
        """The name of the file system implementation."""

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> FileSystem:
        """Returns a FileSystem object."""


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

    @abstractmethod
    def provides_data_type(self, data_type: str) -> bool:
        """
        Whether the mete info provider provides access to data of the queried type
        :param data_type: A string labelling the data
        :return: True if data of that type can be requested from the meta infor provider
        """

    @staticmethod
    def get_roi_from_query_string(query_string: str) -> Optional[Polygon]:
        roi_as_wkt = query_string.split(';')[0]
        if roi_as_wkt == '':
            return None
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


class MetaInfoProviderAccessor(metaclass=ABCMeta):

    @classmethod
    def name(cls) -> str:
        """The name of the meta info provider implementation."""

    @classmethod
    def create_from_parameters(cls, parameters: dict) -> MetaInfoProvider:
        """Returns a MetaInfoProvider object."""


class DataUtils:

    @staticmethod
    def get_time_from_string(time_string: str, adjust_to_last_day: bool = False) -> datetime:
        # note: This an excerpt of a method in cate_core
        """
        Retrieves a datetime object from a string. If this is not possible, a ValueError is thrown.
        :param time_string: A string in UTC time format
        :param adjust_to_last_day: If true (and if the time string has no information about the number of days of
        the month), the returned datetime will be set to the last day of the month; otherwise to the first.
        :return: A datetime object corresponding to the UTC string that ahs been passed in.
        """
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
                return dt + td if adjust_to_last_day else dt
            except ValueError:
                pass
        raise ValueError('Invalid date/time value: "%s"' % time_string)

    @staticmethod
    def get_days_of_month(year: int, month: int) -> int:
        """
        Determines the number of days for a given month
        :param year: The year (required to determine whether it is a leap year)
        :param month: The month
        :return: The number of days of this month
        """
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
        """
        Determines whether a year is a leap year.
        :param year: The year.
        :return: True, when the given year is a leap year
        """
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
        elif os.path.isdir(file_name):
            return 'application/x-directory'
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

    def get(self, data_set_meta_info: DataSetMetaInfo) -> Sequence[FileRef]:
        """
        Retrieves data
        :return:
        """
        return self._file_system.get(data_set_meta_info)

    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        """
        Evaluates a query and retrieves a result set for it.
        :return:
        """
        return self._meta_info_provider.query(query_string)

    def provides_data_type(self, data_type: str) -> bool:
        """
        Whether the data store provides access to data of the queried type
        :param data_type: A string labelling the data
        :return: True if data of that type can be requested from the meta infor provider
        """
        return self._meta_info_provider.provides_data_type(data_type)


class WritableDataStore(DataStore):
    """
    An extension of the DataStore that additionally allows to put data sets.
    """

    def __init__(self, file_system: FileSystem, meta_info_provider: MetaInfoProvider, identifier: str):
        if not isinstance(file_system, WritableFileSystem):
            raise TypeError('Writable Data Store cannot be instantiated with a non-writable File System.')
        if not isinstance(meta_info_provider, UpdateableMetaInfoProvider):
            raise TypeError('Writable Data Store cannot be instantiated with a non-updateable Meta Info Provider.')
        super().__init__(file_system, meta_info_provider, identifier)
        self._writable_file_system = file_system
        self._updateable_meta_info_provider = meta_info_provider

    @abstractmethod
    def put(self):
        """
        Puts a data set into the data store.
        :return:
        """
        # check for data type
        # 1. Put the data
        # 2. Ensure where data has been put
        # create meta data info
        # 3. Update meta info provider
        self._writable_file_system.put()

    def update(self):
        """
        Causes the data store to update its registry: Newly found data will be registered, faulty registry entries
        will be removed.
        """
        # 1. Scan writable file system
        found_data_set_meta_infos = self._writable_file_system.scan()
        registered_data_set_meta_infos = self._updateable_meta_info_provider.get_all_data()



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

    @abstractmethod
    def scan(self) -> Sequence[DataSetMetaInfo]:
        """Retrieves a sequence of data set meta informations of all file refs found in the file system."""


class UpdateableMetaInfoProvider(MetaInfoProvider):
    """
    A MetaInfoProvider that can be updated when data is put there.
    """

    @abstractmethod
    def update(self, data_set_meta_info: DataSetMetaInfo):
        """Adds information about the data set to its internal registry."""

    @abstractmethod
    def remove(self, data_set_meta_info: DataSetMetaInfo):
        """Removes information about this data set from its internal registry."""

    @abstractmethod
    def get_all_data(self) -> Sequence[DataSetMetaInfo]:
        """Returns all available data set meta infos."""
