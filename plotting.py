import datetime as dt
from dateutil.relativedelta import *
import logging
import pandas as pd
import matplotlib.dates as md
import matplotlib.pyplot as plt
import numpy as np
from utils import *


# Averages NaN values between two points (e.g., [1,Nan,Nan,2] --> [1,1.333,1.666,2])
#
# @param data - list or 1D-array of data
#
# @return list or 1D-array where NaN values between number values exist 
#
def interp_continuous(data):
    tempData = data.copy()
    for i in range(len(tempData)):
        if i == 0 or i == len(tempData)-1:
            if tempData[i] == 0:
                tempData[i] = np.nan
                continue
        
        if tempData[i] == 0:
            if tempData[i-1] == np.nan:
                tempData[i] = np.nan
            else:
                count = 3
                for j in range(i+1,len(tempData)):
                    if tempData[j] != 0:
                        #tempData[i] = np.mean([tempData[i-1],tempData[j]])
                        tempValues = np.linspace(tempData[i-1],tempData[j],count)
                        tempValues = tempValues[1:-1]
                        l = i
                        for k in tempValues:
                            tempData[l] = k
                            l+=1
                        break
                    elif j == len(tempData)-1:
                        if tempData[j] == 0:
                            tempData[i] = np.nan
                            break
                    count+=1
    return tempData


# Basic line plot for each site/fuelType/fuelVariation
#
# @ Param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
# @ Param outliers - boolean to include or not the outliers (points outside of [0,400] range)
#
def plot_lines(dataFrame, outliers=False):
    if dataFrame is None:
        print("dataFrame not provided")
        return 
    if not outliers:
        dataFrame = filter_outliers(dataFrame)
    dataFrame['fuel_type'] = dataFrame['fuel_type'].fillna('None').str.lower()
    dataFrame['fuel_variation'] = dataFrame['fuel_variation'].fillna('None').str.lower()
    df = dataFrame.groupby(['site_number','fuel_type','fuel_variation','date']).mean()
    mids = df.index
    # Dropping one level from multi index (date) and find all the unique combinations of the other levels
    combos = mids.droplevel('date').unique()
    if len(combos) < 50:
        fig, ax = plt.subplots(figsize=(17,9))
        legend = []
        for combo in combos:
            x = pd.to_datetime(df.loc[combo,:].index)
            y = df.loc[combo,:].values
            ax.plot(x,y,'.-')
            legend.append('{} - {} - {}'.format(*combo))
        ax.set_ylabel("Fuel Mositure (%)", fontsize = 15)
        ax.set_xlabel("Time (Years)", fontsize = 15)
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


# Standard deviation plot for each fuelType/fuelVariation (averaging all sites)
#
# @ Param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
# @ Param outliers - boolean to include or not the outliers (points outside of [0,400] range)
#
def plot_lines_mean(dataFrame, outliers=False):
    if dataFrame is None:
        print("dataFrame not provided")
        return 
    if not outliers:
        dataFrame = filter_outliers(dataFrame)
    dataFrame['fuel_type'] = dataFrame['fuel_type'].fillna('None').str.lower()
    dataFrame['fuel_variation'] = dataFrame['fuel_variation'].fillna('None').str.lower()
    df = dataFrame.groupby(['fuel_type','fuel_variation',dataFrame.date.dt.year, dataFrame.date.dt.month]).agg(['mean','std'])
    df.index.names = ['fuel_type','fuel_variation','year','month']
    mid = df.index
    year_combos = mid.droplevel('month').unique()
    combos = year_combos.droplevel('year').unique()
    fig, ax = plt.subplots(figsize=(17,9))
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
    ax.set_xlabel("Time (Years)", fontsize = 15)
    ax.tick_params(axis='both', length = 10, width = 1, labelsize=13)
    ax.xaxis.set_major_locator(md.YearLocator())
    ax.xaxis.set_minor_locator(md.MonthLocator(bymonth=[7]))
    ax.xaxis.set_major_formatter(md.DateFormatter("\n%Y"))
    ax.xaxis.set_minor_formatter(md.DateFormatter("%b"))
    plt.grid(True)
    plt.legend(legend,loc='upper left')
    plt.xticks(rotation = 45)
    plt.show()


# Bar plot that shows mean and standard devaition values for all the data each year unless monthly paramter is set to True.
#
# @ Param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
# @ Param monthly - boolean to do yearly or monthly bars
# @ Param outliers - boolean to include or not the outliers (points outside of [0,400] range)
#
def plot_bars_mean(dataFrame, monthly=False, outliers=False):
    if dataFrame is None:
        print("dataFrame not provided")
        return 
    if not outliers:
        dataFrame = filter_outliers(dataFrame)
    dataFrame['fuel_type'] = dataFrame['fuel_type'].fillna('None').str.lower()
    dataFrame['fuel_variation'] = dataFrame['fuel_variation'].fillna('None').str.lower()
    if monthly:
        df = dataFrame.groupby([dataFrame.date.dt.year,dataFrame.date.dt.month]).agg(['mean','std'])
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
    fig, ax = plt.subplots(figsize=(17,9))
    plt.bar(dates,means,width=width,alpha=.5)
    plt.bar(dates,stds,width=width,alpha=.5)
    ax.set_ylabel("Fuel Mositure (%)", fontsize = 15)
    ax.set_xlabel("Time (Years)", fontsize = 15)
    ax.tick_params(axis='both', length = 10, width = 1, labelsize=13)
    ax.xaxis.set_major_locator(md.YearLocator())
    ax.xaxis.set_minor_locator(md.MonthLocator(bymonth=[7]))
    ax.xaxis.set_major_formatter(md.DateFormatter("\n%Y"))
    ax.xaxis.set_minor_formatter(md.DateFormatter("%b"))
    plt.legend(['Mean','Std'],loc='upper left')
    plt.xticks(rotation = 45)
    plt.show()
    

# Line plot showing the average, all time minimum, and current year's FMC values
#
# @param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
# @param siteName - the name if the site being observed
# @param outliers - boolean to include or not the outliers (points outside of [0,400] range)
#
def plot_biweekly_avg_min(dataFrame,siteName,outliers=False):
    if dataFrame is None:
        print("dataFrame not provided")
        return 
    if len(dataFrame.site_number.unique()) > 1:
        print("Can only procees one station.")
        print(f"Total number of stations: {len(dataFrame.site_number.unique())}")
        return
    if not outliers:
        dataFrame = filter_outliers(dataFrame)
    # Change all fuel variations descritors that are NaN to the string "None"
    dataFrame.fuel_variation[dataFrame.fuel_variation.isna()] = "None"
    minYear = min(dataFrame.date.dt.year)
    maxYear = max(dataFrame.date.dt.year)
    # Loops through each fuel type (Chamise, Manzanita, Sagebrush, etc)
    for i in dataFrame.fuel_type.unique():
        # Creates a daraframe only containing one of the fuel types
        tempLFMC = dataFrame[dataFrame.fuel_type == i].reset_index(drop=True)
        # Loops through each of the fuel variations (New Growth, Old Growth, etc)
        for j in tempLFMC.fuel_variation.unique():
            # Creates a dataframe with data from only the current year
            newLFMC = tempLFMC[np.logical_and(tempLFMC.fuel_variation.str.lower() == j.lower(),tempLFMC.date.dt.year==maxYear)].reset_index(drop=True)
            # Creates a dataframe with data from every year that does not include the present year
            oldLFMC = tempLFMC[np.logical_and(tempLFMC.date.dt.year.between(minYear,maxYear-1),tempLFMC.fuel_variation.str.lower() == j.lower())].reset_index(drop=True)
            # Arrays to hold the region's average FMC, all time minimum FMC, and the current year's monthly averaged FMC
            avgs = np.zeros(25)
            mins = np.zeros(25)
            current = np.zeros(25)
            # The month being observed (1-12)
            cMonth = 1
            # All days below this value are the first half of a month, the days after this value are the last half of a month
            cDay = 14
            # Loops through biweekly values (e.g., [1,2] where 1 is the first half of month 1 and 2 in the second half of month 1)
            for k in range(1,26):
                # If k is an even number, you are getting data for the second half of cMonth. cMonth will also be incremented by 1
                if k % 2 == 0:
                    # If there is no data for the 2 weeks in the current year, 
                    # the value for that 2 week period will be 0 (e.g., current[k-1] = 0)
                    if newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day>cDay)].percent.size < 1:
                        pass
                    # If there is data for the 2 week period in the current year, get the average FMC for that period
                    else:
                        current[k-1] = np.mean(newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day>cDay)].percent)
                    # If there is no data for the 2 week period form previous years, 
                    # the minimum and average values for that 2 week period will be 0 (e.g., avgs[k-1] = 0)
                    if len(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent) < 1:
                        pass
                    # If there is data for the 2 week period in the current year, get the monthly average and all time low FMC for that period
                    else:
                        avgs[k-1] = np.mean(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent)
                        mins[k-1] = min(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent)
                    # Increments the current month by 1
                    cMonth+=1
                # If k is an odd number, you are getting data for the first half of cMonth
                else:
                    # If there is no data for the 2 week period in the current year, 
                    # the value for that 2 week period will be 0 (e.g., current[k-1] = 0)
                    if newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day<=cDay)].percent.size < 1:
                        current[k-1] = 0
                    # If there is data for the 2 week period in the current year, get the average FMC for that period
                    else:
                        current[k-1] = np.mean(newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day<=cDay)].percent)
                    # If there is no data for the 2 week period form previous years, 
                    # the minimum and average values for that 2 week period will be 0 (e.g., avgs[k-1] = 0)
                    if len(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent) < 1:
                        avgs[k-1] = 0
                        mins[k-1] = 0
                    # If there is data for the 2 week period in the current year, get the monthly average and all time low FMC for that period
                    else:
                        avgs[k-1] = np.mean(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent)
                        mins[k-1] = min(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent)
            # Sets all values less than 1 to NaNs
            current_point = [np.nan if x<1 else x for x in current]
            # Smooths out lines (if there are any gaps between points, the interp_continuous function connects the points)
            current_conti = interp_continuous(current)
            avgs = interp_continuous(avgs)
            mins = interp_continuous(mins)
            # Plot the Average, Minimum, and the Current Year's FMC values
            fig, ax = plt.subplots(figsize=(17,7))
            ax.plot(range(1,26),avgs,"--",color="green",label="Average Values",lw=3)
            ax.plot(range(1,26),mins,color="red",label="Minimum Values",lw=3)
            ax.plot(range(1,26),current_point,color="blue",marker=".",markersize=15,label=f"{maxYear} Values",lw=3)
            ax.plot(range(1,26),current_conti,color="blue",lw=3)
            plt.xticks(np.arange(1, 26, 2), ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],fontsize=15)
            plt.yticks(fontsize=15)
            plt.grid(True)
            plt.xlabel("Time (Bi-weekly)",fontsize=20)
            plt.ylabel("LFMC (%)",fontsize=20)
            fig.suptitle(f"{siteName} - {i}, {j}", x= 0.5, y =0.96,fontsize=25,fontweight='bold')
            plt.title(f"{minYear} - {maxYear}",fontsize=15)
            plt.legend(fontsize=15)
            plt.grid(True)
 

# Line plot showing the average, all time maximum, and current year's FMC values
#
# @param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
# @param siteName - the name if the site being observed
# @param outliers - boolean to include or not the outliers (points outside of [0,400] range)
#
def plot_biweekly_avg_max(dataFrame,siteName,outliers=False):
    if dataFrame is None:
        print("dataFrame not provided")
        return 
    if len(dataFrame.site_number.unique()) > 1:
        print("Can only procees one station.")
        print(f"Total number of stations: {len(dataFrame.site_number.unique())}")
        return
    if not outliers:
        dataFrame = filter_outliers(dataFrame)
    # Change all fuel variations descritors that are NaN to the string "None"
    dataFrame.fuel_variation[dataFrame.fuel_variation.isna()] = "None"
    minYear = min(dataFrame.date.dt.year)
    maxYear = max(dataFrame.date.dt.year)
    # Loops through each fuel type (Chamise, Manzanita, Sagebrush, etc)
    for i in dataFrame.fuel_type.unique():
        # Creates a daraframe only containing one of the fuel types
        tempLFMC = dataFrame[dataFrame.fuel_type == i].reset_index(drop=True)
        # Loops through each of the fuel variations (New Growth, Old Growth, etc)
        for j in tempLFMC.fuel_variation.unique():
            # Creates a dataframe with data from only the current year
            newLFMC = tempLFMC[np.logical_and(tempLFMC.fuel_variation.str.lower() == j.lower(),tempLFMC.date.dt.year==maxYear)].reset_index(drop=True)
            # Creates a dataframe with data from every year that does not include the present year
            oldLFMC = tempLFMC[np.logical_and(tempLFMC.date.dt.year.between(minYear,maxYear-1),tempLFMC.fuel_variation.str.lower() == j.lower())].reset_index(drop=True)
            # Arrays to hold the region's average FMC, all time minimum FMC, and the current year's monthly averaged FMC
            avgs = np.zeros(25)
            maxs = np.zeros(25)
            current = np.zeros(25)
            # The month being observed (1-12)
            cMonth = 1
            # All days below this value are the first half of a month, the days after this value are the last half of a month
            cDay = 14
            # Loops through biweekly values (e.g., [1,2] where 1 is the first half of month 1 and 2 in the second half of month 1)
            for k in range(1,26):
                # If k is an even number, you are getting data for the second half of cMonth. cMonth will also be incremented by 1
                if k % 2 == 0:
                    # If there is no data for the 2 weeks in the current year, 
                    # the value for that 2 week period will be 0 (e.g., current[k-1] = 0)
                    if newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day>cDay)].percent.size < 1:
                        pass
                    # If there is data for the 2 week period in the current year, get the average FMC for that period
                    else:
                        current[k-1] = np.mean(newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day>cDay)].percent)
                    # If there is no data for the 2 week period form previous years, 
                    # the minimum and average values for that 2 week period will be 0 (e.g., avgs[k-1] = 0)
                    if len(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent) < 1:
                        pass
                    # If there is data for the 2 week period in the current year, get the monthly average and all time high FMC for that period
                    else:
                        avgs[k-1] = np.mean(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent)
                        maxs[k-1] = max(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent)
                    # Increments the current month by 1
                    cMonth+=1
                # If k is an odd number, you are getting data for the first half of cMonth
                else:
                    # If there is no data for the 2 week period in the current year, 
                    # the value for that 2 week period will be 0 (e.g., current[k-1] = 0)
                    if newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day<=cDay)].percent.size < 1:
                        current[k-1] = 0
                    # If there is data for the 2 week period in the current year, get the average FMC for that period
                    else:
                        current[k-1] = np.mean(newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day<=cDay)].percent)
                    # If there is no data for the 2 week period form previous years, 
                    # the minimum and average values for that 2 week period will be 0 (e.g., avgs[k-1] = 0)
                    if len(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent) < 1:
                        pass
                    # If there is data for the 2 week period in the current year, get the monthly average and all time high FMC for that period
                    else:
                        avgs[k-1] = np.mean(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent)
                        maxs[k-1] = max(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent)
            # Sets all values less than 1 to NaNs
            current_point = [np.nan if x<1 else x for x in current]
            # Smooths out lines (if there are any gaps between points, the interp_continuous function connects the points)
            current_conti = interp_continuous(current)
            avgs = interp_continuous(avgs)
            maxs = interp_continuous(maxs)
            # Plot the Average, Minimum, and the Current Year's FMC values
            fig, ax = plt.subplots(figsize=(17,7))
            ax.plot(range(1,26),avgs,"--",color="green",label="Average Values",lw=3)
            ax.plot(range(1,26),maxs,color="red",label="Maximum Values",lw=3)
            ax.plot(range(1,26),current_point,color="blue",marker=".",markersize=15,label=f"{maxYear} Values",lw=3)
            ax.plot(range(1,26),current_conti,color="blue",lw=3)
            plt.xticks(np.arange(1, 26, 2), ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],fontsize=15)
            plt.yticks(fontsize=15)
            plt.grid(True)
            plt.xlabel("Time (Bi-weekly)",fontsize=20)
            plt.ylabel("LFMC (%)",fontsize=20)
            fig.suptitle(f"{siteName} - {i}, {j}", x= 0.5, y =0.96,fontsize=25,fontweight='bold')
            plt.title(f"{minYear} - {maxYear}",fontsize=15)
            plt.legend(fontsize=15)
            plt.grid(True)


# Line plot showing the average, the standard deviation, and current year's FMC values
#
# @param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
# @param siteName - the name if the site being observed
# @param outliers - boolean to include or not the outliers (points outside of [0,400] range)
#
def plot_biweekly_avg_std(dataFrame,siteName,outliers=False):
    if dataFrame is None:
        print("dataFrame not provided")
        return 
    if len(dataFrame.site_number.unique()) > 1:
        print("Can only procees one station.")
        print(f"Total number of stations: {len(dataFrame.site_number.unique())}")
        return
    if not outliers:
        dataFrame = filter_outliers(dataFrame)
    # Change all fuel variations descritors that are NaN to the string "None"
    dataFrame.fuel_variation[dataFrame.fuel_variation.isna()] = "None"
    minYear = min(dataFrame.date.dt.year)
    maxYear = max(dataFrame.date.dt.year)
    # Loops through each fuel type (Chamise, Manzanita, Sagebrush, etc)
    for i in dataFrame.fuel_type.unique():
        # Creates a daraframe only containing one of the fuel types
        tempLFMC = dataFrame[dataFrame.fuel_type == i].reset_index(drop=True)
        # Loops through each of the fuel variations (New Growth, Old Growth, etc)
        for j in tempLFMC.fuel_variation.unique():
            # Creates a dataframe with data from only the current year
            newLFMC = tempLFMC[np.logical_and(tempLFMC.fuel_variation.str.lower() == j.lower(),tempLFMC.date.dt.year==maxYear)].reset_index(drop=True)
            # Creates a dataframe with data from every year that does not include the present year
            oldLFMC = tempLFMC[np.logical_and(tempLFMC.date.dt.year.between(minYear,maxYear-1),tempLFMC.fuel_variation.str.lower() == j.lower())].reset_index(drop=True)
            # Arrays to hold the region's average FMC, all time minimum FMC, and the current year's monthly averaged FMC
            avgs = np.zeros(25)
            stds = np.zeros(25)
            current = np.zeros(25)
            # The month being observed (1-12)
            cMonth = 1
            # All days below this value are the first half of a month, the days after this value are the last half of a month
            cDay = 14
            # Loops through biweekly values (e.g., [1,2] where 1 is the first half of month 1 and 2 in the second half of month 1)
            for k in range(1,26):
                # If k is an even number, you are getting data for the second half of cMonth. cMonth will also be incremented by 1
                if k % 2 == 0:
                    # If there is no data for the 2 weeks in the current year, 
                    # the value for that 2 week period will be 0 (e.g., current[k-1] = 0)
                    if newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day>cDay)].percent.size < 1:
                        pass
                    # If there is data for the 2 week period in the current year, get the average FMC for that period
                    else:
                        current[k-1] = np.mean(newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day>cDay)].percent)
                    # If there is no data for the 2 week period form previous years, 
                    # the minimum and average values for that 2 week period will be 0 (e.g., avgs[k-1] = 0)
                    if len(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent) < 1:
                        pass
                    # If there is data for the 2 week period in the current year, get the monthly average and all time high FMC for that period
                    else:
                        avgs[k-1] = np.mean(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent)
                        stds[k-1] = np.std(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent)
                    # Increments the current month by 1
                    cMonth+=1
                # If k is an odd number, you are getting data for the first half of cMonth
                else:
                    # If there is no data for the 2 week period in the current year, 
                    # the value for that 2 week period will be 0 (e.g., current[k-1] = 0)
                    if newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day<=cDay)].percent.size < 1:
                        current[k-1] = 0
                    # If there is data for the 2 week period in the current year, get the average FMC for that period
                    else:
                        current[k-1] = np.mean(newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day<=cDay)].percent)
                    # If there is no data for the 2 week period form previous years, 
                    # the minimum and average values for that 2 week period will be 0 (e.g., avgs[k-1] = 0)
                    if len(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent) < 1:
                        pass
                    # If there is data for the 2 week period in the current year, get the monthly average and all time high FMC for that period
                    else:
                        avgs[k-1] = np.mean(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent)
                        stds[k-1] = np.std(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent)
            # Sets all values less than 1 to NaNs
            current_point = [np.nan if x<1 else x for x in current]
            # Smooths out lines (if there are any gaps between points, the interp_continuous function connects the points)
            current_conti = interp_continuous(current)
            avgs = interp_continuous(avgs)
            stds = interp_continuous(stds)
            # Plot the Average, Minimum, and the Current Year's FMC values
            fig, ax = plt.subplots(figsize=(17,7))
            ax.plot(range(1,26),avgs,"--",color="green",label="Average Values",lw=3)
            #ax.plot(range(1,26),stds,color="red",label="Maximum Values",lw=3)
            ax.fill_between(range(1,26), avgs - stds, avgs + stds, alpha=0.4, color="orange",label="Standard Deviation")
            ax.plot(range(1,26),current_point,color="blue",marker=".",markersize=15,label=f"{maxYear} Values",lw=3)
            ax.plot(range(1,26),current_conti,color="blue",lw=3)
            plt.xticks(np.arange(1, 26, 2), ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],fontsize=15)
            plt.yticks(fontsize=15)
            plt.grid(True)
            plt.xlabel("Time (Bi-weekly)",fontsize=20)
            plt.ylabel("LFMC (%)",fontsize=20)
            fig.suptitle(f"{siteName} - {i}, {j}", x= 0.5, y =0.96,fontsize=25,fontweight='bold')
            plt.title(f"{minYear} - {maxYear}",fontsize=15)
            plt.legend(fontsize=15)
            plt.grid(True)
            plt.show()


# Line plot showing the average, all time maximum, and current year's FMC values
#
# @param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
# @param siteName - the name if the site being observed
# @param outliers - boolean to include or not the outliers (points outside of [0,400] range)
#
def plot_monthly_avg_percentile(dataFrame,siteName,outliers=False):
    if dataFrame is None:
        print("dataFrame not provided")
        return 
    #if len(dataFrame.site_number.unique()) > 1:
    #    print("Can only procees one station.")
    #    print(f"Total number of stations: {len(dataFrame.site_number.unique())}")
    #    return
    if not outliers:
        dataFrame = filter_outliers(dataFrame)
    # Change all fuel variations descritors that are NaN to the string "None"
    dataFrame.fuel_variation[dataFrame.fuel_variation.isna()] = "None"
    minYear = min(dataFrame.date.dt.year)
    maxYear = max(dataFrame.date.dt.year)
    numOfMonths = 0
    for a in dataFrame.date.dt.year.unique():
        numOfMonths += len(dataFrame[dataFrame.date.dt.year==a].date.dt.month.unique())
    
    # Loops through each fuel type (Chamise, Manzanita, Sagebrush, etc)
    for i in dataFrame.fuel_type.unique():
        # Creates a daraframe only containing one of the fuel types
        tempLFMC = dataFrame[dataFrame.fuel_type == i].reset_index(drop=True)
        # Loops through each of the fuel variations (New Growth, Old Growth, etc)
        for j in tempLFMC.fuel_variation.unique():
            # Creates a dataframe with data from only the current year
            newLFMC = tempLFMC[tempLFMC.fuel_variation.str.lower() == j.lower()].reset_index(drop=True)
            # Arrays to hold the region's percentile values
            two = np.zeros(numOfMonths)
            five = np.zeros(numOfMonths)
            fifty = np.zeros(numOfMonths)
            eightyfive = np.zeros(numOfMonths)
            ninetyfive = np.zeros(numOfMonths)
            hundred = np.zeros(numOfMonths)
            dates = []
            # Create a datetime object  that can be easily iterable
            cYear = minYear
            cMonth = min(dataFrame[dataFrame.date.dt.year == minYear].date.dt.month.unique())
            cDate = dt.datetime(cYear, cMonth, 1)
            # Loops through monthly values
            print(numOfMonths)
            for k in range(0,numOfMonths):
                tempDf = newLFMC[np.logical_and(newLFMC.date.dt.year==cDate.year,newLFMC.date.dt.month==cDate.month)]
                if len(tempDf.percent) < 1:
                    pass
                else:
                    two[k] = np.percentile(tempDf.percent,2)
                    five[k] = np.percentile(tempDf.percent,5)
                    fifty[k] = np.percentile(tempDf.percent,50)
                    eightyfive[k] = np.percentile(tempDf.percent,85)
                    ninetyfive[k] = np.percentile(tempDf.percent,95)
                    hundred[k] = np.percentile(tempDf.percent,100)
                dates.append(cDate)
                cDate = cDate+relativedelta(months=+1)
            print("done")

            # Smooths out lines (if there are any gaps between points, the interp_continuous function connects the points)
            two = interp_continuous(two)
            five = interp_continuous(five)
            fifty = interp_continuous(fifty)
            eightyfive = interp_continuous(eightyfive)
            ninetyfive = interp_continuous(ninetyfive)
            hundred = interp_continuous(hundred)
            
            # Plot the Average, Minimum, and the Current Year's FMC values
            fig, ax = plt.subplots(figsize=(17,7))
            #ax.plot(range(1,26),stds,color="red",label="Maximum Values",lw=3)
            ax.fill_between(dates, two, five, alpha=0.4, color="red",label="2nd - 5th")
            ax.fill_between(dates, five, fifty, alpha=0.4, color="orange",label="5th - 50th")
            ax.fill_between(dates, fifty, eightyfive, alpha=0.4, color="yellow",label="50th - 85th")
            ax.fill_between(dates, eightyfive, ninetyfive, alpha=0.4, color="green",label="85th - 95th")
            ax.fill_between(dates, ninetyfive, hundred, alpha=0.4, color="blue",label="95th - 100th")
            

            #plt.xticks(np.arange(1, 26, 2), ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],fontsize=15)
            #plt.yticks(fontsize=15)
            plt.grid(True)
            plt.xlabel("Time (Monthly)",fontsize=20)
            plt.ylabel("LFMC (%)",fontsize=20)
            #fig.suptitle(f"{siteName} - {i}, {j}", x= 0.5, y =0.96,fontsize=25,fontweight='bold')
            plt.title(f"{minYear} - {maxYear}",fontsize=15)
            plt.legend(fontsize=15)
            plt.grid(True)
            plt.show()


# Line plot showing the average, the standard deviation, and current year's FMC values
#
# @param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
# @param siteName - the name if the site being observed
# @param outliers - boolean to include or not the outliers (points outside of [0,400] range)
#
def plot_biweekly_percentile(dataFrame,siteName,outliers=False):
    if dataFrame is None:
        print("dataFrame not provided")
        return 
    if len(dataFrame.site_number.unique()) > 1:
        print("Can only procees one station.")
        print(f"Total number of stations: {len(dataFrame.site_number.unique())}")
        return
    if not outliers:
        dataFrame = filter_outliers(dataFrame)
    # Change all fuel variations descritors that are NaN to the string "None"
    dataFrame.fuel_variation[dataFrame.fuel_variation.isna()] = "None"
    minYear = min(dataFrame.date.dt.year)
    maxYear = max(dataFrame.date.dt.year)
    # Loops through each fuel type (Chamise, Manzanita, Sagebrush, etc)
    for i in dataFrame.fuel_type.unique():
        # Creates a daraframe only containing one of the fuel types
        tempLFMC = dataFrame[dataFrame.fuel_type == i].reset_index(drop=True)
        # Loops through each of the fuel variations (New Growth, Old Growth, etc)
        for j in tempLFMC.fuel_variation.unique():
            # Creates a dataframe with data from only the current year
            newLFMC = tempLFMC[np.logical_and(tempLFMC.fuel_variation.str.lower() == j.lower(),tempLFMC.date.dt.year==maxYear)].reset_index(drop=True)
            # Creates a dataframe with data from every year that does not include the present year
            oldLFMC = tempLFMC[np.logical_and(tempLFMC.date.dt.year.between(minYear,maxYear-1),tempLFMC.fuel_variation.str.lower() == j.lower())].reset_index(drop=True)
            # Arrays to hold the region's average FMC, all time minimum FMC, and the current year's monthly averaged FMC
            two = np.zeros(25)
            five = np.zeros(25)
            fifty = np.zeros(25)
            eightyfive = np.zeros(25)
            ninetyfive = np.zeros(25)
            hundred = np.zeros(25)
            current = np.zeros(25)
            # The month being observed (1-12)
            cMonth = 1
            # All days below this value are the first half of a month, the days after this value are the last half of a month
            cDay = 14
            # Loops through biweekly values (e.g., [1,2] where 1 is the first half of month 1 and 2 in the second half of month 1)
            for k in range(0,25):
                # If k is an even number, you are getting data for the second half of cMonth. cMonth will also be incremented by 1
                if k % 2 == 0:
                    # If there is no data for the 2 weeks in the current year, 
                    # the value for that 2 week period will be 0 (e.g., current[k-1] = 0)
                    if newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day>cDay)].percent.size < 1:
                        pass
                    # If there is data for the 2 week period in the current year, get the average FMC for that period
                    else:
                        current[k] = np.mean(newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day>cDay)].percent)
                    # If there is no data for the 2 week period form previous years, 
                    # the minimum and average values for that 2 week period will be 0 (e.g., avgs[k-1] = 0)
                    if len(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent) < 1:
                        pass
                    # If there is data for the 2 week period in the current year, get the monthly average and all time high FMC for that period
                    else:
                        two[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent,2)
                        five[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent,5)
                        fifty[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent,50)
                        eightyfive[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent,85)
                        ninetyfive[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent,95)
                        hundred[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day>cDay)].percent,100)
                    # Increments the current month by 1
                    cMonth+=1
                # If k is an odd number, you are getting data for the first half of cMonth
                else:
                    # If there is no data for the 2 week period in the current year, 
                    # the value for that 2 week period will be 0 (e.g., current[k-1] = 0)
                    if newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day<=cDay)].percent.size < 1:
                        current[k] = 0
                    # If there is data for the 2 week period in the current year, get the average FMC for that period
                    else:
                        current[k] = np.mean(newLFMC[np.logical_and(newLFMC.date.dt.month == cMonth,newLFMC.date.dt.day<=cDay)].percent)
                    # If there is no data for the 2 week period form previous years, 
                    # the minimum and average values for that 2 week period will be 0 (e.g., avgs[k-1] = 0)
                    if len(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent) < 1:
                        pass
                    # If there is data for the 2 week period in the current year, get the monthly average and all time high FMC for that period
                    else:
                        two[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent,2)
                        five[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent,5)
                        fifty[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent,50)
                        eightyfive[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent,85)
                        ninetyfive[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent,95)
                        hundred[k] = np.percentile(oldLFMC[np.logical_and(oldLFMC.date.dt.month == cMonth,oldLFMC.date.dt.day<=cDay)].percent,100)
            # Sets all values less than 1 to NaNs
            current_point = [np.nan if x<1 else x for x in current]
            # Smooths out lines (if there are any gaps between points, the interp_continuous function connects the points)
            current_conti = interp_continuous(current)
            two = interp_continuous(two)
            five = interp_continuous(five)
            fifty = interp_continuous(fifty)
            eightyfive = interp_continuous(eightyfive)
            ninetyfive = interp_continuous(ninetyfive)
            hundred = interp_continuous(hundred)
            
            # Plot the Average, Minimum, and the Current Year's FMC values
            fig, ax = plt.subplots(figsize=(17,7))
            #ax.plot(range(1,26),stds,color="red",label="Maximum Values",lw=3)
            ax.fill_between(range(0,25), ninetyfive, hundred, alpha=0.4, color="blue",label="95th - 100th")
            ax.fill_between(range(0,25), eightyfive, ninetyfive, alpha=0.4, color="green",label="85th - 95th")
            ax.fill_between(range(0,25), fifty, eightyfive, alpha=0.4, color="yellow",label="50th - 85th")
            ax.fill_between(range(0,25), five, fifty, alpha=0.4, color="orange",label="5th - 50th")
            ax.fill_between(range(0,25), two, five, alpha=0.4, color="red",label="2nd - 5th")
            
            ax.plot(range(0,25),current_point,color="black",marker=".",markersize=15,label=f"{maxYear} Values",lw=3)
            ax.plot(range(0,25),current_conti,color="black",lw=3)
            plt.xticks(np.arange(0, 25, 2), ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],fontsize=15)
            plt.yticks(fontsize=15)
            plt.grid(True)
            plt.xlabel("Time (Bi-weekly)",fontsize=20)
            plt.ylabel("LFMC (%)",fontsize=20)
            fig.suptitle(f"{siteName} - {i}, {j}", x= 0.5, y =0.96,fontsize=25,fontweight='bold')
            plt.title(f"{minYear} - {maxYear}",fontsize=15)
            plt.legend(fontsize=15)
            plt.grid(True)
            plt.show()


# Bar plot that shows the fuel types found in the dataFrame
#
# @param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
#
def plot_yearly_obs(dataFrame):
    years = []
    for i in range(2000,2022):
        tempLFMC = dataFrame[dataFrame.date.dt.year == i].reset_index(drop=True)
        years.append(len(tempLFMC.percent))
    fig, ax = plt.subplots(figsize=(17,9))
    ax.bar(range(2000,2022),years)
    plt.xticks(range(2000,2022),rotation=45,fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel("Observations",fontsize=15,fontweight='bold')
    plt.xlabel("Time (Years)",fontsize=15,fontweight='bold')
    plt.ticklabel_format(style='plain', axis='y')
    plt.show()
    

def fuel_types(dataFrame):
    fig, ax = plt.subplots(figsize=(19,10))
    obs = []
    ftype = []
    for fuel in dataFrame.fuel_type.unique():
        obs.append(len(dataFrame[dataFrame.fuel_type == fuel]))
        ftype.append(fuel)
    obsDf = pd.DataFrame({"fuel_type":ftype,"obs":obs})
    obsDf = obsDf.sort_values(by="obs",ascending=False).reset_index(drop=True)
    print(obsDf)
    print(f"Fuel Type: {obsDf.obs[0]}")
    print(f"Number of Obs: {obsDf.fuel_type[0]}")
    ax.bar(range(len(obsDf.obs)),obsDf.obs)
    plt.xticks(range(len(obsDf.obs)),obsDf.fuel_type,rotation=35,horizontalalignment='right')
    ax.set_xlabel("Vegetation Types",fontsize=14)
    ax.set_ylabel("Number of Observations",fontsize=14)
    #plt.title(f"Number of Observations of Each Vegetation Type in the {regionName} Region from"+ 
    #          f" {min(df.date.dt.year.unique())} to {max(df.date.dt.year.unique())}",fontsize=20)
    plt.title(f"{min(dataFrame.date.dt.year.unique())} - {max(dataFrame.date.dt.year.unique())}",fontsize=20)
    for label in ax.yaxis.get_majorticklabels():
        label.set_fontsize(13)
    for label in ax.xaxis.get_majorticklabels():
        label.set_fontsize(13)  
    plt.show()
    

def plot_violin(dataFrame,stationList,stationName):
    if stationName == None or len([stationName]) > 1:
        print(f"Need a single station. {len(dataFrame.site_number.unique())} stations in dataset.")
        return
    if len(dataFrame.fuel_type.unique()) > 1:
        print("Too many fuel types in dataset")
        return
    
    fig, ax = plt.subplots(figsize=(19,10))
    tempDf = np.zeros(12)
    hold = []
    for i in range(1,len(tempDf)+1):
        if len(dataFrame[dataFrame.date.dt.month == i].percent) < 1:
            hold.append(np.array([0]))
        else:
            hold.append(dataFrame[dataFrame.date.dt.month == i].percent.values)
    plt.violinplot(hold,showmedians=True)
    plt.xticks(range(1,13),["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],fontsize=14)
    plt.xlabel("Time (Months)",fontsize=14)
    plt.ylabel("Moisture Content (%)",fontsize=14)
    for label in ax.yaxis.get_majorticklabels():
        label.set_fontsize(13)
    for label in ax.xaxis.get_majorticklabels():
        label.set_fontsize(13)  
    plt.suptitle(f"{stationList.site[stationName]} - {dataFrame.fuel_type[0]}, {dataFrame.fuel_variation[0]}",x= 0.52,y =0.96,fontsize=25,fontweight='bold')
    plt.title(f"{min(dataFrame.date.dt.year)} - {max(dataFrame.date.dt.year)}",fontsize=15)
    plt.show()
    

def plot_fisk(dataFrame,stationList,stationName):
    if stationName == None or len([stationName]) > 1:
        print(f"Need a single station. {len(dataFrame.site_number.unique())} stations in dataset.")
        return
    if len(dataFrame.fuel_type.unique()) > 1:
        print("Too many fuel types in dataset")
        return
    fig, ax = plt.subplots(figsize=(19,10))
    tempDf = np.zeros(12)
    hold = []
    for i in range(1,len(tempDf)+1):
        if len(dataFrame[dataFrame.date.dt.month == i].percent) < 1:
            hold.append(np.array([0]))
        else:
            hold.append(dataFrame[dataFrame.date.dt.month == i].percent.values)
    plt.boxplot(hold)
    plt.xticks(range(1,13),["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],fontsize=14)
    plt.xlabel("Time (Months)",fontsize=14)
    plt.ylabel("Moisture Content (%)",fontsize=14)
    for label in ax.yaxis.get_majorticklabels():
        label.set_fontsize(13)
    for label in ax.xaxis.get_majorticklabels():
        label.set_fontsize(13)  
    plt.suptitle(f"{stationList.site[stationName]} - {dataFrame.fuel_type[0]}, {dataFrame.fuel_variation[0]}",x= 0.52,y =0.96,fontsize=25,fontweight='bold')
    plt.title(f"{min(dataFrame.date.dt.year)} - {max(dataFrame.date.dt.year)}",fontsize=15)
    plt.show()