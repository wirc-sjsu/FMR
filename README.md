# Fuel Mositure Content Database

The goal of this project is to be able to neatly organize [the NFMD data](http://www.wfas.net/nfmd/public/index.php) into a local database and be able to query and plot easily the exact data requiered by the user from the database.

## Getting Started

### Dependencies

Python 3 and package modules
* matplotlib 
* pandas 
* requests 
* lxml

### Installing using Anaconda

* Clone Github repository
* Install Anaconda
* Create environment for running the code:

      $ conda create -n fmcdb python=3 matplotlib pandas requests lxml

* Activate the environment

      $ conda activate fmcd

### Create your own Fuel Moisture Database

* Import database class doing:
```python
from FMDB import FMDB
```
* Create an FMDB object doing:
```python
db = FMDB()
```

Note: If anything specified, the default is going to be a folder called `FMDB` in the current path tree. One can specify a path where the DB should be created. For instance:
```python
db = FMDB('FMDB_CA')
```

### Create/Update the list of stations to consider (from state or GACC)
### Create/Update local fuel mositure database
### Query data into local fuel moisture database
### Plot fuel moisture data

## Authors

* jDrucker1
* Fergui
