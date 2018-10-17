========
Examples
========

This section lists a few examples to explain how the Data Access Component can be used.

How to show available stores
============================

You can get a list of available stores by calling show_stores:

.. code-block:: console
    >>> from multiply_data_access import DataAccessComponent
    >>> data_access_component = DataAccessComponent()
    INFO:root:Read data store aws_s2
    INFO:root:Read data store cams
    INFO:root:Read data store emulators
    INFO:root:Read data store wv_emulator
    INFO:root:Read data store aster_dem
    INFO:root:Read data store modis_mcd43a1
    INFO:root:Read data store S2L2
    INFO:root:Scanning local file system, not remote
    INFO:root:Scanning local file system, not remote
    INFO:root:Scanning local file system, not remote
    INFO:root:Scanning local file system, not remote
    INFO:root:Scanning local file system, not remote
    INFO:root:Scanning local file system, not remote
    >>> data_access_component.show_stores()
    Data store aws_s2
    Data store cams
    Data store emulators
    Data store wv_emulator
    Data store aster_dem
    Data store modis_mcd43a1
    Data store S2L2

Ask for available Data Types
============================

You can ask the Data Access Component for the types of data that are available:

.. code-block:: console
    >>> data_access_component.get_provided_data_types()
    ['AWS_S2_L1C',
     'CAMS',
     'ISO_MSI_A_EMU',
     'ISO_MSI_B_EMU',
     'WV_EMU',
     'Aster DEM',
     'MCD43A1.006',
     'AWS_S2_L2']

Query for Data
==============

To query for data you need to hand in
* a representation of the geographic area in Well-Known-Text-format.
This might looks something like this:
ROI = "POLYGON((-2.20397502663252 39.09868106889479,-1.9142106223355313 39.09868106889479," \
             "-1.9142106223355313 38.94504502508093,-2.20397502663252 38.94504502508093," \
             "-2.20397502663252 39.09868106889479))"
You can use https://arthur-e.github.io/Wicket/sandbox-gmaps3.html to get WKT representations of
other regions of interest.
Note that you can pass in an empty string if you don't want to specify a region.
* a start time in UTC format
* an end time in UTC format
The platform can read different forms of the UTC format.
The following times would be recognized:
* 2017-09-01T12:30:30
* 2017-09-01 12:30:30
* 2017-09-01
* 2017-09
* 2017
You need to specify start and end times.

* a comma-separated list of data types
This might be any combination of data types (of course, it makes only sense for those that are provided).

An example for a query string would be then:

.. code-block:: console
    >>> ROI = "POLYGON((-2.20397502663252 39.09868106889479,-1.9142106223355313 39.09868106889479," \
              "-1.9142106223355313 38.94504502508093,-2.20397502663252 38.94504502508093," \
              "-2.20397502663252 39.09868106889479))"
    >>> start_time = '2017-01-01'
    >>> end_time = '2017-01-20'
    >>> s2_data_infos = data_access_component.query(BARRAX_ROI, start_time, end_time, 'AWS_S2_L1C')
    [Data Set:
    Id: 30/S/WJ/2017/1/16/0,
    Type: AWS_S2_L1C,
    Start Time: 2017-01-16T10:53:55,
    End Time: 2017-01-16T10:53:55,
    Coverage: POLYGON((-3.00023345437724 39.7502679265611,-3.00023019602957 38.7608644567253,
    -1.73659678081167 38.7540360477761,-1.71871965133358 39.7431961916792,-3.00023345437724 39.7502679265611)),
    Data Set:
    Id: 30/S/WJ/2017/1/19/0,
    Type: AWS_S2_L1C,
    Start Time: 2017-01-19T11:05:33,
    End Time: 2017-01-19T11:05:33,
    Coverage: POLYGON((-3.00023345437724 39.7502679265611,-3.00023019602957 38.7608644567253,
    -1.73659678081167 38.7540360477761,-1.71871965133358 39.7431961916792,-3.00023345437724 39.7502679265611))]

Getting data
============

It is recommended to query for data first to see what is available before you exectute the ``get_data_urls`` command.
The ``get_data_urls`` command takes the same arguments as the ``query`` command above.
In the following example, we are asking to retrieve the emulators for the Sentinel-2 MSI sensors A and B.

.. code-block:: console
    >>> data_access_component.get_data_urls('', start_time, end_time, 'ISO_MSI_A_EMU,ISO_MSI_B_EMU')
    INFO:root:Downloading isotropic_MSI_emulators_correction_xap_S2A.pkl
    99 %
    INFO:root:Downloaded isotropic_MSI_emulators_correction_xap_S2A.pkl
    INFO:root:Downloading isotropic_MSI_emulators_correction_xbp_S2A.pkl
    99 %
    INFO:root:Downloaded isotropic_MSI_emulators_correction_xbp_S2A.pkl
    INFO:root:Downloading isotropic_MSI_emulators_correction_xcp_S2A.pkl
    100 %
    INFO:root:Downloaded isotropic_MSI_emulators_correction_xcp_S2A.pkl
    INFO:root:Downloading isotropic_MSI_emulators_optimization_xap_S2A.pkl
    100 %
    INFO:root:Downloaded isotropic_MSI_emulators_optimization_xap_S2A.pkl
    INFO:root:Downloading isotropic_MSI_emulators_optimization_xbp_S2A.pkl
    99 %
    INFO:root:Downloaded isotropic_MSI_emulators_optimization_xbp_S2A.pkl
    INFO:root:Downloading isotropic_MSI_emulators_optimization_xcp_S2A.pkl
    99 %
    INFO:root:Downloaded isotropic_MSI_emulators_optimization_xcp_S2A.pkl
    INFO:root:Downloading isotropic_MSI_emulators_correction_xap_S2B.pkl
    100 %
    INFO:root:Downloaded isotropic_MSI_emulators_correction_xap_S2B.pkl
    INFO:root:Downloading isotropic_MSI_emulators_correction_xbp_S2B.pkl
    100 %
    INFO:root:Downloaded isotropic_MSI_emulators_correction_xbp_S2B.pkl
    INFO:root:Downloading isotropic_MSI_emulators_correction_xcp_S2B.pkl
    100 %
    INFO:root:Downloaded isotropic_MSI_emulators_correction_xcp_S2B.pkl
    INFO:root:Downloading isotropic_MSI_emulators_optimization_xap_S2B.pkl
    99 %
    INFO:root:Downloaded isotropic_MSI_emulators_optimization_xap_S2B.pkl
    INFO:root:Downloading isotropic_MSI_emulators_optimization_xbp_S2B.pkl
    99 %
    INFO:root:Downloaded isotropic_MSI_emulators_optimization_xbp_S2B.pkl
    INFO:root:Downloading isotropic_MSI_emulators_optimization_xcp_S2B.pkl
    100 %
    INFO:root:Downloaded isotropic_MSI_emulators_optimization_xcp_S2B.pkl
    ['C:/Users/user/.multiply/data/emus/ISO_MSI_A_EMU/isotropic_MSI_emulators_correction_xap_S2A.pkl',
     'C:/Users/user/.multiply/data/emus/ISO_MSI_A_EMU/isotropic_MSI_emulators_correction_xbp_S2A.pkl',
     'C:/Users/user/.multiply/data/emus/ISO_MSI_A_EMU/isotropic_MSI_emulators_correction_xcp_S2A.pkl',
     'C:/Users/user/.multiply/data/emus/ISO_MSI_A_EMU/isotropic_MSI_emulators_optimization_xap_S2A.pkl',
     'C:/Users/user/.multiply/data/emus/ISO_MSI_A_EMU/isotropic_MSI_emulators_optimization_xbp_S2A.pkl',
     'C:/Users/user/.multiply/data/emus/ISO_MSI_A_EMU/isotropic_MSI_emulators_optimization_xcp_S2A.pkl',
     'C:/Users/user/.multiply/data/emus/ISO_MSI_B_EMU/isotropic_MSI_emulators_correction_xap_S2B.pkl',
     'C:/Users/user/.multiply/data/emus/ISO_MSI_B_EMU/isotropic_MSI_emulators_correction_xbp_S2B.pkl',
     'C:/Users/user/.multiply/data/emus/ISO_MSI_B_EMU/isotropic_MSI_emulators_correction_xcp_S2B.pkl',
     'C:/Users/user/.multiply/data/emus/ISO_MSI_B_EMU/isotropic_MSI_emulators_optimization_xap_S2B.pkl',
     'C:/Users/user/.multiply/data/emus/ISO_MSI_B_EMU/isotropic_MSI_emulators_optimization_xbp_S2B.pkl',
     'C:/Users/user/.multiply/data/emus/ISO_MSI_B_EMU/isotropic_MSI_emulators_optimization_xcp_S2B.pkl']

As the data was not locally available, it was downloaded.
Executing the same command again would simply give us the list of urls which is here at the end.

When you have already queried for data, you may use that query result to actually retrieve the data:

.. code-block:: console
    >>> s2_data_infos = data_access_component.query(BARRAX_ROI, start_time, end_time, 'AWS_S2_L1C')
    >>> data_access_component.get_data_urls_from_data_set_meta_infos(s2_data_infos)
    [Data Set:
      Id: 30/S/WJ/2017/1/16/0,
      Type: AWS_S2_L1C,
      Start Time: 2017-01-16T10:53:55,
      End Time: 2017-01-16T10:53:55,
      Coverage: POLYGON((-3.00023345437724 39.7502679265611,-3.00023019602957 38.7608644567253,-1.73659678081167 38.7540360477761,-1.71871965133358 39.7431961916792,-3.00023345437724 39.7502679265611))
    , Data Set:
      Id: 30/S/WJ/2017/1/19/0,
      Type: AWS_S2_L1C,
      Start Time: 2017-01-19T11:05:33,
      End Time: 2017-01-19T11:05:33,
      Coverage: POLYGON((-3.00023345437724 39.7502679265611,-3.00023019602957 38.7608644567253,-1.73659678081167 38.7540360477761,-1.71871965133358 39.7431961916792,-3.00023345437724 39.7502679265611))
    ]

Putting Data
============

Assume you have data available that you want to add to a store.
You can add it using the ``put``-command.
Just hand in the path to the file and the id of the store you want to add it to.

.. code-block:: console
    >>> dac.put('E:\\Data\\S2L2\\AWS_S2_L2\\2017\\01\\19\\', 'S2L2')
    INFO:root:Added data to data store S2L2.

You could have omitted the id in this case, as there is only one writable store for S2L2 data in the AWS format.
If no store is found, the data is not added.
If multiple stores are found, the data is added to an arbitrarily picked store.
Note that in any case the data is copied to the data store's file system.
After the putting process, you will be able to find the data in a ``query``:

.. code-block:: console
    >>> dac.query(ROI, start_time, end_time, 'AWS_S2_L2')
    [Data Set:
      Id: /AWS_S2_L2/2017/01/19/,
      Type: AWS_S2_L2,
      Start Time: 2017-01-19 11:05:33,
      End Time: 2017-01-19 11:05:33,
      Coverage: POLYGON((-3.000233454377241 39.75026792656397, -1.7187196513335372 39.74319619168243, -1.7365967808116474 38.754036047778804, -3.0002301960295696 38.760864456727795, -3.000233454377241 39.75026792656397))
    ]
