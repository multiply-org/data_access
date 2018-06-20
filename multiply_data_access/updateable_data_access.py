from abc import abstractmethod
from typing import Sequence
from .data_access import DataSetMetaInfo, DataStore, FileSystem, MetaInfoProvider
from .data_set_meta_info_provider import DataSetMetaInfoProvision

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


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
        found_data_set_meta_infos = self._writable_file_system.scan()
        registered_data_set_meta_infos = self._updateable_meta_info_provider.get_all_data()
        meta_info_provision = DataSetMetaInfoProvision()
        for found_data_set_meta_info in found_data_set_meta_infos:
            already_registered = False
            for registered_data_set_meta_info in registered_data_set_meta_infos:
                if found_data_set_meta_info.data_type == registered_data_set_meta_info.data_type and \
                        found_data_set_meta_info.identifier == registered_data_set_meta_info.identifier:
                    already_registered = True
                    break
            if not already_registered:
                data_set_meta_info = meta_info_provision.get_data_set_meta_info(
                    found_data_set_meta_info.data_type, found_data_set_meta_info.identifier)
                self._updateable_meta_info_provider.update(data_set_meta_info)
        for registered_data_set_meta_info in registered_data_set_meta_infos:
            found = False
            for found_data_set_meta_info in found_data_set_meta_infos:
                if found_data_set_meta_info.data_type == registered_data_set_meta_info.data_type and \
                        found_data_set_meta_info.identifier == registered_data_set_meta_info.identifier:
                    found = True
                    break
            if not found:
                self._updateable_meta_info_provider.remove(registered_data_set_meta_info)


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
