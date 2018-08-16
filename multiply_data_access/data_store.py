from .data_set_meta_info_extraction import DataSetMetaInfoProvision
from multiply_core.observations import get_valid_type
from multiply_core.util import FileRef
from multiply_data_access.data_access import DataSetMetaInfo, FileSystem, MetaInfoProvider
from typing import List, Sequence


class DataStore(object):
    """
    A store which provides access to data sets and information about these.
    """

    def __init__(self, file_system: FileSystem, meta_info_provider: MetaInfoProvider, identifier: str):
        self._file_system = file_system
        self._meta_info_provider = meta_info_provider
        self.meta_info_provision = DataSetMetaInfoProvision()
        self._id = identifier

    def __repr__(self):
        return 'Data store {}'.format(self._id)

    @property
    def id(self):
        """The identifier of the data store."""
        return self._id

    def get(self, data_set_meta_info: DataSetMetaInfo) -> Sequence[FileRef]:
        """
        Retrieves data
        :return:
        """
        file_refs = self._file_system.get(data_set_meta_info)
        self._meta_info_provider.notify_got(data_set_meta_info)
        return file_refs

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
        :return: True if data of that type can be requested from the meta info provider
        """
        return self._meta_info_provider.provides_data_type(data_type)

    def get_provided_data_types(self) -> List[str]:
        """
        :return: A list of the data types provided by this data store.
        """
        return self._meta_info_provider.get_provided_data_types()

    def get_as_dict(self) -> dict:
        """
        :return: A representation of this data store in a dictionary format
        """
        inner_dict = {'FileSystem': self._file_system.get_as_dict(),
                      'MetaInfoProvider': self._meta_info_provider.get_as_dict(), 'Id': self.id}
        return {'DataStore': inner_dict}

    def put(self, from_url: str):
        """
        Puts a data set into the data store.
        :return:
        """
        if not self._file_system.can_put():
            raise UserWarning('Cannot put data to data store')
        data_type = get_valid_type(from_url)
        if data_type == '':
            raise UserWarning('Could not determine data type of {}'.format(from_url))
        data_set_meta_info = self.meta_info_provision.get_data_set_meta_info(data_type, from_url)
        updated_data_set_meta_info = self._file_system.put(from_url, data_set_meta_info)
        self._meta_info_provider.update(updated_data_set_meta_info)

    def update(self):
        """
        Causes the data store to update its registry: Newly found data will be registered, faulty registry entries
        will be removed.
        """
        found_data_set_meta_infos = self._file_system.scan()
        registered_data_set_meta_infos = self._meta_info_provider.get_all_data()
        for found_data_set_meta_info in found_data_set_meta_infos:
            already_registered = False
            for registered_data_set_meta_info in registered_data_set_meta_infos:
                if found_data_set_meta_info.data_type == registered_data_set_meta_info.data_type and \
                        found_data_set_meta_info.identifier == registered_data_set_meta_info.identifier:
                    already_registered = True
                    break
            if not already_registered:
                data_set_meta_info = self.meta_info_provision.get_data_set_meta_info(
                    found_data_set_meta_info.data_type, found_data_set_meta_info.identifier)
                self._meta_info_provider.update(data_set_meta_info)
        for registered_data_set_meta_info in registered_data_set_meta_infos:
            found = False
            for found_data_set_meta_info in found_data_set_meta_infos:
                if found_data_set_meta_info.data_type == registered_data_set_meta_info.data_type and \
                        found_data_set_meta_info.identifier == registered_data_set_meta_info.identifier:
                    found = True
                    break
            if not found:
                self._meta_info_provider.remove(registered_data_set_meta_info)
