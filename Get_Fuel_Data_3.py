# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 14:54:16 2020

@author: jackr
"""

## Libraries ##
import pandas as pd
import wget
import os
import numpy as np
import csv


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


stationDataFrame = pd.read_pickle("stationID.pkl")

'''
# Get site list
pd.set_option('display.max_colwidth', -1)
url = "https://www.wfas.net/nfmd/ajax/states_map_site_xml.php?state=CA"
file = wget.download(url)

tempData = pd.read_csv(file,sep="/>",engine='python')
numberOfStations = int(str(tempData.shape)[4:7])
print(tempData.shape)
head = [str(i) for i in np.arange(0,numberOfStations+1,1)]

#head = ['0','1','2','3','4']
siteData = pd.read_csv(file,names=head,sep="/>",engine='python')
urlList = []
stationIDList = []

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
        
        
    stationIDList.append(stationName1 + "," + gaccName + "," + stateName + "," + grupName1 + "," + str(latName) + "," + str(lonName))
    urlList.append("https://www.wfas.net/nfmd/public/download_site_data.php?site="+stationName+"&gacc="+gaccName+"&state="+
                   stateName+"&grup="+grupName)
    if os.path.exists("stationID.pkl"):
        #stationDataFrame = pd.read_csv("stationID.csv",engine='python')
        stationDataFrame = pd.read_pickle("stationID.pkl")
        stationDataFrame.loc[len(stationDataFrame.index)] = [stationName1,gaccName,stateName,grupName1]
    else:
        stationDataFrame = pd.DataFrame({"Site": [stationName1],"GACC":[gaccName],"State":[stateName],"Group":[grupName1]})
    #stationDataFrame.to_csv("stationID.csv",index=False)
    stationDataFrame.to_pickle("stationID.pkl")

#print(len(urlList[0]))
#print(stationIDList[0])
if os.path.exists(file):
    os.remove(file)
else:
    print("The file does not exist")
    
#print(urlList)

# Lists to store needed variables
dates = []
fuelType = []
fuelVariation = []
fuelData = []

#print(urlList)
# Loop to download data and get the needed variables
site = 0
yearStart=2000
yearEnd = 2020

for i in urlList:
    # downloads site "i" data file
    file = wget.download(i)
    head = ["datetime","fuel","percent"]
    data1 = pd.read_csv(file,sep="	",names=head,skiprows=1, usecols=[4,5,6])
    count = 0
    for j in data1.datetime:
        # Check if the given date's year is in the range provided 
        if int(j[0:4]) >= yearStart and int(j[0:4]) <= yearEnd:
            
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
            if os.path.exists(j[0:4]+".pkl"):
                #theDataFrame = pd.read_csv(str(j[0:4])+".csv",engine='python')
                theDataFrame = pd.read_pickle(str(j[0:4])+".pkl")
                theDataFrame.loc[len(theDataFrame.index)] = [site,j,fuel,variation,data1.percent[count]]
            else:
                theDataFrame = pd.DataFrame({"stationID": [site],"dateTime":[j],"fuelType":[fuel],"fuelVariation":[variation],"fuelData":[data1.percent[count]]})
            
            # Turns "theDataFrame" into a csv file
            theDataFrame.to_pickle(str(j[0:4])+".pkl")
        count+=1
    site+=1
    # Deletes site download file
    if os.path.exists(file):
        os.remove(file)
    else:
        print("The file does not exist")

'''
'''
for i in urlList:
    file = wget.download(i)
    head = ["date","fuel","percent"]
    data1 = pd.read_csv(file,sep="	",names=head,skiprows=1, usecols=[4,5,6])
    count = 0
    for j in data1.date:
        if int(j[0:4]) >= yearStart or int(j[0:4]) <= yearEnd:
            if "," in data1.fuel[count]:
                tempVariation = data1.fuel[count].split()
                fuel = tempVariation[0]
                variation = tempVariation[1]
            else:
                fuel = data1.fuel[count]
                variation = None
        
            if os.path.exists(j[0:4]+".csv"):
        #print('True')
        #head = ['stationID','dateTime','fuelType','fuelVariation','fuelData']
                theDataFrame = pd.read_csv(str(j[0:4])+".csv",engine='python')
        #tempDataFrame = pd.DataFrame({"stationID": [site],"dateTime":[i],"fuelType":[fuel],"fuelVariation":[variation],"fuelData":[data1.percent[count]]})
        #theDataFrame = pd.concat([dateDataFrame,tempDataFrame])
        #theDataFrame.append(tempDataFrame,ignore_index = True)
                theDataFrame.loc[len(theDataFrame.index)] = [site,j,fuel,variation,data1.percent[count]]
            else:
        #print('False')
                theDataFrame = pd.DataFrame({"stationID": [site],"dateTime":[j],"fuelType":[fuel],"fuelVariation":[variation],"fuelData":[data1.percent[count]]})
            theDataFrame.to_csv(str(i[0:4])+".csv",index=False)
            count+=1
    #theDataFrame.to_csv(str(i[0:4])+".csv",index=False)
    
#print(data1.date[0][0:4])
#theDataFrame.to_csv('fuel_data.csv',index=False)
        if os.path.exists(file):
            os.remove(file)
        else:
            print("The file does not exist")

'''
'''
for i in urlList:
    #print(len(i))
    if count == 0:
        file = wget.download(i)
        head = ["date","fuel","percent"]
        data1 = pd.read_csv(file,names=head,skiprows=1, usecols=[4,5,6],delim_whitespace=True)
        print(data1.date)
    count +=1
'''
'''   
    datesTemp = []
    for j in data1.date:
        datesTemp.append(j)
    dates.append(datesTemp)

    fuelTypeTemp = []
    fuelVariantTemp = []
    for k in data1.fuel:
        if "," in k:
            tempList = k.split()
            fuelTypeTemp.append(tempList[0])
            fuelVariantTemp.append(tempList[1])
        else:
            fuelTypeTemp.append(k)
    fuelType.append(fuelTypeTemp)
    fuelVariation.append(fuelVariantTemp)

    fuelDataTemp = []
    for l in data1.percent:
        fuelDataTemp.append(l)
    fuelData.append(fuelDataTemp)

    if os.path.exists(file):
        os.remove(file)
    else:
        print("The file does not exist")


# Puts data into dataframes and then is converted to a binary file (pickle)
siteFile = pd.DataFrame({"Station": stationIDList})
dataFile = pd.DataFrame({"StationID": siteID,"Date":dates,"Fuel_Type":fuelType,"Fuel_Variation":fuelVariation,"Fuel_Moisture":fuelData})
print(siteFile.Station)
siteFile.to_pickle('site_ID_data',index=False)
dataFile.to_pickle('fuel_data',index=False)
'''




