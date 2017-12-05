"""
Description
===========

This module contains the MULTIPLY data access API.

Verification
============

Components
==========
"""

from abc import ABCMeta, abstractmethod
from typing import Sequence
from multiply_data_access.data_access import FileRef

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


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

class WritableFileSystem(FileSystem):
    """
    An extension of a file system that allows to put files.
    """
    @abstractmethod
    def put(self):
        """Adds a data set to the file system by putting it at the expected location."""

class LocalFileSystem(WritableFileSystem):
    """
    A representation of a file system on the local disk.
    """


