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
# seperator = "-"
# month = get_Index(someString,variableStart,seperator)
# month would be equal to 7
#
def get_Index(stringData,startOfVariable,seperator):
    count = startOfVariable

    while stringData[count] != str(seperator):
        count += 1
    return count

def create_Station_ID_List(siteName,latName,lonName,gaccName,stateName,grupName):
    stationDataFrame = pd.DataFrame({"Site": [siteName],"Latitude":[latName],"Longitude":[lonName],"GACC":[gaccName],
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
    tempLat = []
    tempLon = []
    tempGacc = []
    tempState = []
    tempGrup = []
    Outtercount = 0
    
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
    
        if os.path.exists("stationID.pkl"):
            stationDataFrame = pd.read_pickle("stationID.pkl")
            foundSite = False
            for i in stationDataFrame.Site:
                if i == stationName1:
                    foundSite = True
            if foundSite == False:
                tempUrlList.append("https://www.wfas.net/nfmd/public/download_site_data.php?site="+stationName+"&gacc="+
                                   gaccName+"&state="+stateName+"&grup="+grupName)
                tempSite.append(stationName1)
                tempLat.append(latName)
                tempLon.append(lonName)
                tempGacc.append(gaccName)
                tempState.append(stateName)
                tempGrup.append(grupName1)
        
        else:
            create_Station_ID_List(stationName1,latName,lonName,gaccName,stateName,grupName1)
            tempUrlList.append("https://www.wfas.net/nfmd/public/download_site_data.php?site="+stationName+"&gacc="+
                                   gaccName+"&state="+stateName+"&grup="+grupName)
            
        Outtercount+=1
    
    tempCounter = 0
    if os.path.exists("stationID.pkl"):
        for j in tempUrlList:
            stationDataFrame = pd.read_pickle("stationID.pkl")
            stationDataFrame.loc[len(stationDataFrame.index)] = [tempSite[tempCounter],tempLat[tempCounter],tempLon[tempCounter],
                                                                 tempGacc[tempCounter],tempState[tempCounter],tempGrup[tempCounter]]
            urlList.append(j)
            stationDataFrame.to_pickle("stationID.pkl")
            stationDataFrame.to_csv("stationID.csv",index=False)
            tempCounter+=1
        
    print(tempCounter)
    print(len(tempUrlList))
    print(tempUrlList)
    if os.path.exists(file):
        os.remove(file)
    else:
        print("The file does not exist")
    
    
update_Station_ID_List()