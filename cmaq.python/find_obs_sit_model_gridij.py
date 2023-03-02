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
if aqm_ver="":
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
YMDH_date_format = "%Y%m%d/%H"
YMD_date_format = "%Y%m%d"
YM_date_format = "%Y%m"
Y_date_format = "%Y"
M_date_format = "%m"
D_date_format = "%d"
H_date_format = "%H"
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

var=["no2"]
## var.append[sel_var]
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

msg=datetime.datetime.now()
msg=msg - date_inc
grddot2d_date=msg.strftime("%Y%m%d")
##
## Current operational CMAQ does include runs for AK and HI domain
## Current EMC development CMAQ does not include runs for AK and HI domain
##
find_dir=[
          "/lfs/h1/ops/"+envir+"/com/aqm/"+aqm_ver,
          "/lfs/h2/emc/ptmp/"+user+"/com/aqm/"+envir,
          "/lfs/h2/emc/physics/noscrub/"+user+"/com/aqm/"+envir
         ]
metout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver

figout=stmp_dir

obs_site_name="Westport, CT"
obs_site_id="090019003"
obs_site_lat=41.1189
obs_site_lon=-73.336900
date=sdate
while date <= edate:
    flag_find_idir="no"
    for idir in find_dir:
        comout=idir
        print("check "+idir)
        flag_find_cyc="yes"
        for cyc in cycle:
            check_file="aqm."+cyc+".aconc_sfc.ncf"
            aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/"+check_file
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
            else:
                flag_find_cyc="no"
                print("Can not find "+aqmfilein)
                break
        if flag_find_cyc == "yes":
            flag_find_idir="yes"
            break
    if flag_find_idir == "yes":
        print("comout set to "+comout)
    else:
        date = date + date_inc
        continue
    

    for cyc in cycle:
        msg=datetime.datetime.now()
        print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        s1_title="CMAQ "+fig_exp.upper()+" "+date.strftime(YMD_date_format)+" "+cyc
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[1:3]))

        metfilein=metout+"/cs."+grddot2d_date+"/aqm."+cyc+".grdcro2d.ncf"
        if os.path.exists(metfilein):
            print(metfilein+" exists")
            model_data = netcdf.Dataset(metfilein)
            cro_lat = model_data.variables['LAT'][0,0,:,:]
            cro_lon = model_data.variables['LON'][0,0,:,:]
            jmax=cro_lat.shape[0]
            imax=cro_lat.shape[1]
            print('"Dimension 0 is %d"' % (jmax))
            print('"Dimension 1 is %d"' % (imax))
            model_data.close()
        else:
            print("Can not find "+metfilein)
            sys,exit()

        metfilein=metout+"/cs."+grddot2d_date+"/aqm."+cyc+".grddot2d.ncf"
        if os.path.exists(metfilein):
            print(metfilein+" exists")
            model_data = netcdf.Dataset(metfilein)
            dot_lat = model_data.variables['LATD'][0,0,:,:]
            dot_lon = model_data.variables['LOND'][0,0,:,:]
            jmax=dot_lat.shape[0]
            imax=dot_lat.shape[1]
            print('"Dimension 0 is %d"' % (jmax))
            print('"Dimension 1 is %d"' % (imax))
            model_data.close()
        else:
            print("Can not find "+metfilein)
            sys,exit()

        for j in range(0,jmax-1):
            flag_ij="no"
            for i in range(0,imax-1):
                if obs_site_lon >= dot_lon[j][i] and obs_site_lon < dot_lon[j][i+1] and obs_site_lon >= dot_lon[j+1][i] and obs_site_lon < dot_lon[j+1][i+1] and obs_site_lat >= dot_lat[j][i] and obs_site_lat >= dot_lat[j][i+1] and obs_site_lat < dot_lat[j+1][i] and obs_site_lat < dot_lat[j+1][i+1]:
                    mdl_i=i
                    mdl_j=j
                    flag_ij="yes"
                    break
            if flag_ij == "yes":
                break
        print( "obs lon = "+str(obs_site_lon))
        print( "obs lat = "+str(obs_site_lat))
        print( "model i = "+str(mdl_i)+" and model j = "+str(mdl_j))
        print( "lat UL = "+str(dot_lat[mdl_j+1][mdl_i])+" and lat UR = "+str(dot_lat[mdl_j+1][mdl_i+1]))
        print( "lat LL = "+str(dot_lat[mdl_j][mdl_i])+" and lat LR = "+str(dot_lat[mdl_j][mdl_i+1]))
        print( "lon UL = "+str(dot_lon[mdl_j+1][mdl_i])+" and lon UR = "+str(dot_lon[mdl_j+1][mdl_i+1]))
        print( "lon LL = "+str(dot_lon[mdl_j][mdl_i])+" and lon LR = "+str(dot_lon[mdl_j][mdl_i+1]))
        print( "mdl lon = "+str(cro_lon[mdl_j][mdl_i]))
        print( "mdl lat = "+str(cro_lat[mdl_j][mdl_i]))

        aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".aconc_sfc.ncf"
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm = netcdf.Dataset(aqmfilein)
            cs_var = cs_aqm.variables['TFLAG'][:,0,:]
            nstep=len(cs_var)
            for ivar in range(0,num_var):
                if var[ivar] == "o3":
                    o3_cs = cs_aqm.variables['O3'][:,0,:,:]
                if var[ivar] == "pm25":
                    pm_cs = cs_aqm.variables['PM25_TOT'][:,0,:,:]
                if var[ivar] == "no2":
                    no2_cs = cs_aqm.variables['NO2'][:,0,:,:]
            cs_aqm.close()
            tmax=no2_cs.shape[0]
            jmax=no2_cs.shape[1]
            imax=no2_cs.shape[2]
            print('"Dimension 0 is %d"' % (tmax))
            print('"Dimension 1 is %d"' % (jmax))
            print('"Dimension 2 is %d"' % (imax))
            max_no2=np.amax(no2_cs)
            min_no2=np.amin(no2_cs)
            print('"MAX of NO2 is  %f"' % (max_no2))
            print('"MIN of NO2 is  %f"' % (min_no2))
            result = np.where(no2_cs == np.amax(no2_cs))
            nidx=result[0]   # is an array
            jidx=result[1]   # is an array
            iidx=result[2]   # is an array
            print(nidx[0])   # only one will be found, can be more than if not unique
            print(jidx[0])   # only one will be found, can be more than if not unique
            print(iidx[0])   # only one will be found, can be more than if not unique
            mld_max_no2=no2_cs[0,0,0]   # to double check the number from result[*] number
            mld_max_no2=no2_cs[61,169,369]   # to double check the number from result[*] number
            print('"CONC of NO2 is            %f"' % (no2_cs[nidx[0],jidx[0],iidx[0]]))
            print('"Asssigned CONC of NO2 is  %f"' % (no2_cs[61,169,369]))
            for n in range(0,tmax):
                print("===================")
                no2_2d=no2_cs[n,:,:]
                print("n = "+str(n)+"  no2 = "+str(no2_2d[mdl_j,mdl_i]))
                max_no2_2d=np.amax(no2_2d)
                min_no2_2d=np.amin(no2_2d)
                print('"MAX of NO2 is  %f"' % (max_no2_2d))
                print('"MIN of NO2 is  %f"' % (min_no2_2d))
                result = np.where(no2_2d == np.amax(no2_2d))
                jidx=result[0]   # is an array
                iidx=result[1]   # is an array
                print(jidx[0])   # only one will be found, can be more than if not unique
                print(iidx[0])   # only one will be found, can be more than if not unique
                if n == 61:
                    mld_max_no2_2d=no2_2d[169,369]
                    print('"CONC of NO2 is           %f"' % (no2_2d[jidx[0],iidx[0]]))
                    print('"Assigned CONC of NO2 is  %f"' % mld_max_no2_2d)
                print('"MAX CONC of NO2 at time step %d is  %f"' % (n,no2_2d[jidx[0],iidx[0]]))

        else:
            print("Can not find "+aqmfilein)
            sys.exit()
    date = date + date_inc
