# FMDB

The goal of this project is to be able to neatly organize the NFMD data into a database and be able to extract the exact data you want.

## Getting Started

### Dependencies

* python3

### Installing

* Download FMDB_class.py onto your local machine

### Executing

* Create a new python script
* import the FMDB_class.py

```
import FMDB_class
```

* Create a FMDB object. The object currently needs you to give it the directory path, but this won't be required in the next version.

```
testDB = new FMDB_class(path to current directory)
```

* Create a station ID list for the state you would like the data from. 
* Calling the udate station ID will return a url list with the download links for the data for each station
* The url list returned will be used by the update database function to get the data

```
urlList = testDB.update_Station_ID_List("CA")
```

* Create
