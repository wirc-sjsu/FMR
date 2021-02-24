# Fuel Mositure Content Database

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

* Create the database. 
* This function is also used to update the database

```
testDB.update_Data_File(urlList)
```

### Retrieving Data From the Database

* Once the database has been created, you can run the get_data function.
* The function has a large number of arguements to allow you to get the exact data you want.
* For each arguement, if you do not provide an input, it will grab everything from that category. For example, if you do not have an input for the stationID arguemnt, it will grab all of the stations. 
* The function will always return a dataframe with all the data. You can also set makeFile True to create a csv file with all of the data.

```
#get_Data(startYear=int(datetime.datetime.now().year),endYear=int(datetime.datetime.now().year),stationID=None,fuelType=None,fuelVariation=None,
#                 latitude1=None,latitude2=None,longitude1=None,longitude2=None,makeFile=False)

coords = [36.93,37.47,-122.43,-121.84]
testDataframe = testDB.get_Data(2000,2021,None,"Chamise","New",*coords,True)
```
