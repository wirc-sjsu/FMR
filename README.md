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

### Create/Update the list of stations to consider (from State or GACC)

Note: Once you have a stationID list from one of the ways listed below, that stationID list is permanent unless you delete it. So, if you create a stationID list for all the sites in California and then call one of the create/update functions (seen below) for a different state/gacc, those new sites will be added to the existing stationID list.

There are multiple ways to create/update the stationID list. 

#### By State
To update the stationID list by a given state, use update_state_stations function. By changing the state argument, you change which state you are grabbing all of the stations from. By default this function will grab the site data for California, so these two calls update the same stations:
```python
db.update_state_stations(state="CA")
db.update_state_stations() 
```
Alternatively, you can use the function as seen below if you want a different state.
```python
db.update_state_stations("AZ")
```
#### By GACC
You can also update the stationID list via a GACC. By changing the gacc argument, you change which GACC you are grabbing all of the stations from. By default this function will grab the site data for the NOCC GACC, so these two calls update the same stations:
```python
db.update_gacc_stations(gacc="NOCC")
db.update_gacc_stations()
```
Alternatively you can use the function as seen below.
```python
db.update_gacc_stations("EACC")
```
#### All US stations
Lastly, you can update all the stations in the United States by the function below.
```python
db.update_all()
```

### Create/Update local fuel mositure database

Based on the stationID list that you created above, those sites will be grabbed from the NFMD
and will be put onto your local database. 
By default, this function will grab data from 2000 - Present. You can change this via the arguments.
```python
db.update_data()
```
When giving a specified year range that you want:
```python
db.update_data(1990,2010)
```
or 
```python
db.update_data(startYear=1990,endYear=2010)
 ```
Where 1990 - 2010 is the range of years you want to save data from into your local database.

Note: for each year you get data from, a respective pickle file will be created to hold all the
      data from that year (i.e. 1990.pkl, 1991.pkl,..., 2001.pkl, etc).


### Query data into local fuel moisture database

The user can query fuel moisture data from the local database using the set of parameters:
* **startYear**: Integer number of the start year considering the data from. Default: present year. Example: 2000.
* **endYear**: Integer number of the end year considering the data to. Default: present year. Example: 2020.
* **stationID**: Integer number of list of integer numbers representing the site_number associated to each station in the local database. Example: [0,20]. To see the current local stations' information you can do:
```python
db.sites()
```
* **fuelType**: String or list of strings representing the fuel type that the user wants to specify (case insensitive). Default: None, which considers all the fuel types. Example: ['Sage','Sagebrush'].
* **fuelVariation**: String or list of strings representing the fuel variation that the user wants to specify (case insensitive). Default: None, which considers all the fuel types. Example: ['Black','California'].
* **fuelCombo**: List of tuples with a specific combination between fuel type and fuel variation. Default: [], which does not specify any specific fuel combination. Example: [('Sage','Black'),('Sagebrsh','California')]. This is specially useful in the context of the example provided where defining fuelType as ['Sage','Sagebrush'] and fuelVariation as ['Black','California'] return as combinations Sage - Black, Sagebrush - Black, and Sagebrush - California. But maybe we are only interested on Sage - Black and Sagebrush - California. The only way to have that is to select this two specific combinations using fuelCombo.
* **latitude1**: Float number of the minimum geographical latitude coordinate in WGS84 degrees. Default: None, which did not filter by coordinates. Example: 36.93.
* **latitude2**: Float number of the maximum geographical latitude coordinate in WGS84 degrees. Default: None, which did not filter by coordinates. Example: 40.75.
* **longitude1**: Float number of the minimum geographical longitude coordinate in WGS84 degrees. Default: None, which did not filter by coordinates. Example: -122.43.
* **longitude2**: Float number of the maximum geographical longitude coordinate in WGS84 degrees. Default: None, which did not filter by coordinates. Example: -118.81.
* **makeFile**: Boolean asserting if create or not a resulting CSV file with the data. Default: False. Example: True. The file is generated in the database path with name depending on time of creation using: data_{year}{month}{day}\_{hours}{minutes}{seconds}.

All the default parameters are set when the class is initialized as:
```python
db.params = {'startYear': int(datetime.datetime.now().year), 'endYear': int(datetime.datetime.now().year), 
                    'stationID': None, 'fuelType': None, 'fuelVariation': None, 
                    'latitude1': None, 'latitude2': None, 'longitude1': None, 'longitude2': None, 'makeFile': False}
````
 To change these parameters, you can do this:
```python
db.params['startYear'] = 2000      # This will start the data from 2000
db.params['stationID'] = 20        # This will specify data only from station with stationID 20
db.params['fuelType'] = 'Chamise'  # This will specify only fuel type 'Chamise'
db.params['makeFile'] = True       # This will save the data you get into a CSV file
```
Once you have the parameters you want, you can call the get_data function.
```python
allFMDB = db.get_data()
```
 If you have the makeFile parameter as True and just want a CSV file with the data:
```python
 db.get_data()
```
### Plot fuel moisture data

There are a couple different plots you can create. All the plots have the flag outliers, which is set to False by default. This flag prevents the plot functions to plot fuel moisture content values larger than 400 and smaller than 0. So, it gets rid of the outliers. If the user wants to see the outliers, then this flag can be set to True.

Basic line plot for each site/fuelType/fuelVariation
```python
db.plot_lines(allFMDB)
```
By default the plot_lines function will automatically call the get_data function if not dataframe is provided
in the argument.
```python
db.plot_lines()
```

Standard deviation plot for each fuelType/fuelVariation. 
Mean line is plotted for each month along with its standard deviation for each fuelType/fuelVariation.
i.e. lines you will have : [Chamise - Old Growth, Chamise - New Growth, Chamise - None].
```python
db.plot_lines_mean(allFMDB)
```
By default the plot_lines_mean function will automatically call the get_data function if not dataframe is provided
in the argument.
```python
db.plot_lines_mean()
```

Bar plot that shows mean and standard deviation values for all the data each year unless monthly parameter 
is set to True.
```python
db.plot_bars_mean(allFMDB, monthly=False)
db.plot_bars_mean(allFMDB, monthly=True)
db.plot_bars_mean(allFMDB, True)
```
By default the plot_bars_mean function will automatically call the get_data function if not dataframe is provided
in the argument.
```python
db.plot_bars_mean()
```

## Authors

* jdrucker1
* Fergui
