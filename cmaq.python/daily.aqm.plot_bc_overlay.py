import os
import numpy as np
import netCDF4 as netcdf
import re
import maps2d_plot_util as maps2d_plot_util
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
### Read data of all time step in once, then print one at a time
### PASSED AGRUEMENTS
if len(sys.argv) < 5:
    print("you must set 5 arguments as model[prod|para|...] variabels[o3|pm25|all] cycle[06|12|all]  start_date end_date")
    sys.exit()
else:
    envir = sys.argv[1]
    sel_var = sys.argv[2]
    sel_cyc = sys.argv[3]
    start_date = sys.argv[4]
    end_date = sys.argv[5]

if envir.lower() == "para":
    fig_exp="ncopara"
else:
    fig_exp=envir.lower()

script_dir=os.getcwd()
print("Script directory is "+script_dir)

user=os.environ['USER']
ifile="/u/ho-chun.huang/versions/run.ver"
rfile=open(ifile, 'r')
for line in rfile:
    nfind=line.find("export")
    if nfind != -1:
        line=line.rstrip("\n")
        ver=line.split("=")
        ver_name=ver[0].split(" ")
        if ver_name[1] == "aqm_ver":
            aqm_ver=ver[1]
rfile.close()
if aqm_ver=="":
    aqm_ver="v6.1"
print("aqm_ver="+aqm_ver)

stmp_dir="/lfs/h2/emc/stmp/"+user
if not os.path.exists(stmp_dir):
    os.mkdir(stmp_dir)

ptmp_dir="/lfs/h2/emc/ptmp/"+user
if not os.path.exists(ptmp_dir):
    os.mkdir(ptmp_dir)

log_dir=ptmp_dir+"/batch_logs"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

working_dir=stmp_dir+"/aqm_plot_working"
if os.path.exists(working_dir):
    os.chdir(working_dir)
else:
    os.makedirs(working_dir)
    os.chdir(working_dir)

msg_file=working_dir+"/devmachine"
subprocess.call(["cat /etc/cluster_name > "+msg_file], shell=True)
if os.path.isfile(msg_file):
    with open(msg_file, 'r') as sh:
        line=sh.readline()
        dev_machine=line.rstrip()
        print("currently on "+dev_machine)
        sh.close()

msg_file=working_dir+"/prodmachine"
subprocess.call(["cat /lfs/h1/ops/prod/config/prodmachinefile > "+msg_file], shell=True)
if os.path.isfile(msg_file):
    with open(msg_file, 'r') as sh:
        prod_machine="99"
        line=sh.readline()
        line1=line.rstrip()
        abc=line1.split(':')
        if abc[0] == 'primary':
            prod_machine=abc[1]
        else:
            line=sh.readline()
            line1=line.rstrip()
            abc=line1.split(':')
            if abc[0] == 'primary':
                prod_machine=abc[1]
        print(prod_machine)
        sh.close()

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
   cycle=[ "t06z", "t12z" ]
elif sel_cyc == "06":
   cycle=[ "t06z" ]
elif sel_cyc == "12":
   cycle=[ "t12z" ]
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
##
## Current operational CMAQ does not apply Bias-Correction procedure for AK and HI domain
## Current EMC development CMAQ does not apply Bias-Correction procedure for AK and HI domain
##
msg=datetime.datetime.now()
msg=msg - date_inc
grdcro2d_date=msg.strftime("%Y%m%d")

find_dir=[
          "/lfs/h1/ops/"+envir+"/com/aqm/"+aqm_ver,
          "/lfs/h2/emc/ptmp/"+user+"/com/aqm/"+envir,
          "/lfs/h2/emc/physics/noscrub/"+user+"/BiasCor_updated/"+envir,
          "/lfs/h2/emc/physics/noscrub/"+user+"/com/aqm/"+envir,
          "/lfs/h2/emc/physics/noscrub/"+user+"/verification/aqm/"+envir
         ]
metout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
dcomdir="/lfs/h1/ops/prod/dcom"
obsdir="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/epa_airnow_acsii"

#
# NO Bias-correction for Ak and HI for both aqmv6 and aqmv7
#
flag_ak = False
flag_hi = False

figout=stmp_dir

##
## new area need to be added ahead of ak.  The last three areas need to be fixed as "ak",   "hi",  "can"
## this is due to the code below remove plotting of ak and hi if no ak and hi input files ash been found
##
flag_proj="LambertConf"
##
## marker size (s= in the scatter plot command) is the wxH. s=100 is the area of 10x10
## Thus increase and decrease by squrt(s) or using nxn wiht n from 1,....large integer
##
mksize= [     64, 64, 16,     36,      36,      36,     49,     49,     49,     49,     64,     64,    121,    100,    121,     36 ]
## mksize= [  64, 64, 16,      16,      25,     25,     36,     36,     36,     36,     49,     49,    121,    100,    121,     36 ]
if flag_proj == "LambertConf":
    regname = [ "Mckinney",  "aznw", "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
    rlon0 = [ -125., -120., -165.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0,  -75.0, -166.0, -161.5, -141.0 ]
    rlon1 = [  -110., -100., -70.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0,  -71.0, -132.0, -153.1, -60.0 ]
    rlat0 = [   40., 30.0, 10.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   40.2,   53.2,   17.8,   38.0 ]
    rlat1 = [   45., 40., 75.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   41.8,   71.2,   23.1,   70.0 ]
else:
    regname = [   "Mckinney",  "aznw", "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
    rlon0 = [ -125., -120., -175.0, -124.0,  -100.0, -128.0,  -82.0, -125.0,  -95.0, -125.0, -105.0, -105.0,  -75.0, -170.0, -161.0, -141.0 ]
    rlon1 = [  -110., -100., -55.0,  -70.0,   -65.0,  -90.0,  -67.0, -103.0,  -79.0, -105.0,  -85.0,  -85.0,   -71.0, -130.0, -154.0,  -60.0 ]
    rlat0 = [    40., 30.0, 0.0,   22.0,    22.0,   24.5,   37.0,   38.0,   24.0,   30.0,   38.0,   24.0,   40.2,   52.0,   18.0,   38.0 ]
    rlat1 = [   45., 40., 70.0,   51.0,    50.0,   54.5,   48.0,   52.0,   38.0,   45.0,   52.0,   40.0,   41.8,   72.0,   23.0,   70.0 ]
xsize = [     10, 10, 10,     10,       8,      8,      8,      8,      8,      8,      8,      8,     10,      8,      8,     10 ]
ysize = [      5, 5, 8,      8,       8,      8,      8,      8,      8,      8,      8,      8,      5,      8,      8,     8 ]
if 1 == 1:
    iplot = [    0, 0,   1,      1,       1,      1,      1,      1,      1,      1,      0,      0,      1,      0,      0, 0 ]
else:
    iplot = [    1, 1,   1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1, 1 ]
num_reg=len(iplot)

date=sdate
while date <= edate:
    flag_find_idir=False
    for idir in find_dir:
        comout=idir
        print("check "+idir)
        flag_find_cyc=True
        for cyc in cycle:
            flag_find_var=True
            for ivar in range(0,num_var):
                if var[ivar] == "o3":
                    check_file="ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                elif var[ivar] == "pm25":
                    check_file="pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/"+check_file
                aqmfilein2=comout+"/"+check_file
                flag_new_dir = False
                if os.path.exists(aqmfilein):
                    print(aqmfilein+" exists")
                else:
                    if os.path.exists(aqmfilein2):
                        print(aqmfilein2+" exists")
                        flag_new_dir = True
                    else:
                        flag_find_var=False
                        print("Can not find "+aqmfilein)
                        print("Can not find "+aqmfilein2)
                        break
            if not flag_find_var:
                flag_find_cyc=False
                break
        if flag_find_cyc:
            flag_find_idir=True
            break
    if flag_find_idir:
        print("comout set to "+comout)
    else:
        date = date + date_inc
        continue

    if not flag_ak and iplot[num_reg-3] == 1:
        iplot[num_reg-3] = 0
    if not flag_hi and iplot[num_reg-2] == 1:
        iplot[num_reg-2] = 0
    print("iplot length = "+str(num_reg))


    for cyc in cycle:
        msg=datetime.datetime.now()
        print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        s1_title="CMAQ "+fig_exp.upper()+"_BC "+date.strftime(YMD_date_format)+" "+cyc
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[1:3]))

        metfilein=metout+"/cs."+grdcro2d_date+"/aqm."+cyc+".grdcro2d.ncf"
        if os.path.exists(metfilein):
            print(metfilein+" exists")
            model_data = netcdf.Dataset(metfilein)
            cs_lat = model_data.variables['LAT'][0,0,:,:]
            cs_lon = model_data.variables['LON'][0,0,:,:]
            model_data.close()
        else:
            print("Can not find "+metfilein)

        for ivar in range(0,num_var):
            if var[ivar] == "o3":
                if flag_new_dir:
                    model_filein=comout+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                else:
                    model_filein=comout+"/cs."+date.strftime(YMD_date_format)+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                if os.path.exists(model_filein):
                    print(model_filein+" exists")
                    model_data = netcdf.Dataset(model_filein)
                    o3_cs  = model_data.variables['O3'][:,0,:,:]
                    nstep=len(o3_cs)
                    model_data.close()
                else:
                    print("Can not find "+model_filein)
                    sys.exit()
            elif var[ivar] == "pm25":
                if flag_new_dir:
                    model_filein=comout+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                else:
                    model_filein=comout+"/cs."+date.strftime(YMD_date_format)+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                if os.path.exists(model_filein):
                    print(model_filein+" exists")
                    model_data = netcdf.Dataset(model_filein)
                    pm_cs = model_data.variables['pm25'][:,0,:,:]
                    nstep=len(pm_cs)
                    model_data.close()
                else:
                    print("Can not find "+model_filein)
                    sys.exit()
            if flag_ak:
                if var[ivar] == "o3":
                    model_filein=comout+"/ak."+date.strftime(YMD_date_format)+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                    if os.path.exists(model_filein):
                        print(model_filein+" exists")
                        model_data = netcdf.Dataset(model_filein)
                        o3_cs  = model_data.variables['O3'][:,0,:,:]
                        nstep=len(o3_cs)
                        model_data.close()
                    else:
                        print("Can not find "+model_filein)
                        flag_ak = False
                        iplot[num_reg-3] = 0
                elif var[ivar] == "pm25":
                    model_filein=comout+"/ak."+date.strftime(YMD_date_format)+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                    if os.path.exists(model_filein):
                        print(model_filein+" exists")
                        model_data = netcdf.Dataset(model_filein)
                        pm_cs = model_data.variables['pm25'][:,0,:,:]
                        nstep=len(pm_cs)
                        model_data.close()
                    else:
                        print("Can not find "+model_filein)
                        flag_ak = False
                        iplot[num_reg-3] = 0
            if flag_hi:
                if var[ivar] == "o3":
                    model_filein=comout+"/hi."+date.strftime(YMD_date_format)+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                    if os.path.exists(model_filein):
                        print(model_filein+" exists")
                        model_data = netcdf.Dataset(model_filein)
                        o3_cs  = model_data.variables['O3'][:,0,:,:]
                        nstep=len(o3_cs)
                        model_data.close()
                    else:
                        print("Can not find "+model_filein)
                        iplot[num_reg-2] = 0
                        flag_hi = False
                elif var[ivar] == "pm25":
                    model_filein=comout+"/hi."+date.strftime(YMD_date_format)+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                    if os.path.exists(model_filein):
                        print(model_filein+" exists")
                        model_data = netcdf.Dataset(model_filein)
                        pm_cs = model_data.variables['pm25'][:,0,:,:]
                        nstep=len(pm_cs)
                        model_data.close()
                    else:
                        print("Can not find "+model_filein)
                        flag_hi = False
                        iplot[num_reg-2] = 0
        for ivar in range(0,num_var):
            msg=datetime.datetime.now()
            print("Start processing "+var[ivar])
            jobid="aqm"+"_"+envir+"obs_"+date.strftime(YMD_date_format)+"_"+var[ivar]+"_"+cyc+"_bc"
            figdir = figout+"/"+jobid
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("working on "+date.strftime(YMD_date_format)+" "+cyc+" "+var[ivar])
            if var[ivar] == "o3":
                s3_title="Ozone sfc_conc (ppbV)"
                scale=1000.
                clevs = [ 3., 6., 9., 12., 25., 35., 45., 55., 65., 70., 75., 85., 95., 105. ]
                var_cs=o3_cs*scale
                if flag_ak:
                    var_ak=o3_ak*scale
                if flag_hi:
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
                if flag_ak:
                    var_ak=pm_ak
                if flag_hi:
                    var_hi=pm_hi
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
                if flag_ak:
                    var_ak=pm_ak
                if flag_hi:
                    var_hi=pm_hi
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
            fcst_hour=fcst_ini
            ## for over lay plot
            ## code is design to process the graphic in sequence from 1st hour
            ## obs_hour and fcst_hour need to be consistently increase by one hour, whike
            ## model forecast output is directly read "n" if model output
            ## thus, obs and fcst will not sync if n start from the middle
            ## for n in range(0,17):
            ## for n in range(0,2):
            for n in range(0,nstep):
                nout=n+1
                str_fcst_hr=str(nout)
                fhh=str_fcst_hr.zfill(3)
                ## READ hourly EPA AirNOW OBS data
                ## note obs is forward average and model is backward, so they are different by an hour
                obs_hour=fcst_hour
                fcst_hour=fcst_hour+hour_inc

                ## Read in one hourly data one at a time
                flag_with_obs=True
                obsfile= "HourlyAQObs_"+obs_hour.strftime(obs_YMDH_date_format)+".dat"
                ifile=os.path.join(dcomdir,obs_hour.strftime(YMD_date_format),"airnow",obsfile)
                ifile2=os.path.join(obsdir,obs_hour.strftime(Y_date_format),obs_hour.strftime(YMD_date_format),obsfile)
                if os.path.exists(ifile):
                    infile=ifile
                    print(infile+" exists")
                elif os.path.exists(ifile2):
                    infile=ifile2
                    print(infile+" exists")
                else:
                    print("Can not find both "+ifile+" and "+ifile2)
                    flag_with_obs=False

                if flag_with_obs:
                    airnow = []
                    colnames = ['Latitude','Longitude','ValidDate','ValidTime','PM25','PM25_Unit','OZONE','OZONE_Unit']
    
                    df = pd.read_csv(infile,usecols=colnames)
    
                    df[df['PM25']<0]=np.nan # ignore negative PM2.5 values
    
                    df['Datetime'] = df['ValidDate'].astype(str)+' '+df['ValidTime'] # merge date and time columns
                    ## note 2020 epa time format is MM/DD/YY while 2022 timestamp is MM/DD/YYYY
                    if obs_hour.strftime(Y_date_format) == "2020":
                        df['Datetime'] = pd.to_datetime(df['Datetime'],format='%m/%d/%y %H:%M') # convert dates/times into datetime format
                    else:
                        df['Datetime'] = pd.to_datetime(df['Datetime'],format='%m/%d/%Y %H:%M') # convert dates/times into datetime format
                    colnames_dt = ['Latitude','Longitude','Datetime','PM25','PM25_Unit','OZONE','OZONE_Unit']
    # is there a similar command of pd.close_csv() ??
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

                s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+fhh
                title=s1_title+"\n"+s2_title+" "+s3_title
                pvar_cs = var_cs[n,:,:]
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
                        fig, ax = plt.subplots(figsize=(xsize[ireg],ysize[ireg]))

                        ax = plt.axes(projection=aqmproj)
                        ax.set_extent(extent)
                        ax.coastlines('50m')
                        states_provinces = cfeature.NaturalEarthFeature(
                             category='cultural',
                             name='admin_1_states_provinces_lines',
                             scale='50m',
                             facecolor='none')
                        ax.add_feature(states_provinces, facecolor='none', edgecolor='gray')
                        ## rivers_50m = cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '50m')
                        ## ax.add_feature(cfeature.LAND, edgecolor='black')
                        ## ax.add_feature(cfeature.OCEAN, edgecolor='black')
                        ## ax.add_feature(cfeature.COASTLINE)
                        ax.add_feature(cfeature.BORDERS, facecolor='none', linestyle=':')
                        ax.add_feature(cfeature.LAKES, facecolor='None', edgecolor='black', alpha=0.5)
                        ## ax.add_feature(cfeature.RIVERS)
                        if figarea == "ak":
                            cf1 = ax.contourf(
                                     ak_lon, ak_lat, pvar_ak,
                                     levels=clevs, cmap=cmap, norm=norm, extend='both',
                                     transform=ccrs.PlateCarree() )
                        elif figarea == "hi":
                            cf1 = ax.contourf(
                                     hi_lon, hi_lat, pvar_hi,
                                     levels=clevs, cmap=cmap, norm=norm, extend='both',
                                     transform=ccrs.PlateCarree() )
                        else:
                            cf1 = ax.contourf(
                                     cs_lon, cs_lat, pvar_cs,
                                     levels=clevs, cmap=cmap, norm=norm, extend='both',
                                     transform=ccrs.PlateCarree() )
                            if figarea == "dset":
                                if flag_ak:
                                    ax.contourf(
                                         ak_lon, ak_lat, pvar_ak,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                                if flag_hi:
                                    ax.contourf(
                                         hi_lon, hi_lat, pvar_hi,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                        ax.set_title(title)
                        ## cb2.set_label('Discrete intervals, some other units')
                        fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,shrink=1.0,format=cbar_num_format)
                        if flag_with_obs:
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
    
                                if var[ivar] == 'pm25':
                                    if dt[row] == obs_hour and bool_nanpm == False:
                                        var_lon.append(lon[row])
                                        var_lat.append(lat[row])
                                        plot_var.append(pm25_obs[row])
                                        var_unit.append(pmunit[row])
                                        if pmunit[row]!='UG/M3':
                                            print('Uh oh! pm25 row '+str(row)+' is in units of '+str(pmunit[row]))
                                elif var[ivar] == 'o3':
                                    if dt[row] == obs_hour and bool_nano3 == False:
                                        var_lon.append(lon[row])
                                        var_lat.append(lat[row])
                                        plot_var.append(o3_obs[row])
                                        var_unit.append(pmunit[row])
                                        if o3unit[row]!='PPB':
                                            print('Uh oh! o3 row '+str(row)+' is in units of '+str(o3unit[row])) 
                                else:
                                    print('Chosen variable not recognized'+str(var))
    
                            if var[ivar] == 'pm25':
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
                                        flag_find_color=False
                                        for j in range(0,nlev-1):
                                            if plot_var[i] >= clevs[j] and plot_var[i] < clevs[j+1]:
                                                color.append(ccols[j])
                                                flag_find_color=True
                                                break
                                        if not flag_find_color:
                                            print("Can not assign proper value for color, program stop")
                                            sys.exit()
    
                            elif var[ivar] == 'o3':
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
                                        flag_find_color=False
                                        for j in range(0,nlev-1):
                                            if plot_var[i] >= clevs[j] and plot_var[i] < clevs[j+1]:
                                                color.append(ccols[j])
                                                flag_find_color=True
                                                break
                                        if not flag_find_color:
                                            print('Can not assign proper value for color, program stop')
                                            sys.exit()
    
                            ## s = [20*4**n for n in range(len(x))]
                            ## ax.scatter(var_lon,var_lat,c=color,cmap=cmap,marker='o',s=100,zorder=1, transform=ccrs.PlateCarree(), edgecolors='black')
                            ax.scatter(var_lon,var_lat,c=color,cmap=cmap,marker='o',s=mksize[ireg],zorder=1, transform=ccrs.PlateCarree(), edgecolors='black')
    
                        if flag_with_obs:
                            savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"bcobs."+date.strftime(YMD_date_format)+"."+cyc+"."+str(format(nout,'02d'))+"."+var[ivar]+".k1.png"
                        else:
                            ## savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"bc."+date.strftime(YMD_date_format)+"."+cyc+"."+str(format(nout,'02d'))+"."+var[ivar]+".k1.png"
                            savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"bcobs."+date.strftime(YMD_date_format)+"."+cyc+"."+str(format(nout,'02d'))+"."+var[ivar]+".k1.png"
                        plt.savefig(savefig_name, bbox_inches='tight')
                        plt.close()
            ##
            ## scp by cycle and variable
            ##
            os.chdir(figdir)
            parta=os.path.join("/usr", "bin", "scp")
            if 1 == 1 :
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", date.strftime(Y_date_format), date.strftime(YMD_date_format), cyc)
            else:
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
            subprocess.call(['scp -p * '+partb], shell=True)
            msg=datetime.datetime.now()
            print("End   processing "+var[ivar])
            print("FIG DIR = "+figdir)
        msg=datetime.datetime.now()
        print("End   processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    date = date + date_inc
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
