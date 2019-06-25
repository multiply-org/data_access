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

    assert 4 == len(provided_data_types)
    expected_data_types = ['S1_SLC','S2_L1C', 'S3_L1_OLCI_RR', 'S3_L1_OLCI_FR']
    assert all([a == b for a, b in zip(provided_data_types, expected_data_types)])


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


def test_mundi_meta_info_provider_query():
    parameters = {}
    mundi_meta_info_provider = MundiMetaInfoProviderAccessor.create_from_parameters(parameters)

    query_string = "POLYGON((9.8 53.6,10.2 53.6,10.2 53.4,9.8 53.4,9.8 53.6));2018-06-01;2018-06-05;S2_L1C"
    data_set_meta_infos = mundi_meta_info_provider.query(query_string)

    assert 2 == len(data_set_meta_infos)

    assert 'S2B_MSIL1C_20180602T104019_N0206_R008_T32UNE_20180602T132118' == data_set_meta_infos[0].identifier
    assert 'POLYGON ((10.3882277619999996 54.1384156120000029, 10.3173421249999997 54.0163176499999977, ' \
           '10.2348201129999996 53.8730417960000025, 10.1528176469999991 53.7297406859999995, ' \
           '10.0714324099999999 53.5864079979999985, 9.9905949619999994 53.4430542019999990, ' \
           '9.9101521629999993 53.2996597570000006, 9.8301509550000006 53.1562272170000014, ' \
           '9.8297230889999998 53.1554540790000019, 8.9997008679999997 53.1611735449999969, ' \
           '8.9996937989999992 54.1481041039999980, 10.3882277619999996 54.1384156120000029))' \
           == data_set_meta_infos[0].coverage
    assert 'S2_L1C' == data_set_meta_infos[0].data_type
    assert '2018-06-02T10:40:19Z' == data_set_meta_infos[0].start_time
    assert '2018-06-02T10:40:19Z' == data_set_meta_infos[0].end_time

    assert 'S2A_MSIL1C_20180604T103021_N0206_R108_T32UNE_20180604T141551' == data_set_meta_infos[1].identifier
    assert 'POLYGON ((9.5329991839999995 54.1443829669999985, 9.6393092639999995 54.1279838920000032, ' \
           '9.7303900619999997 54.1138008249999984, 9.7304462029999996 54.1139137250000033, ' \
           '9.7459873600000009 54.1115134209999979, 9.7459783400000006 54.1114953069999984, ' \
           '9.7461166410000004 54.1114721849999967, 9.7458160340000006 54.1108685330000014, ' \
           '10.0791996249999993 54.0551552350000009, 10.0792399160000006 54.0552348470000013, ' \
           '10.0829703790000007 54.0546105379999986, 10.0830927999999993 54.0548524700000002, ' \
           '10.1046638760000000 54.0511033299999966, 10.1046137130000009 54.0510042180000028, ' \
           '10.4340695340000007 53.9936632220000021, 10.4341582939999995 53.9938358810000025, ' \
           '10.4518227370000005 53.9907657299999997, 10.4517716210000007 53.9906664869999986, ' \
           '10.4518087590000004 53.9906596909999976, 10.4515281689999995 53.9901149660000002, ' \
           '10.6729949840000007 53.9495901889999985, 10.6415649559999999 53.1498598900000019, ' \
           '8.9997008679999997 53.1611735449999969, 8.9996937989999992 54.1481041039999980, ' \
           '9.5329991839999995 54.1443829669999985))' == data_set_meta_infos[1].coverage
    assert 'S2_L1C' == data_set_meta_infos[1].data_type
    assert '2018-06-04T10:30:21Z' == data_set_meta_infos[1].start_time
    assert '2018-06-04T10:30:21Z' == data_set_meta_infos[1].end_time


def test_mundi_file_system_accessor_name():
    assert 'MundiFileSystem' == MundiFileSystemAccessor.name()


def test_mundi_file_system_accessor_create_from_parameters():
    parameters = {}
    mundi_file_system = MundiFileSystemAccessor.create_from_parameters(parameters)

    assert mundi_file_system is not None
    assert isinstance(mundi_file_system, MundiFileSystem)