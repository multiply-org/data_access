.. MULTIPLY documentation master file, created by
   sphinx-quickstart on Mon Oct  8 16:00:55 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================
MULTIPLY Data Access
====================

This is the help for the MULTIPLY Data Access Component (DAC).
The DAC forms part of the MULTIPLY platform, which is a platform for the retrieval of bio-physical land parameters
(such as fAPAR or LAI) on user-defined spatial and temporal grids from heterogeneous data sources, in particular from
EO data in the microwave domain (Sentinel-1), optical high resolution domain (Sentinel-2),
and optical coarse resolution domain (Sentinel-3).
The DAC has been designed to work as part of the platform, but can also be used separately to manage and query for
data from local and remote sources.

The MULTIPLY Data Access Component serves to access all data that is required by components of the MULTIPLY platform.
It can be queried for any supported type of data for a given time range and spatial region and provide URL's to the
locally provided data.
In particular, the Data Access Component takes care of downloading data that is not yet available locally.

The Data Access Component relies on the concept of Data Stores: All data is organized in such a data store.
Such a store might provide access to locally stored data or encapsulate access to remotely stored data.
Users may register new data stores and, if they find that the provided implementations are not sufficient,
implement their own data store realizations.

This help is organized into the following sections.

.. toctree::
   :maxdepth: 1

   basic_concepts
   installation
   user_guide
   examples

:doc:`basic_concepts` explains the structure of the Data Access Component and how it works.
:doc:`installation` guides through the installation and configuration process,
:doc:`user_guide` shows how the Data Access Component can be used and extended,
and :doc:`examples` gives a few practical examples.
