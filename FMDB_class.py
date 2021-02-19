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
import pathlib as plb
import pandas as pd
import wget


#temp = osp.abspath(os.getcwd())
#print(temp+"\FMDB")
#temp = plb.Path().parent.absolute()

class FMDB(object):
    
    # Constructor for FMDB class
    #
    # @ Param folder_path - path where this script is located
    #
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.exists_here()
    

    # Checks if FMDB directory exists. If not, it is created
    #     
    def exists_here(self):
        if osp.exists(self.folder_path+"/FMDB"):
            print("FMDB Folder Exists")
        else:
            os.makedirs("FMDB")
    
    
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
    
    
    # Creates a PKL file with NFMD stations
    #
    # @ Param siteNumber - site number corresponding to a station
    # @ Param siteName - name of a station
    # @ Param latName - latitude of a station
    # @ Param lonName - longitude of a station
    # @ Param gaccName - geographical area coordination center of a station
    # @ Param stateName - state of a station
    # @ Param grupName - group managing a station
    #
    @staticmethod
    def create_Station_ID_List(self,siteNumber,siteName,latName,lonName,gaccName,stateName,grupName):
        stationDataFrame = pd.DataFrame({"Site_Number": [siteNumber],"Site": [siteName],"Latitude":[latName],"Longitude":[lonName],"GACC":[gaccName],
                                         "State":[stateName],"Group":[grupName]})
        stationDataFrame.to_pickle("FMDB/stationID.pkl")
    
    @staticmethod
    def build_StID(tempUrlList,siteList,latList,lonList,gaccList,stateList,grupList,create=True):
        
        urlList = []
        if create == False:
            foundList = [False] * len(tempUrlList)
            stationDataFrame = pd.read_pickle("FMDB/stationID.pkl")
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
        pd.set_option('display.max_colwidth', -1)
        url = "https://www.wfas.net/nfmd/ajax/states_map_site_xml.php?state="+state
        file = wget.download(url)

        # Find the total number of stations 
        siteData = pd.read_csv(file,sep="/>",engine='python')
        numberOfStations = int(str(siteData.shape)[4:7])
        head = [str(i) for i in np.arange(0,numberOfStations+1,1)]
    
        # Lists to be used later in the function
        urlList = []
        tempUrlList = []
        tempSite = []
        tempLat = []
        tempLon = []
        tempGacc = []
        tempState = []
        tempGrup = []
    
        # From line 67 - 118, get the needed variables for each site
        # site example: <marker site="12 Rd @ 54 Rd" gacc="NOCC" state="CA" grup="Tahoe NF" lat="39.570555555556" lng="-120.49277777778" active="0" currency="3"/>
        for i in range(len(head)-2):
            #print(str(siteData.columns[0]))
            stringStart = str(siteData.columns[i])

            if i == 0:
                stationEnd=self.get_Index(stringStart,23,'"')
            
            else:
                stationEnd=self.get_Index(stringStart,14,'"')
      
            gaccEnd=self.get_Index(stringStart,stationEnd+8,'"')
            stateEnd=self.get_Index(stringStart,gaccEnd+9,'"')
            grupEnd=self.get_Index(stringStart,stateEnd+8,'"')
            latEnd=self.get_Index(stringStart,grupEnd+7,'"')
            
            # Download link has "%20" instead of spaces, but we still need spaces for PKL file
            # Example site download link: https://www.wfas.net/nfmd/public/download_site_data.php?site=12%20Rd%20@%2054%20Rd&gacc=NOCC&state=CA&grup=Tahoe%20NF
            if i == 0:    
                stationName = stringStart[23:stationEnd].replace(" ","%20")
                stationName1 = stringStart[23:stationEnd]
            else:
                stationName = stringStart[14:stationEnd].replace(" ","%20")
                stationName1 = stringStart[14:stationEnd]
        
            gaccName = stringStart[stationEnd+8:gaccEnd]
            stateName = stringStart[gaccEnd+9:stateEnd]
            grupName = stringStart[stateEnd+8:grupEnd].replace(" ","%20")
            grupName1 = stringStart[stateEnd+8:grupEnd]
        
            if stringStart[grupEnd+11] == '"': 
                latName = float(stringStart[grupEnd+7:grupEnd+10])
            else:
                latName = float(stringStart[grupEnd+7:grupEnd+12])
    
            if stringStart[latEnd+13] == '"':
                lonName = float(stringStart[latEnd+7:latEnd+12])
            else:
                lonName = float(stringStart[latEnd+7:latEnd+14])
        
            tempUrlList.append("https://www.wfas.net/nfmd/public/download_site_data.php?site="+stationName+"&gacc="+
                                   gaccName+"&state="+stateName+"&grup="+grupName)
            tempSite.append(stationName1)
            tempLat.append(latName)
            tempLon.append(lonName)
            tempGacc.append(gaccName)
            tempState.append(stateName)
            tempGrup.append(grupName1)
        
        kwarg = [tempUrlList,tempSite,tempLat,tempLon,tempGacc,tempState,tempGrup]
        if osp.exists("FMDB/stationID.pkl"):
            urlList = self.build_StID(*kwarg,False) 
        else:
            urlList = self.build_StID(*kwarg,True)
                    
        '''
            # Prepare data for stationID PKL file and get put station data download links in a list
            if os.path.exists("FMDB/stationID.pkl"):
                tempUrlList.append("https://www.wfas.net/nfmd/public/download_site_data.php?site="+stationName+"&gacc="+
                                   gaccName+"&state="+stateName+"&grup="+grupName)
                tempSite.append(stationName1)
                tempLat.append(latName)
                tempLon.append(lonName)
                tempGacc.append(gaccName)
                tempState.append(stateName)
                tempGrup.append(grupName1)
            else:
                self.create_Station_ID_List(0,stationName1,latName,lonName,gaccName,stateName,grupName1)
                urlList.append("https://www.wfas.net/nfmd/public/download_site_data.php?site="+stationName+"&gacc="+
                               gaccName+"&state="+stateName+"&grup="+grupName)

        # Sorts download links in order of sites in stationID.pkl file
        foundList = [False] * len(tempUrlList)
        if os.path.exists("FMDB/stationID.pkl"):
            stationDataFrame = pd.read_pickle("FMDB/stationID.pkl")
            for k in range(len(stationDataFrame.Site)):
                for l in range(len(tempUrlList)):
                    if stationDataFrame.Site[k] == tempSite[l]:
                        if stationDataFrame.Group[k] == tempGrup[l]:
                            urlList.append(tempUrlList[l])
                            foundList[l] = True
        
            # If a new site is added to the NFMD, append it to the end of the stationID.pkl file
            numberOfStations = len(stationDataFrame.Site)
            for m in range(len(foundList)):
                if foundList[m] == False:
                    stationDataFrame.loc[len(stationDataFrame.index)] = [numberOfStations,tempSite[m],tempLat[m],tempLon[m],
                                                                     tempGacc[m],tempState[m],tempGrup[m]]
                    urlList.append(tempUrlList[m])
                    stationDataFrame.to_pickle("FMDB/stationID.pkl")
                    stationDataFrame.to_csv("FMDB/stationID.csv",index=False)
                    numberOfStations += 1
        '''
            # Removes site list file from local directory
        if os.path.exists(file):
             os.remove(file)
        else:
            print("The file does not exist")
    
        return urlList
    
    
    # Creates/updates the datafiles in the FMDB folder
    #
    # @ Param urlList - a list of all of the download links for each station from a given state
    # i.e. urlList = [https://www.wfas.net/nfmd/public/download_site_data.php?site=Vallecito&gacc=SOCC&state=CA&grup=PGE-SOCC, ...]
    #
    def update_Data_File(self,urlList):
        if os.path.exists("FMDB/stationID.pkl"):
            stationIdDataFrame = pd.read_pickle("FMDB/stationID.pkl")
        
            # Years you would like data for. Each year is made into a seperate PKL file
            # For example: 2000.pkl, 2001.pkl, etc.
            yearStart=int(datetime.datetime.now().year)-10
            yearEnd = int(datetime.datetime.now().year)

            # Loop to download data and get the needed variables
            for i in urlList:
                # downloads site "i" data file
                file = wget.download(i)
            
                # Read downloaded file for identifying the station
                # For example: https://www.wfas.net/nfmd/public/download_site_data.php?site=12%20Rd%20@%2054%20Rd&gacc=NOCC&state=CA&grup=Tahoe%20NF
                stringStart = str(i)
                
                stationEnd = self.get_Index(stringStart,61,'&')
                gaccEnd = self.get_Index(stringStart,stationEnd+6,'&')
                stateEnd = self.get_Index(stringStart,gaccEnd+7,'&')
                if stateEnd+6 == "=":
                    currentGroup = stringStart[stateEnd+7::].replace("%20"," ")
                elif stateEnd+7 == "=":
                    currentGroup = stringStart[stateEnd+8::].replace("%20"," ")
                else:
                    currentGroup = stringStart[stateEnd+6::].replace("%20"," ")
                currentSite = str(i)[61:stationEnd].replace("%20"," ")
            
                # Get site number corresponding to the station in the stationID.pkl file
                #
                # If update_Data_File is called without the stationID list being updated
                # skips the current site (file)
                siteExists = False
                for j in range(len(stationIdDataFrame.Site)):
                    if currentSite == stationIdDataFrame.Site[j]:
                        if currentGroup == stationIdDataFrame.Group[j]:
                            currentSite = stationIdDataFrame.Site_Number[j]
                            siteExists = True
                if siteExists == False:
                    print(currentSite+" not in stationID file")
                    break

            
                head = ["datetime","fuel","percent"]
                data1 = pd.read_csv(file,sep="	",names=head,skiprows=1, usecols=[4,5,6])
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
                                        for k in range(len(stationDataFrame.Site_Number)):
                                            if i == stationDataFrame.Site_Number[k]:
                                                stationName.append(stationDataFrame.Site[k])
                                        #print(stationName)
                                        if fuelType == None:
                                            fuelDataList.append(yearDataFrame.fuelData[j])
                                            fuelTypeList.append(yearDataFrame.fuelType[j])
                                            fuelVarList.append(yearDataFrame.fuelVariation[j])
                                            datesList.append(yearDataFrame.dateTime[j])
                                        elif yearDataFrame.fuelType[j].lower() == fuelType.lower():
                                            if fuelVariation == None:
                                                fuelDataList.append(yearDataFrame.fuelData[j])
                                                fuelTypeList.append(yearDataFrame.fuelType[j])
                                                fuelVarList.append(yearDataFrame.fuelVariation[j])
                                                datesList.append(yearDataFrame.dateTime[j])
                                            elif yearDataFrame.fuelVariation[j] is None:
                                                continue
                                            elif fuelVariation.lower() in yearDataFrame.fuelVariation[j].lower():
                                                #print("Station ID:",yearDataFrame.stationID[j])
                                                #print("Fuel Variation:",yearDataFrame.fuelVariation[j])
                                                #print("")
                                                fuelDataList.append(yearDataFrame.fuelData[j])
                                                fuelTypeList.append(yearDataFrame.fuelType[j])
                                                fuelVarList.append(yearDataFrame.fuelVariation[j])
                                                datesList.append(yearDataFrame.dateTime[j])
                                            else:
                                                continue
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
                                    elif yearDataFrame.fuelType[j].lower() == fuelType.lower():
                                        if fuelVariation == None:
                                            fuelDataList.append(yearDataFrame.fuelData[j])
                                            fuelTypeList.append(yearDataFrame.fuelType[j])
                                            fuelVarList.append(yearDataFrame.fuelVariation[j])
                                            datesList.append(yearDataFrame.dateTime[j])
                                        elif fuelVariation.lower() in yearDataFrame.fuelVariation[j].lower():
                                            fuelDataList.append(yearDataFrame.fuelData[j])
                                            fuelTypeList.append(yearDataFrame.fuelType[j])
                                            fuelVarList.append(yearDataFrame.fuelVariation[j])
                                            datesList.append(yearDataFrame.dateTime[j])
                else:
                    print(str(startYear)+".pkl does not exist")
                startYear+=1
                print(startYear)
            count = 1
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
            print(len(fuelDataList))
            print(len(stationName))
            for i in range(1,len(fuelDataList)):
                fuelDataFrame.loc[len(fuelDataFrame.index)] = [stationName[i],datesList[i],fuelTypeList[i],fuelVarList[i],fuelDataList[i]]
            fuelDataFrame['dateTime'] = pd.to_datetime(fuelDataFrame['dateTime'])
            b = fuelDataFrame[['Site','fuelType','fuelVariation','dateTime','fuelData']]
            print(b.Site)
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
    def plot_Data(dataFrame):
        print("Here2")
        print(dataFrame.Site)
        df = dataFrame.groupby(['Site','fuelType','fuelVariation','dateTime']).mean()
        mids = df.index
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
            plt.legend(legend,loc='upper right')
            plt.show()
        else:
            print('Too many plots!')
        
        
if __name__ == '__main__':

    testDB = FMDB(osp.abspath(os.getcwd()))
    
    #python FMDB_class.py arg1 arg2# will run this test code #####
    
    #urlList = testDB.update_Station_ID_List("CA")
    #testDB.update_Data_File(urlList)
    print("Getting Data")
    coords = [36.93,37.47,-122.43,-121.84]
    testDataframe = testDB.get_Data(2000,2021,None,"Chamise","New",*coords,True)
    #testDataframe = testDB.get_Data(startYear=2000,endYear=2021,stationID=None,fuelType="Chamise",fuelVariation="Old",
                 #*coords,makeFile=False)
    print("Plotting")
    testDB.plot_Data(testDataframe)
    # For fueltype and fuelVariation, set up way to make all lowercase when verifying

    #tester = pd.read_csv("FMDB/data (5).csv")
    #print(tester.dateTime[0])



     