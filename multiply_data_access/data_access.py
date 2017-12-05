"""
Description
===========

This module contains the MULTIPLY data access API.

Technical Requirements
======================

Verification
============

Components
==========
"""

import os
from abc import ABCMeta, abstractmethod
from typing import List, NamedTuple, Sequence, Tuple, Union
from datetime import datetime, timedelta
import json
from shapely.wkt import loads
from shapely.geometry import Polygon

__author__ = 'Alexander Löw (Ludwig Maximilians-Universität München), ' \
             'Tonio Fincke (Brockmann Consult GmbH)'

class DataSetMetaInfo:
    """
    A representation of meta information about a data set. To be retrieved from a query on a MetaInfProvider.
    """

    @property
    def start_time(self) -> str:
        """The dataset's start time."""

    @property
    def end_time(self) -> str:
        """The dataset's end time."""

    @property
    def coverage(self) -> str:
        """The dataset's spatial coverage, given as WKT string."""

    @property
    def identifier(self) -> str:
        """An identifier so that the data set can be found on the Data Store's File System."""


class FileRef:
    """
    A reference to the physical location of a file.
    """

    @property
    def url(self) -> str:
        """The URL indicating where the file is physically located."""

    @property
    def mime_type(self):
        """The mime type of the file in question."""

class FileSystem(metaclass=ABCMeta):
    """
    An abstraction of a file system on which data sets are physically stored
    """

    @abstractmethod
    def get(self) -> Sequence[FileRef]:
        """Retrieves a sequence of 'FileRef's."""

    @abstractmethod
    def open(self):
        """"""


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
    def get_start_time_from_query_string(query_string:str):
        start_time_as_string = query_string.split(';')[1]
        return MetaInfoProvider._get_time_from_string(start_time_as_string, False)

    @staticmethod
    def get_end_time_from_query_string(self, query_string:str):
        end_time_as_string = query_string.split(';')[2]
        return self._get_time_from_string(end_time_as_string, True)

    @staticmethod
    def _get_time_from_string(time_string: str, upper_bound:bool) -> datetime:
        # note: This an excerpt of a method in cate_core
        format_to_timedelta = [("%Y-%m-%dT%H:%M:%S", timedelta()),
                               ("%Y-%m-%d %H:%M:%S", timedelta()),
                               ("%Y-%m-%d", timedelta(hours=24, seconds=-1)),
                               ("%Y-%m", timedelta(weeks=4, seconds=-1)),
                               ("%Y", timedelta(days=365, seconds=-1))]
        for f, td in format_to_timedelta:
            try:
                dt = datetime.strptime(time_string, f)
                return dt + td if upper_bound else dt
            except ValueError:
                pass
        raise ValueError('Invalid date/time value: "%s"' % time_string)

    @staticmethod
    def get_data_types_from_query_string(query_string: str) -> List[str]:
        return query_string.split(';')[3].split(',')

class DataStore(object):
    """
    A store which provides access to data sets and information about these.
    """

    def __init__(self, file_system: FileSystem, meta_info_provider: MetaInfoProvider):
        self.file_system = file_system
        self._meta_info_provider = meta_info_provider

    @property
    def id(self):
        """The identifier of the data store."""

    def get(self):
        """
        Retrieves data
        :return:
        """
        self._file_system.get()

    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        """
        Evaluates a query and retrieves a result set for it.
        :return:
        """
        return self._meta_info_provider.query(str)

    def open(self):
        """
        Retrieves a data set.
        :return:
        """
        self.file_system.open()


class WritableDataStore(DataStore):
    """
    An extension of the DataStore that additionally allows to put data sets.
    """

    @abstractmethod
    def put(self):
        """
        Puts a data set into the data store.
        :return:
        """
        # self.file_system.put()
        pass


class JsonMetaInfoProvider(MetaInfoProvider):
    """
    A MetaInfoProvider that retrieves its meta information from a JSON file.
    """

    def __init__(self, path_to_json_file: str):
        json_file = open(path_to_json_file)
        self.meta_info_dict = json.load(json_file)

    def query(self, query_string: str) -> List[DataSetMetaInfo]:
        roi = self.get_roi_from_query_string(query_string)
        start_time = self.get_start_time_from_query_string(query_string)
        end_time = self.get_end_time_from_query_string(query_string)
        data_types = self.get_data_types_from_query_string(query_string)


class WritableFileSystem(FileSystem):
    """
    An extension of a file system that allows to put files.
    """

    @abstractmethod
    def put(self):
        """Adds a data set to the file system by putting it at the expected location."""
