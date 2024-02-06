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

user=os.environ['USER']

### PASSED AGRUEMENTS
if len(sys.argv) < 6:
    print("you must set 6 arguments as model1[prod|para|...] model2 cycle[06|12|all]  start_date end_date")
    sys.exit()
else:
    envir1 = sys.argv[1]
    envir2 = sys.argv[2]
    sel_cyc = sys.argv[3]
    start_date = sys.argv[4]
    end_date = sys.argv[5]

if envir1.lower() == "para":
    fig_exp1="ncopara"
elif envir1.lower() == "para_bc":
    fig_exp1="ncoparabc"
else:
    fig_exp1=envir1.lower()
if envir2.lower() == "para":
    fig_exp2="ncopara"
elif envir2.lower() == "para_bc":
    fig_exp2="ncoparabc"
else:
    fig_exp2=envir2.lower()
fig_id=fig_exp2+"-"+fig_exp1
title_id=fig_exp2.upper()+"-"+fig_exp1.upper()

stmp_dir="/lfs/h2/emc/stmp/"+user
if not os.path.exists(stmp_dir):
    os.mkdir(stmp_dir)

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
working_dir=stmp_dir+"/"+envir1+"_"+envir2+"_"+workid
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

os.chdir(working_dir)

msg_file=working_dir+"/msg_"+start_date+"_"+sel_cyc
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

YMDH_date_format = "%Y%m%d/%H"
YMD_date_format = "%Y%m%d"
YM_date_format = "%Y%m"
Y_date_format = "%Y"
M_date_format = "%m"
D_date_format = "%d"
H_date_format = "%H"
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

if envir1 == "prod":
    var=[ "veg", "lai" ]
else:
    var=[ "veg", "lai" ]

if envir2 == "prod":
    var2=[ "veg", "lai" ]
else:
    var2=[ "veg", "lai" ]

figid=[ "veg", "lai" ]

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
cbar_num_format = "%0.2f"
cbar_num_format = "%0.d"
plt.close('all') # close all figures

msg=datetime.datetime.now()
msg=msg - date_inc
grdcro2d_date=msg.strftime("%Y%m%d")

##
## Current operational CMAQ does include runs for AK and HI domain
## Current EMC development CMAQ does not include runs for AK and HI domain
##
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
find_dir=[
          "/lfs/h2/emc/ptmp/"+user+"/com/aqm/"+envir1,
          "/lfs/h2/emc/physics/noscrub/"+user+"/com/aqm/"+envir1
         ]
sub_met_dir=[
            "cs."+sdate.strftime(YMD_date_format),
            "cs."+sdate.strftime(YMD_date_format)+".met"
            ]
metout1="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
metout2="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
flag_find_idir="no"
for idir in find_dir:
    if envir1 == "prod":
        comout1="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
    elif envir1 == "ncopara":
        comout1="/lfs/h1/ops/para/com/aqm/"+aqm_ver
    else:
        comout1=idir
    print("check "+idir)
    flag_find_sdir="no"
    for sdir in sub_met_dir:
        subout=sdir
        flag_find_cyc="yes"
        for cyc in cycle:
            check_file="aqm."+cyc+".metcro2d.ncf"
            aqmfilein=comout1+"/"+sdir+"/"+check_file
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
            else:
                flag_find_cyc="no"
                break
        if flag_find_cyc == "yes":
            flag_find_sdir="yes"
            break
    if flag_find_sdir== "yes":
        slen=len(subout)
        subdir_marker1=subout[slen-3:slen]
        flag_find_idir="yes"
        break
if flag_find_idir == "yes":
    print("comout1 set to "+comout1)
else:
    sys.exit()

if envir1 == "prod" or envir1 == "para6x" or envir1 == "para6b":
    flag_ak = "yes"
    flag_hi = "yes"
else:
    flag_ak = "no"
    flag_hi = "no"

find_dir=[
          "/lfs/h2/emc/ptmp/"+user+"/com/aqm/"+envir2,
          "/lfs/h2/emc/physics/noscrub/"+user+"/com/aqm/"+envir2
         ]
flag_find_idir="no"
for idir in find_dir:
    if envir2 == "prod":
        comout2="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
    elif envir2 == "ncopara":
        comout2="/lfs/h1/ops/para/com/aqm/"+aqm_ver
    else:
        comout2=idir
    print("check "+idir)
    flag_find_sdir="no"
    for sdir in sub_met_dir:
        subout=sdir
        flag_find_cyc="yes"
        for cyc in cycle:
            check_file="aqm."+cyc+".metcro2d.ncf"
            aqmfilein=comout2+"/"+sdir+"/"+check_file
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
            else:
                flag_find_cyc="no"
                break
        if flag_find_cyc == "yes":
            flag_find_sdir="yes"
            break
    if flag_find_sdir== "yes":
        slen=len(subout)
        subdir_marker2=subout[slen-3:slen]
        flag_find_idir="yes"
        break
if flag_find_idir == "yes":
    print("comout2 set to "+comout2)
else:
    sys.exit()

if envir2 != "prod" and envir2 != "para6x" and envir2 != "para6b":
    flag_ak = "no"
    flag_hi = "no"


if envir1 == envir2:
    print("Experiemnt "+envir1+" and Experiemnt "+envir2+" shoule be a different runs")
    sys.exit()

figout="/lfs/h2/emc/stmp/"+user

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
    iplot = [      0,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0 ]
else:
    iplot = [      1,      1,       1,      1,      1,      1,      1,      1,      0,      0,      1,      1,      0 ]
num_reg=len(iplot)
if flag_ak == "no" and iplot[num_reg-3] == 1:
    iplot[num_reg-3] = 0
if flag_hi == "no" and iplot[num_reg-2] == 1:
    iplot[num_reg-2] = 0
print("iplot length = "+str(num_reg))

date=sdate
while date <= edate:
    for cyc in cycle:
        msg=datetime.datetime.now()
        print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        s1_title=title_id+" "+date.strftime(YMD_date_format)+" "+cyc
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[1:3]))

        metfilein=metout1+"/cs."+grdcro2d_date+"/aqm."+cyc+".grdcro2d.ncf"
        if os.path.exists(metfilein):
            print(metfilein+" exists")
            model_data = netcdf.Dataset(metfilein)
            cs_lat = model_data.variables['LAT'][0,0,:,:]
            cs_lon = model_data.variables['LON'][0,0,:,:]
            model_data.close()
        else:
            print("Can not find "+metfilein)

        if subdir_marker1 == "met":
            aqmfilein=comout1+"/cs."+date.strftime(YMD_date_format)+"."+subdir_marker1+"/aqm."+cyc+".metcro2d.ncf"
        else:
            aqmfilein=comout1+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro2d.ncf"
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm1 = netcdf.Dataset(aqmfilein)
            cs_var = cs_aqm1.variables['TFLAG'][:,0,:]
            nstep=len(cs_var)  ## use 1st model as reference to constraint difference fcst hours bwtenn 48 and 729
        else:
            print("Can not find "+aqmfilein)
            sys.exit()
    
        if subdir_marker2 == "met":
            aqmfilein=comout2+"/cs."+date.strftime(YMD_date_format)+"."+subdir_marker2+"/aqm."+cyc+".metcro2d.ncf"
        else:
            aqmfilein=comout2+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro2d.ncf"
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm2 = netcdf.Dataset(aqmfilein)
            cs_var = cs_aqm2.variables['TFLAG'][:,0,:]
            nstep2=len(cs_var)
            if nstep2 != nstep:
                print("time step of "+envir2+" CONUS domain "+str(nstep2)+" is different from "+envir1+" CONUS domain "+str(nstep))
                ## sys.exit()  ## for difference bwtenn 48 and 72 fcst fours
        else:
            print("Can not find "+aqmfilein)
            sys.exit()

        if flag_ak == "yes":
            metfilein=metout1+"/ak."+grdcro2d_date+"/aqm."+cyc+".grdcro2d.ncf"
            if os.path.exists(metfilein):
                print(metfilein+" exists")
                model_data = netcdf.Dataset(metfilein)
                ak_lat = model_data.variables['LAT'][0,0,:,:]
                ak_lon = model_data.variables['LON'][0,0,:,:]
                model_data.close()
            else:
                print("Can not find "+metfilein)
                flag_ak = "no"
                iplot[num_reg-3] = 0
    
            if subdir_marker1 == "met":
                aqmfilein=comout1+"/ak."+date.strftime(YMD_date_format)+"."+subdir_marker1+"/aqm."+cyc+".metcro2d.ncf"
            else:
                aqmfilein=comout1+"/ak."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro2d.ncf"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                ak_aqm1 = netcdf.Dataset(aqmfilein)
                ak_var = ak_aqm1.variables['TFLAG'][:,0,:]
                nstep_ak=len(ak_var)
                if nstep_ak != nstep:
                    print("time step of AK domain "+str(nstep_ak)+" is different from CONUS domain "+str(nstep))
                    sys.exit()
            else:
                print("Can not find "+aqmfilein)
                flag_ak = "no"
                iplot[num_reg-3] = 0
        
            if subdir_marker2 == "met":
                aqmfilein=comout2+"/ak."+date.strftime(YMD_date_format)+"."+subdir_marker2+"/aqm."+cyc+".metcro2d.ncf"
            else:
                aqmfilein=comout2+"/ak."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro2d.ncf"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                ak_aqm2 = netcdf.Dataset(aqmfilein)
                ak_var = ak_aqm2.variables['TFLAG'][:,0,:]
                nstep_ak=len(ak_var)
                if nstep_ak != nstep:
                    print("time step of "+envir2+" AK domain "+str(nstep_ak)+" is different from CONUS domain "+str(nstep))
                    ## sys.exit()
            else:
                print("Can not find "+aqmfilein)
                flag_ak = "no"
                iplot[num_reg-3] = 0
    
        if flag_hi == "yes":
            metfilein=metout1+"/hi."+grdcro2d_date+"/aqm."+cyc+".grdcro2d.ncf"
            if os.path.exists(metfilein):
                print(metfilein+" exists")
                model_data = netcdf.Dataset(metfilein)
                hi_lat = model_data.variables['LAT'][0,0,:,:]
                hi_lon = model_data.variables['LON'][0,0,:,:]
                model_data.close()
            else:
                print("Can not find "+metfilein)
                flag_hi = "no"
                iplot[num_reg-2] = 0
    
            if subdir_marker1 == "met":
                aqmfilein=comout1+"/hi."+date.strftime(YMD_date_format)+"."+subdir_marker1+"/aqm."+cyc+".metcro2d.ncf"
            else:
                aqmfilein=comout1+"/hi."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro2d.ncf"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                hi_aqm1 = netcdf.Dataset(aqmfilein)
                hi_var = hi_aqm1.variables['TFLAG'][:,0,:]
                nstep_hi=len(hi_var)
                nstep_hi= nstep
                if nstep_hi != nstep:
                    print("time step of HI domain "+str(nstep_hi)+" is different from CONUS domain "+str(nstep))
                    sys.exit()
            else:
                print("Can not find "+aqmfilein)
                flag_hi = "no"
                iplot[num_reg-2] = 0
        
            if subdir_marker2 == "met":
                aqmfilein=comout2+"/hi."+date.strftime(YMD_date_format)+"."+subdir_marker2+"/aqm."+cyc+".metcro2d.ncf"
            else:
                aqmfilein=comout2+"/hi."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro2d.ncf"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                hi_aqm2 = netcdf.Dataset(aqmfilein)
                hi_var = hi_aqm2.variables['TFLAG'][:,0,:]
                nstep_hi=len(hi_var)
                if nstep_hi != nstep:
                    print("time step of "+envir2+" HI domain "+str(nstep_hi)+" is different from CONUS domain "+str(nstep))
                    ## sys.exit()
            else:
                print("Can not find "+aqmfilein)
                flag_hi = "no"
                iplot[num_reg-2] = 0
        for ivar in range(0,num_var):
            if var[ivar] == "cfracp":
                data_var1="cfrac"
                data_var2="cfrac"
            else:
                data_var1=var[ivar]
                data_var2=var2[ivar]
            plot_var=figid[ivar]
            read_var1=data_var1.upper()
            read_var2=data_var2.upper()
            msg=datetime.datetime.now()
            print("Start processing "+plot_var)
            figdir = figout+"/aqm"+"_"+envir1+"_"+date.strftime(YMD_date_format)+"_"+figid[ivar]+"_"+cyc+"_v5v6diff"
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("working on "+date.strftime(YMD_date_format)+" "+cyc+" "+plot_var)
            if plot_var == "pbl2":
                if envir1 == "prod":
                    s3_title="  \u0394[GFS PBL - CMAQ ACM2 PBL] height (M)"
                else:
                    s3_title="  \u0394[PBL height] (M)"
                scale=1.
                clevs = [ -4000., -3000., -2000., -1000., -500., -100., -1., 1., 100., 500., 1000., 2000., 3000., 4000. ]
                cbar_num_format = "%0.d"
            elif plot_var == "wspd":
                s3_title="  \u0394[Wind speed at 10 m] (m/s)"
                scale=1.
                clevs = [ -30., -25., -20., -15., -10., -5., -1.0, 1.0, 5., 10., 15., 20., 25., 30. ]
                cbar_num_format = "%0.d"
            elif plot_var == "rn":
                s3_title="  \u0394[Nonconvective Precipitation] (cm)"
                scale=1.
                clevs = [ -3., -2.5, -2., -1.5, -1.0, -0.5, -0.05, 0.05, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 ]
                cbar_num_format = "%0.2f"
            elif plot_var == "rc":
                s3_title="  \u0394[Convective Precipitation] (cm)"
                scale=1.
                clevs = [ -3., -2.5, -2., -1.5, -1.0, -0.5, -0.05, 0.05, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 ]
                cbar_num_format = "%0.2f"
            elif plot_var == "swrad":
                s3_title="  \u0394[Solar Rad reaching SFC] ($Watts/M^2$)"
                scale=1.
                clevs = [ -1000., -800., -600., -400., -200., -100., -1.0, 1.0, 100., 200., 400., 600., 800., 1000. ]
                cbar_num_format = "%0.d"
            elif plot_var == "cfrac":
                s3_title="  \u0394[Total Cloud Fraction] (unitless)"
                scale=1.
                clevs = [ -1.0, -0.8, -0.6, -0.4, -0.2, -0.1, -0.05, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0 ]
                cbar_num_format = "%0.2f"
            elif plot_var == "cldc":
                s3_title="  \u0394[Total Cloud Cover]  (%)"
                scale=100.
                clevs = [ -400., -80., -60., -40., -20., -10., -1.0, 1.0, 10., 20., 40., 60., 80., 400. ]
                cbar_num_format = "%0.d"
            elif plot_var == "snocov":
                s3_title="  \u0394[Snow Cover Fraction] (unitless)"
                scale=1.
                clevs = [ -1.0, -0.8, -0.6, -0.4, -0.2, -0.1, -0.05, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0 ]
                cbar_num_format = "%0.2f"
            elif plot_var == "veg":
                s3_title="  \u0394[Vegetation Coverage] (unitless)"
                scale=1.
                clevs = [ -1.0, -0.8, -0.6, -0.4, -0.2, -0.1, -0.05, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0 ]
                cbar_num_format = "%0.2f"
            elif plot_var == "lai":
                s3_title="  \u0394[Leaf-Area Index] ($m^2/m^2$)"
                scale=1.
                clevs = [ -6.0, -5.0, -4.0, -3.0, -2.0, -1.0, -0.05, 0.05, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0 ]
                cbar_num_format = "%0.2f"
            else:
                s3_title=plot_var.upper()+" undefined"
                print(s3_title)
                continue
            var_cs1 = cs_aqm1.variables[read_var1][:,0,:,:]*scale
            var_cs2 = cs_aqm2.variables[read_var2][:,0,:,:]*scale
            if flag_ak == "yes":
                var_ak1 = ak_aqm1.variables[read_var1][:,0,:,:]*scale
                var_ak2 = ak_aqm2.variables[read_var2][:,0,:,:]*scale
            if flag_hi == "yes":
                var_hi1 = hi_aqm1.variables[read_var1][:,0,:,:]*scale
                var_hi2 = hi_aqm2.variables[read_var2][:,0,:,:]*scale
            ## cmap = plt.get_cmap('coolwarm')
            cmap = mpl.colors.ListedColormap([
                   (0.0000,0.0000,0.7843), (0.0000,0.0000,1.0000), (0.3137,0.3137,1.0000), (0.4706,0.4706,1.0000),
                   (0.5882,0.5882,1.0000), (0.8627,0.8627,1.0000), (1.0000,1.0000,1.0000), (1.0000,0.8627,0.8627),
                   (1.0000,0.5882,0.5882), (1.0000,0.4706,0.4706), (0.9804,0.3137,0.3137), (0.9804,0.2353,0.2353),
                   (0.7843,0.0000,0.0000)
                   ])
            cmap.set_over((0.5882,0.0000,0.0000))
            cmap.set_under((0.0000,0.0000,0.5882))
            norm = mpl.colors.BoundaryNorm(boundaries=clevs, ncolors=cmap.N)
            gs = gridspec.GridSpec(1,1)
            fcst_hour=fcst_ini-hour_inc
            for n in range(0,nstep):
            ## for n in range(15,16):
                nout=n
                fcst_hour=fcst_hour+hour_inc
                if nstep > 99:
                    s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+str(format(nout,'03d'))
                else:
                    s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+str(format(nout,'02d'))
                title=s1_title+"\n"+s2_title+" "+s3_title
                val1 = var_cs1[n,:,:]
                val2 = var_cs2[n,:,:]
                diff = []
                for x, y in zip(val2, val1):
                    diff.append(x-y)
                pvar_cs= diff 
                if flag_ak == "yes":
                    val1 = var_ak1[n,:,:]
                    val2 = var_ak2[n,:,:]
                    diff = []
                    for x, y in zip(val2, val1):
                        diff.append(x-y)
                    pvar_ak= diff
                if flag_hi == "yes":
                    val1 = var_hi1[n,:,:]
                    val2 = var_hi2[n,:,:]
                    diff = []
                    for x, y in zip(val2, val1):
                        diff.append(x-y)
                    pvar_hi= diff
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
                        if figarea == "ak" and flag_ak == "yes":
                            try:
                               cf1 = ax.contourf(
                                     ak_lon, ak_lat, pvar_ak,
                                     levels=clevs, cmap=cmap, norm=norm, extend='both',
                                     transform=ccrs.PlateCarree() )
                            except ValueError:
                                continue
                        elif figarea == "hi" and flag_hi == "yes":
                            try:
                               cf1 = ax.contourf(
                                     hi_lon, hi_lat, pvar_hi,
                                     levels=clevs, cmap=cmap, norm=norm, extend='both',
                                     transform=ccrs.PlateCarree() )
                            except ValueError:
                                continue
                        else:
                            try:
                               cf1 = ax.contourf(
                                     cs_lon, cs_lat, pvar_cs,
                                     levels=clevs, cmap=cmap, norm=norm, extend='both',
                                     transform=ccrs.PlateCarree() )
                            except ValueError:
                                continue
                            if figarea == "dset":
                                if flag_ak == "yes":
                                    try:
                                       ax.contourf(
                                         ak_lon, ak_lat, pvar_ak,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                                    except ValueError:
                                        continue
                                if flag_hi == "yes":
                                    try:
                                       ax.contourf(
                                         hi_lon, hi_lat, pvar_hi,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                                    except ValueError:
                                        continue
                        ax.set_title(title)
                        ## cb2.set_label('Discrete intervals, some other units')
                        ## fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,shrink=0.8,format=cbar_num_format)
                        fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,format=cbar_num_format)
                        savefig_name = figdir+"/aqm."+figarea+"."+fig_id+"."+date.strftime(YMD_date_format)+"."+cyc+"."+str(format(nout,'02d'))+"."+figid[ivar]+".k1.png"
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
            print("End   processing "+plot_var)
        cs_aqm1.close()
        cs_aqm2.close()
        if flag_ak == "yes":
            ak_aqm1.close()
            ak_aqm2.close()
        if flag_hi == "yes":
            hi_aqm1.close()
            hi_aqm2.close()
        msg=datetime.datetime.now()
        print("End   processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc
