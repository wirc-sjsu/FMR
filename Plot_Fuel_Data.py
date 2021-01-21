# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 18:24:35 2021

@author: jackr
"""

# Import libraries
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as md
import datetime
import numpy as np


currentYear = 2000
endYear = 2020
stationID = 179
fuel = "Chamise"
variation = "New"

fuelList = []
datesList = []

while currentYear <= endYear:
    if os.path.exists(str(currentYear)+".pkl"):
        yearDataFrame = pd.read_pickle(str(currentYear)+".pkl")
        for i in range(len(yearDataFrame.stationID)):
            if yearDataFrame.stationID[i] == stationID:
                #print("fuel Type:",yearDataFrame.fuelType[i])
                #print("fuel Variation",yearDataFrame.fuelVariation[i])
                if yearDataFrame.fuelType[i] == fuel:
                    #print("2")
                    if yearDataFrame.fuelVariation[i] == variation:
                        fuelList.append(yearDataFrame.fuelData[i])
                        datesList.append(yearDataFrame.dateTime[i])
                        continue
    else:
        print(str(currentYear)+".pkl does not exist")
    currentYear+=1

datesList = pd.to_datetime(datesList,format='%Y-%m-%d')
df = pd.DataFrame(list(zip(datesList,fuelList)),columns = ["dateTime", "fuelValue"])
df = df.sort_values(by='dateTime')

#plt.plot(datesList,fuelList)
#datesList = pd.to_datetime(datesList,format='%Y-%m-%d')
dateMin = np.datetime64(datesList[0],'Y')
dateMax = np.datetime64(datesList[-1],'Y') + np.timedelta64(1, 'Y')
fig, ax = plt.subplots()
ax.plot(df.dateTime,df.fuelValue)
ax.grid(True)
#dateMin = str(datesList[0])[0:4]
#dateMax = str(datesList[len(datesList)-1])[0:4]
ax.set_xlim(pd.Timestamp(df.dateTime[0]),pd.Timestamp(df.dateTime[len(df.dateTime)-1]))

#fig.autofmt_xdate()
#ax.set_xlim([datetime.date(2000, 1, 1), datetime.date(2020, 12, 30)])
#ax.xaxis.set_major_locator(md.YearLocator())
#ax.xaxis.set_minor_locator(md.MonthLocator())
#ax.xaxis.set_major_formatter(md.DateFormatter("\n%Y"))
#ax.xaxis.set_minor_formatter(md.DateFormatter("%b"))
#plt.setp(ax.xaxis.get_minorticklabels(),size=12,rotation=45)
#ax.tick_params(axis='x', length = 10, width = 1)
#ax.axes.xaxis.set_ticklabels([])
#plt.setp(ax.yaxis.get_majorticklabels(),size=12)

plt.show()