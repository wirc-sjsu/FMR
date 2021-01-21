# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 14:10:38 2020

@author: jackr
"""

## Libraries ##
import pandas as pd
import wget
import os
import numpy as np
import csv

#stationDataFrame = pd.read_pickle("stationID.pkl")
## Funtions ##

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
# month = get_Index(someString,variableStart,seperator)
# month would be equal to 7
#
def get_Index(stringData,startOfVariable,seperator):
    count = startOfVariable

    while stringData[count] != str(seperator):
        count += 1
    return count

def create_Station_ID_List(siteNumber,siteName,latName,lonName,gaccName,stateName,grupName):
    stationDataFrame = pd.DataFrame({"Site_Number": [siteNumber],"Site": [siteName],"Latitude":[latName],"Longitude":[lonName],"GACC":[gaccName],
                                     "State":[stateName],"Group":[grupName]})
    stationDataFrame.to_pickle("stationID.pkl")
    stationDataFrame.to_csv("stationID.csv",index=False)
    
def update_Station_ID_List():
    # Get site list
    pd.set_option('display.max_colwidth', -1)
    url = "https://www.wfas.net/nfmd/ajax/states_map_site_xml.php?state=CA"
    file = wget.download(url)

    tempData = pd.read_csv(file,sep="/>",engine='python')
    numberOfStations = int(str(tempData.shape)[4:7])
    head = [str(i) for i in np.arange(0,numberOfStations+1,1)]

    siteData = pd.read_csv(file,names=head,sep="/>",engine='python')
    
    urlList = []
    tempUrlList = []
    tempSite = []
    finalSite = []
    tempLat = []
    tempLon = []
    tempGacc = []
    tempState = []
    tempGrup = []
    finalGrup = []
    
    #print("About to get all the links")
    for i in range(len(head)-2):
        stringStart = str(siteData[str(i)])
        #print(stringStart)
        if i == 0:
            stationEnd=get_Index(stringStart,28,'"')
            
        else:
            stationEnd=get_Index(stringStart,19,'"')
      
        gaccEnd=get_Index(stringStart,stationEnd+8,'"')
        stateEnd=get_Index(stringStart,gaccEnd+9,'"')
        grupEnd=get_Index(stringStart,stateEnd+8,'"')
        latEnd=get_Index(stringStart,grupEnd+7,'"')
        #lonEnd=get_Index(stringStart,latEnd+7,'"')

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
            create_Station_ID_List(0,stationName1,latName,lonName,gaccName,stateName,grupName1)
            urlList.append("https://www.wfas.net/nfmd/public/download_site_data.php?site="+stationName+"&gacc="+
                                   gaccName+"&state="+stateName+"&grup="+grupName)

    
    foundList = [False] * len(tempUrlList)
    if os.path.exists("stationID.pkl"):
        stationDataFrame = pd.read_pickle("stationID.pkl")
        for k in range(len(stationDataFrame.Site)):
            for l in range(len(tempUrlList)):
                if stationDataFrame.Site[k] == tempSite[l]:
                    if stationDataFrame.Group[k] == tempGrup[l]:
                        urlList.append(tempUrlList[l])
                        foundList[l] = True
                        finalSite.append(tempSite[l])
                        finalGrup.append(tempGrup[l])
        
        numberOfStations = len(stationDataFrame.Site)
        for m in range(len(foundList)):
            if foundList[m] == False:
                stationDataFrame.loc[len(stationDataFrame.index)] = [numberOfStations,tempSite[m],tempLat[m],tempLon[m],
                                                                 tempGacc[m],tempState[m],tempGrup[m]]
                urlList.append(tempUrlList[m])
                finalSite.append(tempSite[m])
                finalGrup.append(tempSite[m])
                stationDataFrame.to_pickle("stationID.pkl")
                stationDataFrame.to_csv("stationID.csv",index=False)
                numberOfStations += 1
        
    if os.path.exists(file):
        os.remove(file)
    else:
        print("The file does not exist")
    
    return urlList


def update_Data_File(urlList):
    if os.path.exists("stationID.pkl"):
        stationIdDataFrame = pd.read_pickle("stationID.pkl")
        # Loop to download data and get the needed variables
        yearStart=2000
        yearEnd = 2020

        for i in urlList:
            # downloads site "i" data file
            file = wget.download(i)
            
            stringStart = str(i)
            stationEnd = get_Index(stringStart,61,'&')
            gaccEnd = get_Index(stringStart,stationEnd+6,'&')
            stateEnd = get_Index(stringStart,gaccEnd+7,'&')
            if stateEnd+6 == "=":
                currentGroup = stringStart[stateEnd+7::].replace("%20"," ")
            elif stateEnd+7 == "=":
                currentGroup = stringStart[stateEnd+8::].replace("%20"," ")
            else:
                currentGroup = stringStart[stateEnd+6::].replace("%20"," ")
            currentSite = str(i)[61:stationEnd].replace("%20"," ")
            print("list:",currentSite)
            print("groups:",currentGroup)
            
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
            
                    # checks to see if year file is already made, otherwise, adds datetime, fueltype, fuel variation, and fuel data 
                    # to csv file
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
                    #yearDataFrame.to_csv(stationYear+".csv",index=False)
                count+=1
                #print(currentSite)
            if os.path.exists(file):
                os.remove(file)
                
            

stationList = update_Station_ID_List()
update_Data_File(stationList)




