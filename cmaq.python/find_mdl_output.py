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

script_dir=os.getcwd()
print("Script directory is "+script_dir)

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

### PASSED AGRUEMENTS
if len(sys.argv) < 4:
    print("you must set 4 arguments as model[prod|para|...] cycle[06|12]  start_date end_date")
    sys.exit()
else:
    envir = sys.argv[1]
    sel_cyc = sys.argv[2]
    start_date = sys.argv[3]
    end_date = sys.argv[4]

if envir.lower() == "para":
    fig_exp="ncopara"+BC_fig_append
else:
    fig_exp=envir.lower()

stmp_dir="/lfs/h2/emc/stmp/"+user
if not os.path.exists(stmp_dir):
    os.mkdir(stmp_dir)

ptmp_dir="/lfs/h2/emc/ptmp/"+user
if not os.path.exists(ptmp_dir):
    os.mkdir(ptmp_dir)

log_dir=ptmp_dir+"/batch_logs"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

working_dir=ptmp_dir+"/aqm_plot_working"
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

working_dir=stmp_dir+"/aqm_plot_working"
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

os.chdir(working_dir)

msg_file=working_dir+"/msg_read"
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

        metfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro2d.ncf"
        if os.path.exists(metfilein):
            print(metfilein+" exists")
            cs_aqm = netcdf.Dataset(metfilein)
            cs_var = cs_aqm.variables['TFLAG'][:,0,:]
            nstep=len(cs_var)
            pbl_cs= cs_aqm.variables['PBL'][:,0,:,:]
            temp2_cs= cs_aqm.variables['TEMP2'][:,0,:,:]
            q2_cs= cs_aqm.variables['Q2'][:,0,:,:]
            cfrac_cs= cs_aqm.variables['CFRAC'][:,0,:,:]
            wspd10_cs= cs_aqm.variables['WSPD10'][:,0,:,:]
            wdir10_cs = cs_aqm.variables['WDIR10'][:,0,:,:]
            cs_aqm.close()
        aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".aconc_sfc.ncf"
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm = netcdf.Dataset(aqmfilein)
            cs_var = cs_aqm.variables['TFLAG'][:,0,:]
            nstep=len(cs_var)
            o3_cs = cs_aqm.variables['O3'][:,0,:,:]
            no_cs = cs_aqm.variables['NO'][:,0,:,:]
            no2_cs = cs_aqm.variables['NO2'][:,0,:,:]
            cs_aqm.close()
        outfile1=os.path.join(os.getcwd(),"Westport."+date.strftime(YMD_date_format)+"."+cyc+".all.txt")
        if os.path.exists(outfile1):
            os.remove(outfile1)
        with open(outfile1, 'a') as sh:
            sh.write("fcst_hour,o3(ppb),no2(ppb),wspd10(m/s),wdir10(degree)\n")
        outfile2=os.path.join(os.getcwd(),"Westport."+date.strftime(YMD_date_format)+"."+cyc+".txt")
        if os.path.exists(outfile2):
            os.remove(outfile2)
        with open(outfile1, 'a') as sh:
            sh.write("fcst_hour,o3(ppb),no2(ppb),wspd10(m/s),wdir10(degree),no(ppb),pbl(m),temp2(K),q2(kg/kg),cloud_fraction(unitless)\n")
            for n in range(0,nstep):
                nidx=str(n+1)
                ic=nidx.zfill(2)
                pbl_2d=pbl_cs[n,mdl_j,mdl_i]
                temp2_2d=temp2_cs[n,mdl_j,mdl_i]
                q2_2d=q2_cs[n,mdl_j,mdl_i]
                cfrac_2d=cfrac_cs[n,mdl_j,mdl_i]
                wspd10_2d=wspd10_cs[n,mdl_j,mdl_i]
                wdir10_2d=wdir10_cs[n,mdl_j,mdl_i]
                o3_2d=o3_cs[n,mdl_j,mdl_i]*1000.
                no_2d=no_cs[n,mdl_j,mdl_i]*1000.
                no2_2d=no2_cs[n,mdl_j,mdl_i]*1000.
                sh.write(ic+","+str(o3_2d)+","+str(no2_2d)+","+str(wspd10_2d)+","+str(wdir10_2d)+","+str(no_2d)+","+str(pbl_2d)+","+str(temp2_2d)+","+str(q2_2d)+","+str(cfrac_2d)+"\n")
            sh.close()
        with open(outfile2, 'a') as sh:
            sh.write("fcst_hour,o3(ppb),no2(ppb),wspd10(m/s),wdir10(degree)\n")
            for n in range(0,nstep):
                nidx=str(n+1)
                ic=nidx.zfill(2)
                pbl_2d=pbl_cs[n,mdl_j,mdl_i]
                temp2_2d=temp2_cs[n,mdl_j,mdl_i]
                q2_2d=q2_cs[n,mdl_j,mdl_i]
                cfrac_2d=cfrac_cs[n,mdl_j,mdl_i]
                wspd10_2d=wspd10_cs[n,mdl_j,mdl_i]
                wdir10_2d=wdir10_cs[n,mdl_j,mdl_i]
                o3_2d=o3_cs[n,mdl_j,mdl_i]*1000.
                no_2d=no_cs[n,mdl_j,mdl_i]*1000.
                no2_2d=no2_cs[n,mdl_j,mdl_i]*1000.
                sh.write(ic+","+str(o3_2d)+","+str(no2_2d)+","+str(wspd10_2d)+","+str(wdir10_2d)+"\n")
            sh.close()
    date = date + date_inc
