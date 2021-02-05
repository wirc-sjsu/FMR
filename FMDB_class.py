# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 10:11:53 2021

@author: jackr
"""
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
        if self.exists_here():
            self.update_Station_ID_List()
            self.update_Data_File()
    

    # Checks if directory exists. If not, create it
    #     
    def exists_here(self):
        if osp.exists(self.folder_path+"\FMDB"):
            return True
        os.makedirs("FMDB")
        return True
    
    
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
    def get_Index(self,stringData,startOfVariable,seperator):
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
    def create_Station_ID_List(self,siteNumber,siteName,latName,lonName,gaccName,stateName,grupName):
        stationDataFrame = pd.DataFrame({"Site_Number": [siteNumber],"Site": [siteName],"Latitude":[latName],"Longitude":[lonName],"GACC":[gaccName],
                                         "State":[stateName],"Group":[grupName]})
        stationDataFrame.to_pickle("stationID.pkl")
    
    # Updates the Station ID list
    #
    # @ Param state - state that you want fuel mositure from
    #
    def update_Station_ID_List(self,state):
    
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
            stringStart = str(siteData[str(i)])

            if i == 0:
                stationEnd=self.get_Index(stringStart,28,'"')
            
            else:
                stationEnd=self.get_Index(stringStart,19,'"')
      
            gaccEnd=self.get_Index(stringStart,stationEnd+8,'"')
            stateEnd=self.get_Index(stringStart,gaccEnd+9,'"')
            grupEnd=self.get_Index(stringStart,stateEnd+8,'"')
            latEnd=self.get_Index(stringStart,grupEnd+7,'"')
            
            # Download link has "%20" instead of spaces, but we still need spaces for PKL file
            # Example site download link: https://www.wfas.net/nfmd/public/download_site_data.php?site=12%20Rd%20@%2054%20Rd&gacc=NOCC&state=CA&grup=Tahoe%20NF
            if i == 0:    
                stationName = stringStart[28:stationEnd].replace(" ","%20")
                stationName1 = stringStart[28:stationEnd]
            else:
                stationName = stringStart[19:stationEnd].replace(" ","%20")
                stationName1 = stringStart[19:stationEnd]
        
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
        
        
            # Prepare data for stationID PKL file and get put station data download links in a list
            if os.path.exists("stationID.pkl"):
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
        if os.path.exists("stationID.pkl"):
            stationDataFrame = pd.read_pickle("stationID.pkl")
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
                    stationDataFrame.to_pickle("stationID.pkl")
                    stationDataFrame.to_csv("stationID.csv",index=False)
                    numberOfStations += 1
    
            # Removes site list file from local directory
        if os.path.exists(file):
             os.remove(file)
        else:
            print("The file does not exist")
    
        return urlList
    
    def update_Data_File(self,urlList):
        if os.path.exists("stationID.pkl"):
            stationIdDataFrame = pd.read_pickle("stationID.pkl")
        
            # Years you would like data for. Each year is made into a seperate PKL file
            # For example: 2000.pkl, 2001.pkl, etc.
            yearStart=2000
            yearEnd = 2020

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
                for j in range(len(stationIdDataFrame.Site)):
                    if currentSite == stationIdDataFrame.Site[j]:
                        if currentGroup == stationIdDataFrame.Group[j]:
                            currentSite = stationIdDataFrame.Site_Number[j]

            
                head = ["datetime","fuel","percent"]
                data1 = pd.read_csv(file,sep="	",names=head,skiprows=1, usecols=[4,5,6])
                count = 0
                for j in data1.datetime:
                    stationYear = j[0:4]

                    # Check if the given date's year is in the range provided 
                    if int(stationYear) >= yearStart and int(stationYear) <= yearEnd:
                    
                        # lines 126-133 deal with if a plant is a variation
                        if "," in data1.fuel[count]:
                            tempVariation = data1.fuel[count].split()
                            fuel = tempVariation[0][0:len(tempVariation[0])-1]
                            variation = tempVariation[1]
                        else:
                            fuel = data1.fuel[count]
                            variation = None
            
                        # checks to see if year file is already made, otherwise, it creates a PKL file with
                        # datetime, fueltype, fuel variation, and fuel data
                        if os.path.exists(stationYear+".pkl"):
                            yearDataFrame = pd.read_pickle(stationYear+".pkl")
                            foundData = False
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
                
                        yearDataFrame.to_pickle(stationYear+".pkl")
                    count+=1
                if os.path.exists(file):
                    os.remove(file)




        