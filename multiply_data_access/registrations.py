import pkg_resources
from multiply_data_access.data_access import FileSystem, MetaInfoProvider

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


#: List of FileSystem implementations supported by the CLI.
# Entries are classes derived from :py:class:`FileSystem` class.
#: MULTIPLY plugins may extend this list by their implementations during plugin initialisation.
FILE_SYSTEM_REGISTRY = []


#: List of MetaInfoProvider implementations supported by the CLI.
# Entries are classes derived from :py:class:`MetaInfoProvider` class.
#: MULTIPLY plugins may extend this list by their implementations during plugin initialisation.
META_INFO_PROVIDER_REGISTRY = []


def _set_up_file_system_registry():
    registered_file_systems = pkg_resources.iter_entry_points('file_system_plugins')
    for registered_file_system in registered_file_systems:
        FILE_SYSTEM_REGISTRY.append(registered_file_system.load())


def _set_up_meta_info_provider_registry():
    registered_meta_info_providers = pkg_resources.iter_entry_points('meta_info_provider_plugins')
    for registered_meta_info_provider in registered_meta_info_providers:
        META_INFO_PROVIDER_REGISTRY.append(registered_meta_info_provider.load())


def create_file_system_from_dict(file_system_as_dict: dict) -> FileSystem:
    if len(FILE_SYSTEM_REGISTRY) == 0:
        _set_up_file_system_registry()
    parameters = file_system_as_dict['parameters']
    for file_system_accessor in FILE_SYSTEM_REGISTRY:
        if file_system_accessor.name() == file_system_as_dict['type']:
            return file_system_accessor.create_from_parameters(parameters)
    raise UserWarning('Could not find file system of type {0}'.format(file_system_as_dict['type']))


def create_meta_info_provider_from_dict(meta_info_provider_as_dict: dict) -> MetaInfoProvider:
    if len(META_INFO_PROVIDER_REGISTRY) == 0:
        _set_up_meta_info_provider_registry()
    parameters = meta_info_provider_as_dict['parameters']
    for meta_info_provider_accessor in META_INFO_PROVIDER_REGISTRY:
        if meta_info_provider_accessor.name() == meta_info_provider_as_dict['type']:
            return meta_info_provider_accessor.create_from_parameters(parameters)
    raise UserWarning('Could not find meta info provider of type {0}'.format(meta_info_provider_as_dict['type']))
