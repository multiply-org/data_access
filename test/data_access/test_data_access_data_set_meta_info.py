from multiply_data_access import DataSetMetaInfo

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


def test_meta_info_provider_equals():
    data_set_meta_info = DataSetMetaInfo(coverage="POLYGON((15 15, 25 15, 25 25, 15 25, 15 15))",
                                     start_time="2017-03-21 14:33:00",
                                     end_time="2017-03-21 14:45:00",
                                     data_type="TYPE_D",
                                     identifier="dterftge")
    other_coverage = DataSetMetaInfo(coverage="POLYGON((10 10, 20 10, 20 20, 10 20, 10 10))",
                                         start_time="2017-03-21 14:33:00",
                                         end_time="2017-03-21 14:45:00",
                                         data_type="TYPE_D",
                                         identifier="ctfgb")
    other_start_time = DataSetMetaInfo(coverage="POLYGON((15 15, 25 15, 25 25, 15 25, 15 15))",
                                       start_time="2017-03-20 14:33:00",
                                       end_time="2017-03-21 14:45:00",
                                       data_type="TYPE_D",
                                       identifier="frgswh")
    other_end_time = DataSetMetaInfo(coverage="POLYGON((15 15, 25 15, 25 25, 15 25, 15 15))",
                                     start_time="2017-03-21 14:33:00",
                                     end_time="2017-03-22 14:45:00",
                                     data_type="TYPE_D",
                                     identifier="dtfsgtr")
    other_data_type = DataSetMetaInfo(coverage="POLYGON((15 15, 25 15, 25 25, 15 25, 15 15))",
                                      start_time="2017-03-21 14:33:00",
                                      end_time="2017-03-21 14:45:00",
                                      data_type="TYPE_A",
                                      identifier="drtwr")
    equal_except_for_id = DataSetMetaInfo(coverage="POLYGON((15 15, 25 15, 25 25, 15 25, 15 15))",
                                          start_time="2017-03-21 14:33:00",
                                          end_time="2017-03-21 14:45:00",
                                          data_type="TYPE_D",
                                          identifier="tfgtzz")
    assert not data_set_meta_info.equals(other_coverage)
    assert not data_set_meta_info.equals(other_start_time)
    assert not data_set_meta_info.equals(other_end_time)
    assert not data_set_meta_info.equals(other_data_type)
    assert data_set_meta_info.equals(equal_except_for_id)


def test_meta_info_provider_equals_except_data_type():
    data_set_meta_info = DataSetMetaInfo(coverage="POLYGON((15 15, 25 15, 25 25, 15 25, 15 15))",
                                     start_time="2017-03-21 14:33:00",
                                     end_time="2017-03-21 14:45:00",
                                     data_type="TYPE_D",
                                     identifier="dterftge")
    other_coverage = DataSetMetaInfo(coverage="POLYGON((10 10, 20 10, 20 20, 10 20, 10 10))",
                                         start_time="2017-03-21 14:33:00",
                                         end_time="2017-03-21 14:45:00",
                                         data_type="TYPE_D",
                                         identifier="ctfgb")
    other_start_time = DataSetMetaInfo(coverage="POLYGON((15 15, 25 15, 25 25, 15 25, 15 15))",
                                       start_time="2017-03-20 14:33:00",
                                       end_time="2017-03-21 14:45:00",
                                       data_type="TYPE_D",
                                       identifier="frgswh")
    other_end_time = DataSetMetaInfo(coverage="POLYGON((15 15, 25 15, 25 25, 15 25, 15 15))",
                                     start_time="2017-03-21 14:33:00",
                                     end_time="2017-03-22 14:45:00",
                                     data_type="TYPE_D",
                                     identifier="dtfsgtr")
    other_data_type = DataSetMetaInfo(coverage="POLYGON((15 15, 25 15, 25 25, 15 25, 15 15))",
                                      start_time="2017-03-21 14:33:00",
                                      end_time="2017-03-21 14:45:00",
                                      data_type="TYPE_A",
                                      identifier="drtwr")
    equal_except_for_id = DataSetMetaInfo(coverage="POLYGON((15 15, 25 15, 25 25, 15 25, 15 15))",
                                          start_time="2017-03-21 14:33:00",
                                          end_time="2017-03-21 14:45:00",
                                          data_type="TYPE_D",
                                          identifier="tfgtzz")
    assert not data_set_meta_info.equals_except_data_type(other_coverage)
    assert not data_set_meta_info.equals_except_data_type(other_start_time)
    assert not data_set_meta_info.equals_except_data_type(other_end_time)
    assert data_set_meta_info.equals_except_data_type(other_data_type)
    assert data_set_meta_info.equals_except_data_type(equal_except_for_id)
