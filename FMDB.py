# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 10:11:53 2021

@author: jackr
"""
import datetime
import matplotlib.dates as md
import matplotlib.pyplot as plt
import numpy as np
import os.path as osp
import os
import pandas as pd
import logging
import io
from collections.abc import Iterator
from lxml import etree
from utils import *

pd.set_option('display.max_colwidth', None)

class FMDBError(Exception):
    pass

class FMDB(object):
    
    # Constructor for FMDB class
    #
    # @ Param folder_path - path where this script is located
    #
    def __init__(self, folder_path=osp.abspath(os.getcwd())):
        self.folder_path = osp.join(folder_path,"FMDB")
        self.exists_here()
        self.stations_path = osp.join(self.folder_path,"stationID.pkl")
        self.last_update_path = osp.join(self.folder_path,"last_update.txt")
        if osp.exists(self.last_update_path):
            self.last_updated = open(self.last_update_path).read()
            self.updated_dt = datetime.datetime.strptime(self.last_updated,'%Y-%m-%d %H:%M:%S')
            logging.info('FMDB - Last updated at {}'.format(self.last_updated))
        else:
            self.last_updated = ''
            self.updated_dt = None
    
    # Checks if FMDB directory exists. If not, it is created
    #    
    def exists_here(self):
        if osp.exists(self.folder_path):
            logging.info("FMDB - Existent DB path {}".format(self.folder_path))
        else:
            os.makedirs(self.folder_path)
    
    # Build site_number to refer to sites in the data
    #   
    def build_stations(self, df):
        if osp.exists(self.stations_path):
            df_local = self.sites()
            lenLocal = len(df_local)
            df_new = df[~df.isin(df_local)].dropna()
            lenNew = len(df_new)
            df_new.index = range(lenLocal,lenLocal+lenNew-1)
            df_new.index.name = 'site_number'
            df_local.append(df_new)
            df_local.to_pickle(self.stations_path)
            df_local.to_csv(osp.join(self.folder_path,"stationID.csv"))
        else:
            df_local = df
            df_local.index = range(len(df_local))
            df_local.index.name = 'site_number'
        df_local.to_pickle(self.stations_path)
        df_local.to_csv(osp.join(self.folder_path,"stationID.csv"))
    
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
        numberOfStations = len(tree)
        logging.info('{} stations found'.format(numberOfStations))
        stations = []
        for site in tree:
            attribs = dict(site.attrib)
            attribs.update({'url': siteURL(**attribs)})
            stations.append(attribs)

        df = pd.DataFrame(stations)
        df.lat = df.lat.astype(float)
        df.lng = df.lng.astype(float)
        self.build_stations(df) 

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
        numberOfStations = len(tree)
        logging.info('{} stations found'.format(numberOfStations))
        stations = []
        for site in tree:
            attribs = dict(site.attrib)
            attribs.update({'url': siteURL(**attribs)})
            stations.append(attribs)

        df = pd.DataFrame(stations)
        df.lat = df.lat.astype(float)
        df.lng = df.lng.astype(float)
        self.build_stations(df)
    
    # Creates/updates the datafiles in the FMDB folder
    #
    # @ Param state - state that you want fuel mositure from
    # @ Param startYear - start year you would like data for
    # @ Param endYear - end year you would like data for
    #       Each year is made into a seperate PKL file
    #       For example: 2000.pkl, 2001.pkl, etc.
    #
    def update_state_data(self, state="CA", startYear=2000, endYear=int(datetime.datetime.now().year)):
        if self.updated_dt is None or (datetime.datetime.now()-self.updated_dt).days > 1:
            self.update_state_stations(state)
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
                df.columns = [c.lower() for c in df.columns]
                df = df[["date", "fuel", "percent"]]
                df['date'] = pd.to_datetime(df.date)
                df['year'] = df.date.dt.year.astype(int)
                # Loop to every year in the data
                for year,group in df.groupby('year'):
                    if int(year) >= startYear and int(year) <= endYear: 
                        year_path = osp.join(self.folder_path,"{}.pkl".format(year))
                        group['site_number'] = sid
                        if osp.exists(year_path):
                            df_local = pd.read_pickle(year_path)
                            group = group[(~group.isin(df_local)[['date', 'fuel', 'percent']]).any(1)]
                            if len(group):
                                split = split_fuel(group)
                                group = pd.concat((group, split),axis=1)
                                group = df_local.append(group)
                            else:
                                continue
                        else:
                            split = split_fuel(group)
                            group = pd.concat((group, split),axis=1)
                        group.reset_index(drop=True).to_pickle(year_path)
            self.updated_dt = datetime.datetime.now()
            self.last_updated = self.updated_dt.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.last_update_path,'w') as f:
                f.write(self.last_updated)

    def filter_stations(self, stationID, lat1, lat2, lon1, lon2):
        stationDataFrame = self.sites()
        if stationID is None:
            subset = stationDataFrame
        else:
            subset = stationDataFrame.iloc[stationID]
        if any([lat1 is None, lat2 is None, lon1 is None, lon2 is None]):
            return list(subset.index)
        else:
            return list(subset[np.logical_and(lat1 < subset.lat, 
                                                    np.logical_and(lat2 > subset.lat, 
                                                            np.logical_and(lon1 < subset.lng, 
                                                                            lon2 > subset.lng)))].index)

    def get_data(self, startYear=int(datetime.datetime.now().year), endYear=int(datetime.datetime.now().year), stationID=None, 
                fuelType=None, fuelVariation=None, latitude1=None, latitude2=None, longitude1=None, longitude2=None, makeFile=False):
        lat1,lat2,lon1,lon2 = check_coords(latitude1, latitude2, longitude1, longitude2)
        stationIDs = self.filter_stations(stationID,lat1,lat2,lon1,lon2)
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
                    yearDataFrame = pd.read_pickle(year_path)
                    fltr = yearDataFrame.site_number.isin(stationIDs)
                    if fuelType != None:
                        fltr = np.logical_and(fltr,yearDataFrame.fuel_type.str.lower().isin(fuelTypes))
                    if fuelVariation != None:
                        fltr = np.logical_and(fltr,yearDataFrame.fuel_variation.str.lower().isin(fuelVariations))
                    data = data.append(yearDataFrame[fltr])
                # If data file does not exist (i.e. you have data files from 2000-2021 but you call 1999)
                else:
                    logging.warning("{} does not exist. Try updating the DB before getting data using update_state_data.".format(year_path))
                startYear += 1
            logging.info('{} records found'.format(len(data)))
            if len(data):
                data = data[['site_number','date','fuel_type','fuel_variation','percent']]
                data = data.sort_values(by=list(data.columns))
            if makeFile:
                # use currentDateTime.csv (to seconds 20200309_0209+seconds.csv)
                out_path = osp.join(self.folder_path,'data_{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}.csv'.format(*datetime.datetime.now().timetuple()))
                data.to_csv(out_path, index=False, date_format='%Y-%m-%d')
        else:   
            logging.error("{} does not exist. Try updating the stations before getting data using update_state_stations.".format(self.stations_path))
        return data

    @staticmethod
    def plot_lines(dataFrame):
        dataFrame['fuel_variation'] = dataFrame['fuel_variation'].fillna('None')
        df = dataFrame.groupby(['site_number','fuel_type','fuel_variation','date'],dropna=False).mean()
        mids = df.index
        # Dropping one level from multi index (date) and find all the unique combinations of the other levels
        combos = mids.droplevel('date').unique()
        if len(combos) < 50:
            fig, ax = plt.subplots()
            legend = []
            for combo in combos:
                x = pd.to_datetime(df.loc[combo,:].index)
                y = df.loc[combo,:].values
                ax.plot(x,y,'.-')
                legend.append('{} - {} - {}'.format(*combo))
            ax.set_ylabel("Fuel Mositure (%)", fontsize = 15)
            ax.set_xlabel("Time", fontsize = 20)
            ax.tick_params(axis='both', length = 10, width = 1, labelsize=13)
            ax.xaxis.set_major_locator(md.YearLocator())
            ax.xaxis.set_minor_locator(md.MonthLocator(bymonth=[7]))
            ax.xaxis.set_major_formatter(md.DateFormatter("\n%Y"))
            ax.xaxis.set_minor_formatter(md.DateFormatter("%b"))
            plt.grid(True)
            plt.legend(legend,loc='upper left')
            plt.xticks(rotation = 45)
            plt.show()
        else:
            logging.error('Too many plots. Consider filtering data using get_data parameters.')
    
    @staticmethod
    def plot_lines_mean(dataFrame):
        dataFrame['fuel_variation'] = dataFrame['fuel_variation'].fillna('None')
        df = dataFrame.groupby(['fuel_type','fuel_variation',dataFrame.date.dt.year, dataFrame.date.dt.month]).agg(['mean','std'])
        df.index.names = ['fuel_type','fuel_variation','year','month']
        mid = df.index
        year_combos = mid.droplevel('month').unique()
        combos = year_combos.droplevel('year').unique()
        fig, ax = plt.subplots()
        legend = []
        for combo in combos:
            combo_data = df.loc[combo,'percent']
            dates = pd.to_datetime(['{:04d}-{:02d}'.format(y,m) for y,m in df.loc[combo].index.to_numpy()])
            means = combo_data.values[:,0]
            stds = combo_data.values[:,1]
            ax.plot(dates, means, '.-')
            ax.fill_between(dates, means - stds, means + stds, alpha=0.2)
            legend.append('{} - {}'.format(*combo))
        ax.set_ylabel("Fuel Mositure (%)", fontsize = 15)
        ax.set_xlabel("Time", fontsize = 20)
        ax.tick_params(axis='both', length = 10, width = 1, labelsize=13)
        ax.xaxis.set_major_locator(md.YearLocator())
        ax.xaxis.set_minor_locator(md.MonthLocator(bymonth=[7]))
        ax.xaxis.set_major_formatter(md.DateFormatter("\n%Y"))
        ax.xaxis.set_minor_formatter(md.DateFormatter("%b"))
        plt.grid(True)
        plt.legend(legend,loc='upper left')
        plt.xticks(rotation = 45)
        plt.show()
    
    @staticmethod
    def plot_bars_mean(dataFrame, monthly=False):
        dataFrame['fuel_variation'] = dataFrame['fuel_variation'].fillna('None')
        if monthly:
            df = dataFrame.groupby([dataFrame.date.dt.year,dataFrame.date.dt.month],dropna=False).agg(['mean','std'])
            df.index.names = ['year','month']
            dates = pd.to_datetime(['{:04d}-{:02d}'.format(y,m) for y,m in df.index.to_numpy()])
            width = len(dates)*.1
        else:
            df = dataFrame.groupby([dataFrame.date.dt.year],dropna=False).agg(['mean','std'])
            df.index.names = ['year']
            dates = pd.to_datetime(['{:04d}-01'.format(y) for y in df.index.to_numpy()])
            width = len(dates)*52*.2
        means = df['percent']['mean']
        stds = df['percent']['std']
        stds.iloc[stds.isna()] = 0.
        fig, ax = plt.subplots()
        plt.bar(dates,means,width=width,alpha=.5)
        plt.bar(dates,stds,width=width,alpha=.5)
        ax.set_ylabel("Fuel Mositure (%)", fontsize = 15)
        ax.set_xlabel("Time", fontsize = 20)
        ax.tick_params(axis='both', length = 10, width = 1, labelsize=13)
        ax.xaxis.set_major_locator(md.YearLocator())
        ax.xaxis.set_minor_locator(md.MonthLocator(bymonth=[7]))
        ax.xaxis.set_major_formatter(md.DateFormatter("\n%Y"))
        ax.xaxis.set_minor_formatter(md.DateFormatter("%b"))
        plt.legend(['Mean','Std'],loc='upper left')
        plt.xticks(rotation = 45)
        plt.show()

    def sites(self):
        if osp.exists(self.stations_path):
            return pd.read_pickle(self.stations_path)
        else:
            return None

if __name__ == '__main__':
    import time
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    fmdb = FMDB()
    st = time.time()
    fmdb.update_state_data(state="CA")
    et = time.time()
    logging.info('Elapsed time: {}s'.format(et-st))