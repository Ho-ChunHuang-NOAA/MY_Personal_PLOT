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
user=os.environ['USER']

if len(sys.argv) < 5:
    print("you must set 5 arguments as model1[prod|para|...] variabels[o3|pm25|all] cycle[06|12|all]  start_date end_date")
    sys.exit()
else:
    envir = sys.argv[1]
    sel_var = sys.argv[2]
    sel_cyc = sys.argv[3]
    start_date = sys.argv[4]
    end_date = sys.argv[5]

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
plt.close('all') # close all figures

figout="/lfs/h2/emc/stmp/"+user

date=sdate
while date <= edate:
    for cyc in cycle:
        for ivar in range(0,num_var):
            print("Start processing "+var[ivar])
            figdir = figout+"/aqm"+"_"+envir+"bc-"+envir+"_"+date.strftime(YMD_date_format)+"_"+var[ivar]+"_"+cyc+"_diff"
            print("figdir = "+figdir)
            ##
            ## scp by cycle and variable
            ##
            if os.path.exists(figdir):
                os.chdir(figdir)
                parta=os.path.join("/usr", "bin", "scp")
                if 1 == 1 :
                    partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", date.strftime(Y_date_format), date.strftime(YMD_date_format), cyc)
                else:
                    partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
                subprocess.call(['scp -p * '+partb], shell=True)
                print("End   processing "+var[ivar])
                print("FIG DIR = "+figdir)
    msg=datetime.datetime.now()
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc