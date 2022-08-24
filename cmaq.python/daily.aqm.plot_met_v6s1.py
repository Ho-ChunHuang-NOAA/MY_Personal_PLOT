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

script_dir=os.getcwd()
print("Script directory is "+script_dir)

user=os.environ['USER']

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
YMDH_date_format = "%Y%m%d/%H"
YMD_date_format = "%Y%m%d"
YM_date_format = "%Y%m"
Y_date_format = "%Y"
M_date_format = "%m"
D_date_format = "%d"
H_date_format = "%H"
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

## var=[ "pbl", "wspd10", "rn" ] 
## figid=[ "pbl2", "wspd", "rn" ]

var=[ "pbl" ]
figid=[ "pbl2" ]
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
cbar_num_format = "%.d"
plt.close('all') # close all figures

msg=datetime.datetime.now()
msg=msg - date_inc
grdcro2d_date=msg.strftime("%Y%m%d")
##
## Current operational CMAQ does include runs for AK and HI domain
## Current EMC development CMAQ does not include runs for AK and HI domain
##
aqm_ver="v6.1"
find_dir=[
          "/lfs/h1/ops/"+envir+"/com/aqm/"+aqm_ver,
          "/lfs/h2/emc/ptmp/"+user+"/com/aqm/"+envir,
          "/lfs/h2/emc/physics/noscrub/"+user+"/com/aqm/"+envir
         ]
metout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver

figout=stmp_dir

flag_proj="LambertConf"
##mksize= [     16,     25,      36,      36,     49,     49,     49,     49,     64,     64,    121,    100,    121,     36 ]
mksize= [     16,      16,      25,     25,     36,     36,     36,     36,     49,     49,    121,    100,    121,     36 ]
if flag_proj == "LambertConf":
    regname = [   "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
    rlon0 = [ -161.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0,  -75.0, -166.0, -161.5, -141.0 ]
    rlon1 = [  -73.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0,  -71.0, -132.0, -153.1, -60.0 ]
    rlat0 = [   14.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   40.2,   53.2,   17.8,   38.0 ]
    rlat1 = [   72.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   41.8,   71.2,   23.1,   70.0 ]
else:
    regname = [   "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
    rlon0 = [ -175.0, -124.0,  -100.0, -128.0,  -82.0, -125.0,  -95.0, -125.0, -105.0, -105.0,  -75.0, -170.0, -161.0, -141.0 ]
    rlon1 = [  -55.0,  -70.0,   -65.0,  -90.0,  -67.0, -103.0,  -79.0, -105.0,  -85.0,  -85.0,   -71.0, -130.0, -154.0,  -60.0 ]
    rlat0 = [    0.0,   22.0,    22.0,   24.5,   37.0,   38.0,   24.0,   30.0,   38.0,   24.0,   40.2,   52.0,   18.0,   38.0 ]
    rlat1 = [   70.0,   51.0,    50.0,   54.5,   48.0,   52.0,   38.0,   45.0,   52.0,   40.0,   41.8,   72.0,   23.0,   70.0 ]
xsize = [     10,     10,       8,      8,      8,      8,      8,      8,      8,      8,     10,      8,      8,     10 ]
ysize = [      8,      8,       8,      8,      8,      8,      8,      8,      8,      8,      5,      8,      8,     8 ]
if 1 == 2:
    iplot = [      1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1, 1 ]
else:
    iplot = [      0,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0, 0 ]
num_reg=len(iplot)


date=sdate
while date <= edate:
    sub_met_dir=[
                "cs."+date.strftime(YMD_date_format),
                "cs."+date.strftime(YMD_date_format)+".met"
                ]
    flag_find_idir="no"
    for idir in find_dir:
        comout=idir
        print("check "+idir)
        flag_find_sdir="no"
        for sdir in sub_met_dir:
            subout=sdir
            flag_find_cyc="yes"
            for cyc in cycle:
                check_file="aqm."+cyc+".metcro2d.ncf"
                aqmfilein=comout+"/"+sdir+"/"+check_file
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
            subdir_marker=subout[slen-3:slen]
            flag_find_idir="yes"
            break
    if flag_find_idir == "yes":
        print("comout set to "+comout)
    else:
        date = date + date_inc
        continue
    
    if envir == "prod" or envir == "para6x" or envir == "para6b":
        flag_ak = "yes"
        for cyc in cycle:
            check_file="aqm."+cyc+".metcro2d.ncf"
            aqmfilein=comout+"/ak."+date.strftime(YMD_date_format)+"/"+check_file
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
            else:
                flag_ak="no"
                print("Can not find "+aqmfilein)
                break
        flag_hi = "yes"
        for cyc in cycle:
            check_file="aqm."+cyc+".metcro2d.ncf"
            aqmfilein=comout+"/hi."+date.strftime(YMD_date_format)+"/"+check_file
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
            else:
                flag_hi="no"
                print("Can not find "+aqmfilein)
                break
    else:
        flag_ak = "no"
        flag_hi = "no"

    if flag_ak == "no" and iplot[num_reg-3] == 1:
        iplot[num_reg-3] = 0
    if flag_hi == "no" and iplot[num_reg-2] == 1:
        iplot[num_reg-2] = 0
    print("iplot length = "+str(num_reg))

    for cyc in cycle:
        msg=datetime.datetime.now()
        print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        s1_title=fig_exp.upper()+" "+date.strftime(YMD_date_format)+" "+cyc
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

        if subdir_marker == "met":
            aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"."+subdir_marker+"/aqm."+cyc+".metcro2d.ncf"
        else:
            aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro2d.ncf"
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm = netcdf.Dataset(aqmfilein)
            cs_var = cs_aqm.variables['TFLAG'][:,0,:]
            nstep=len(cs_var)
        else:
            print("Can not find "+aqmfilein)

        if flag_ak == "yes":
            metfilein=metout+"/ak."+grdcro2d_date+"/aqm."+cyc+".grdcro2d.ncf"
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

            if subdir_marker == "met":
                aqmfilein=comout+"/ak."+date.strftime(YMD_date_format)+"."+subdir_marker+"/aqm."+cyc+".metcro2d.ncf"
            else:
                aqmfilein=comout+"/ak."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro2d.ncf"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                ak_aqm = netcdf.Dataset(aqmfilein)
                ak_var = ak_aqm.variables['TFLAG'][:,0,:]
                nstep_ak=len(ak_var)
                if nstep_ak != nstep:
                    print("time step of AK domain "+str(nstep_ak)+" is different from CONUS domain "+str(nstep))
                    sys.exit()
            else:
                print("Can not find "+aqmfilein)
                flag_ak = "no"
                iplot[num_reg-3] = 0
    
        if flag_hi == "yes":
            metfilein=metout+"/hi."+grdcro2d_date+"/aqm."+cyc+".grdcro2d.ncf"
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
    
            if subdir_marker == "met":
                aqmfilein=comout+"/hi."+date.strftime(YMD_date_format)+"."+subdir_marker+"/aqm."+cyc+".metcro2d.ncf"
            else:
                aqmfilein=comout+"/hi."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro2d.ncf"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                hi_aqm = netcdf.Dataset(aqmfilein)
                hi_var = hi_aqm.variables['TFLAG'][:,0,:]
                nstep_hi=len(hi_var)
                nstep_hi= nstep
                if nstep_hi != nstep:
                    print("time step of HI domain "+str(nstep_hi)+" is different from CONUS domain "+str(nstep))
                    sys.exit()
            else:
                print("Can not find "+aqmfilein)
                flag_hi = "no"
                iplot[num_reg-2] = 0
        for ivar in range(0,num_var):
            if var[ivar] == "cfracp":
                data_var="cfrac"
            else:
                data_var=var[ivar]
            plot_var=figid[ivar]
            msg=datetime.datetime.now()
            print("Start processing "+plot_var)
            figdir = figout+"/aqm"+"_"+envir+"_"+date.strftime(YMD_date_format)+"_"+plot_var+"_"+cyc+"_metv6"
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("working on "+date.strftime(YMD_date_format)+" "+cyc+" "+plot_var)
            read_var=data_var.upper()
            var_cs = cs_aqm.variables[read_var][:,0,:,:]
            if flag_ak == "yes":
                var_ak = ak_aqm.variables[read_var][:,0,:,:]
            if flag_hi == "yes":
                var_hi = hi_aqm.variables[read_var][:,0,:,:]

            ##    s3_title=plot_var.upper()+" sfc_conc ($\u03bcg/m^3$)"
            ##  var=[ "pbl", "rn", "rc", "rgrnd", "cfrac", "cfracp", "snocov", "veg", "lai" ]
            if plot_var == "pbl2":
                s3_title="GFS PBL height (M)"
                scale=1.
                clevs = [ 250., 500., 1000., 1500., 2000., 2500., 3000., 3500., 4000., 4500. ]
                cbar_num_format = "%.d"
##                      (0.9020,0.8627,0.1961), (0.9412,0.5098,0.1569), (0.9804,0.2353,0.2353),
## (1.0000,0.5490,0.0000), 
                cmap = mpl.colors.ListedColormap([
                       (0.0000,0.8000,0.8000), (0.4314,0.4314,1.0000), (0.0000,0.5020,0.0000), (0.0000,0.8627,0.0000),
                       (1.0000,1.0000,0.0000), (1.0000,0.6500,0.0000), (0.9412,0.5098,0.1569), (0.9804,0.2353,0.2353),
                       (0.8627,0.0784,0.2353)
                      ])
                cmap.set_over('magenta')
                var_cs=var_cs*scale
                if flag_ak == "yes":
                    var_ak=var_ak*scale
                if flag_hi == "yes":
                    var_hi=var_hi*scale
            elif plot_var == "wspd":
                s3_title="Wind speed at 10 m (m/s)"
                scale=1.
                clevs = [ 1, 2, 4, 6, 8, 10, 12, 15, 18, 20, 25, 30 ]
                cbar_num_format = "%.1f"
                cmap = mpl.colors.ListedColormap([
                      (0.8627,0.8627,1.0000), (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000),
                      (0.2157,0.2157,1.0000), (0.0000,0.7843,0.7843), (0.0000,0.8627,0.0000), (0.6275,0.9020,0.1961),
                      (0.9020,0.8627,0.1961), (0.9020,0.6863,0.1765), (0.9412,0.5098,0.1569), (0.9804,0.2353,0.2353)
                      ])
                cmap.set_over('magenta')
                var_cs=var_cs*scale
                if flag_ak == "yes":
                    var_ak=var_ak*scale
                if flag_hi == "yes":
                    var_hi=var_hi*scale
            elif plot_var == "rn":
                s3_title="Nonconvective Precipitation (cm)"
                scale=1.
                clevs = [ 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0 ]
                cbar_num_format = "%.1f"
                cmap = mpl.colors.ListedColormap([
                      (0.8627,0.8627,1.0000), (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000),
                      (0.2157,0.2157,1.0000), (0.0000,0.7843,0.7843), (0.0000,0.8627,0.0000), (0.6275,0.9020,0.1961),
                      (0.9020,0.8627,0.1961), (0.9020,0.6863,0.1765), (0.9412,0.5098,0.1569), (0.9804,0.2353,0.2353)
                      ])
                cmap.set_over('magenta')
                var_cs=var_cs*scale
                if flag_ak == "yes":
                    var_ak=var_ak*scale
                if flag_hi == "yes":
                    var_hi=var_hi*scale
            elif plot_var == "rc":
                s3_title="Convective Precipitation (cm)"
                scale=1.
                clevs = [ 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0 ]
                cbar_num_format = "%.2f"
                cmap = mpl.colors.ListedColormap([
                      (0.8627,0.8627,1.0000), (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000),
                      (0.2157,0.2157,1.0000), (0.0000,0.7843,0.7843), (0.0000,0.8627,0.0000), (0.6275,0.9020,0.1961),
                      (0.9020,0.8627,0.1961), (0.9020,0.6863,0.1765), (0.9412,0.5098,0.1569), (0.9804,0.2353,0.2353)
                      ])
                cmap.set_over('magenta')
                var_cs=var_cs*scale
                if flag_ak == "yes":
                    var_ak=var_ak*scale
                if flag_hi == "yes":
                    var_hi=var_hi*scale
            elif plot_var == "swrad":
                s3_title="Solar Rad reaching SFC ($Watts/M^2$)"
                scale=1.
                clevs = [ 150., 300., 450., 600., 750., 900., 1050., 1200. ]
                cbar_num_format = "%.d"
                cmap = mpl.colors.ListedColormap([
                      (0.9020,0.9020,0.0000), (1.0000,1.0000,0.0000), (1.0000,0.8431,0.0000), (1.0000,0.5490,0.0000),
                      (0.9804,0.2353,0.2353), (0.8627,0.0784,0.2353), (0.5451,0.0000,0.0000)
                      ])
                cmap.set_over('magenta')
                var_cs=var_cs*scale
                if flag_ak == "yes":
                    var_ak=var_ak*scale
                if flag_hi == "yes":
                    var_hi=var_hi*scale
            elif plot_var == "cfrac":
                s3_title="Total Cloud Fraction (unitless)"
                scale=1.
                clevs = [ 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9 ]
                cbar_num_format = "%.1f"
                cmap = mpl.colors.ListedColormap([
                      (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000), (0.0000,0.7843,0.7843),
                      (0.9020,0.9020,0.0000), (0.9020,0.6863,0.1765), (0.5569,0.9882,0.0000), (0.1961,0.8039,0.1961),
                      (0.0000,0.5000,0.0000)
                      ])
                cmap.set_over((0.0000,0.3000,0.0000))
                var_cs=var_cs*scale
                if flag_ak == "yes":
                    var_ak=var_ak*scale
                if flag_hi == "yes":
                    var_hi=var_hi*scale
            elif plot_var == "cldc":
                s3_title="Total Cloud Cover  (%)"
                scale=100.
                clevs = [ 15., 30., 45., 60., 75., 90. ]
                cbar_num_format = "%.d"
                ##       (1.0000,0.5490,0.0000),
                cmap = mpl.colors.ListedColormap([
                      (0.8039,0.5216,0.2471), (1.0000,0.7000,0.0000), (1.0000,1.0000,0.0000),
                      (0.5569,0.9882,0.0000), (0.0000,0.8039,0.0000), (0.0000,0.5020,0.0000)
                      ])
                cmap.set_over((0.0000,0.2500,0.0000))
                var_cs=var_cs*scale
                if flag_ak == "yes":
                    var_ak=var_ak*scale
                if flag_hi == "yes":
                    var_hi=var_hi*scale
            elif plot_var == "snocov":
                s3_title="Snow Cover Fraction (unitless)"
                scale=1.
                clevs = [ 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9 ]
                cbar_num_format = "%.1f"
                cmap = mpl.colors.ListedColormap([
                      (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000),
                      (0.0000,0.7843,0.7843), (0.0000,0.8627,0.0000), (0.6275,0.9020,0.1961),
                      (0.9020,0.8627,0.1961), (0.9412,0.5098,0.1569), (0.9804,0.2353,0.2353),
                      ])
                cmap.set_over('magenta')
                var_cs=var_cs*scale
                if flag_ak == "yes":
                    var_ak=var_ak*scale
                if flag_hi == "yes":
                    var_hi=var_hi*scale
            elif plot_var == "veg":
                s3_title="Vegetation Coverage (unitless)"
                scale=1.
                clevs = [ 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9 ]
                cbar_num_format = "%.1f"
                cmap = mpl.colors.ListedColormap([
                      (0.6000,1.0000,0.6000), (0.4000,1.0000,0.4000), (0.2000,1.0000,0.2000), (0.0000,1.0000,0.0000),
                      (0.0000,0.8000,0.0000), (0.0000,0.6000,0.0000), (0.0000,0.4000,0.0000), (0.0000,0.2000,0.0000)
                      ])
                cmap.set_over((0.0000,0.0500,0.0000))
                var_cs=var_cs*scale
                if flag_ak == "yes":
                    var_ak=var_ak*scale
                if flag_hi == "yes":
                    var_hi=var_hi*scale
            elif plot_var == "lai":
                s3_title="Leaf-Area Index ($m^2/m^2$)"
                scale=1.
                clevs = [ 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.5, 6.0 ]
                cbar_num_format = "%.1f"
                cmap = mpl.colors.ListedColormap([
                      (0.6000,1.0000,0.6000), (0.4000,1.0000,0.4000), (0.2000,1.0000,0.2000), (0.0000,1.0000,0.0000),
                      (0.0000,0.8000,0.0000), (0.0000,0.7000,0.0000), (0.0000,0.6000,0.0000), (0.0000,0.5000,0.0000),
                      (0.0000,0.4000,0.0000), (0.0000,0.3000,0.0000)
                      ])
                cmap.set_over((0.0000,0.1000,0.0000))
                var_cs=var_cs*scale
                if flag_ak == "yes":
                    var_ak=var_ak*scale
                if flag_hi == "yes":
                    var_hi=var_hi*scale
            else:
                s3_title=plot_var.upper()+" undefined"
                print(s3_title)
                continue
            cmap.set_under('whitesmoke')
            norm = mpl.colors.BoundaryNorm(boundaries=clevs, ncolors=cmap.N)
            gs = gridspec.GridSpec(1,1)
            fcst_hour=fcst_ini-hour_inc
            ## for n in range(nstep-1,nstep):
            for n in range(0,nstep):
                nout=n
                fcst_hour=fcst_hour+hour_inc
                if nstep > 99:
                    s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+str(format(nout,'03d'))
                else:
                    s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+str(format(nout,'02d'))
                title=s1_title+"\n"+s2_title+" "+s3_title
                pvar_cs = var_cs[n,:,:]
                if flag_ak == "yes":
                    pvar_ak = var_ak[n,:,:]
                if flag_hi == "yes":
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
                        savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"."+date.strftime(YMD_date_format)+"."+cyc+"."+str(format(nout,'02d'))+"."+figid[ivar]+".k1.png"
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
            print("FIG DIR = "+figdir)
        cs_aqm.close()
        if flag_ak == "yes":
            ak_aqm.close()
        if flag_hi == "yes":
            hi_aqm.close()
        msg=datetime.datetime.now()
        print("End   processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc
                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
