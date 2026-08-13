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
    aqm_ver="v7.0"
print("aqm_ver="+aqm_ver)

wgrib2=os.environ['WGRIB2']
if wgrib2 == "":
    print("No definition of WGRIB2 can be found, please load module wgrib2/2.0.8")
    sys.exit()

### PASSED AGRUEMENTS
if len(sys.argv) < 3:
    print("you must set 3 arguments as cycle[06|12|all]  start_date end_date")
    sys.exit()
else:
    sel_cyc = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

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
if py_code.startswith("dev_plot_aot_aqmv7_"):
    fig_sec_id = py_code.split("_")[-1].split(".")[0]
else:
    fig_sec_id = np
print(f" Test fig dir location id = {fig_sec_id}")

nfind=py_code.find("py")
if nfind == -1:
    workid=py_code
else:
    workid=py_code[0:nfind-1]
working_dir=stmp_dir+"/aqm_"+workid+"_p5"
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

os.chdir(working_dir)

msg_file=working_dir+"/msg_rzdm_aot_v7_"+start_date+"_"+sel_cyc
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

sdate = datetime.datetime.strptime(start_date, '%Y%m%d')
edate = datetime.datetime.strptime(end_date, '%Y%m%d')
YMDH_date_format = "%Y%m%d/%H"
YMD_date_format = "%Y%m%d"
YM_date_format = "%Y%m"
Y_date_format = "%Y"
M_date_format = "%m"
D_date_format = "%d"
H_date_format = "%H"
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

var=[ "aod" ]
comout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver

num_var=len(var)
print("var length = "+str(num_var))
if num_var == 0:
    print(f"no variable to scp")
    sys.exit()

if sel_cyc == "all":
   cyc_opt=[ "06", "12" ]
elif sel_cyc == "06":
   cyc_opt=[ "06" ]
elif sel_cyc == "12":
   cyc_opt=[ "12" ]
else:
    print("seletced cycle"+sel_cyc+" can not be recongized.")
    sys.exit()

figout=stmp_dir

date=sdate
while date <= edate:
    YY=date.strftime(Y_date_format)
    YM=date.strftime(YM_date_format)
    YMD=date.strftime(YMD_date_format)
    for cyc in cyc_opt:
        cycle="t"+cyc+"z"
        for ivar in range(0,num_var):
            figdir = figout+"/aqm"+"_prod_"+YMD+"_"+var[ivar]+"_"+cycle+"_p5"
            if os.path.exists(figdir):
                os.chdir(figdir)
                parta=os.path.join("/usr", "bin", "scp")
                if 1 == 1 :
                    partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "regional", "restricted", "aqm", "web", "fig", date.strftime(Y_date_format), YMD, cycle)
                    partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "regional", "restricted", "aqm", "web", "fig", date.strftime(Y_date_format), YMD, cycle)
                else:
                    partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "ftp")
                    partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
                subprocess.call(['scp -p * '+partb], shell=True)
                print("FIG DIR = "+figdir)
    date = date + date_inc
