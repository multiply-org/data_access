"""
Description
===========

This module contains an implementation of a file system that allows to get and put data stored on the local hard drive.
"""
from .data_access import DataSetMetaInfo, DataUtils, FileRef, WritableFileSystem
from datetime import datetime, timedelta, MAXYEAR
from enum import Enum
from typing import Sequence
import os.path
import shutil

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

_DATA_TYPE_PATTERN = 'dt'
_DAY_PATTERN = 'dd'
_MONTH_PATTERN = 'mm'
_YEAR_PATTERN = 'yy'
_ALLOWED_PATTERNS = [_DATA_TYPE_PATTERN, _YEAR_PATTERN, _MONTH_PATTERN, _DAY_PATTERN]


class TimeStep(Enum):
    DAILY = 0
    MONTHLY = 1
    YEARLY = 2
    NONE = 3


class LocalFileSystem(WritableFileSystem):
    """
    A representation of a file system on the local disk.
    """

    def __init__(self, path: str, pattern: str):
        self.path = self._get_validated_path(path)
        self._validate_pattern(pattern)
        self.pattern = pattern
        self._derive_timestep(self.pattern)

    def _derive_timestep(self, pattern: str):
        if '/{}/'.format(_DAY_PATTERN) in pattern:
            self.time_step = TimeStep.DAILY
        elif '/{}/'.format(_MONTH_PATTERN) in pattern:
            self.time_step = TimeStep.MONTHLY
        elif '/{}/'.format(_YEAR_PATTERN) in pattern:
            self.time_step = TimeStep.YEARLY
        else:
            self.time_step = TimeStep.NONE

    @staticmethod
    def _get_validated_path(path: str) -> str:
        if not os.path.exists(path):
            raise ValueError('Could not find path {0}'.format(path))
        if not path.endswith('/'):
            path = path + '/'
        return path

    @staticmethod
    def _validate_pattern(pattern: str):
        if not pattern:
            return
        pattern = pattern[1:-1]
        split_pattern = pattern.split('/')
        for token in split_pattern:
            if token not in _ALLOWED_PATTERNS:
                raise ValueError('Invalid pattern: {0} not allowed in {1}'.format(token, pattern))

    def get(self, data_set_meta_info: DataSetMetaInfo) -> Sequence[FileRef]:
        relative_path = self.path + self.pattern
        relative_path = relative_path.replace('/{}/'.format(_DATA_TYPE_PATTERN),
                                              '/{}/'.format(data_set_meta_info.data_type))
        start_time = DataUtils.get_time_from_string(data_set_meta_info.start_time)
        end_time = DataUtils.get_time_from_string(data_set_meta_info.end_time)
        file_refs = []
        time = start_time
        while time <= end_time:
            relative_path = relative_path.replace('/{}/'.format(_YEAR_PATTERN), '/{:04d}/'.format(time.year))
            relative_path = relative_path.replace('/{}/'.format(_MONTH_PATTERN), '/{:02d}/'.format(time.month))
            relative_path = relative_path.replace('/{}/'.format(_DAY_PATTERN), '/{:02d}/'.format(time.day))
            time = self._get_next_time_step(time)
            if not os.path.exists(relative_path):
                continue
            file_names = os.listdir(relative_path)
            for file_name in file_names:
                if data_set_meta_info.identifier in file_name:
                    mime_type = DataUtils.get_mime_type(file_name)
                    file_refs.append(FileRef(relative_path + file_name, mime_type))
        return file_refs

    def _get_next_time_step(self, time: datetime) -> datetime:
        if self.time_step == TimeStep.DAILY:
            return time + timedelta(days=1)
        if self.time_step == TimeStep.MONTHLY:
            num_delta_days = DataUtils.get_days_of_month(time.year, time.month)
            return time + timedelta(days=num_delta_days)
        if self.time_step == TimeStep.YEARLY:
            if DataUtils.is_leap_year(time.year):
                return time + timedelta(days=366)
            else:
                return time + timedelta(days=365)
        return datetime(year=MAXYEAR, month=12, day=31)

    def put(self, from_url: str, data_set_meta_info: DataSetMetaInfo):
        # we assume here that it suffices to consider the start time for putting a data set correctly
        time = DataUtils.get_time_from_string(data_set_meta_info.start_time)
        relative_path = self.path + self.pattern
        relative_path = relative_path.replace('/{}/'.format(_DATA_TYPE_PATTERN),
                                              '/{}/'.format(data_set_meta_info.data_type))
        relative_path = relative_path.replace('/{}/'.format(_YEAR_PATTERN), '/{:04d}/'.format(time.year))
        relative_path = relative_path.replace('/{}/'.format(_MONTH_PATTERN), '/{:02d}/'.format(time.month))
        relative_path = relative_path.replace('/{}/'.format(_DAY_PATTERN), '/{:02d}/'.format(time.day))
        if not os.path.exists(relative_path):
            os.makedirs(relative_path)
        shutil.copy(from_url, relative_path)

    def remove(self, data_set_meta_info: DataSetMetaInfo):
        time = DataUtils.get_time_from_string(data_set_meta_info.start_time)
        relative_path = self.path + self.pattern
        relative_path = relative_path.replace('/{}/'.format(_DATA_TYPE_PATTERN),
                                              '/{}/'.format(data_set_meta_info.data_type))
        relative_path = relative_path.replace('/{}/'.format(_YEAR_PATTERN), '/{:04d}/'.format(time.year))
        relative_path = relative_path.replace('/{}/'.format(_MONTH_PATTERN), '/{:02d}/'.format(time.month))
        relative_path = relative_path.replace('/{}/'.format(_DAY_PATTERN), '/{:02d}/'.format(time.day))
        if os.path.exists(relative_path):
            file_names = os.listdir(relative_path)
            for file_name in file_names:
                if data_set_meta_info.identifier in file_name:
                    os.remove(relative_path + file_name)
        while not self.path == relative_path and len(os.listdir(relative_path)) == 0:
            os.rmdir(relative_path)
            relative_path = relative_path[:relative_path[:relative_path.rfind('/')].rfind('/')]
