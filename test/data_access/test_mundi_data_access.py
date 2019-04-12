__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


from multiply_data_access.mundi_data_access import MundiFileSystem, MundiFileSystemAccessor, \
    MundiMetaInfoProvider, MundiMetaInfoProviderAccessor


def test_mundi_meta_info_provider_name():
    parameters = {}
    mundi_meta_info_provider = MundiMetaInfoProviderAccessor.create_from_parameters(parameters)

    assert 'MundiMetaInfoProvider' == mundi_meta_info_provider.name()


def test_mundi_meta_info_provider_provides_data_type():
    parameters = {}
    mundi_meta_info_provider = MundiMetaInfoProviderAccessor.create_from_parameters(parameters)

    assert mundi_meta_info_provider.provides_data_type('S2_L1C')
    assert not mundi_meta_info_provider.provides_data_type('AWS_S2_L1C')
    assert not mundi_meta_info_provider.provides_data_type('')
    # noinspection SpellCheckingInspection
    assert not mundi_meta_info_provider.provides_data_type('vfsgt')


def test_mundi_meta_info_provider_get_provided_data_types():
    parameters = {}
    mundi_meta_info_provider = MundiMetaInfoProviderAccessor.create_from_parameters(parameters)

    provided_data_types = mundi_meta_info_provider.get_provided_data_types()

    assert 1 == len(provided_data_types)
    assert 'S2_L1C' == provided_data_types[0]


def test_mundi_meta_info_provider_encapsulates_data_type():
    parameters = {}
    mundi_meta_info_provider = MundiMetaInfoProviderAccessor.create_from_parameters(parameters)

    assert not mundi_meta_info_provider.encapsulates_data_type('S2_L1C')
    assert not mundi_meta_info_provider.encapsulates_data_type('AWS_S2_L1C')
    assert not mundi_meta_info_provider.encapsulates_data_type('')
    # noinspection SpellCheckingInspection
    assert not mundi_meta_info_provider.encapsulates_data_type('vfsgt')


def test_mundi_meta_info_provider_accessor_name():
    assert 'MundiMetaInfoProvider' == MundiMetaInfoProviderAccessor.name()


def test_mundi_meta_info_provider_accessor_create_from_parameters():
    parameters = {}
    mundi_meta_info_provider = MundiMetaInfoProviderAccessor.create_from_parameters(parameters)

    assert mundi_meta_info_provider is not None
    assert isinstance(mundi_meta_info_provider, MundiMetaInfoProvider)


def test_mundi_file_system_accessor_name():
    assert 'MundiFileSystem' == MundiFileSystemAccessor.name()


def test_mundi_file_system_accessor_create_from_parameters():
    parameters = {}
    mundi_file_system = MundiFileSystemAccessor.create_from_parameters(parameters)

    assert mundi_file_system is not None
    assert isinstance(mundi_file_system, MundiFileSystem)
