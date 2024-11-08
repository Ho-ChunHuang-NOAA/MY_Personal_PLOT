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

user=os.environ['USER']

### PASSED AGRUEMENTS
if len(sys.argv) < 5:
    print("you must set 5 arguments as [g16|g18] [aodc|aodf] quality_flag[high|med|all] start_date end_date")
    sys.exit()
else:
    sat_sel = sys.argv[1]
    scan_sel = sys.argv[2]
    qc_sel = sys.argv[3]
    start_date = sys.argv[4]
    end_date = sys.argv[5]

mdl="gefs"
expid="gefsv12.3"

if qc_sel.lower() == "high":
    qc_list=[ "high" ]
elif qc_sel.lower() == "med" or qc_sel.lower() == "medium":
    qc_list=[ "medium" ]
elif qc_sel.lower() == "low":
    qc_list=[ "low" ]
    prints(f"QC Flag Low is not support at current time, program exit.")
    sys.exit()
else:
    qc_list=[ "high" ]

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
working_dir=f"{stmp_dir}/ftp_{sat_sel}_{scan_sel}_{qc_sel}_{expid}_{start_date}"
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

os.chdir(working_dir)

msg_file=f"{working_dir}/msg_{sat_sel}_{scan_sel}_{qc_sel}_{expid}_{start_date}"
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
Julian_date_format = "%j"
Y_date_format = "%Y"
M_date_format = "%m"
D_date_format = "%d"
H_date_format = "%H"
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

if sat_sel == "all" or sat_sel == "ALL":
    satid=["g16", "g18", "g1618"]
elif sat_sel == "g16" or sat_sel == "g18" or sat_sel == "g1618":
    satid=[]
    satid.append(sat_sel)
else:
    print(f"Input sat ID = {sat_sel}, is not defined")
    sys.exit()

scan_check=scan_sel.upper()
if scan_check == "ALL":
    scanid=["AODC", "AODF"]
elif scan_check == "AODC" or scan_check == "AODF":
    scanid=[]
    scanid.append(scan_check)
else:
    print(f"Input Scan ID = {scan_sel}, is not defined")
    sys.exit()

date=sdate
while date <= edate:
    YY=date.strftime(Y_date_format)
    YM=date.strftime(YM_date_format)
    YMD=date.strftime(YMD_date_format)
    JDAY=date.strftime(Julian_date_format)
    for scan in scanid:
        for goes in satid:
            figdir = f"{stmp_dir}/{goes}_{scan}_{expid}_{YMD}"
            if os.path.exists(figdir):
                os.chdir(figdir)
                output_file=working_dir+"/count_abi_aod_figure"
                cmd=f"ls {mdl}*.png > {output_file}"
                subprocess.call([cmd], shell=True)
                with open(output_file,"r") as ofile:
                    filein_aod=ofile.readlines()
                ofile.close()
                if len(filein_aod) != 0:
                    parta=os.path.join("/usr", "bin", "scp")
                    if 1 == 1 :
                        partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", YY, YMD)
                    else:
                        partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
                        partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "ftp")
                    subprocess.call(['scp -p * '+partb], shell=True)
                    print("FIG DIR = "+figdir)
            else:
                print("Can not find "+figdir)
    msg=datetime.datetime.now()
    print("End   processing "+YMD+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc
