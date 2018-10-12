==========
User Guide
==========

The MULTIPLY Data Access Component is accessible through its Python API.

Usage via the Python API
========================

This section gives an overview about how the Data Access Component can be used within Python.
The only component that is supposed to be used directly is the DataAccessComponent object.

.. autoclass:: multiply_data_access.data_access_component.DataAccessComponent
    :members:

.. autoclass:: multiply_data_access.data_access.DataSetMetaInfo
    :members:


.. How can it be used?
..  Use it from Python (currently only option):
..	 show_stores
..	 query
..	 put
..	 get_provided_data_types
..	 get_data_urls
..	 get_data_urls_from_data_set_meta_infos
..	 read_data_stores
..	 create_local_data_store

Extending the Data Access Component
===================================

.. Extend it
..  Create new File System
..  Create new Meta Info Provider
..  Add new Data Type

.. with deeper explanation of all the background and contents (the class/method-autodocumentation?)