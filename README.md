<img alt="MULTIPLY" align="right" src="https://raw.githubusercontent.com/multiply-org/multiply-core/master/doc/source/_static/logo/Multiply_multicolour.png" />

[![Build Status](https://travis-ci.org/multiply-org/data-access.svg?branch=master)](https://travis-ci.org/multiply-org/data-access)
                
# data-access

This is the repository containing the Data Access functionality for the MULTIPLY platform.
In particular it contains code to select data from pre-defined data stores that fulfils pre-defined user queries (on a 
region of interest, a temporal region, and data types). 
Also, it enables users to register their own data stores or extend the data access component by providing 
implementations as plug-ins.

## Contents

* `multiply_data_access/` - main package
* `recipe/` - contains the conda recipe to build and deploy the package for Anaconda and Miniconda distributions
* `test/` - test package
* `setup.py` - main build script, to be run with Python 3.6

## How to install

The first step is to clone the latest code and step into the check out directory: 

    $ git clone https://github.com/multiply-org/data-access.git
    $ cd data-access
    
The MULTIPLY Data Access has been developed against Python 3.6. 
It cannot be guaranteed to work with previous Python versions.

The MULTIPLY Data Access can be run from sources directly, once the following module requirements are resolved:

* `shapely`
* `pyyaml`

To install the MULTIPLY Data Access into an existing Python environment just for the current user, use

    $ python setup.py install --user
    
To install the MULTIPLY Data Access for development and for the current user, use

    $ python setup.py develop --user

## How to use

MULTIPLY Data Access is available as Python Package. 
To import it into your python application, use

    $ import multiply_data_access

## License
