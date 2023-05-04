# mark a known place to help us geo-locate ourselves
## Markers
## ========================================
## character      description
## ========================================
## '.'            point marker
## ','            pixel marker
## 'o'            circle marker
## 'v'            triangle_down marker
## '^'            triangle_up marker
## '<'            triangle_left marker
## '>'            triangle_right marker
## '1'            tri_down marker
## '2'            tri_up marker
## '3'            tri_left marker
## '4'            tri_right marker
## 's'            square marker
## 'p'            pentagon marker
## '*'            star marker
## 'h'            hexagon1 marker
## 'H'            hexagon2 marker
## '+'            plus marker
## 'x'            x marker
## 'D'            diamond marker
## 'd'            thin_diamond marker
## '|'            vline marker
## '_'            hline marker
## 
## Line Styles
## ========================================
## character      description
## ========================================
## '-'            solid line style
## '--'           dashed line style
## '-.'           dash-dot line style
## ':'            dotted line style
## 
## Example format strings:
## 
## 'b'    # blue markers with default shape
## 'or'   # red circles
## '-g'   # green solid line
## '--'   # dashed line with default color
## '^k:'  # black triangle_up markers connected by a dotted line
## 
## Colors
## 
## The supported color abbreviations are the single letter codes
## ========================================
## character      color
## ========================================
## 'b'            blue
## 'g'            green
## 'r'            red
## 'c'            cyan
## 'm'            magenta
## 'y'            yellow
## 'k'            black
## 'w'            white
## from mpl_toolkits.basemap import Basemap
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

### PASSED AGRUEMENTS
if len(sys.argv) < 4:
    print("you must set 4 arguments as model_exp [prod|para1...#] cycle [06|12] start_date end_date in yyyymmdd")
    sys.exit()
else:
    envir = sys.argv[1]
    cyc_in = sys.argv[2]
    start_date = sys.argv[3]
    end_date = sys.argv[4]

user=os.environ['USER']

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

warnings.filterwarnings('ignore')
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelsize'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.formatter.useoffset'] = False
cycle=[]
cycle.append(cyc_in)
working_dir="/lfs/h2/emc/stmp/"+os.environ['USER']+"/working/fireemis/"+envir
date = sdate
while date <= edate:
    for cyc in cycle:
        figout=figdir+"/fireemis_"+envir+"_"+date.strftime(YMD_date_format)+"_"+cyc
        print(figout)
        if os.path.exists(figout):
            os.chdir(figout)
            cyc_out="t"+cyc+"z"
            parta=os.path.join("/usr", "bin", "scp")
            if 1 == 1 :
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", date.strftime(Y_date_format), date.strftime(YMD_date_format), cyc_out )
            else:
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "ftp")
            subprocess.call(["scp -p * "+partb], shell=True)
    date = date + date_inc
