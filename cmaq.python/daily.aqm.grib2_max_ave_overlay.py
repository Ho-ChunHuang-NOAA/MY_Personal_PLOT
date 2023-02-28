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

user=os.environ['USER']
wgrib2=os.environ['WGRIB2']
if wgrib2 == "":
    print("No definition of WGRIB2 can be found, please load module wgrib2/2.0.8")
    sys.exit()

script_dir=os.getcwd()
print("Script directory is "+script_dir)

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

##
## Current operational CMAQ does include runs for AK and HI domain
## Current EMC development CMAQ does not include runs for AK and HI domain
##
grid148="148"
grid227="227"
grid198="198"
grid139="139"
grid196="196"
grid793="793"

caseid="v70"
nfind=envir.find(caseid)
if nfind == -1:
    print("AQMv6 simulation")
    s1_lead="CMAQ"
    aqmv7 = False
    nfind=envir.find("_bc")
    if nfind == -1:
        print("not a bias_correction cases")
        EXP=envir
        BC_append=""
        BC_fig_append=BC_append
        print("exp="+EXP)
        print("BC_append="+BC_append)
    else:
        print("A bias_correction cases")
        EXP=envir[0:nfind]
        BC_append="_bc"
        BC_fig_append="bc"
        print("exp="+EXP)
        print("BC_append="+BC_append)
    if EXP.lower() == "prod" or EXP.lower() == "para" or EXP.lower() == "firev4":
        aqm_ver="v6.1"
        exp_grid=grid148
        expid="cs"
        comout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
        comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+EXP.lower()
        comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/verification/aqm/"+EXP.lower()
    else:
        print("Experiement ID "+EXP.lower()+" not found for this code, Program exit")
        sys.exit()
    usrout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/verification/aqm/"+EXP.lower()
    usrout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+EXP.lower()
    if not os.path.exists(comout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
        if not os.path.exists(usrout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
            print("Can not find output dir with experiment id "+EXP.lower())
            sys.exit()
else:
    print("AQMv7 simulation")
    s1_lead="Online CMAQ"
    aqmv7 = True
    aqm_ver="v7.0"
    exp_grid=grid793

    nfind=envir.find("_bc")
    if nfind == -1:
        print("not a bias_correction cases")
        EXP=envir
        n0=len(caseid)
        n1=len(EXP)
        expid=envir[n0:n1]
        BC_append=""
        BC_fig_append=BC_append
        print("exp="+EXP)
        print("expid="+expid)
        print("BC_append="+BC_append)
    else:
        EXP=envir[0:nfind]
        n0=len(caseid)
        n1=len(EXP)
        expid=EXP[n0:n1]
        BC_append="_bc"
        BC_fig_append="bc"
        print("exp="+EXP)
        print("expid="+expid)
        print("BC_append="+BC_append)
    comout="/lfs/h2/emc/ptmp/jianping.huang/emc.para/com/aqm/"+aqm_ver+"/aqm."+aqm_ver+"."+expid
    comout="/lfs/h2/emc/aqmtemp/para/com/aqm/"+aqm_ver
    usrout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/verification/aqm/"+EXP.lower()
    if not os.path.exists(comout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
        if not os.path.exists(usrout+"/cs."+sdate.strftime(YMD_date_format)):
            print("Can not find output dir with experiment id "+EXP.lower())
            sys.exit()

if EXP.lower() == "para":
    fig_exp="ncopara"
else:
    fig_exp=EXP.lower()+BC_fig_append

var=[ "ozmax8", "ozmax1", "pmave24", "pmmax1" ]
num_var=len(var)
print("var length = "+str(num_var))

if sel_cyc == "all":
   cycle=[ "t06z", "t12z" ]
   cycle=[ "06", "12" ]
elif sel_cyc == "06":
   cycle=[ "t06z" ]
   cycle=[ "06" ]
elif sel_cyc == "12":
   cycle=[ "t12z" ]
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

dcomout="/lfs/h1/ops/prod/dcom"
obsdir="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/epa_airnow_acsii"
figout=stmp_dir

##
## new area need to be added ahead of ak.  The last three areas need to be fixed as "ak",   "hi",  "can"
## this is due to the code below remove plotting of ak and hi if no ak and hi input files ash been found
##
flag_proj="LambertConf"
## from 22.574179720000018 to 51.47512722912568
## from 228.37073225113136 to 296.6273160909873
# old -70.6 to -120.4
#     22.2 to 50.7
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
    iplot = [    1, 1,   1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1, 1 ]
else:
    iplot = [    0,  0, 1,      0,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0, 0 ]
num_reg=len(iplot)

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
        s1_title=s1_lead+" "+EXP.upper()+BC_append.upper()+" "+date.strftime(YMD_date_format)+" t"+cyc+"z"
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[0:2]))

        for ivar in range(0,num_var):
            if var[ivar] == "ozmax8":
                fileid="max_8hr_o3"
            elif var[ivar] == "ozmax1":
                fileid="max_1hr_o3"
            elif var[ivar] == "pmave24":
                fileid="ave_24hr_pm25"
            elif var[ivar] == "pmmax1":
                fileid="max_1hr_pm25"
            fcst_hour=fcst_ini
            figdir = figout+"/aqm"+"_"+EXP.lower()+"obs_"+date.strftime(YMD_date_format)+"_"+var[ivar]+cycle_time+BC_append.lower()
            print(figdir)
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("working on "+date.strftime(YMD_date_format)+" t"+cyc+"z "+var[ivar])
            flag_read_latlon="no"
            hour_end = 72
            for fcst_hr in range(0,hour_end):
                nout=fcst_hr+1
                str_fcst_hr=str(nout)
                ## fhh=str_pad(fcst_hr,3,'0',STR_PAD_LEFT)
                fhh2=str_fcst_hr.zfill(2)
                fhh3=str_fcst_hr.zfill(3)
                ## READ hourly EPA AirNOW OBS data
                ## note obs is forward average and model is backward, so they are different by an hour
                obs_hour=fcst_hour
                fcst_hour=fcst_hour + hour_inc

                ## Read in one hourly data at a time
                base_dir = obsdir+"/"+obs_hour.strftime(Y_date_format)+'/'+obs_hour.strftime(YMD_date_format)+'/'
                obsfile= base_dir+'HourlyAQObs_'+obs_hour.strftime(obs_YMDH_date_format)+'.dat'
                flag_find_epa_ascii="no"
                if os.path.exists(obsfile):
                ##    print(obsfile+" exists")
                    flag_find_epa_ascii="yes"
                else:
                    base_dir = dcomout+"/"+obs_hour.strftime(YMD_date_format)+'/airnow/'
                    obsfile= base_dir+'HourlyAQObs_'+obs_hour.strftime(obs_YMDH_date_format)+'.dat'
                    if os.path.exists(obsfile):
                        flag_find_epa_ascii="yes"
                ##    else:
                ##        print("Can not find "+obsfile)

                if flag_find_epa_ascii == "yes":
                    airnow = []
                    colnames = ['Latitude','Longitude','ValidDate','ValidTime','PM25','PM25_Unit','OZONE','OZONE_Unit']
    
                    df = pd.read_csv(obsfile,usecols=colnames)
    
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

                if var[ivar] == "pm25":
                    if aqmv7:
                        aqmfilein=comout+"/"+expid+"."+date.strftime(YMD_date_format)+"/"+cyc+"/aqm."+cycle_time+".pm25"+BC_append+".f"+fhh2+"."+exp_grid+".grib2"
                    else:
                        aqmfilein=comout+"/"+expid+"."+date.strftime(YMD_date_format)+"/aqm."+cycle_time+".pm25"+BC_append+".f"+fhh2+"."+exp_grid+".grib2"
                    aqmfilein2=usrout+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cycle_time+".pm25"+BC_append+".f"+fhh2+"."+exp_grid+".grib2"
                    if os.path.exists(aqmfilein):
                        ## print(aqmfilein+" exists")
                        outfile=working_dir+"/pm25."+fhh2+".nc"
                        subprocess.call([wgrib2+' -d 1 -netcdf '+outfile+' '+aqmfilein], shell=True)
                        aqmfilein=outfile
                        cs_aqm = netcdf.Dataset(aqmfilein)
                        cs_lat = cs_aqm.variables['latitude'][:,:]
                        cs_lon = cs_aqm.variables['longitude'][:,:]
                        pm_cs = cs_aqm.variables['PMTF_1sigmalevel'][0,:,:]
                        cs_aqm.close()
                    elif os.path.exists(aqmfilein2):
                        ## print(aqmfilein2+" exists")
                        outfile=working_dir+"/pm25."+fhh2+".nc"
                        subprocess.call([wgrib2+' -d 1 -netcdf '+outfile+' '+aqmfilein2], shell=True)
                        aqmfilein2=outfile
                        cs_aqm = netcdf.Dataset(aqmfilein2)
                        cs_lat = cs_aqm.variables['latitude'][:,:]
                        cs_lon = cs_aqm.variables['longitude'][:,:]
                        pm_cs = cs_aqm.variables['PMTF_1sigmalevel'][0,:,:]
                        cs_aqm.close()
                    else:
                        print("Can not find "+aqmfilein)
                        print("Can not find "+aqmfilein2)
                        continue
                        ## sys.exit()
                ## in ppm
                if var[ivar] == "o3":
                    if aqmv7:
                        aqmfilein=comout+"/"+expid+"."+date.strftime(YMD_date_format)+"/"+cyc+"/aqm."+cycle_time+".awpozcon"+BC_append+".f"+fhh2+"."+exp_grid+".grib2"
                    else:
                        aqmfilein=comout+"/"+expid+"."+date.strftime(YMD_date_format)+"/aqm."+cycle_time+".awpozcon"+BC_append+".f"+fhh2+"."+exp_grid+".grib2"
                    aqmfilein2=usrout+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cycle_time+".awpozcon"+BC_append+".f"+fhh2+"."+exp_grid+".grib2"
                    if os.path.exists(aqmfilein):
                        ## print(aqmfilein+" exists")
                        outfile=working_dir+"/o3."+fhh2+".nc"
                        subprocess.call([wgrib2+' -d 1 -netcdf '+outfile+' '+aqmfilein], shell=True)
                        aqmfilein=outfile
                        cs_aqm = netcdf.Dataset(aqmfilein)
                        cs_lat = cs_aqm.variables['latitude'][:,:]
                        cs_lon = cs_aqm.variables['longitude'][:,:]
                        o3_cs = cs_aqm.variables['OZCON_1sigmalevel'][0,:,:]
                        scale= 1.
                        cs_aqm.close()
                    elif os.path.exists(aqmfilein2):
                        ## print(aqmfilein2+" exists")
                        outfile=working_dir+"/o3."+fhh2+".nc"
                        subprocess.call([wgrib2+' -d 1 -netcdf '+outfile+' '+aqmfilein2], shell=True)
                        aqmfilein2=outfile
                        cs_aqm = netcdf.Dataset(aqmfilein2)
                        cs_lat = cs_aqm.variables['latitude'][:,:]
                        cs_lon = cs_aqm.variables['longitude'][:,:]
                        o3_cs = cs_aqm.variables['OZCON_1sigmalevel'][0,:,:]
                        scale= 1.
                        cs_aqm.close()
                    else:
                        print("Can not find "+aqmfilein)
                        print("Can not find "+aqmfilein2)
                        continue
                        ## sys.exit()

            ## if flag_ak == "no" and iplot[num_reg-3] == 1:
            ##     iplot[num_reg-3] = 0
            ## if flag_hi == "no" and iplot[num_reg-2] == 1:
            ##     iplot[num_reg-2] = 0
            ## print("iplot length = "+str(num_reg))
            ##
                s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+fhh3
                ##    for ivar in range(0,num_var):
                msg=datetime.datetime.now()
                ## print("Start processing "+var[ivar])
                if var[ivar] == "o3":
                    s3_title="Ozone sfc_conc (ppbV)"
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
                        var_ak=pm_ak
                    if flag_hi == "yes":
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
                    if flag_ak == "yes":
                        var_ak=pm_ak
                    if flag_hi == "yes":
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
                                if flag_ak == "yes":
                                    ax.contourf(
                                         ak_lon, ak_lat, pvar_ak,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                                if flag_hi == "yes":
                                    ax.contourf(
                                         hi_lon, hi_lat, pvar_hi,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                        ax.set_title(title)
                        ## cb2.set_label('Discrete intervals, some other units')
                        fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,shrink=1.0,format=cbar_num_format)

                        if flag_find_epa_ascii == "yes":
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
                                elif var[ivar]== 'o3':
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
                                        flag_find_color="no"
                                        for j in range(0,nlev-1):
                                            if plot_var[i] >= clevs[j] and plot_var[i] < clevs[j+1]:
                                                color.append(ccols[j])
                                                flag_find_color="yes"
                                                break
                                        if flag_find_color =="no":
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
                                        flag_find_color='no'
                                        for j in range(0,nlev-1):
                                            if plot_var[i] >= clevs[j] and plot_var[i] < clevs[j+1]:
                                                color.append(ccols[j])
                                                flag_find_color='yes'
                                                break
                                        if flag_find_color =='no':
                                            print('Can not assign proper value for color, program stop')
                                            sys.exit()
    
                            ## s = [20*4**n for n in range(len(x))]
                            ## ax.scatter(var_lon,var_lat,c=color,cmap=cmap,marker='o',s=100,zorder=1, transform=ccrs.PlateCarree(), edgecolors='black')
                            ax.scatter(var_lon,var_lat,c=color,cmap=cmap,marker='o',s=mksize[ireg],zorder=1, transform=ccrs.PlateCarree(), edgecolors='black')

                        savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"obs."+date.strftime(YMD_date_format)+"."+cycle_time+"."+fhh2+"."+var[ivar]+".k1.png"
                        plt.savefig(savefig_name, bbox_inches='tight')
                        plt.close()
            ## scp by cycle and variable
            ##
            os.chdir(figdir)
            parta=os.path.join("/usr", "bin", "scp")
            if 1 == 1 :
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", date.strftime(Y_date_format), date.strftime(YMD_date_format), cycle_time)
            else:
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer_36")
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "ftp")
            subprocess.call(['scp -p * '+partb], shell=True)
            msg=datetime.datetime.now()
            print("End   processing "+var[ivar])
            print("FIG DIR = "+figdir)
        msg=datetime.datetime.now()
        print("End   processing "+date.strftime(YMD_date_format)+" "+cycle_time+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc
