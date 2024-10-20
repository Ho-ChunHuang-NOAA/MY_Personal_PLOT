#!/usr/bin/env python
# coding: utf-8

# In[69]:


import os
import numpy as np
import netCDF4 as netcdf
import re
import warnings
import logging
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors 
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys
import datetime
import shutil
import subprocess

import pandas as pd
import datetime as dts
from datetime import date, time, timedelta
from netCDF4 import Dataset
from matplotlib import dates

### NOTE: This code is still not able to produce a full 72 hours of graphs, it will instead produce
###       plots from either 06z or 12z until the day's end. Sorry about that!


#######################################################
##########      PLOTTING MODEL DATA          ##########
#######################################################


### Read data of all time step in once, then print one at a time
### PASSED ARGUMENTS

### envir options: prod | para6d | v70a1 | v70b1
### sel_var options: o3 | pm25
### sel_cyc options: 06 | 12

os.chdir("/Users/florawalchenbach/lapenta_project")

envir = 'v70b1'
sel_var = 'pm25'
sel_cyc = '12'
start_date = '20220614'
end_date = '20220614'


## EPA data is forward-averaged, NOAA data is back-averaged
if sel_cyc == '06':         
        cyc_shift = 6
        end = 24 - cyc_shift
else:
        cyc_shift = 12
        end = 24 - cyc_shift

    
if envir.lower() == "para6d":
    fig_exp="ncopara"+BC_fig_append
else:
    fig_exp=envir.lower()

script_dir=os.getcwd()
print("Script directory is "+script_dir)

user=os.environ['USER']

stmp_dir="/Users/florawalchenbach/lapenta_project"+user
if not os.path.exists(stmp_dir):
    os.mkdir(stmp_dir)

ptmp_dir="/Users/florawalchenbach/lapenta_project"+user
if not os.path.exists(ptmp_dir):
    os.mkdir(ptmp_dir)

log_dir=ptmp_dir+"/batch_logs"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

py_code=sys.argv[0]
nfind=py_code.find("py")
if nfind == -1:
    workid=py_code
else:
    workid=py_code[0:nfind-1]
working_dir=stmp_dir+"/"+envir+"_"+workid
if not os.path.exists(working_dir):
    os.makedirs(working_dir)

os.chdir(working_dir)

sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:]))
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:]))

obs_YMDH_date_format = "%Y%m%d%H"
YMDH_date_format = "%Y%m%d/%H"
YMD_date_format = "%Y%m%d"
YM_date_format = "%Y%m"
Y_date_format = "%Y"
M_date_format = "%m"
D_date_format = "%d"
H_date_format = "%H"
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

if sel_var == "all":
   var=[ "o3", "pm25" ]
elif sel_var == "o3":
   var=[ "o3" ]
elif sel_var == "pm25":
   var=[ "pm25" ]
else:
    print("input variable "+sel_var+" can not be recongized.")
    sys.exit()
num_var=len(var)
print("var length = "+str(num_var))

if sel_cyc == "all":
   cycle=[ "06", "12" ]
elif sel_cyc == "06":
   cycle=[ "06" ]
elif sel_cyc == "12":
   cycle=[ "12" ]
else:
    print("seletced cycle"+sel_cyc+" can not be recongized.")
    sys.exit()

warnings.filterwarnings('ignore')
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.formatter.useoffset'] = False
cbar_num_format = "%d"
plt.close('all') # close all figures

msg=datetime.datetime.now()
msg=msg - date_inc
grdcro2d_date=msg.strftime("%Y%m%d")
##
aqm_ver="v7.0"
if envir == "prod":
    comout="/Users/florawalchenbach/lapenta_project"
elif envir =="para6d":
    comout="/Users/florawalchenbach/lapenta_project"
elif envir =="v70a1":
    comout="/Users/florawalchenbach/lapenta_project"
elif envir =="v70b1":
    comout="/Users/florawalchenbach/lapenta_project"
else:
    print("Experiment is not recognized or defined in this program")
    sys.exit()

figout=stmp_dir

flag_proj="LambertConf"
if flag_proj == "LambertConf":
    regname = [   "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",   "ak",   "hi",  "can" ] 
    rlon0 = [ -161.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0, -166.0, -161.5, -141.0 ]
    rlon1 = [  -73.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0, -132.0, -153.1,  -60.0 ]
    rlat0 = [   14.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   53.2,   17.8,   38.0 ]
    rlat1 = [   72.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   71.2,   23.1,   70.0 ]
else:
    regname = [   "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",   "ak",   "hi",  "can" ] 
    rlon0 = [ -175.0, -124.0,  -100.0, -128.0,  -82.0, -125.0,  -95.0, -125.0, -105.0, -105.0, -170.0, -161.0, -141.0 ]
    rlon1 = [  -55.0,  -70.0,   -65.0,  -90.0,  -67.0, -103.0,  -79.0, -105.0,  -85.0,  -85.0, -130.0, -154.0,  -60.0 ]
    rlat0 = [    0.0,   22.0,    22.0,   24.5,   37.0,   38.0,   24.0,   30.0,   38.0,   24.0,   52.0,   18.0,   38.0 ]
    rlat1 = [   70.0,   51.0,    50.0,   54.5,   48.0,   52.0,   38.0,   45.0,   52.0,   40.0,   72.0,   23.0,   70.0 ]
xsize = [     10,     10,       8,      8,      8,      8,      8,      8,      8,      8,      8,      8,     10 ]
ysize = [      8,      8,       8,      8,      8,      8,      8,      8,      8,      8,      8,      8,      8 ]
if 1 == 2:
    iplot = [      1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      0,      0,      0 ]
else:
    iplot = [      0,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0 ]
num_reg=len(iplot)


### Change region by changing location of "1" above


date=sdate
while date <= edate:
    flag_find_idir = "yes"

    if flag_find_idir == "yes":
        print("comout set to "+comout)
    else:
        date = date + date_inc
        continue
    
    flag_ak = "no"
    flag_hi = "no"

    for cyc in cycle:
        cycle_time="t"+cyc+"z"
        msg=datetime.datetime.now()
        print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        if envir != 'prod' and envir != 'para6d':
            s1_title="Online CMAQ vs Airnow Obs "+fig_exp.upper()+" "+date.strftime(YMD_date_format)+" t"+cyc+"z"
        else:
            s1_title="Offline CMAQ vs Airnow Obs "+fig_exp.upper()+" "+date.strftime(YMD_date_format)+" t"+cyc+"z"
            
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[0:2]))

        for ivar in range(0,num_var):
            fcst_hour=fcst_ini
            figdir = figout+"/aqm"+"_"+envir+"_"+date.strftime(YMD_date_format)+"_"+var[ivar]+cycle_time
            print(figdir)
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("working on "+date.strftime(YMD_date_format)+" t"+cyc+"z "+var[ivar])
            time = sdate   
            for i in range(cyc_shift):
                time+=hour_inc

            
            for fcst_hr in range(0,end):
                str_fcst_hr=str(fcst_hr)
                fhh=str_fcst_hr.zfill(3)
                
                if var[ivar] == 'pm25' and envir != 'v70b1' and envir != 'v70a1':
                    aqmfilein=comout+"/"+envir+"/"+date.strftime(YMD_date_format)+cyc+"/aqm.t"+cyc+"z.aconc_sfc.ncf" 
                    latlon_data = "/Users/florawalchenbach/lapenta_project/aqm.t06z.grdcro2d.ncf.txt"
                    if os.path.exists(aqmfilein) and os.path.exists(latlon_data):
                        cs_aqm = netcdf.Dataset(aqmfilein)
                        latlon_cs_aqm = netcdf.Dataset(latlon_data)
                        if fcst_hr == 0:
                            cs_lat = latlon_cs_aqm.variables['LAT'][:,:]
                            cs_lon = latlon_cs_aqm.variables['LON'][:,:]
                            latmax=np.amax(cs_lat)
                            latmin=np.amin(cs_lat)
                            lonmax=np.amax(cs_lon)
                            lonmin=np.amin(cs_lon)
                            ## print("from "+str(latmin)+" to "+str(latmax))
                            ## print("from "+str(lonmin)+" to "+str(lonmax))
                            
                            cs_lon = cs_lon[0,0,:,:]
                            cs_lat = cs_lat[0,0,:,:]
                        else:
                            pm_cs = cs_aqm.variables['PM25_TOT'][fcst_hr,0,:,:]
                        cs_aqm.close()
        
                elif var[ivar] == 'pm25' and envir != 'prod' and envir != 'para6d':
                    aqmfilein=comout+'/'+envir+"/"+date.strftime(YMD_date_format)+cyc+"/aqm.t"+cyc+"z.chem_sfc.f"+fhh+".nc"
                    if os.path.exists(aqmfilein):
                        cs_aqm = netcdf.Dataset(aqmfilein)
                        if fcst_hr == 0:
                            cs_lat = cs_aqm.variables['lat'][:,:]
                            cs_lon = cs_aqm.variables['lon'][:,:]
                            latmax=np.amax(cs_lat)
                            latmin=np.amin(cs_lat)
                            lonmax=np.amax(cs_lon)
                            lonmin=np.amin(cs_lon)
                            ## print("from "+str(latmin)+" to "+str(latmax))
                            ## print("from "+str(lonmin)+" to "+str(lonmax))
                            
                            cs_lon = cs_lon[:,:]
                            cs_lat = cs_lat[:,:]
                        else:
                            pm_cs = cs_aqm.variables['PM25_TOT'][0,:,:]
                        cs_aqm.close()
                    else:
                        if envir != 'prod' and envir != 'para6d':
                            print("Can not find "+aqmfilein)
                            sys.exit()
                        else:
                            print("Can not find "+aqmfilein+" and/or "+latlon_data)
                            sys.exit()
                        
                elif var[ivar] == "o3" and envir != 'v70b1' and envir != 'v70a1':
                    aqmfilein=comout+"/"+envir+"/"+date.strftime(YMD_date_format)+cyc+"/aqm.t"+cyc+"z.aconc_sfc.ncf" 
                    latlon_data = "/Users/florawalchenbach/lapenta_project/aqm.t06z.grdcro2d.ncf.txt"
                    if os.path.exists(aqmfilein) and os.path.exists(latlon_data):
                        cs_aqm = netcdf.Dataset(aqmfilein)
                        latlon_cs_aqm = netcdf.Dataset(latlon_data)
                        if fcst_hr == 0:
                            cs_lat = latlon_cs_aqm.variables['LAT'][:,:]
                            cs_lon = latlon_cs_aqm.variables['LON'][:,:]
                            latmax=np.amax(cs_lat)
                            latmin=np.amin(cs_lat)
                            lonmax=np.amax(cs_lon)
                            lonmin=np.amin(cs_lon)
                            ## print("from "+str(latmin)+" to "+str(latmax))
                            ## print("from "+str(lonmin)+" to "+str(lonmax))
                            
                            cs_lon = cs_lon[0,0,:,:]
                            cs_lat = cs_lat[0,0,:,:]
                            
                        else:
                            o3_cs = cs_aqm.variables['O3'][fcst_hr,0,:,:]
                        cs_aqm.close()
                
                elif var[ivar] == 'o3' and envir != 'prod' and envir != 'para6d':
                    aqmfilein=comout+'/'+envir+"/"+date.strftime(YMD_date_format)+cyc+"/aqm.t"+cyc+"z.chem_sfc.f"+fhh+".nc"
                    if os.path.exists(aqmfilein):
                        cs_aqm = netcdf.Dataset(aqmfilein)
                        if fcst_hr == 0:
                            cs_lat = cs_aqm.variables['lat'][:,:]
                            cs_lon = cs_aqm.variables['lon'][:,:]
                            latmax=np.amax(cs_lat)
                            latmin=np.amin(cs_lat)
                            lonmax=np.amax(cs_lon)
                            lonmin=np.amin(cs_lon)
                            ## print("from "+str(latmin)+" to "+str(latmax))
                            ## print("from "+str(lonmin)+" to "+str(lonmax))
                            
                            cs_lon = cs_lon[:,:]
                            cs_lat = cs_lat[:,:]
                        else:
                            o3_cs = cs_aqm.variables['o3'][0,:,:]
                        cs_aqm.close()
                    else:
                        if envir != 'prod' and envir != 'para6d':
                            print("Can not find "+aqmfilein)
                            sys.exit()
                        else:
                            print("Can not find "+aqmfilein+" and/or "+latlon_data)
                            sys.exit()
            
                if fcst_hr > 0:
                    ## READ hourly EPA AirNOW OBS data
                    ## note obs is forward average and model is backward, so they are different by an hour
                    obs_hour=fcst_hour
                    fcst_hour=fcst_hour+hour_inc

                    ## Read in one hourly data at a time
                    base_dir = '/Users/florawalchenbach/lapenta_project/epa_airnow_acsii/'+obs_hour.strftime(Y_date_format)+'/'+obs_hour.strftime(YMD_date_format)+'/'
                    obsfile= base_dir+'HourlyAQObs_'+obs_hour.strftime(obs_YMDH_date_format)+'.dat'
                    airnow = []
                    colnames = ['Latitude','Longitude','ValidDate','ValidTime','PM25','PM25_Unit','OZONE','OZONE_Unit']

                    df = pd.read_csv(obsfile,usecols=colnames)
    
                    df[df['PM25']<0]=np.nan # ignore negative PM2.5 values
    
                    df['Datetime'] = df['ValidDate'].astype(str)+' '+df['ValidTime'] # merge date and time columns
                    df['Datetime'] = pd.to_datetime(df['Datetime'],format='%m/%d/%Y %H:%M') # convert dates/times into datetime format
                    colnames_dt = ['Latitude','Longitude','Datetime','PM25','PM25_Unit','OZONE','OZONE_Unit']
   ## is there a similar command of pd.close_csv() ??
                    df = df[colnames_dt]
                    airnow.append(df)
    
                    airnow = pd.concat(airnow, ignore_index=True) # combine list of dataframes into one

                    lat = airnow['Latitude']
                    lon = airnow['Longitude']
                    dt = airnow['Datetime']
                    pm25_obs = airnow['PM25']
                    pmunit = airnow['PM25_Unit']
                    o3_obs = airnow['OZONE']
                    o3unit = airnow['OZONE_Unit']

                    if fcst_hr > 99:
                        s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+str(format(fcst_hr,'03d'))
                    else:
                        s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+str(format(fcst_hr,'02d'))
                    ##    for ivar in range(0,num_var):
                    msg=datetime.datetime.now()
                    ## print("Start processing "+var[ivar])
                    if var[ivar] == "o3":
                        s3_title="Ozone sfc_conc (ppbV)"
                        if envir == 'prod' or envir == 'para6d':
                            scale = 1000.
                        else:
                            scale = 1.
                        clevs = [ 3., 6., 9., 12., 25., 35., 45., 55., 65., 70., 75., 85., 95., 105. ]
                        var_cs=o3_cs*scale
                        if flag_ak == "yes":
                            var_ak=o3_ak*scale
                        if flag_hi == "yes":
                            var_hi=o3_hi*scale
                        cmap = mpl.colors.ListedColormap([
                              (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000),
                              (0.0000,0.7490,1.0000), (0.0000,1.0000,1.0000),
                              (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                              (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000), (0.9412,0.5098,0.1569),
                              (1.0000,0.0000,0.0000), (0.7020,0.0000,0.0000)
                              ])
                        cmap.set_under((0.8627,0.8627,1.0000))
                        cmap.set_over((0.4310,0.2780,0.7250)) 
                        
                    elif var[ivar] == "pm25":
                        s3_title="PM25 sfc_conc ($\u03bcg/m^3$)"
                        scale=1.
                        clevs = [ 3., 6., 9., 12., 15., 35., 55., 75., 100., 125., 150., 250., 300., 400., 500., 600., 750. ]
                        var_cs=pm_cs
                        if flag_ak == "yes":
                            var_ak=pm_ak[0,0,:,:]
                        if flag_hi == "yes":
                            var_hi=pm_hi[0,0,:,:]
                        cmap = mpl.colors.ListedColormap([
                              (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                              (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000),
                              (1.0000,0.3840,0.3840), (1.0000,0.0000,0.0000), (0.8000,0.0000,0.0000), (0.7020,0.0000,0.0000),
                              (0.6120,0.5100,0.8120), (0.5180,0.3880,0.7650), (0.4310,0.2780,0.7250),(0.2980,0.1920,0.5020),
                              (0.4706,0.4706,0.4706), (0.7843,0.7843,0.7843)
                              ])
                        cmap.set_under((0.8627,0.8627,1.0000))
                        cmap.set_over((0.9412,0.9412,0.9412))
                    elif var[ivar] == "pm25_nonseason":
                        s3_title="PM25 sfc_conc ($\u03bcg/m^3$)"
                        scale=1.
                        clevs = [ 0., 3., 6., 9., 12., 25., 35., 45., 55., 65., 75., 85., 95., 105. ]
                        var_cs=pm_cs
                        if flag_ak == "yes":
                            var_ak=pm_ak[0,0,:,:]
                        if flag_hi == "yes":
                            var_hi=pm_hi[0,0,:,:]
                        cmap = mpl.colors.ListedColormap([
                              (0.9412,0.9412,0.9412), (0.8627,0.8627,1.0000), (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000),
                              (0.2157,0.2157,1.0000), (0.0000,0.7843,0.7843), (0.0000,0.8627,0.0000), (0.6275,0.9020,0.1961),
                              (0.9020,0.8627,0.1961), (0.9020,0.6863,0.1765), (0.9412,0.5098,0.1569), (0.9804,0.2353,0.2353),
                              (0.9412,0.0000,0.5098)
                              ])
                        cmap.set_over('magenta')
                        cmap.set_under('whitesmoke')
                    norm = mpl.colors.BoundaryNorm(boundaries=clevs, ncolors=cmap.N)
                    gs = gridspec.GridSpec(1,1)
                    
                    title=s1_title+"\n"+s2_title+" "+s3_title
                    pvar_cs = var_cs[:,:]
                    if flag_ak == "yes":
                        pvar_ak = var_ak[:,:]
                    if flag_hi == "yes":
                        pvar_hi = var_hi[:,:]
                    for ireg in range(0,num_reg):
                        if iplot[ireg] == 1:
                            figarea=regname[ireg]
                            extent=[ rlon0[ireg], rlon1[ireg], rlat0[ireg], rlat1[ireg] ]
                            clat=0.5*(rlat0[ireg] + rlat1[ireg])
                            clon=0.5*(rlon0[ireg] + rlon1[ireg])
                            if figarea == "ak":
                                aqmproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, standard_parallels=(57, 63), globe=None)
                            elif figarea == "hi":
                                aqmproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, standard_parallels=(19, 21), globe=None)
                            else:
                                aqmproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, false_easting=-58.775, false_northing=48.772, standard_parallels=(33, 45), globe=None)
                            
                            fig, ax1 = plt.subplots(figsize=(xsize[ireg],ysize[ireg]), sharey=True, sharex=True)
                            ax1 = plt.axes(projection=aqmproj)
                            ax1.set_extent(extent)
                            ax1.coastlines('50m')
                            states_provinces = cfeature.NaturalEarthFeature(
                                 category='cultural',
                                 name='admin_1_states_provinces_lines',
                                 scale='50m',
                                 facecolor='none')
                            ax1.add_feature(states_provinces, facecolor='none', edgecolor='gray')
                            ax1.add_feature(cfeature.BORDERS, facecolor='none', linestyle=':')
                            ax1.add_feature(cfeature.LAKES, facecolor='None', edgecolor='black', alpha=0.5)
                            
                            if figarea == "ak":
                                cf1 = ax1.contourf(
                                         ak_lon, ak_lat, pvar_ak,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both', zorder=0,
                                         transform=ccrs.PlateCarree() )
                            elif figarea == "hi":
                                cf1 = ax1.contourf(
                                         hi_lon, hi_lat, pvar_hi,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both', zorder=0,
                                         transform=ccrs.PlateCarree() )
                            else:
                                cf1 = ax1.contourf(
                                         cs_lon, cs_lat, pvar_cs,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both', zorder=0,
                                         transform=ccrs.PlateCarree() )
                                if figarea == "dset":
                                    if flag_ak == "yes":
                                        ax1.contourf(
                                             ak_lon, ak_lat, pvar_ak,
                                             levels=clevs, cmap=cmap, norm=norm, extend='both', zorder=0,
                                             transform=ccrs.PlateCarree() )
                                    if flag_hi == "yes":
                                        ax1.contourf(
                                             hi_lon, hi_lat, pvar_hi,
                                             levels=clevs, cmap=cmap, norm=norm, extend='both', zorder=0,
                                             transform=ccrs.PlateCarree() )
                            ax1.set_title(title)
                            fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,shrink=1.0,format=cbar_num_format)
                            
                            
                            
                            #######################################################
                            ##########      PLOTTING OBS DATA            ##########
                            #######################################################
    
                            var_lat = []
                            var_lon = []
                            plot_var = []
                            var_unit = []
                            length = len(lat)

                            for row in range(length):
                                bool_nanpm = pd.isnull(pm25_obs[row])
                                bool_nano3 = pd.isnull(o3_obs[row])

                                if sel_var == 'pm25':
                                    if dt[row] == time and bool_nanpm == False:
                                        var_lon.append(lon[row])
                                        var_lat.append(lat[row])
                                        plot_var.append(pm25_obs[row])
                                        var_unit.append(pmunit[row])
                                        if pmunit[row]!='UG/M3':
                                            print('Uh oh! pm25 row '+str(row)+' is in units of '+str(pmunit[row]))
                                elif sel_var == 'o3':
                                    if dt[row] == time and bool_nano3 == False:
                                        var_lon.append(lon[row])
                                        var_lat.append(lat[row])
                                        plot_var.append(o3_obs[row])
                                        var_unit.append(pmunit[row])
                                        if o3unit[row]!='PPB':
                                            print('Uh oh! o3 row '+str(row)+' is in units of '+str(o3unit[row])) 
                                else:
                                    print('Chosen variable not recognized'+str(var))

                            if sel_var == 'pm25':
                                num_pm25=len(plot_var)
                                clevs = [ 3., 6., 9., 12., 15., 35., 55., 75., 100., 125., 150., 250., 300., 400., 500., 600., 750. ]
                                nlev=len(clevs)
                                ccols = [
                                        (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                                        (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000),
                                        (1.0000,0.3840,0.3840), (1.0000,0.0000,0.0000), (0.8000,0.0000,0.0000), (0.7020,0.0000,0.0000),
                                        (0.6120,0.5100,0.8120), (0.5180,0.3880,0.7650), (0.4310,0.2780,0.7250),(0.2980,0.1920,0.5020),
                                        (0.4706,0.4706,0.4706), (0.7843,0.7843,0.7843)
                                        ]
                                ncols=len(ccols)
                                if ncols+1 != nlev:
                                    print("Warning: color interval does not match with color setting")
                                color=[]
                                for i in range(0,num_pm25):
                                    if plot_var[i] < clevs[0]:
                                        color.append((0.8627,0.8627,1.0000))
                                    elif plot_var[i] >= clevs[nlev-1]:
                                        color.append((0.9412,0.9412,0.9412))
                                    else:
                                        flag_find_color="no"
                                        for j in range(0,nlev-1):
                                            if plot_var[i] >= clevs[j] and plot_var[i] < clevs[j+1]:
                                                color.append(ccols[j])
                                                flag_find_color="yes"
                                                break
                                        if flag_find_color =="no":
                                            print("Can not assign proper value for color, program stop")
                                            sys.exit()

                            elif sel_var == 'o3':
                                num_o3=len(plot_var)
                                clevs = [ 3., 6., 9., 12., 25., 35., 45., 55., 65., 70., 75., 85., 95., 105. ]
                                nlev=len(clevs)
                                ccols = [
                                         (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000),
                                         (0.0000,0.7490,1.0000), (0.0000,1.0000,1.0000),
                                         (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                                         (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000), (0.9412,0.5098,0.1569),
                                         (1.0000,0.0000,0.0000), (0.7020,0.0000,0.0000)
                                        ]
                                ncols=len(ccols)
                                if ncols+1 != nlev:
                                    print('Warning: color interval does not match with color setting')
                                color=[]
                                for i in range(0,num_o3):
                                    if plot_var[i] < clevs[0]:
                                        color.append((0.8627,0.8627,1.0000))
                                    elif plot_var[i] >= clevs[nlev-1]:
                                        color.append((0.4310,0.2780,0.7250))
                                    else:
                                        flag_find_color='no'
                                        for j in range(0,nlev-1):
                                            if plot_var[i] >= clevs[j] and plot_var[i] < clevs[j+1]:
                                                color.append(ccols[j])
                                                flag_find_color='yes'
                                                break
                                        if flag_find_color =='no':
                                            print('Can not assign proper value for color, program stop')
                                            sys.exit()

                            ax1.scatter(var_lon,var_lat,c=color,cmap=cmap,marker='o',s=100,zorder=1, transform=ccrs.PlateCarree(), edgecolors='black')

                            time+=hour_inc 
                            
                            savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"."+date.strftime(YMD_date_format)+"."+cycle_time+"."+str(format(fcst_hr,'02d'))+"."+var[ivar]+".k1.png"
                            plt.savefig(savefig_name, bbox_inches='tight')
                            plt.close()
            
        msg=datetime.datetime.now()
        print("End   processing "+var[ivar])
        print("FIG DIR = "+figdir)
        msg=datetime.datetime.now()
        print("End   processing "+date.strftime(YMD_date_format)+" "+cycle_time+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc


# In[ ]:





# In[ ]:




