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

## from cartopy import config
## config['data_dir'] = '/apps/ops/prod/data/cartopy'

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
            aqm_ver_prod=ver[1]
rfile.close()
if aqm_ver_prod=="":
    aqm_ver_prod="v6.1"
print("aqm_ver="+aqm_ver_prod)
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

working_root=stmp_dir+"/aqm_plot_working_max_ave"
if os.path.exists(working_root):
    os.chdir(working_root)
else:
    os.makedirs(working_root)
    os.chdir(working_root)

msg_file=working_root+"/devmachine"
subprocess.call(["cat /etc/cluster_name > "+msg_file], shell=True)
if os.path.isfile(msg_file):
    with open(msg_file, 'r') as sh:
        line=sh.readline()
        dev_machine=line.rstrip()
        print("currently on "+dev_machine)
        sh.close()

msg_file=working_root+"/prodmachine"
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
if len(sys.argv) < 4:
    print("you must set 4 arguments as model[prod|para|...] cycle[06|12|all]  start_date end_date")
    sys.exit()
else:
    envir = sys.argv[1]
    sel_cyc = sys.argv[2]
    start_date = sys.argv[3]
    end_date = sys.argv[4]

if envir.lower() == "para":
    fig_exp="ncopara"
else:
    fig_exp=envir.lower()

sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:]))
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:]))
YMDH_date_format = "%Y%m%d/%H"
YMD_date_format = "%Y%m%d"
YM_date_format = "%Y%m"
Y_date_format = "%Y"
M_date_format = "%m"
Month_date_format = "%B"
D_date_format = "%d"
H_date_format = "%H"
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

grid148="148"
grid227="227"
grid198="198"
grid139="139"
grid196="196"
grid793="793"

flag_ak=True
flag_hi=True
aqmv6=False
aqmv7=False
caseid="v70"
nfind=envir.find(caseid)
if nfind == -1:
    print("AQMv6 simulation")
    s1_lead="CMAQ"
    aqmv6 = True
    nfind=envir.find("_bc")
    if nfind == -1:
        print("not a bias_correction cases")
        EXP=envir
        BC_append=""
        BC_fig_append=BC_append
        print("exp="+EXP)
        print("BC_append="+BC_append)
        flag_ak=True
        flag_hi=True
    else:
        print("A bias_correction cases")
        EXP=envir[0:nfind]
        BC_append="_bc"
        BC_fig_append="bc"
        print("exp="+EXP)
        print("BC_append="+BC_append)
        flag_ak=False
        flag_hi=False
    if EXP.lower() == "prod" or EXP.lower() == "para" or EXP.lower() == "firev4":
        aqm_ver=aqm_ver_prod
        exp_grid=grid148
        expid="cs"
        comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+EXP.lower()
        comout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
    else:
        print("Experiement ID "+EXP.lower()+" not found for this code, Program exit")
        sys.exit()
    usrout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+EXP.lower()
    usrout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/verification/aqm/"+EXP.lower()
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
        expid="aqm"   # after 4/1/2023 directory will be changed into aqm.yyyymmdd
        BC_append=""
        BC_fig_append=BC_append
        print("exp="+EXP)
        print("expid="+expid)
        print("BC_append="+BC_append)
        flag_ak=True
        flag_hi=True
    else:
        EXP=envir[0:nfind]
        n0=len(caseid)
        n1=len(EXP)
        expid=EXP[n0:n1]
        expid="aqm"   # after 4/1/2023 directory will be changed into aqm.yyyymmdd
        BC_append="_bc"
        BC_fig_append="bc"
        print("exp="+EXP)
        print("expid="+expid)
        print("BC_append="+BC_append)
        flag_ak=False
        flag_hi=False
    if sdate.strftime(Y_date_format) == "2023":
        ## correct one should be comout="/lfs/h2/emc/ptmp/jianping.huang/emc.para/com/aqm/"+aqm_ver
        ## Force to use user archived directory
        comout="/lfs/h2/emc/ptmp/jianping.huang/emc.para/com/aqm/"+aqm_ver
    else:
        ## correct one should be comout="/lfs/h2/emc/aqmtemp/para/com/aqm/"+aqm_ver
        ## Force to use user archived directory
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
   cycle=[ "06", "12" ]
elif sel_cyc == "06":
   cycle=[ "06" ]
elif sel_cyc == "12":
   cycle=[ "12" ]
else:
    print("seletced cycle "+sel_cyc+" can not be recongized.")
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

dcomdir="/lfs/h1/ops/prod/dcom"
obsdir="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/epa_airnow_acsii"
figout=stmp_dir

##
## new area need to be added ahead of ak.  The last three areas need to be fixed as "ak",   "hi",  "can"
## this is due to the code below remove plotting of ak and hi if no ak and hi input files ash been found
##
flag_proj="LambertConf"
mksize= [ 121 ]
regname = [ "ctdeep" ]
rlon0 = [ -75.  ]
rlon1 = [ -71.  ]
rlat0 = [  40.4 ]
rlat1 = [  42.2 ]
xsize = [  10   ]
ysize = [   8   ]
iplot = [   1   ]
num_reg=len(iplot)

flag_ak = False
flag_hi = False

##
## EPA daily max/ave obs format; any changes in the order of parameter need to be updated in std_hdr
##
## Valid date|AQSID|site name|parameter name|reporting units|value|averaging period|data source|AQI|AQI Category|latitude|longitude|full AQSID with 3 digit country code prefix
## 01/09/23|060290014|Bakersfield - California Ave|PM2.5-24hr|UG/M3|4.5|24|California Air Resources Board|19|0|35.356615|-119.062613|840060290014
std_hdr = [ "ValidDate", "AQSID",           "SiteName",   "VariableName", "Unit",
            "Value",     "AveragingPeriod", "DataSource", "AQI",          "AQICategory",
            "Latitude",  "Longitude",       "full AQSID with 3 digit country code prefix" ]
nhdr=len(std_hdr)
for n in range(0,nhdr):
    if std_hdr[n] == "VariableName":
        loc_name=n
        break
for n in range(0,nhdr):
    if std_hdr[n] == "Unit":
        loc_unit=n
        break
for n in range(0,nhdr):
    if std_hdr[n] == "Value":
        loc_value=n
        break
for n in range(0,nhdr):
    if std_hdr[n] == "Longitude":
        loc_lon=n
        break
for n in range(0,nhdr):
    if std_hdr[n] == "Latitude":
        loc_lat=n
        break
obsfile="daily_data_v2.dat"
date=sdate
while date <= edate:
    if flag_ak:
        for cyc in cycle:
            cycle_time="t"+cyc+"z"
            for ivar in range(0,num_var):
                if var[ivar] == "ozmax8":
                    fileid="max_8hr_o3"
                elif var[ivar] == "ozmax1":
                    fileid="max_1hr_o3"
                elif var[ivar] == "pmave24":
                    fileid="ave_24hr_pm25"
                elif var[ivar] == "pmmax1":
                    fileid="max_1hr_pm25"
                if aqmv7:
                    check_file="aqm."+cycle_time+"."+fileid+BC_append+"."+grid793+".grib2"
                    aqmfilein=comout+"/"+expid+"."+date.strftime(YMD_date_format)+"/"+cyc+"/"+check_file
                    aqmfilein2=usrout+"/cs."+date.strftime(YMD_date_format)+"/"+check_file
                if aqmv6:
                    check_file="aqm."+cycle_time+"."+fileid+BC_append+"."+grid198+".grib2"
                    aqmfilein=comout+"/ak."+date.strftime(YMD_date_format)+"/"+check_file
                    aqmfilein2=usrout+"/ak."+date.strftime(YMD_date_format)+"/"+check_file
                if os.path.exists(aqmfilein):
                    print(aqmfilein+" exists")
                elif os.path.exists(aqmfilein2):
                    print(aqmfilein2+" exists")
                else:
                    flag_ak=False
                    print("Can not find "+aqmfilein+" and "+aqmfilein2)
                    break
    if flag_hi:
        for cyc in cycle:
            cycle_time="t"+cyc+"z"
            for ivar in range(0,num_var):
                if var[ivar] == "ozmax8":
                    fileid="max_8hr_o3"
                elif var[ivar] == "ozmax1":
                    fileid="max_1hr_o3"
                elif var[ivar] == "pmave24":
                    fileid="ave_24hr_pm25"
                elif var[ivar] == "pmmax1":
                    fileid="max_1hr_pm25"
                if aqmv7:
                    check_file="aqm."+cycle_time+"."+fileid+BC_append+"."+grid793+".grib2"
                    aqmfilein=comout+"/"+expid+"."+date.strftime(YMD_date_format)+"/"+cyc+"/"+check_file
                    aqmfilein2=usrout+"/cs."+date.strftime(YMD_date_format)+"/"+check_file
                if aqmv6:
                    check_file="aqm."+cycle_time+"."+fileid+BC_append+"."+grid196+".grib2"
                    aqmfilein=comout+"/hi."+date.strftime(YMD_date_format)+"/"+check_file
                    ## check_file="aqm."+cycle_time+"."+fileid+BC_append+"."+grid139+".grib2"
                    aqmfilein2=usrout+"/hi."+date.strftime(YMD_date_format)+"/"+check_file
                if os.path.exists(aqmfilein):
                    print(aqmfilein+" exists")
                elif os.path.exists(aqmfilein2):
                    print(aqmfilein2+" exists")
                else:
                    flag_hi=False
                    print("Can not find "+aqmfilein+" and "+aqmfilein2)
                    break

    print("iplot length = "+str(num_reg))

    for cyc in cycle:
        cycle_time="t"+cyc+"z"
        working_dir=working_root+"/"+envir+"_"+date.strftime(YMD_date_format)+cycle_time
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)

        s1_title=s1_lead+" "+EXP.upper()+BC_append.upper()+" "+date.strftime(YMD_date_format)+" "+cycle_time
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[0:2]))
        for ivar in range(0,num_var):
            if var[ivar] == "ozmax8":
                obsid="OZONE-8HR"
                fileid="max_8hr_o3"
                varid="OZMAX8_1sigmalevel"
            elif var[ivar] == "ozmax1":
                obsid="OZONE-1HR"
                fileid="max_1hr_o3"
                varid="OZMAX1_1sigmalevel"
            elif var[ivar] == "pmave24":
                obsid="PM2.5-24hr"
                fileid="ave_24hr_pm25"
                varid="PMTF_1sigmalevel"
            elif var[ivar] == "pmmax1":
                obsid=""
                fileid="max_1hr_pm25"
                varid="PDMAX1_1sigmalevel"
            msg=datetime.datetime.now()
            print("Start processing "+date.strftime(YMD_date_format)+" "+cycle_time+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))

            file_hdr="aqm."+cycle_time+"."+fileid+BC_append+"."+exp_grid
            if aqmv7:
                aqmfilein=comout+"/"+expid+"."+date.strftime(YMD_date_format)+"/"+cyc+"/"+file_hdr+".grib2"
                aqmfilein2=usrout+"/cs."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
            if aqmv6:
                aqmfilein=comout+"/"+expid+"."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
                aqmfilein2=usrout+"/"+expid+"."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                outfile=working_dir+"/"+file_hdr+"."+date.strftime(YMD_date_format)+"."+cycle_time+".nc"
                subprocess.call([wgrib2+' -netcdf '+outfile+' '+aqmfilein], shell=True)
                aqmfilein=outfile
                cs_aqm = netcdf.Dataset(aqmfilein)
                cs_lat = cs_aqm.variables['latitude'][:,:]
                cs_lon = cs_aqm.variables['longitude'][:,:]
                cs_var = cs_aqm.variables['time'][:]
                nstep=len(cs_var)
                ozpm_cs = cs_aqm.variables[varid][:,:,:]
                cs_aqm.close()
            elif os.path.exists(aqmfilein2):
                print(aqmfilein2+" exists")
                outfile=working_dir+"/"+file_hdr+"."+date.strftime(YMD_date_format)+"."+cycle_time+".nc"
                subprocess.call([wgrib2+' -netcdf '+outfile+' '+aqmfilein2], shell=True)
                aqmfilein2=outfile
                cs_aqm = netcdf.Dataset(aqmfilein2)
                cs_lat = cs_aqm.variables['latitude'][:,:]
                cs_lon = cs_aqm.variables['longitude'][:,:]
                cs_var = cs_aqm.variables['time'][:]
                nstep=len(cs_var)
                ozpm_cs = cs_aqm.variables[varid][:,:,:]
                cs_aqm.close()
            else:
                print("Can not find "+aqmfilein+" "+aqmfilein2)
                continue
    
            if aqmv7 and flag_ak:
                ak_lat=cs_lat
                ak_lon=cs_lon
                ozpm_ak=ozpm_cs

            if aqmv7 and flag_hi:
                hi_lat=cs_lat
                hi_lon=cs_lon
                ozpm_hi=ozpm_cs

            if aqmv6 and flag_ak:
                file_hdr="aqm."+cycle_time+"."+fileid+BC_append+"."+grid198
                aqmfilein=comout+"/ak."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
                aqmfilein2=usrout+"/ak."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
                if os.path.exists(aqmfilein):
                    print(aqmfilein+" exists")
                    outfile=working_dir+"/ak."+file_hdr+"."+date.strftime(YMD_date_format)+"."+cycle_time+".nc"
                    subprocess.call([wgrib2+' -netcdf '+outfile+' '+aqmfilein], shell=True)
                    aqmfilein=outfile
                    ak_aqm = netcdf.Dataset(aqmfilein)
                    ak_lat = ak_aqm.variables['latitude'][:,:]
                    ak_lon = ak_aqm.variables['longitude'][:,:]
                    ak_var = ak_aqm.variables['time'][:]
                    nstep_ak=len(ak_var)
                    ozpm_ak = ak_aqm.variables[varid][:,:,:]
                    ak_aqm.close()
                elif os.path.exists(aqmfilein2):
                    print(aqmfilein2+" exists")
                    outfile=working_dir+"/ak."+file_hdr+"."+date.strftime(YMD_date_format)+"."+cycle_time+".nc"
                    subprocess.call([wgrib2+' -netcdf '+outfile+' '+aqmfilein2], shell=True)
                    aqmfilein2=outfile
                    ak_aqm = netcdf.Dataset(aqmfilein2)
                    ak_lat = ak_aqm.variables['latitude'][:,:]
                    ak_lon = ak_aqm.variables['longitude'][:,:]
                    ak_var = ak_aqm.variables['time'][:]
                    nstep_ak=len(ak_var)
                    ozpm_ak = ak_aqm.variables[varid][:,:,:]
                    ak_aqm.close()
                else:
                    print("Can not find "+aqmfilein+" "+aqmfilein2)
                    flag_ak = False
                    iplot[num_reg-3] = 0
        
            if aqmv6 and flag_hi:
                file_hdr="aqm."+cycle_time+"."+fileid+BC_append+"."+grid196
                aqmfilein=comout+"/hi."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
                aqmfilein2=usrout+"/hi."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
                if os.path.exists(aqmfilein):
                    print(aqmfilein+" exists")
                    outfile=working_dir+"/hi."+file_hdr+"."+date.strftime(YMD_date_format)+"."+cycle_time+".nc"
                    subprocess.call([wgrib2+' -netcdf '+outfile+' '+aqmfilein], shell=True)
                    aqmfilein=outfile
                    hi_aqm = netcdf.Dataset(aqmfilein)
                    hi_lat = hi_aqm.variables['latitude'][:]
                    hi_lon = hi_aqm.variables['longitude'][:]
                    hi_var = hi_aqm.variables['time'][:]
                    nstep_hi=len(hi_var)
                    ozpm_hi = hi_aqm.variables[varid][:,:,:]
                    hi_aqm.close()
                elif os.path.exists(aqmfilein2):
                    print(aqmfilein2+" exists")
                    outfile=working_dir+"/hi."+file_hdr+"."+date.strftime(YMD_date_format)+"."+cycle_time+".nc"
                    subprocess.call([wgrib2+' -netcdf '+outfile+' '+aqmfilein2], shell=True)
                    aqmfilein2=outfile
                    hi_aqm = netcdf.Dataset(aqmfilein2)
                    hi_lat = hi_aqm.variables['latitude'][:]
                    hi_lon = hi_aqm.variables['longitude'][:]
                    hi_var = hi_aqm.variables['time'][:]
                    nstep_hi=len(hi_var)
                    ozpm_hi = hi_aqm.variables[varid][:,:,:]
                    hi_aqm.close()
                else:
                    print("Can not find "+aqmfilein+" "+aqmfilein2)
                    flag_hi = False
                    iplot[num_reg-2] = 0
    
            msg=datetime.datetime.now()
            print("Start processing "+var[ivar])
            jobid="aqm"+"_"+envir+"_"+date.strftime(YMD_date_format)+"_"+var[ivar]+"_"+cyc
            figdir = figout+"/"+jobid
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("figdir = "+figdir)
            print("working on "+date.strftime(YMD_date_format)+" "+cycle_time+" "+var[ivar])
            if var[ivar] == "ozmax8" or var[ivar] == "ozmax1":
                ## s3_title="Max 8HR-AVG SFC Ozone CONC (ppbV)"
                s3_title=fileid+" (ppbV)"
                scale=1.
                clevs = [ 3., 6., 9., 12., 25., 35., 45., 55., 65., 71., 75., 85., 95., 105. ]
                var_cs=ozpm_cs*scale
                if flag_ak:
                    var_ak=ozpm_ak*scale
                if flag_hi:
                    var_hi=ozpm_hi*scale
                cmap = mpl.colors.ListedColormap([
                      (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000),
                      (0.0000,0.7490,1.0000), (0.0000,1.0000,1.0000),
                      (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                      (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000), (0.9412,0.5098,0.1569),
                      (1.0000,0.0000,0.0000), (0.7020,0.0000,0.0000)
                      ])
                cmap.set_under((0.8627,0.8627,1.0000))
                cmap.set_over((0.4310,0.2780,0.7250))
            elif var[ivar] == "pmave24" or var[ivar] == "pmmax1":
                ## s3_title="PM25 sfc_conc ($\u03bcg/m^3$)"
                s3_title=fileid+" ($\u03bcg/m^3$)"
                scale=1.
                clevs = [ 3., 6., 9., 12., 15., 35., 55., 75., 100., 125., 150., 250., 300., 400., 500., 600., 750. ]
                var_cs=ozpm_cs
                if flag_ak:
                    var_ak=ozpm_ak
                if flag_hi:
                    var_hi=ozpm_hi
                cmap = mpl.colors.ListedColormap([
                      (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                      (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000),
                      (1.0000,0.3840,0.3840), (1.0000,0.0000,0.0000), (0.8000,0.0000,0.0000), (0.7020,0.0000,0.0000),
                      (0.6120,0.5100,0.8120), (0.5180,0.3880,0.7650), (0.4310,0.2780,0.7250),(0.2980,0.1920,0.5020),
                      (0.4706,0.4706,0.4706), (0.7843,0.7843,0.7843)
                      ])
                cmap.set_under((0.8627,0.8627,1.0000))
                cmap.set_over((0.9412,0.9412,0.9412))
            elif var[ivar] == "pmave24_nonseason":
                ## s3_title="PM25 sfc_conc ($\u03bcg/m^3$)"
                s3_title=fig_var_name+" ($\u03bcg/m^3$)"
                scale=1.
                clevs = [ 0., 3., 6., 9., 12., 25., 35., 45., 55., 65., 75., 85., 95., 105. ]
                var_cs=ozpm_cs
                if flag_ak:
                    var_ak=ozpm_ak
                if flag_hi:
                    var_hi=ozpm_hi
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
            try:
                nstep
            except NameError:
                if flag_ak:
                    nstep = nstep_ak
                elif flag_hi:
                    nstep = nstep_hi
                else:
                    print(" no nstep ahs been defined")
                    sys.exit()
            ## for n in range(0,2):
            for n in range(0,nstep):
                obs_hour=fcst_hour
                #########################################################
                ##########      Read Forecast Day OBS DATA     ##########
                #########################################################
                flag_with_obs=True
                if obsid == "":
                    flag_with_obs=False
                else:
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
                    rfile=open(infile, 'r')
                    count=0
                    obs_o3pm=[]
                    obs_o3pm_lat=[]
                    obs_o3pm_lon=[]
                    for line in rfile:
                        line=line.rstrip("\n")
                        val=line.split("|")
                        if val[loc_name] == obsid:
                            obs_o3pm.append(float(val[loc_value]))
                            obs_o3pm_lat.append(float(val[loc_lat]))
                            obs_o3pm_lon.append(float(val[loc_lon]))
                    rfile.close()
                    if len(obs_o3pm) == 0:
                        flag_with_obs=False

                cmonth=fcst_hour.strftime(Month_date_format)[0:3]
                begdate="05Z"+fcst_hour.strftime(D_date_format)+cmonth.upper()+fcst_hour.strftime(Y_date_format)

                nout=n+1
                fcst_hour=fcst_hour+date_inc
                cmonth=fcst_hour.strftime(Month_date_format)[0:3]
                enddate="04Z"+fcst_hour.strftime(D_date_format)+cmonth.upper()+fcst_hour.strftime(Y_date_format)
                s2_title = begdate+"-"+enddate
                title=s1_title+"\n"+s2_title+" "+s3_title
                pvar_cs = var_cs[n,:,:]
                if flag_ak:
                    pvar_ak = var_ak[n,:,:]
                if flag_hi:
                    pvar_hi = var_hi[n,:,:]
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
                        ax.coastlines('10m')
                        states_provinces = cfeature.NaturalEarthFeature(
                             name='admin_1_states_provinces_lakes',
##                             name='admin_1_states_provinces_lines',
                             category='cultural',
                             scale='10m',
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
                            if var[ivar] == "pmave24":
                                num_pm25=len(obs_o3pm)
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
                                    if obs_o3pm[i] < clevs[0]:
                                        color.append((0.8627,0.8627,1.0000))
                                    elif obs_o3pm[i] >= clevs[nlev-1]:
                                        color.append((0.9412,0.9412,0.9412))
                                    else:
                                        flag_find_color=False
                                        for j in range(0,nlev-1):
                                            if obs_o3pm[i] >= clevs[j] and obs_o3pm[i] < clevs[j+1]:
                                                color.append(ccols[j])
                                                flag_find_color=True
                                                break
                                        if not flag_find_color:
                                            print("Can not assign proper value for color, program stop")
                                            sys.exit()
    
                            elif var[ivar] == "ozmax1" or var[ivar] == "ozmax8":
                                num_o3=len(obs_o3pm)
                                clevs = [ 3., 6., 9., 12., 25., 35., 45., 55., 65., 71., 75., 85., 95., 105. ]
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
                                    if obs_o3pm[i] < clevs[0]:
                                        color.append((0.8627,0.8627,1.0000))
                                    elif obs_o3pm[i] >= clevs[nlev-1]:
                                        color.append((0.4310,0.2780,0.7250))
                                    else:
                                        flag_find_color=False
                                        for j in range(0,nlev-1):
                                            if obs_o3pm[i] >= clevs[j] and obs_o3pm[i] < clevs[j+1]:
                                                color.append(ccols[j])
                                                flag_find_color=True
                                                break
                                        if not flag_find_color:
                                            print('Can not assign proper value for color, program stop')
                                            sys.exit()
    
                            ## s = [20*4**n for n in range(len(x))]
                            ## ax.scatter(obs_o3pm_lon,obs_o3pm_lat,c=color,cmap=cmap,marker='o',s=100,zorder=1, transform=ccrs.PlateCarree(), edgecolors='black')
                            ax.scatter(obs_o3pm_lon,obs_o3pm_lat,c=color,cmap=cmap,marker='o',s=mksize[ireg],zorder=1, transform=ccrs.PlateCarree(), edgecolors='black')
                        if flag_with_obs:
                            savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"obs."+date.strftime(YMD_date_format)+"."+cycle_time+"."+fileid+".day"+str(format(nout,'01d'))+".k1.png"
                        else:
                            ## savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"."+date.strftime(YMD_date_format)+"."+cycle_time+"."+fileid+".day"+str(format(nout,'01d'))+".k1.png"
                            savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"obs."+date.strftime(YMD_date_format)+"."+cycle_time+"."+fileid+".day"+str(format(nout,'01d'))+".k1.png"
                        plt.savefig(savefig_name, bbox_inches='tight')
                        plt.close()
            ##
            ## scp by cycle and variable
            ##
            os.chdir(figdir)
            parta=os.path.join("/usr", "bin", "scp")
            if 1 == 1 :
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", date.strftime(Y_date_format), date.strftime(YMD_date_format), cycle_time)
            else:
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
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