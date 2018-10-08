============
Installation
============

Requirements
============
The MULTIPLY Data Access Component has been developed against Python 3.6.
It cannot be guaranteed to work with previous Python versions, so we suggest using 3.6 or higher.
The DAC will attempt downloading data from remote sources.
We therefore recommend to run it on a computer which has a lot of storage (solid state disks are recommended)
and also a good internet connection.

Installing from source
======================

To install the Data Access Component, you need to clone the latest version of the MULTIPLY code from GitHub and
step into the checked out directory:

- git clone https://github.com/multiply-org/data-access.git
- cd data-access

To install the MULTIPLY Data Access into an existing Python environment just for the current user, use:

- python setup.py install --user

To install the MULTIPLY Data Access for development and for the current user, use

- python setup.py develop --user

.. describing how the module can be installed (including possibly how the documentation can be rebuild).
(one can argue that maybe to put this higher up in the structure, but considering that this is only done once,
I thought it better to put it lower in the documentation).