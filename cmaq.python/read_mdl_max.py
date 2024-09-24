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

script_dir=os.getcwd()
print("Script directory is "+script_dir)

### PASSED AGRUEMENTS
if len(sys.argv) < 6:
    print("you must set 6 arguments as model1 model2 variabels[o3|pm25|all] cycle[06|12|all]  start_date end_date")
    sys.exit()
else:
    envir1 = sys.argv[1]
    envir2 = sys.argv[2]
    sel_var = sys.argv[3]
    sel_cyc = sys.argv[4]
    start_date = sys.argv[5]
    end_date = sys.argv[6]

stmp_dir="/lfs/h2/emc/stmp/"+user
if not os.path.exists(stmp_dir):
    os.mkdir(stmp_dir)
figdir=stmp_dir

ptmp_dir="/lfs/h2/emc/ptmp/"+user
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
working_dir=stmp_dir+"/"+workid
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

os.chdir(working_dir)

msg_file=working_dir+"/msg_"+sel_var+"_"+start_date+"_"+sel_cyc
cmd="cat /etc/cluster_name"
subprocess.call([cmd+" > "+msg_file], shell=True)
cmd="cat /etc/wcoss.conf | grep cluster_name | awk -F\":\" '{print $2}'"
subprocess.call([cmd+" > "+msg_file], shell=True)
if os.path.isfile(msg_file):
    with open(msg_file, 'r') as sh:
        line=sh.readline()
        machine=line.rstrip()
    sh.close()
if machine.lower() == "dogwood":
    remote="cactus"
elif machine.lower() == "cactus":
    remote="dogwood"
else:
    print("System name not defined for this script")
    sys.exit()

cmd="cat /etc/wcoss.conf | grep sec_profile | awk -F\":\" '{print $2}'"
subprocess.call([cmd+" > "+msg_file], shell=True)
if os.path.isfile(msg_file):
    with open(msg_file, 'r') as sh:
        line=sh.readline()
        machine_type=line.rstrip()
        flag_primary=False
        if machine_type.upper() == "PRIMARYSYS":
            flag_primary=True
    sh.close()

msg="Current machine is "+machine
if flag_primary:
    msg=msg+" as PRIMARYSYS"
else:
    msg=msg+" as BACKUPSYS"
print(msg)

msg="Remote  machine is "+remote
if not flag_primary:
    msg=msg+" as PRIMARYSYS"
else:
    msg=msg+" as BACKUPSYS"
print(msg)

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

if envir1.lower() == "aqmv70":
    comout1="/lfs/h1/ops/para/com/aqm/v7.0"
    comout1="/lfs/h1/ops/prod/com/aqm/v7.0"
    comout1="/lfs/h2/emc/physics/noscrub/"+user+"/rrfs_sfc_chem_met/"+envir1.lower()
elif envir1.lower() == "aqmv707":
    comout1="/lfs/h2/emc/physics/noscrub/"+user+"/rrfs_sfc_chem_met/"+envir1.lower()
elif envir1.lower() == "aqmv708":
    comout1="/lfs/h1/ops/para/com/aqm/v7.0"
    comout1="/lfs/h2/emc/physics/noscrub/"+user+"/rrfs_sfc_chem_met/"+envir1.lower()
else:
    print(f"{envir1} not defined")
    sys.exit()

if envir2.lower() == "aqmv70":
    comout2="/lfs/h1/ops/para/com/aqm/v7.0"
    comout2="/lfs/h1/ops/prod/com/aqm/v7.0"
    comout2="/lfs/h2/emc/physics/noscrub/"+user+"/rrfs_sfc_chem_met/"+envir2.lower()
elif envir2.lower() == "aqmv707":
    comout2="/lfs/h2/emc/physics/noscrub/"+user+"/rrfs_sfc_chem_met/"+envir2.lower()
elif envir2.lower() == "aqmv708":
    comout2="/lfs/h1/ops/para/com/aqm/v7.0"
    comout2="/lfs/h2/emc/physics/noscrub/"+user+"/rrfs_sfc_chem_met/"+envir2.lower()
else:
    print(f"{envir2} not defined")
    sys.exit()


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
##
## Current operational CMAQ does include runs for AK and HI domain
## Current EMC development CMAQ does not include runs for AK and HI domain
##
## ilen=len(envir)
## print("experiment is "+envir[0:ilen])
## sys.exit()

aqm_ver="v7.0"
dcomdir="/lfs/h1/ops/prod/dcom"
obsdir="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/epa_airnow_acsii"
obsdir="/lfs/h2/emc/vpppg/noscrub/"+os.environ['USER']+"/dcom/prod/airnow"

##
## new area need to be added ahead of ak.  The last three areas need to be fixed as "ak",   "hi",  "can"
## this is due to the code below remove plotting of ak and hi if no ak and hi input files ash been found
##
flag_proj="LambertConf"
## from 22.574179720000018 to 51.47512722912568
## from 228.37073225113136 to 296.6273160909873
# old -70.6 to -120.4
#     22.2 to 50.7
mksize= [ 121, 64, 64, 16,     36,      36,      36,     49,     49,     49,     49,     64,     64,    121,    100,    121,     36 ]
if flag_proj == "LambertConf":
    regname = [ "ctdeep", "Mckinney",  "aznw", "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
    rlon0 = [ -75., -125., -120., -165.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0,  -75.0, -166.0, -161.5, -141.0 ]
    rlon1 = [ -71., -110., -100., -70.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0,  -71.0, -132.0, -153.1, -60.0 ]
    rlat0 = [  40.4, 40., 30.0, 10.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   40.2,   53.2,   17.8,   38.0 ]
    rlat1 = [  42.2, 45., 40., 75.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   41.8,   71.2,   23.1,   70.0 ]
else:
    regname = [   "Mckinney",  "aznw", "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
    rlon0 = [ -125., -120., -175.0, -124.0,  -100.0, -128.0,  -82.0, -125.0,  -95.0, -125.0, -105.0, -105.0,  -75.0, -170.0, -161.0, -141.0 ]
    rlon1 = [  -110., -100., -55.0,  -70.0,   -65.0,  -90.0,  -67.0, -103.0,  -79.0, -105.0,  -85.0,  -85.0,   -71.0, -130.0, -154.0,  -60.0 ]
    rlat0 = [    40., 30.0, 0.0,   22.0,    22.0,   24.5,   37.0,   38.0,   24.0,   30.0,   38.0,   24.0,   40.2,   52.0,   18.0,   38.0 ]
    rlat1 = [   45., 40., 70.0,   51.0,    50.0,   54.5,   48.0,   52.0,   38.0,   45.0,   52.0,   40.0,   41.8,   72.0,   23.0,   70.0 ]
xsize = [ 10, 10, 10, 10,     10,       8,      8,      8,      8,      8,      8,      8,      8,     10,      8,      8,     10 ]
ysize = [ 8,   5, 5, 8,      8,       8,      8,      8,      8,      8,      8,      8,      8,      5,      8,      8,     8 ]
if 1 == 1:
    iplot = [ 1, 0, 0,   1,      1,       1,      1,      1,      1,      1,      1,      0,      0,      1,      1,      1, 0 ]
else:
    iplot = [ 1, 1, 1,   1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1, 1 ]
num_reg=len(iplot)

date=sdate
while date <= edate:
    YMD=date.strftime(YMD_date_format)
    for cyc in cycle:
        cycle_time="t"+cyc+"z"
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[0:2]))
        for ivar in range(0,num_var):
            fcst_hour=fcst_ini
            flag_read_latlon=False
            hour_beg = 0
            hour_end = 72
            hour_end = hour_beg + 1
            hour_beg = 24
            hour_end = 48
            if hour_beg != 0:
                set_hour=0
                while set_hour < hour_beg:
                    fcst_hour=fcst_hour+hour_inc
                    set_hour+=1
            for fcst_hr in range(hour_beg,hour_end):
                nout=fcst_hr+1
                str_fcst_hr=str(nout)
                ## fhh=str_pad(fcst_hr,3,'0',STR_PAD_LEFT)
                fhh=str_fcst_hr.zfill(3)
                fhh2=str_fcst_hr.zfill(2)
                print("   ")
                ## READ hourly EPA AirNOW OBS data
                ## note obs is forward average and model is backward, so they are different by an hour
                obs_hour=fcst_hour
                fcst_hour=fcst_hour + hour_inc
                s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+fhh
                ## print(s2_title)

                ## Read in one hourly data one at a time
                flag_with_obs=True
                obsfile= "HourlyAQObs_"+obs_hour.strftime(obs_YMDH_date_format)+".dat"
                ifile=os.path.join(dcomdir,obs_hour.strftime(YMD_date_format),"airnow",obsfile)
                ## ifile=os.path.join(obsdir,obs_hour.strftime(YMD_date_format),"airnow",obsfile)
                ifile2=os.path.join(obsdir,obs_hour.strftime(Y_date_format),obs_hour.strftime(YMD_date_format),obsfile)
                ifile2=os.path.join(obsdir,obs_hour.strftime(YMD_date_format),"airnow",obsfile)
                if os.path.exists(ifile):
                    infile=ifile
                    ## print(infile+" exists")
                elif os.path.exists(ifile2):
                    infile=ifile2
                    ## print(infile+" exists")
                else:
                    ## print("Can not find both "+ifile+" and "+ifile2)
                    flag_with_obs=False

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

                if var[ivar] == "pm25":
                    ## aqmfilein1=comout1+"/aqm."+date.strftime(YMD_date_format)+"/"+cyc+"/aqm.t"+cyc+"z.chem_sfc.f"+fhh+".nc"
                    ## aqmfilein2=comout2+"/aqm."+date.strftime(YMD_date_format)+"/"+cyc+"/aqm.t"+cyc+"z.chem_sfc.f"+fhh+".nc"
                    aqmfilein1=comout1+"/aqm."+date.strftime(YMD_date_format)+"/aqm.t"+cyc+"z.chem_sfc.f"+fhh+".nc"
                    aqmfilein2=comout2+"/aqm."+date.strftime(YMD_date_format)+"/aqm.t"+cyc+"z.chem_sfc.f"+fhh+".nc"
                    if os.path.exists(aqmfilein1):
                        ## print(aqmfilein1+" exists")
                        cs_aqm1 = netcdf.Dataset(aqmfilein1)
                        cs_lat1 = cs_aqm1.variables['lat'][:,:]
                        cs_lon1 = cs_aqm1.variables['lon'][:,:]
        
                        pm_cs1 = cs_aqm1.variables['PM25_TOT'][0,:,:]
                        cs_aqm1.close()
                        check_detail1=False
                        if check_detail1:
                            j=cs_lat1.shape[0]
                            i=cs_lat1.shape[1]
                            print("LAT i= "+str(i)+"  j= "+str(j))
                            j=cs_lon1.shape[0]
                            i=cs_lon1.shape[1]
                            print("LON i= "+str(i)+"  j= "+str(j))
                            j=pm_cs1.shape[0]
                            i=pm_cs1.shape[1]
                            print("PM  i= "+str(i)+"  j= "+str(j))
                        jmax1=pm_cs1.shape[0]
                        imax1=pm_cs1.shape[1]
                    else:
                        print("Can not find "+aqmfilein1)
                    if os.path.exists(aqmfilein2):
                        ## print(aqmfilein2+" exists")
                        cs_aqm2 = netcdf.Dataset(aqmfilein2)
                        cs_lat2 = cs_aqm2.variables['lat'][:,:]
                        cs_lon2 = cs_aqm2.variables['lon'][:,:]
                        pm_cs2 = cs_aqm2.variables['PM25_TOT'][0,:,:]
                        cs_aqm2.close()
                        check_detail1=False
                        if check_detail1:
                            j=cs_lat2.shape[0]
                            i=cs_lat2.shape[1]
                            print("LAT i= "+str(i)+"  j= "+str(j))
                            j=cs_lon2.shape[0]
                            i=cs_lon2.shape[1]
                            print("LON i= "+str(i)+"  j= "+str(j))
                            j=pm_cs2.shape[0]
                            i=pm_cs2.shape[1]
                            print("PM  i= "+str(i)+"  j= "+str(j))
                        jmax2=pm_cs2.shape[0]
                        imax2=pm_cs2.shape[1]
                    else:
                        print("Can not find "+aqmfilein2)
                    ## lon -117 to -109 lat 42 to 50
                    rlon1=-109. + 360.
                    rlon0=-117. + 360.
                    rlat0=42.
                    rlat1=50.
                    ncount_1=0
                    pm25_1=[]
                    plat_1=[]
                    plon_1=[]
                    for j in range(0,jmax1-1):
                        for i in range(0,imax1-1):
                            if cs_lat1[j,i] >= rlat0 and cs_lat1[j,i] <= rlat1 and cs_lon1[j,i] >= rlon0 and cs_lon1[j,i] <= rlon1:
                                ncount_1=ncount_1+1
                                pm25_1.append(pm_cs1[j,i])
                                plat_1.append(cs_lat1[j,i])
                                plon_1.append(cs_lon1[j,i])
                    nc=str(ncount_1)
                    ## print(f"total {envir1} point found in the selected domain = {nc}")
                    ncount_2=0
                    pm25_2=[]
                    plat_2=[]
                    plon_2=[]
                    for j in range(0,jmax2-1):
                        for i in range(0,imax2-1):
                            if cs_lat2[j,i] >= rlat0 and cs_lat2[j,i] <= rlat1 and cs_lon2[j,i] >= rlon0 and cs_lon2[j,i] <= rlon1:
                                ncount_2=ncount_2+1
                                pm25_2.append(pm_cs2[j,i])
                                plat_2.append(cs_lat2[j,i])
                                plon_2.append(cs_lon2[j,i])
                    nc=str(ncount_2)
                    ## print(f"total {envir2} point found in the selected domain = {nc}")
                    regmax1=np.max(pm25_1)
                    regmin1=np.min(pm25_1)
                    regmax2=np.max(pm25_2)
                    regmin2=np.min(pm25_2)
                    print(f"{YMD} {cycle_time} {s2_title} {envir1}  max={regmax1}")
                    print(f"{YMD} {cycle_time} {s2_title} {envir2} max={regmax2}")
                ## in ppm
                if var[ivar] == "o3":
                    aqmfilein=comout+"/aqm."+date.strftime(YMD_date_format)+"/"+cyc+"/aqm.t"+cyc+"z.chem_sfc.f"+fhh+".nc"
                    aqmfilein2=usrout+"/aqm."+date.strftime(YMD_date_format)+"/aqm.t"+cyc+"z.chem_sfc.f"+fhh+".nc"
                    if os.path.exists(aqmfilein):
                        ## print(aqmfilein+" exists")
                        cs_aqm = netcdf.Dataset(aqmfilein)
                        if not flag_read_latlon:
                            cs_lat = cs_aqm.variables['lat'][:,:]
                            cs_lon = cs_aqm.variables['lon'][:,:]
                            flag_read_latlon=True
                        o3_cs = cs_aqm.variables['o3'][0,:,:]
                        scale= 1.
                        cs_aqm.close()
                    elif os.path.exists(aqmfilein2):
                        ## print(aqmfilein2+" exists")
                        cs_aqm = netcdf.Dataset(aqmfilein2)
                        if not flag_read_latlon:
                            cs_lat = cs_aqm.variables['lat'][:,:]
                            cs_lon = cs_aqm.variables['lon'][:,:]
                            flag_read_latlon=True
                        o3_cs = cs_aqm.variables['o3'][0,:,:]
                        scale= 1.
                        cs_aqm.close()
                    else:
                        print("Can not find "+aqmfilein)
                        print("Can not find "+aqmfilein2)
                        sys.exit()

                plot_location = True
                plot_location = False
                if plot_location:
                    prlon0=-165.
                    prlon1=-70.
                    prlat0=10.
                    prlat1=75.
                    prlon0=-125.
                    prlon1=-103.
                    prlat0=38.
                    prlat1=52.
                    extent=[ prlon0, prlon1, prlat0, prlat1 ]
                    clat=0.5*(prlat0 + prlat1)
                    clon=0.5*(prlon0 + prlon1)
                    aqmproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, false_easting=-58.775, false_northing=48.772, standard_parallels=(33, 45), globe=None)
                    fig, ax = plt.subplots(figsize=(8,8))
    
                    ax = plt.axes(projection=aqmproj)
                    ax.set_extent(extent)
                    ax.coastlines('50m')
                    states_provinces = cfeature.NaturalEarthFeature(
                        category='cultural',
                        name='admin_1_states_provinces_lines',
                        scale='50m',
                        facecolor='none')
                    ax.add_feature(states_provinces, facecolor='none', edgecolor='gray')
                    ax.add_feature(cfeature.BORDERS, facecolor='none', linestyle=':')
                    ax.add_feature(cfeature.LAKES, facecolor='None', edgecolor='black', alpha=0.5)
                    ax.scatter(plon_1,plat_1,c='red',marker='o',s=2,zorder=1, transform=ccrs.PlateCarree(), edgecolors='red')
                    savefig_name = figdir+"/test_area.png"
                    print(savefig_name)
                    plt.savefig(savefig_name, bbox_inches='tight')
                    plt.close()
    
                    os.chdir(figdir)
                    parta=os.path.join("/usr", "bin", "scp")
                    if 1 == 2 :
                        partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", date.strftime(Y_date_format), date.strftime(YMD_date_format), cycle_time)
                    else:
                        partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
                        partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer_36")
                        partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "ftp")
                    subprocess.call(['scp -p test_area.png '+partb], shell=True)
    date = date + date_inc
