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
from lxml import etree
from utils import *

pd.set_option('display.max_colwidth', None)

class FMDB(object):
    
    # Constructor for FMDB class
    #
    # @ Param folder_path - path where this script is located
    #
    def __init__(self, folder_path=osp.abspath(os.getcwd())):
        self.folder_path = osp.join(folder_path,"FMDB")
        self.exists_here()
        self.station_path = osp.join(self.folder_path,"stationID.pkl")
    

    # Checks if FMDB directory exists. If not, it is created
    #     
    def exists_here(self):
        if osp.exists(self.folder_path):
            logging.info("DB Folder Already Exists")
        else:
            os.makedirs(self.folder_path)
    
    
    # Put this outside class ############################################################456456456456456464564
    #
    # Finds endpoint of a string given a seperator
    #
    # @ Param stringData - general station data in string format
    # @ Param startOfVariable - index of where a particular variable starts in stringData
    # @ Param seperator - value you want to loop until you find your desired end point
    #
    # @ Return count - index value where the seperator is located
    #
    # Example
    # someString = "KSJC 10-29-20"
    # variableStart = 5
    # seperator = '-'
    # monthEnd = self.get_Index(someString,variableStart,seperator)
    # monthEnd would be equal to 7
    #
    @staticmethod 
    def get_Index(stringData,startOfVariable,seperator):
        count = startOfVariable
        
        while stringData[count] != str(seperator):
            count += 1
        return count
    
    
    @staticmethod
    def find_SiteName(siteDataFrame,siteNumber):
        found = False
        count = 0
        siteName = ""
        while found == False:
            if siteDataFrame.Site_Number[count] == siteNumber:
                siteName = siteDataFrame.Site[count]
                found = True
            count+=1
        return siteName
    
    
    def build_StID(self,tempUrlList,siteList,latList,lonList,gaccList,stateList,grupList,create=True):
        
        urlList = []
        if create == False:
            foundList = [False] * len(tempUrlList)
            stationDataFrame = pd.read_pickle(self.station_path) # make this change wherever FMDB/stationID.pkl
            for i in range(len(stationDataFrame.Site)):
                for j in range(len(tempUrlList)):
                    if stationDataFrame.Site[i] == siteList[j]:
                        if stationDataFrame.Group[i] == grupList[j]:
                            urlList.append(tempUrlList[j])
                            foundList[j] = True
        
                    # If a new site is added to the NFMD, append it to the end of the stationID.pkl file
            numberOfStations = len(stationDataFrame.Site)
            for m in range(len(foundList)):
                if foundList[m] == False:
                    stationDataFrame.loc[len(stationDataFrame.index)] = [numberOfStations,siteList[m],latList[m],lonList[m],
                                                                         gaccList[m],stateList[m],grupList[m]]
                    urlList.append(urlList[m])
                    stationDataFrame.to_pickle("FMDB/stationID.pkl")
                    stationDataFrame.to_csv("FMDB/stationID.csv",index=False)
                    numberOfStations += 1
        else:
            numberOfStations = 1
            stationDataFrame = pd.DataFrame({"Site_Number": [0],"Site": [siteList[0]],"Latitude":[latList[0]],"Longitude":[lonList[0]],
                                             "GACC":[gaccList[0]],"State":[stateList[0]],"Group":[grupList[0]]})
            stationDataFrame.to_pickle("FMDB/stationID.pkl")
            for m in range(1,len(tempUrlList)):
                stationDataFrame.loc[len(stationDataFrame.index)] = [numberOfStations,siteList[m],latList[m],lonList[m],
                                                                     gaccList[m],stateList[m],grupList[m]]
                urlList.append(tempUrlList[m])
                stationDataFrame.to_pickle("FMDB/stationID.pkl")
                stationDataFrame.to_csv("FMDB/stationID.csv",index=False)
                numberOfStations += 1
        return urlList
    
    # Updates the Station ID list
    #
    # @ Param state - state that you want fuel mositure from
    #
    def update_Station_ID_List(self,state="CA"):
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
        
        kwarg = [list(df.url),list(df.site),list(df.lat),list(df.lng),list(df.gacc),list(df.state),list(df.grup)]
        #kwarg = [tempUrlList,tempSite,tempLat,tempLon,tempGacc,tempState,tempGrup]
        if osp.exists("FMDB/stationID.pkl"):
            urlList = self.build_StID(*kwarg,False) 
        else:
            urlList = self.build_StID(*kwarg,True)
    
        return urlList
    
    
    # Creates/updates the datafiles in the FMDB folder
    #
    # @ Param urlList - a list of all of the download links for each station from a given state
    # i.e. urlList = [https://www.wfas.net/nfmd/public/download_site_data.php?site=Vallecito&gacc=SOCC&state=CA&grup=PGE-SOCC, ...]
    #
    def update_Data_File(self,urlList,startYear=2000,endYear=int(datetime.datetime.now().year)):
        if os.path.exists("FMDB/stationID.pkl"):
            stationIdDataFrame = pd.read_pickle("FMDB/stationID.pkl")
        
            # Years you would like data for. Each year is made into a seperate PKL file
            # For example: 2000.pkl, 2001.pkl, etc.
            yearStart = startYear
            yearEnd = endYear

            # Loop to download data and get the needed variables
            for i in urlList:
                # downloads site "i" data file
                page = getURL(i)
                # Read downloaded file for identifying the station
                # For example: https://www.wfas.net/nfmd/public/download_site_data.php?site=12%20Rd%20@%2054%20Rd&gacc=NOCC&state=CA&grup=Tahoe%20NF
                # I.E. from above: site = 12 Rd @ 54, gacc = NOCC, etc.
                df = pd.read_csv(io.StringIO(page.content.decode()),sep="\t")
                df.columns = [c.lower() for c in df.columns]
            
                head = ["datetime", "fuel", "percent"]
                data1 = df[["date", "fuel", "percent"]]
                data1.columns = head
                count = 0
                for j in data1.datetime:
                    stationYear = j[0:4]

                    # Check if the given date's year is in the range provided 
                    if int(stationYear) >= yearStart and int(stationYear) <= yearEnd:
                    
                        # Lines 126-133 deal with if a plant is a variation
                        if "," in data1.fuel[count]:
                            tempVariation = data1.fuel[count].split()
                            fuel = tempVariation[0][0:len(tempVariation[0])-1]
                            variation = tempVariation[1]
                        else:
                            fuel = data1.fuel[count]
                            variation = None
            
                        # Checks to see if year file is already made, otherwise, it creates a PKL file with
                        # datetime, fueltype, fuel variation, and fuel data
                        if os.path.exists("FMDB/"+stationYear+".pkl"):
                            yearDataFrame = pd.read_pickle("FMDB/"+stationYear+".pkl")
                            foundData = False
                            # This loops makes sure that no repeated data is added to the database
                            for k in range(len(yearDataFrame.dateTime)):
                                if yearDataFrame.stationID[k] == currentSite:
                                    if yearDataFrame.dateTime[k] == j:
                                        if yearDataFrame.fuelType[k] == fuel:
                                            if yearDataFrame.fuelVariation[k] == variation:
                                                foundData = True
                                
                            if foundData == False:
                                yearDataFrame.loc[len(yearDataFrame.index)] = [currentSite,j,fuel,variation,data1.percent[count]]

                        else:
                            yearDataFrame = pd.DataFrame({"stationID": [currentSite],"dateTime":[data1.datetime[count]],"fuelType":[fuel],"fuelVariation":[variation],
                                                              "fuelData":[data1.percent[count]]})
                
                        yearDataFrame.to_pickle("FMDB/"+stationYear+".pkl")
                    count+=1
                if os.path.exists(file):
                    os.remove(file)
        else:
            print("stationID.pkl does not exist")


    def get_Data(self,startYear=int(datetime.datetime.now().year),endYear=int(datetime.datetime.now().year),stationID=None,fuelType=None,fuelVariation=None,
                 latitude1=None,latitude2=None,longitude1=None,longitude2=None,makeFile=False):
        fuelDataList = []
        fuelTypeList = []
        fuelVarList = []
        datesList = []
        stationName = []
        
        if latitude1 < latitude2:
            lat1 = latitude1
            lat2 = latitude2
        else:
            lat1 = latitude2
            lat2 = latitude1
            
        if longitude1 <  longitude2:
            lon1 = longitude1
            lon2 = longitude2
        else:
            lon1 = longitude2
            lon2 = longitude1
        
        if osp.exists("FMDB/stationID.pkl"):
            while startYear <= endYear:
                if os.path.exists("FMDB/"+str(startYear)+".pkl"):
                    stationDataFrame = pd.read_pickle("FMDB/stationID.pkl")
                    yearDataFrame = pd.read_pickle("FMDB/"+str(startYear)+".pkl")
                    if stationID == None:
                        stationID = range(len(stationDataFrame.Site))
                    for i in stationID:
                        if -91.0 < lat1 < 91.0 and -91.0 < lat2 < 91.0 and -361 < lon1 < 361 and -361 < lon2 < 361:   
                            if lat1 < stationDataFrame.Latitude[i] < lat2 and lon1 < stationDataFrame.Longitude[i] < lon2:
                                for j in range(len(yearDataFrame.stationID)):
                                    if yearDataFrame.stationID[j] == i:
                                        #print(stationName)
                                        if fuelType == None or fuelType == "None":
                                            fuelDataList.append(yearDataFrame.fuelData[j])
                                            fuelTypeList.append(yearDataFrame.fuelType[j])
                                            fuelVarList.append(yearDataFrame.fuelVariation[j])
                                            datesList.append(yearDataFrame.dateTime[j])
                                            stationName.append(self.find_SiteName(stationDataFrame,i))
                                        elif yearDataFrame.fuelType[j].lower() == fuelType.lower():
                                            if fuelVariation == None:
                                                fuelDataList.append(yearDataFrame.fuelData[j])
                                                fuelTypeList.append(yearDataFrame.fuelType[j])
                                                fuelVarList.append(yearDataFrame.fuelVariation[j])
                                                datesList.append(yearDataFrame.dateTime[j])
                                                stationName.append(self.find_SiteName(stationDataFrame,i))
                                            elif yearDataFrame.fuelVariation[j] is None: # If user specifies a fuel variation, dont take None
                                                continue
                                            elif fuelVariation.lower() in yearDataFrame.fuelVariation[j].lower():
                                                fuelDataList.append(yearDataFrame.fuelData[j])
                                                fuelTypeList.append(yearDataFrame.fuelType[j])
                                                fuelVarList.append(yearDataFrame.fuelVariation[j])
                                                datesList.append(yearDataFrame.dateTime[j])
                                                stationName.append(self.find_SiteName(stationDataFrame,i))
                                            else:
                                                continue
                        # If coordinate points are non existent, but you have stations in args
                        else:
                            for j in range(len(yearDataFrame.stationID)):
                                if yearDataFrame.stationID[j] == i:
                                    for k in range(len(stationDataFrame.Site_Number)):
                                        if i == stationDataFrame.Site_Number[k]:
                                            stationName.append(stationDataFrame.Site[k])
                                    if fuelType == None:
                                        fuelDataList.append(yearDataFrame.fuelData[j])
                                        fuelTypeList.append(yearDataFrame.fuelType[j])
                                        fuelVarList.append(yearDataFrame.fuelVariation[j])
                                        datesList.append(yearDataFrame.dateTime[j])
                                        stationName.append(self.find_SiteName(stationDataFrame,i))
                                    elif yearDataFrame.fuelType[j].lower() == fuelType.lower():
                                        if fuelVariation == None:
                                            fuelDataList.append(yearDataFrame.fuelData[j])
                                            fuelTypeList.append(yearDataFrame.fuelType[j])
                                            fuelVarList.append(yearDataFrame.fuelVariation[j])
                                            datesList.append(yearDataFrame.dateTime[j])
                                            stationName.append(self.find_SiteName(stationDataFrame,i))
                                        elif fuelVariation.lower() in yearDataFrame.fuelVariation[j].lower():
                                            fuelDataList.append(yearDataFrame.fuelData[j])
                                            fuelTypeList.append(yearDataFrame.fuelType[j])
                                            fuelVarList.append(yearDataFrame.fuelVariation[j])
                                            datesList.append(yearDataFrame.dateTime[j])
                                            stationName.append(self.find_SiteName(stationDataFrame,i))
                # If data file does not exist (i.e. you have data files from 2000-2021 but you call 1999)
                else:
                    print(str(startYear)+".pkl does not exist")
                startYear+=1
                print(startYear)
            count = 1
            # instead of data.csv, use currentDateTime.csv (to seconds 20200309_0209+seconds.csv)
            dataFile = "data ("+str(count)+")"
            if osp.exists('FMDB/data.csv'):
                while osp.exists("FMDB/"+dataFile+".csv"):
                    count+=1
                    dataFile = "data ("+str(count)+")"
            else:
                dataFile = "data"
            #[site, date, fuelType, fuel variation, fuelData]
            #print(stationName)
            fuelDataFrame = pd.DataFrame({"Site": [stationName[0]],"dateTime":[datesList[0]],"fuelType":[fuelTypeList[0]],"fuelVariation":[fuelVarList[0]],"fuelData":[fuelDataList[0]]})
            for i in range(1,len(fuelDataList)):
                fuelDataFrame.loc[len(fuelDataFrame.index)] = [stationName[i],datesList[i],fuelTypeList[i],fuelVarList[i],fuelDataList[i]]
            fuelDataFrame['dateTime'] = pd.to_datetime(fuelDataFrame['dateTime'])
            b = fuelDataFrame[['Site','fuelType','fuelVariation','dateTime','fuelData']]
            c = b.sort_values(by=list(b.columns))
            #fuelDataFrame = fuelDataFrame.sort_values('fuelVariation')
            #fuelDataFrame = fuelDataFrame.sort_values('dateTime')
            #fuelDataFrame = fuelDataFrame.sort_values('Site')
            #fuelDataFrame.sort_values(by=list(fuelDataFrame.columns))
            if makeFile == True:
                c.to_csv('FMDB/'+dataFile+'.csv',index=False, date_format='%Y-%m-%d')
            
            return c
        else:
            print("stationID.pkl does not exist")

    @staticmethod
    def plot_line_Data(dataFrame):
        df = dataFrame.groupby(['Site','fuelType','fuelVariation','dateTime']).mean()
        mids = df.index
        # Dropping one level from multi index (datetime) and find all the unique combinations of the other levels
        combos = mids.droplevel('dateTime').unique()
        
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
            #plt.legend(legend,bbox_to_anchor=(0.90, 1))
            plt.legend(legend,loc='upper left')
            plt.show()
        else:
            print('Too many plots!')
    
    
    @staticmethod
    def plot_std1(self,dataFrame):
        dataFrame.index = pd.to_datetime(dataFrame.dateTime)
        df = dataFrame.groupby(['fuelType','fuelVariation',dataFrame.index.year, dataFrame.index.month]).agg(['mean','std'])

        df.index.names = ['fuelType','fuelVariation','year','month']

        mid = df.index

        combos = mid.droplevel('month').unique()
        combos1 = combos.droplevel('year').unique()
        
        fig, ax = plt.subplots()
        legend = []
        months=[]
        count=0
        for combo in combos1:
            means=[]
            stds=[]
            dates = []
            print('combo',combo)
            tempFrame = df.loc[combo,:]
            for i in range(len(tempFrame.index)):
                dates.append(str(tempFrame.index[i][0])+'-'+str(tempFrame.index[i][1]))
            dates1 = pd.to_datetime(dates)
            mean = tempFrame.loc[:,tempFrame.columns.get_level_values(1) == 'mean']
            self.fill_list(mean,means)
            means = np.array(means)
            std = tempFrame.loc[:,tempFrame.columns.get_level_values(1) == 'std']
            self.fill_list(std,stds)
            stds = np.array(stds)
            ax.plot(dates1,means,'.-')
            ax.fill_between(dates1, means - stds, means + stds, alpha=0.2)
            legend.append('{} - {}'.format(*combo))
            count+=1
        ax.set_ylabel("Fuel Mositure (%)", fontsize = 15)
        ax.set_xlabel("Time", fontsize = 20)
        ax.tick_params(axis='both', length = 10, width = 1, labelsize=13)
        ax.xaxis.set_major_locator(md.YearLocator())
        ax.xaxis.set_minor_locator(md.MonthLocator(bymonth=[7]))
        ax.xaxis.set_major_formatter(md.DateFormatter("\n%Y"))
        ax.xaxis.set_minor_formatter(md.DateFormatter("%b"))
        plt.grid(True)
        plt.legend(legend,loc='upper left')
        plt.show()
            #mean = df.loc[combo,:]
        #print(mean)
        ##self.fill_list(mean,means)
        #self.fill_list(month, months)
        #testDB.fill_list(std1,stds)
        #print(len(dates1))
        #print(len(stds))
        #print(len(means))
        ##means = np.array(means)
        #months = np.array(months)
        #print(" ")
        #print('mean:',means)
        #std3 = df.loc[:,df.columns.get_level_values(1) == 'std']
        #ax.plot(dates1,mean,'.-')
        #legend.append('{} - {}'.format(*combo))
    
    @staticmethod
    def plot_std2(self,dataFrame):
        dataFrame.index = pd.to_datetime(dataFrame.dateTime)
        df = dataFrame.groupby(['fuelType','fuelVariation',dataFrame.index.year, dataFrame.index.month]).mean()
        df2 = dataFrame.groupby(['fuelType','fuelVariation',dataFrame.index.year, dataFrame.index.month]).std()
        df3 = dataFrame.groupby(['fuelType','fuelVariation',dataFrame.index.year, dataFrame.index.month]).agg(['mean','std'])

        df.index.names = ['fuelType','fuelVariation','year','month']
        df2.index.names = ['fuelType','fuelVariation','year','month']
        df3.index.names = ['fuelType','fuelVariation','year','month']
        
        mids = df.index
        mid2 = df2.index
        mid3 = df3.index
        
        combos = mids.droplevel('month').unique()
        combos1 = combos.droplevel('year').unique()
        combos2 = mid2.droplevel('month').unique()
        combos3 = combos2.droplevel('year').unique()
        combos4 = mid3.droplevel('month').unique()
        combos5 = combos4.droplevel('year').unique()
        
        fig, ax = plt.subplots()
        legend = []
        dates = []
        
        for i in range(len(df.index)):
            dates.append(str(df.index[i][2])+'-'+str(df.index[i][3]))
        dates1 = pd.to_datetime(dates)
        
        for combo in combos1:
            month = df.loc[:,df.columns.get_level_values(0) == 'month']
            year = df.loc[:,df.columns.get_level_values(0) == 'year']
            for i in range(len(df.index)):
                dates.append(str(year)+'-'+str(month))
            dates1 = pd.to_datetime(dates)
            mean = df.loc[:,df.columns.get_level_values(1) == 'mean']
            std3 = df.loc[:,df.columns.get_level_values(1) == 'std']
            ax.plot(dates1,mean,'.-')
            legend.append('{} - {}'.format(*combo))
            
        for combo in combos3:
            std = df2.loc[combo,:].values
        #print(list(std))
        #return(y.flatten())
        #print(np.array(y)[:,:][0].shape)
        #ax.fill_between(dates1, y.flatten() - std.flatten(), y.flatten() + std.flatten(), alpha=0.2)
            #print(y2)
            #ax.plot(dates2,means5)
            #ax.fill_between(dates2, means5 - stds5, means5 + stds5, alpha=0.2)
        ax.set_ylabel("Fuel Mositure (%)", fontsize = 15)
        ax.set_xlabel("Time", fontsize = 20)
        ax.tick_params(axis='both', length = 10, width = 1, labelsize=13)
        ax.xaxis.set_major_locator(md.YearLocator())
        ax.xaxis.set_minor_locator(md.MonthLocator(bymonth=[7]))
        ax.xaxis.set_major_formatter(md.DateFormatter("\n%Y"))
        ax.xaxis.set_minor_formatter(md.DateFormatter("%b"))
        plt.grid(True)
        #plt.legend(legend,bbox_to_anchor=(0.90, 1))
        plt.legend(legend,loc='upper left')
        plt.show()
        
        '''
        dates = []
        means = []
        stds = []
        #for i in range(len(df.index)):
            #dates.append(str(df.index[i][0])+'-'+str(df.index[i][1]))
            
        #fig, ax = plt.subplots()
        #legend = []
        for combo in combos1:
            x = pd.to_datetime(df.loc[combo,:,:].index)
            y = df.loc[combo,:,:].values
            #ax.plot(x,y,'.-')
            #legend.append('{} - {}'.format(*combo))
        #plt.show()
        '''
        '''    
        std1 = df.loc[:,df.columns.get_level_values(1) == 'std']
        mean1 = df.loc[:,df.columns.get_level_values(1) == 'mean']
        self.fill_list(mean1,means)
        self.fill_list(std1,stds)
        means = np.array(means)
        stds = np.array(stds)
        '''
    
    @staticmethod
    def plot_err_data(dataFrame):
        dataFrame.index = pd.to_datetime(dataFrame.dateTime)
        df = dataFrame.groupby([dataFrame.index.year]).agg(['mean','std'])
        #df = dataFrame.groupby([dataFrame.index.year, dataFrame.index.month]).agg(['mean','std'])
        df.index.names = ['year','month']
        ##df1 = dataFrame.groupby([dataFrame.index.year]).agg(['mean','std'])
        #df2 = df = dataFrame.groupby([dataFrame.index.year,dataFrame.index.month]).std()
        #print(df.columns)
        return df
        #plt.plot(dataFrame.index.month,df.mean, yerr = df.std)
    
        
    @staticmethod
    def fill_list(dataList,outputList):
        for i in dataList.values:
            outputList.append(i[0])


if __name__ == '__main__':

    testDB = FMDB(osp.abspath(os.getcwd()))
    #print(last.index.names)
    #print(last.columns)
    #print(last['fuelData','std'][:])
    #print(last['fuelData','std'].index[0][1])
    #plt.plot(last['fuelData','std'])
    #plt.plot(range(10),range(10))
    #print(last)
    #python FMDB_class.py arg1 arg2# will run this test code #####
    
    #urlList = testDB.update_Station_ID_List("CA")
    #testDB.update_Data_File(urlList,2000,2021)
    #print("Getting Data")
    #hi = pd.read_pickle("FMDB/2001.pkl")
    coords = [36.93,40.75,-122.43,-118.81]

    ## csv output statistics
    testDataframe = testDB.get_Data(2000,2021,None,"Chamise",None,*coords,False)
    testDB.plot_std1(testDB,testDataframe)
    #testDB.plot_std2(testDB,testDataframe)
    #print(what[0])
    '''
    testDataframe2 = testDB.get_Data(2000,2021,None,"Chamise","New",*coords,False)
    #testDataframe = testDB.get_Data(startYear=2000,endYear=2021,stationID=None,fuelType="Chamise",fuelVariation="Old",
                 #*coords,makeFile=False)
    #print("Plotting")
    last=testDB.plot_err_data(testDataframe)
    last2 = testDB.plot_err_data(testDataframe2)
    
    #print(pd.to_datetime(last.index.levels[1].astype(str))+ last.index.levels[0], format='%Y%B')
    #print(len(last.index.levels[0]))
    #print(len(last.index.levels[1]))
    #print(last.level)
    #print(last.droplevel(0))
    #last.rename('year',level=0)
    #f1 = pd.to_datetime([f'{y}-{m}' for y, m in zip(last.index.levels[0], last.index.levels[1])])
    #print(last.index[0][0])
    #print(last.head())
    dates = []
    means = []
    stds = []
    for i in range(len(last.index)):
        dates.append(str(last.index[i][0])+'-'+str(last.index[i][1]))
        #dates.append(str(last.index[i]))
    #f21 = last.loc[2001,('fuelData','std')]
    std1 = last.loc[:,last.columns.get_level_values(1) == 'std']
    mean1 = last.loc[:,last.columns.get_level_values(1) == 'mean']
    #for i in std1.values:
    #    print('last:',i[0])
    dates1 = pd.to_datetime(dates)
   
    testDB.fill_list(mean1,means)
    testDB.fill_list(std1,stds)
    print(len(dates1))
    print(len(stds))
    print(len(means))
    means = np.array(means)
    stds = np.array(stds)
    
    
    #######
    
    dates2 = []
    means2 = []
    stds2 = []
    for i in range(len(last2.index)):
        dates2.append(str(last2.index[i][0])+'-'+str(last2.index[i][1]))
        #dates.append(str(last.index[i]))
    #f21 = last.loc[2001,('fuelData','std')]
    std3 = last2.loc[:,last2.columns.get_level_values(1) == 'std']
    mean3 = last2.loc[:,last2.columns.get_level_values(1) == 'mean']
    #for i in std1.values:
    #    print('last:',i[0])
    dates2 = pd.to_datetime(dates2)
   
    testDB.fill_list(mean3,means2)
    testDB.fill_list(std3,stds2)
    means5 = np.array(means2)
    stds5 = np.array(stds2)
    
    #######
    
    fig, ax = plt.subplots()
    #plt.xlim(min(dates1.year),max(dates1.year))
    
    ax.plot(dates2,means5)
    ax.fill_between(dates2, means5 - stds5, means5 + stds5, alpha=0.2)
    ax.plot(dates1,means)
    ax.fill_between(dates1, means - stds, means + stds, alpha=0.2)
    ax.grid(True)
    #ax.locator_params(axis='x', nbins=len(np.unique(dates1.year)))
    years = list(np.unique(dates1.year))
    years.append(years[-1]+1)
    #ax.xaxis.set_minor_formatter(md.DateFormatter("%b"))
    plt.xticks(pd.to_datetime(['{:04d}-01-01'.format(year) for year in years]))
    ax.xaxis.set_major_formatter(md.DateFormatter('%Y'))
    plt.setp(ax.xaxis.get_minorticklabels(),size=12,rotation=45)
    plt.legend(["Chamise - New","Chamise - Old"])
    plt.show()
    #f32 = last.get_level_values(1)
    #fq = pd.to_datetime(dates)
    #g2 = last["mean"]
    #g1 = last.iloc[:, last.columns.get_level_values(1)=='std']
    #last.plot(y="mean",yerr="std")
    #last.unstack(level=0).plot(subplots=False)
    print("done")
    #print(last.names)
    #last.index = pd.to_datetime(last.index.levels[0],last.index.levels[1])
    #print(last.unstack(level=0)[0])
    #print(last.reset_index(level=['fuelData','std']))
    #testDB.plot_line_Data(testDataframe)
    # For fueltype and fuelVariation, set up way to make all lowercase when verifying

    #tester = pd.read_csv("FMDB/data (5).csv")
    #print(tester.dateTime[0])
    '''

     