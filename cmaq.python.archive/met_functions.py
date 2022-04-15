### Functions for NCEP Project
### Author: Benjamin Yang

# Import modules
import pandas as pd
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from mpl_toolkits.basemap import Basemap
#import cartopy
import datetime
from datetime import timedelta
import pytz
import copy
import time
import os
import sys
#import wrf

# read the following functions
# Read met data
def readWRFmet(infile):
    metlist = ['T2','PSFC','U10','V10','Q2','RAINNC']
 #   metlist = ['T2']
 # if model==1:
 #       for k in metlist:
 #           wrfmet[k] = wrf.combine_files(infile,k,wrf.ALL_TIMES)
    wrfmet = {}
    for k in metlist:
        wrfmet[k] = infile.variables[k][:,:,:]
    return wrfmet

# Read latitude and longitude from file into numpy arrays
def naive_fast(latvar,lonvar,lat0,lon0):
    latvals = latvar[:]
    lonvals = lonvar[:]
    ny,nx = latvals.shape
    dist_sq = (latvals-lat0)**2 + (lonvals-lon0)**2
    minindex_flattened = dist_sq.argmin()  # 1D index of min element
    iy_min,ix_min = np.unravel_index(minindex_flattened, latvals.shape)
    return int(iy_min),int(ix_min)

def DateTime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta

#Normalized Mean Bias - NMB
def nmb(df,name_var1,name_var2):  #var1 is model var2 is observed
    df_new=pd.DataFrame()
    df_new[name_var1]=df[name_var1]
    df_new[name_var2]=df[name_var2]
    df_new['dif_var']=df_new[name_var1]-df_new[name_var2]
    NMB=round((df_new['dif_var'].sum()/df_new[name_var2].sum())*100)
    return NMB

#Normalized Mean Error - NME
def nme(df,name_var1,name_var2):  #var1 is model var2 is observed
    df_new=pd.DataFrame()
    df_new[name_var1]=df[name_var1]
    df_new[name_var2]=df[name_var2]
    df_new['dif_var']= abs(df_new[name_var1]-df_new[name_var2])
    NME=round((df_new['dif_var'].sum()/df_new[name_var2].sum())*100)
    return NME

#Root Mean Squared Error - RMSE
def rmse(df,name_var1,name_var2):  #var1 is model var2 is observed
    df_new=pd.DataFrame()
    df_new[name_var1]=df[name_var1]
    df_new[name_var2]=df[name_var2]
    df_new['dif_var']= (df_new[name_var1]-df_new[name_var2])**(2)
    RMSE=round((df_new['dif_var'].sum()/len(df_new.index))**(0.5))
    return RMSE

#Coefficient of Determination - r^2
def r2(df,name_var1,name_var2):
    df_new=pd.DataFrame()
    df_new[name_var1]=df[name_var1]
    df_new[name_var2]=df[name_var2]
    top_var= ((df_new[name_var1]-np.mean(df_new[name_var1])) * (df_new[name_var2]-np.mean(df_new[name_var2]))).sum()
    bot_var= (((df_new[name_var1]-np.mean(df_new[name_var1]))**2).sum() * ((df_new[name_var2]-np.mean(df_new[name_var2]))**2).sum())**(.5)
    r_squared=round(((top_var/bot_var)**2),2)
    return r_squared

#Calculates and combines into a labeled dataframe
def stats(df,name_var1,name_var2,var_units):
    NMB = nmb(df,name_var1,name_var2)
    NME = nme(df,name_var1,name_var2)
    RMSE = rmse(df,name_var1,name_var2)
    r_squared = r2(df,name_var1,name_var2)
    g = pd.DataFrame([NMB,NME,RMSE,r_squared])
    g.index = ["NMB [%]", "NME [%]", "RMSE [%s]" %var_units, "R^2 [-]"]
    g.columns = [name_var1]
    return g

# Calculate mean
def mean_stat(df,name_var):   
    mean_value = round(np.nanmean(df[name_var]),1)
    return mean_value

# Define function for getting dates between start and end
def perdelta(start, end, delta):
    curr = start
    while curr <= end:
        yield curr
        curr += delta
        
# movingaverage 
def movingaverage(values,window):
    weights = np.repeat(1.0, window)/window
    smas = np.convolve(values,weights,'valid')
    return smas

