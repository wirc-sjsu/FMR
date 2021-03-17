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

Note: Once you have a stationID list from one of the ways listed below, that stationID list is permanant unless you delete it. So, if you create a stationID list for all the sites in California and then call one of the create/update functions (seen below) for a different  state/gacc, those new sites will be added to the existing stationID list.

There are multiple ways to create/update the stationID list. 

To update the stationID list by a given state, use the function below.
 By changing the state argument, you change which state you are grabbing
 all of the stations from.
'''python
db.update_state_stations(state="CA")
'''
 By default this function will grab the site data for California, so you can also
 write the function above as:
 '''python 
 db.update_state_stations()   
 '''
 Alternatively you can use the function as seen below if you want a different state.
 '''python
 db.update_state_stations("AZ")
 '''
-------------------------------
 Or you can update the stationID list via a GACC.
'''python
 db.update_gacc_stations(gacc="NOCC")
'''
 By default this function will grab the site data for the NOCC GACC, so you can also
 write the function above as:
 '''python
 db.update_gacc_stations()
 '''
 Alternatively you can use the function as seen below.
 '''python
 db.update_gacc_stations("EACC")
 '''
### Create/Update local fuel mositure database
### Query data into local fuel moisture database
### Plot fuel moisture data

## Authors

* jDrucker1
* Fergui
