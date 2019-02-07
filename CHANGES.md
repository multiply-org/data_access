## Version 0.4.3

### Improvements and new Features
- Improved handling of vrt files
- Improved performance of remote MODIS lookups
- added check  
- updated dependencies to be consistent

## Version 0.4.2

### Fixes
- Temporary Directories are created if they do not exist already

## Version 0.4.1

### Improvements and new Features
- Added documentation including installation manual
- Default stores are set up on initial start
- Json Meta Info Provider receives supported data types as parameter
- added can_put functionality
- It is possible to explicitly state which data types a Local Data Stores shall be able to provide
- Start and End Time are not necessarily part of a query
- Added environment.yml
- Added support for mcd15a2
- Fixed determination of MODIS Tile Coverages

## Version 0.4

### Improvements and new Features
- Added functionality to create local VRT from remote ASTER files
- Introduced General Access to Remote EO Data
- Introduced LpDaacFileSystem and -MetaInfoProvider to query for MODIS data 
- Introduced LocallyWrappedDataStores
- Data can be put
- Introduced functionality to access S2 Data from AWS
- Enabled updating of data stores
- Can scan local file systems
- Data Stores can tell whether they provide a certain type of data
- MetaInfoProviders and thereby Data Stores can be updated


## Version 0.3

Version for presentation (local data access)

### Features
* Basic Framework for setting up Data Stores and performing Queries
* Implementations of LocalFileSystem and JsonMetaInfoProvider
