import sys
import datetime
import shutil
import subprocess
import fnmatch
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
import numpy as np
import netCDF4 as netcdf
import re
import maps2d_plot_util as maps2d_plot_util
import warnings
import logging
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

now = True
now = False
if now:
    print("The statement is true")
else:
    print("The statement is false")
sys.exit()
### PASSED AGRUEMENTS
if len(sys.argv) < 0:
    print("you must set 3 arguments as model_exp [prod|para1...#] start_date end_date in yyyymmdd")
    sys.exit()
else:
    envir = sys.argv[1]
    ## start_date = sys.argv[2]
    ## end_date = sys.argv[3]

caseid="v70"
nfind=envir.find(caseid)
if nfind == -1:
    print("not AQMv7 simulation")
    nfind=envir.find("_bc")
    if nfind == -1:
        print("not a bias_correction cases")
        EXP=envir
        BC_append=""
        print("exp="+EXP)
        print("BC_append="+BC_append)
    else:
        print("A bias_correction cases")
        EXP=envir[0:nfind]
        BC_append="_bc"
        print("exp="+EXP)
        print("BC_append="+BC_append)
else:
    print("AQMv7 simulation")
    nfind=envir.find("_bc")
    if nfind == -1:
        print("not a bias_correction cases")
        EXP=envir
        n0=len(caseid)
        n1=len(EXP)
        expid=envir[n0:n1]
        BC_append=""
        print("exp="+EXP)
        print("expid="+expid)
        print("BC_append="+BC_append)
    else:
        EXP=envir[0:nfind]
        n0=len(caseid)
        n1=len(EXP)
        expid=EXP[n0:n1]
        BC_append="_bc"
        print("exp="+EXP)
        print("expid="+expid)
        print("BC_append="+BC_append)
sys.exit()
sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:]), 00)
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:]), 23)
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)
YMD_date_format = "%Y%m%d"
YM_date_format = "%Y%m"
MD_date_format = "%m%d"
Y_date_format = "%Y"
M_date_format = "%m"
D_date_format = "%d"
H_date_format = "%H"

msg=datetime.datetime.now()
msg=msg - date_inc
grdcro2d_date=msg.strftime("%Y%m%d")

warnings.filterwarnings('ignore')
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelsize'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.formatter.useoffset'] = False
