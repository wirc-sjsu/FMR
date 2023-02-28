
# Import Necessary Functions
import datetime as dt
from dateutil.relativedelta import *
import logging
import pandas as pd
import matplotlib.dates as md
import matplotlib.pyplot as plt
import numpy as np
from utils import *


# Plotting Functions

# Basic line plot for each site/fuelType/fuelVariation
#
# @ param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
#
def plot_lines(dataFrame):
    # Quit plotting if no data is available
    if len(dataFrame.head(1)["date"]) < 1:
        print("dataFrame has no data")
        return
    dataFrame['fuel_type'] = dataFrame['fuel_type'].fillna('None').str.lower()
    dataFrame['fuel_variation'] = dataFrame['fuel_variation'].fillna('None').str.lower()
    df = dataFrame.groupby(['site_number','fuel_type','fuel_variation','date']).mean()
    mids = df.index
    # Dropping one level from multi index (date) and find all the unique combinations of the other levels
    combos = mids.droplevel('date').unique()
    if len(combos) < 50:
        fig, ax = plt.subplots(figsize=(14,9))
        plt.subplots_adjust(top=.9, bottom=0.15)
        legend = []
        for combo in combos:
            x = pd.to_datetime(df.loc[combo,:].index)
            y = df.loc[combo,:].values
            ax.plot(x,y,'.-')
            legend.append('{} - {} - {}'.format(*combo))
        ax.set_ylabel("Fuel Mositure (%)", fontsize = 20)
        ax.set_xlabel("Time (Years)", fontsize = 20)
        ax.tick_params(axis='both', length = 10, width = 1, labelsize=15)
        ax.tick_params(axis='both', which='minor', labelsize=15)
        ax.xaxis.set_major_locator(md.YearLocator())
        ax.xaxis.set_minor_locator(md.MonthLocator(bymonth=[7]))
        ax.xaxis.set_major_formatter(md.DateFormatter("\n%Y"))
        ax.xaxis.set_minor_formatter(md.DateFormatter("%b"))
        plt.xticks(rotation = 45)
        plt.grid(True)
        plt.legend(legend,loc='upper left')
        plt.show()
    else:
        logging.error('Too many plots. Consider filtering data using get_data parameters.')
        
        
# Standard deviation plot for each fuelType/fuelVariation (averaging all sites)
#
# @ param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
#
def plot_lines_mean(dataFrame):
    # Quit plotting if no data is available
    if len(dataFrame.head(1)["date"]) < 1:
        print("dataFrame has no data")
        return
    dataFrame['fuel_type'] = dataFrame['fuel_type'].fillna('None').str.lower()
    dataFrame['fuel_variation'] = dataFrame['fuel_variation'].fillna('None').str.lower()
    df = dataFrame.groupby(['fuel_type','fuel_variation',dataFrame.date.dt.year, dataFrame.date.dt.month]).agg(['mean','std'])
    df.index.names = ['fuel_type','fuel_variation','year','month']
    mid = df.index
    year_combos = mid.droplevel('month').unique()
    combos = year_combos.droplevel('year').unique()
    fig, ax = plt.subplots(figsize=(14,9))
    plt.subplots_adjust(top=.9, bottom=0.15)
    legend = []
    if len(combos) >= 50:
        logging.error('Too many plots. Consider filtering data using get_data parameters.')
        return
    for combo in combos:
        combo_data = df.loc[combo,'percent']
        dates = pd.to_datetime(['{:04d}-{:02d}'.format(y,m) for y,m in df.loc[combo].index.to_numpy()])
        means = combo_data.values[:,0]
        stds = combo_data.values[:,1]
        ax.plot(dates, means, '.-')
        ax.fill_between(dates, means - stds, means + stds, alpha=0.2)
        legend.append('{} - {}'.format(*combo))
    ax.set_ylabel("Fuel Mositure (%)", fontsize = 20)
    ax.set_xlabel("Time (Years)", fontsize = 20)
    ax.tick_params(axis='both', length = 10, width = 1, labelsize=15)
    ax.tick_params(axis='both', which='minor', labelsize=15)
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
# @ param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
# @ param monthly - boolean to change from yearly to monthly bars
#
def plot_bars_mean(dataFrame, monthly=False):
    # Quit plotting if no data is available
    if len(dataFrame.head(1)["date"]) < 1:
        print("dataFrame has no data")
        return 
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
    fig, ax = plt.subplots(figsize=(14,9))
    plt.subplots_adjust(top=.9, bottom=0.15)
    plt.bar(dates,means,width=width,alpha=.5)
    plt.bar(dates,stds,width=width,alpha=.5)
    ax.set_ylabel("Fuel Mositure (%)", fontsize = 20)
    ax.set_xlabel("Time (Years)", fontsize = 20)
    ax.tick_params(axis='both', length = 10, width = 1, labelsize=15)
    ax.tick_params(axis='both', which='minor', labelsize=15)
    ax.xaxis.set_major_locator(md.YearLocator())
    ax.xaxis.set_minor_locator(md.MonthLocator(bymonth=[7]))
    ax.xaxis.set_major_formatter(md.DateFormatter("\n%Y"))
    ax.xaxis.set_minor_formatter(md.DateFormatter("%b"))
    plt.legend(['Mean','Std'],loc='upper left',prop={'size': 13})
    plt.xticks(rotation = 45)
    plt.show()
    

# Bar plot that shows the number of observations over the time period found in the dataFrame
#
# @param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
#
def plot_yearly_obs(dataFrame):
    # Quit plotting if no data is available
    if len(dataFrame.head(1)["date"]) < 1:
        print("dataFrame has no data")
        return 
    years = []
    minYear = min(dataFrame.date.dt.year)
    maxYear = max(dataFrame.date.dt.year)+1
    for i in range(minYear,maxYear):
        tempLFMC = dataFrame[dataFrame.date.dt.year == i].reset_index(drop=True)
        years.append(len(tempLFMC.percent))
    fig, ax = plt.subplots(figsize=(14,9))
    plt.subplots_adjust(top=.9, bottom=0.15)
    ax.bar(range(minYear,maxYear),years)
    plt.xticks(range(minYear,maxYear),rotation=45,fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel("Observations",fontsize=20)
    plt.xlabel("Time (Years)",fontsize=20)
    plt.ticklabel_format(style='plain', axis='y')
    plt.title(f"Number of Observations from {min(dataFrame.date.dt.year.unique())} - {max(dataFrame.date.dt.year.unique())}",fontsize=25)
    plt.show()
    

# Bar plot that shows the fuel types and number of observations of each fuel type found in the dataFrame
#
# @param dataFrame - pandas dataframe with the data to plot from get_data function in the FMDB.py script
#
def plot_fuel_types(dataFrame):
    # Quit plotting if no data is available
    if len(dataFrame.head(1)["date"]) < 1:
        print("dataFrame has no data")
        return 
    fig, ax = plt.subplots(figsize=(14,9))
    plt.subplots_adjust(top=.9, bottom=0.15)
    obs = []
    ftype = []
    for fuel in dataFrame.fuel_type.unique():
        obs.append(len(dataFrame[dataFrame.fuel_type == fuel]))
        ftype.append(fuel)
    obsDf = pd.DataFrame({"fuel_type":ftype,"obs":obs})
    obsDf = obsDf.sort_values(by="obs",ascending=False).reset_index(drop=True)
    
    if len(obsDf["fuel_type"].unique()) > 25:
        obsDf = obsDf.head(25)
    ax.bar(range(len(obsDf.obs)),obsDf.obs)
    plt.xticks(range(len(obsDf.obs)),obsDf.fuel_type,rotation=35,horizontalalignment='right',fontsize=15)
    plt.yticks(fontsize=15)
    ax.set_xlabel("Vegetation Types",fontsize=20)
    ax.set_ylabel("Number of Observations",fontsize=20)
    #for label in ax.yaxis.get_majorticklabels():
    #    label.set_fontsize(15)
    #for label in ax.xaxis.get_majorticklabels():
    #    label.set_fontsize(15)  
    plt.title(f"Fuel Type Sampling Observations from {min(dataFrame.date.dt.year.unique())} - {max(dataFrame.date.dt.year.unique())}",fontsize=25)
    plt.show()