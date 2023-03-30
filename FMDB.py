# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 10:11:53 2021

@author: jackr
"""
import datetime
import io
import logging
from lxml import etree
import numpy as np
import os.path as osp
import os
import pandas as pd
import plotting as fmplt
import sys
try:
    from .utils import _GACCS
    from .utils import *
except:
    from utils import _GACCS
    from utils import *

pd.set_option('display.max_colwidth', None)

class FMDBError(Exception):
    pass

class FMDB(object):
    
    # Constructor for FMDB class
    #
    # @ Param folder_path - path where this script is located
    #
    def __init__(self, folder_path=osp.join(osp.abspath(os.getcwd()),"FMDB")):
        self.folder_path = folder_path
        self.exists_here()
        self.stations_path = osp.join(self.folder_path,"stationID.pkl")
        self.last_update_path = osp.join(self.folder_path,"last_update.txt")
        self.new_stations = False
        if osp.exists(self.last_update_path):
            self.last_updated = open(self.last_update_path).read()
            self.updated_dt = datetime.datetime.strptime(self.last_updated,'%Y-%m-%d %H:%M:%S')
            logging.info('FMDB - Last updated at {}'.format(self.last_updated))
        else:
            self.last_updated = ''
            self.updated_dt = None
        self.init_params()
    
    # Checks if FMDB directory exists. If not, it is created
    #    
    def exists_here(self):
        if osp.exists(self.folder_path):
            logging.info("FMDB - Existent DB path {}".format(self.folder_path))
        else:
            os.makedirs(self.folder_path)
    
    # Initialize parameters for get_data
    #   
    def init_params(self):
        self.params = {'startYear': int(datetime.datetime.now().year), 'endYear': int(datetime.datetime.now().year), 
                    'stationID': None, 'fuelType': None, 'fuelVariation': None, 'fuelCombo': [],
                    'latitude1': None, 'latitude2': None, 'longitude1': None, 'longitude2': None, 'state': None, 
                    'makeFile': False}
    
    # Build site_number to refer to sites in the data
    # @ Param df - DataFrame with stations' information
    #   
    def build_stations(self, df):
        if osp.exists(self.stations_path):
            df_local = self.sites()
            lenLocal = len(df_local)
            df_new = df[~np.logical_and(df['site'].isin(df_local['site']), 
                            np.logical_and(df['gacc'].isin(df_local['gacc']),
                                np.logical_and(df['state'].isin(df_local['state']),
                                    np.logical_and(df['grup'].isin(df_local['grup']),
                                        np.logical_and(df['lat'].isin(df_local['lat']),
                                                        df['lng'].isin(df_local['lng']))))))]
            lenNew = len(df_new)
            df_new.index = range(lenLocal,lenLocal+lenNew)
            df_new.index.name = 'site_number'
            df_local = df_local.append(df_new)
            if lenNew:
                self.new_stations = True
                logging.info('New {} stations added'.format(lenNew))
        else:
            logging.info('New {} stations added'.format(len(df)))
            df_local = df
            df_local.index = range(len(df_local))
            df_local.index.name = 'site_number'
        df_local.to_pickle(self.stations_path)
        df_local.to_csv(osp.join(self.folder_path,"stationID.csv"))
    
    # Updates the site_number from the list of existent sites
    #
    # @ Param gacc - gacc that you want fuel mositure from
    #
    def update_gacc_stations(self, gacc="NOCC"):
        # Get site list from NFMD for a specific state
        url = gaccURL(gacc)
        # read page
        page = getURL(url)
        # Find the total number of stations 
        tree = etree.fromstring(page.content)
        stations = []
        for site in tree:
            attribs = dict(site.attrib)
            attribs.update({'url': siteURL(**attribs)})
            stations.append(attribs)

        df = pd.DataFrame(stations)
        if len(df):
            df.lat = df.lat.astype(float)
            df.lng = df.lng.astype(float)
            self.build_stations(df)
        else:
            logging.warning('No stations to be built')

    # Updates the site_number from the list of existent sites
    #
    # @ Param state - state that you want fuel mositure from
    #
    def update_state_stations(self, state="CA"):
        # Get site list from NFMD for a specific state
        url = stateURL(state)
        # read page
        page = getURL(url)
        # Find the total number of stations 
        tree = etree.fromstring(page.content)
        stations = []
        for site in tree:
            attribs = dict(site.attrib)
            attribs.update({'url': siteURL(**attribs)})
            stations.append(attribs)

        df = pd.DataFrame(stations)
        if len(df):
            df.lat = df.lat.astype(float)
            df.lng = df.lng.astype(float)
            self.build_stations(df) 
        else:
            logging.warning('No stations to be built')

    # Creates/updates all NFMDB database (stations and data)
    #
    def update_all(self):
        for gacc in _GACCS:
            self.update_gacc_stations(gacc=gacc)
        self.update_data(startYear=1800)

    # Creates/updates the datafiles in the FMDB folder
    #
    # @ Param startYear - start year you would like data for
    # @ Param endYear - end year you would like data for
    #       Each year is made into a seperate PKL file
    #       For example: 2000.pkl, 2001.pkl, etc.
    #
    def update_data(self, startYear=2000, endYear=int(datetime.datetime.now().year)):
        if osp.exists(self.stations_path):
            if self.updated_dt is None or (datetime.datetime.now()-self.updated_dt).days > 1 or self.new_stations:
                stationIds = self.sites()
                nStations = len(stationIds)
                # Loop to download data and get the needed data
                for ns,(sid,url) in enumerate(zip(stationIds.index,stationIds['url'])):
                    logging.info('Updating station {}/{}'.format(ns+1,nStations))
                    logging.debug('{}'.format(url))
                    # downloads site data file
                    page = getURL(url)
                    # Read downloaded file for identifying the station
                    # For example: https://www.wfas.net/nfmd/public/download_site_data.php?site=12%20Rd%20@%2054%20Rd&gacc=NOCC&state=CA&grup=Tahoe%20NF
                    # I.E. from above: site = 12 Rd @ 54, gacc = NOCC, etc.
                    try:
                        df = pd.read_csv(io.StringIO(page.content.decode()),sep="\t")
                    except:
                        logging.warning('url {} has not data'.format(url))
                        continue
                    df.columns = [c.lower() for c in df.columns]
                    df = df[["date", "state", "fuel", "percent"]]
                    df.loc[:,'date'] = pd.to_datetime(df.loc[:,'date'])
                    df.loc[:,'year'] = df.date.dt.year.astype(int)
                    # Loop to every year in the data
                    for year,group in df.groupby('year'):
                        if int(year) >= startYear and int(year) <= endYear: 
                            year_path = osp.join(self.folder_path,"{}.pkl".format(year))
                            group['site_number'] = sid
                            split = split_fuel(group)
                            group = pd.concat((group, split),axis=1)
                            if osp.exists(year_path):
                                df_local = pd.read_pickle(year_path)
                                group = pd.concat([df_local, group]).drop_duplicates(subset=['date', 'state', 'fuel','percent','site_number'],keep="first")
                            group.reset_index(drop=True).to_pickle(year_path)
                self.updated_dt = datetime.datetime.now()
                self.last_updated = self.updated_dt.strftime("%Y-%m-%d %H:%M:%S")
                with open(self.last_update_path,'w') as f:
                    f.write(self.last_updated)
        else:
            logging.error('Before updating the data, update the stations using update_gacc_stations or update_state_stations')

    # Filter stations ID from stationID and coordinates
    #
    # @ Param stationID - list with station IDs or an station ID
    # @ Param state - single state indicated by two letter representation (e.g., CA, TX, NY, etc.)
    # @ Param lat1,lat2,lon1,lon2 - geographical coordinates in WGS84 degrees
    #
    def filter_stations(self, stationID, state, lat1, lat2, lon1, lon2):
        stationDataFrame = self.sites()
        if state is not None:
            try:
                if isinstance(state,str):
                    stationDataFrame = stationDataFrame.loc[stationDataFrame.state.str.lower() == state.lower()]
                else:
                    stationDataFrame = stationDataFrame.loc[stationDataFrame.state.isin(state)]
            except:
                pass
        if stationID is None:
            subset = stationDataFrame
        else:
            try:
                subset = stationDataFrame[stationDataFrame.site.index == stationID]
            except:
                subset = stationDataFrame
        if not len(subset):
            subset = stationDataFrame
        if any([lat1 is None, lat2 is None, lon1 is None, lon2 is None]):
            try: 
                return list([subset.name])
            except:
                return list(subset.index)
        else:
            subset = subset[np.logical_and(lat1 <= subset.lat, 
                                np.logical_and(lat2 >= subset.lat, 
                                    np.logical_and(lon1 <= subset.lng, 
                                                    lon2 >= subset.lng)))]
            try: 
                return list([subset.name])
            except:
                return list(subset.index)

    # Get data using params fields
    #
    def get_data(self):
        startYear = self.params.get('startYear', int(datetime.datetime.now().year)) 
        endYear = self.params.get('endYear', int(datetime.datetime.now().year))
        stationID = self.params.get('stationID')
        fuelType = self.params.get('fuelType')
        fuelVariation = self.params.get('fuelVariation') 
        fuelCombo = self.params.get('fuelCombo', []) 
        latitude1 = self.params.get('latitude1')
        latitude2 = self.params.get('latitude2')
        longitude1 = self.params.get('longitude1')
        longitude2 = self.params.get('longitude2')
        state = self.params.get('state')
        makeFile = self.params.get('makeFile', False)
        
        lat1,lat2,lon1,lon2 = check_coords(latitude1, latitude2, longitude1, longitude2)
        stationIDs = self.filter_stations(stationID,state,lat1,lat2,lon1,lon2)
        logging.debug('stationIDs={}'.format(stationIDs))
        if fuelType != None:
            fuelTypes = [str(ft).lower() for ft in fuelType] if isinstance(fuelType,(list,tuple,np.ndarray)) else [str(fuelType).lower()]
            logging.debug('fuelTypes={}'.format(fuelTypes))
        if fuelVariation != None:
            fuelVariations = [fv.lower() for fv in fuelVariation] if isinstance(fuelVariation,(list,tuple,np.ndarray)) else [str(fuelVariation).lower()]
            logging.debug('fuelVariations={}'.format(fuelVariations))
        data = pd.DataFrame([])
        if osp.exists(self.stations_path):
            while startYear <= endYear:
                logging.info("Getting data from {}".format(startYear))
                year_path = osp.join(self.folder_path,"{}.pkl".format(startYear))
                if osp.exists(year_path):
                    try:
                        yearDataFrame = pd.read_pickle(year_path)
                    except Exception as e:
                        logging.warning('error when reading file {} with exception {}'.format(year_path, e))
                        continue
                    fltr = yearDataFrame.site_number.isin(stationIDs)
                    if len(fuelCombo):
                        fltr_combos = []
                        for Type,Variation in fuelCombo:
                            fltr_combos.append(np.logical_and(yearDataFrame.fuel_type.str.lower() == Type.lower(),
                                                                yearDataFrame.fuel_variation.str.lower() == Variation.lower()))
                        fltr = np.logical_and(fltr, np.logical_or(*fltr_combos)) 
                    else:
                        if fuelType != None:
                            fltr = np.logical_and(fltr,yearDataFrame.fuel_type.str.lower().isin(fuelTypes))
                        if fuelVariation != None:
                            fltr = np.logical_and(fltr,yearDataFrame.fuel_variation.str.lower().str.contains('|'.join(fuelVariations),na=False))
                    data = data.append(yearDataFrame[fltr])
                # If data file does not exist (i.e. you have data files from 2000-2021 but you call 1999)
                else:
                    logging.warning("{} does not exist. Try updating the DB before getting data using update_all or update_data.".format(year_path))
                startYear += 1
            logging.info('{} records found'.format(len(data)))
            if len(data):
                data = data[['site_number','date', 'state','fuel_type','fuel_variation','percent']]
                data = data.sort_values(by=list(data.columns))
            if makeFile:
                sites = self.sites()
                data = data.join(sites[["site","lat","lng"]], on="site_number")
                # use currentDateTime.csv (to seconds 20200309_0209+seconds.csv)
                out_path = osp.join(self.folder_path,'data_{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}.csv'.format(*datetime.datetime.now().timetuple()))
                data.to_csv(out_path, index=False, date_format='%Y-%m-%d')
        else:   
            logging.error("{} does not exist. Try updating the stations before getting data using update_gacc_stations or update_state_stations.".format(self.stations_path))
        return data.reset_index(drop=True)

    # Return DataFrame with the local stations information 
    #
    def sites(self):
        if osp.exists(self.stations_path):
            return pd.read_pickle(self.stations_path)
        else:
            return None

    # Basic line plot for each site/fuelType/fuelVariation
    #
    # @ param dataFrame - pandas dataframe with the data to plot from get_data
    # @ param outliers - boolean to include or not the outliers (points outside of [0,400] range)
    #
    def plot_lines(self,dataFrame,outliers=False):
        if dataFrame is None:
            dataFrame = self.get_data()
        if not outliers:
            dataFrame = filter_outliers(dataFrame)
        fmplt.plot_lines(dataFrame)

    # Standard deviation plot for each fuelType/fuelVariation (averaging all sites)
    #
    # @ param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
    # @ param outliers - boolean to include or not the outliers (points outside of [0,400] range)
    #
    def plot_lines_mean(self,dataFrame,outliers=False):
        if dataFrame is None:
            dataFrame = self.get_data()
        if not outliers:
            dataFrame = filter_outliers(dataFrame)
        fmplt.plot_lines_mean(dataFrame)
        
    # Bar plot that shows mean and standard devaition values for all the data each year unless monthly paramter is set to True.
    #
    # @ param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
    # @ param monthly - boolean to change from yearly to monthly bars
    # @ param outliers - boolean to include or not the outliers (points outside of [0,400] range)
    #
    def plot_bars_mean(self,dataFrame,monthly=False,outliers=False):
        if dataFrame is None:
            dataFrame = self.get_data()
        if not outliers:
            dataFrame = filter_outliers(dataFrame)
        fmplt.plot_bars_mean(dataFrame,monthly)

    # Bar plot that shows the number of observations over each year found in the dataFrame
    #
    # @ param dataFrame - pandas dataframe with the data to plot from get_data
    # @ param outliers - boolean to include or not the outliers (points outside of [0,400] range)
    #
    def plot_yearly_obs(self,dataFrame=None,outliers=False):
        if dataFrame is None:
            dataFrame = self.get_data()
        if not outliers:
            dataFrame = filter_outliers(dataFrame)
        fmplt.plot_yearly_obs(dataFrame)
        
    # Bar plot that shows the fuel types and number of observations of each fuel type found in the dataFrame
    #
    # @ param dataFrame - pandas dataframe with the data to plot from get_data
    # @ param outliers - boolean to include or not the outliers (points outside of [0,400] range)
    #
    def plot_fuel_types(self,dataFrame,outliers=False):
        if dataFrame is None:
            dataFrame = self.get_data()
        if not outliers:
            dataFrame = filter_outliers(dataFrame)
        fmplt.plot_fuel_types(dataFrame)

if __name__ == '__main__':
    import time
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    if len(sys.argv) == 1:
        fmdb = FMDB()
    elif len(sys.argv) == 2:
        fmdb = FMDB(sys.argv[1])
    else:
        print('Usage: {} [path_to_FMDB]'.format(sys.argv[0])) 
        sys.exit(1)
    st = time.time()
    fmdb.update_all()
    et = time.time()
    logging.info('Elapsed time: {}s'.format(et-st))
