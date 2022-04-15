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
if len(sys.argv) < 3:
    print("you must set 3 arguments as model_exp [prod|para1...#] start_date end_date in yyyymmdd")
    sys.exit()
else:
    envir = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

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
area_ref=['can',  'na', 'conus', 'se', 'sw', 'ne',  'nw', 'mdn', 'mds', 'ak', 'hi', 'east', 'west']
lat0_ref=[40.,   0.,   24.,     24.,  30.,  37.,   38.,  38.,   24.,   52.,  18.,  24.,     24.5]
lat1_ref=[70.,   70.,  50.,     38.,  45.,  48.,   52.,  52.,   40.,   72.,  23.,  50.,     54.5]
lon0_ref=[ -141., -141.,  -124.,   -95., -125, -82, -125.,-105., -105., -170.,-161.,-100.,     -128. ]
lon1_ref=[  -60., -60.,   -70.,    -79., -105.,-67.,-103.,-85.,  -85.,  -130.,-154.,-65.,     -90. ]
figdir="/gpfs/dell1/stmp/Ho-Chun.Huang"
##title = [ "dset", "conus", "east us", "west us", "ne us", "nw us", "se us", "sw us", "alaska", "hawaii", "us-can" ] 
reg = [   "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "mds",   "ak",   "hi",  "can" ] 
rlon0 = [ -175.0, -124.0,  -100.0, -128.0,  -82.0, -125.0,  -95.0, -125.0, -105.0, -105.0, -170.0, -161.0, -141.0 ]
rlon1 = [  -55.0,  -70.0,   -65.0,  -90.0,  -67.0, -103.0,  -79.0, -105.0,  -85.0,  -85.0, -130.0, -154.0,  -60.0 ]
rlat0 = [    0.0,   22.0,    22.0,   24.5,   37.0,   38.0,   24.0,   30.0,   38.0,   24.0,   52.0,   18.0,   38.0 ]
rlat1 = [   70.0,   51.0,    50.0,   54.5,   48.0,   52.0,   38.0,   45.0,   52.0,   40.0,   72.0,   23.0,   70.0 ]
iplot = [      1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1 ]
##iplot = [      0,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0 ]
ilen=len(iplot)
print("iplot length = "+str(ilen))
datadir = '/gpfs/dell2/emc/modeling/noscrub/Ho-Chun.Huang/aod_smoke/fire_prod'
datadir1 = "/gpfs/hps3/ptmp/Ho-Chun.Huang/com/aqm/"+envir
datadir2 = "/gpfs/hps3/emc/meso/noscrub/Ho-Chun.Huang/com/aqm/"+envir
datadir3="/gpfs/dell1/ptmp/Ho-Chun.Huang/com/aqm/"+envir,
working_dir="/gpfs/dell1/stmp/Ho-Chun.Huang/working/gbbepx/"+envir
model="aqm"
date = sdate
while date <= edate:
    figout=figdir+"/gbbepx_"+envir+"_"+date.strftime(YMD_date_format)
    if os.path.exists(figout):
        shutil.rmtree(figout)
    os.mkdir(figout)
    filein1=datadir1+"/"+model+"."+date.strftime(YMD_date_format)+".met/"+model+".t06z.fire_location_cs.ncf"
    filein2=datadir2+"/"+model+"."+date.strftime(YMD_date_format)+"/"+model+".t06z.fire_location_cs.ncf"
    filein3=datadir3+"/"+model+"."+date.strftime(YMD_date_format)+"/"+model+".t06z.fire_location_cs.ncf"
    if os.path.exists(filein1):
        filein=filein1
    else:
        if os.path.exists(filein2):
            filein=filein2
        else:
            if os.path.exists(filein3):
                filein=filein3
            else:
                print("Can not find "+filein1+" or "+filein2+" or "+filein3)
                sys.exit()
    if os.path.exists(filein):
        print(filein+" exists")
        model_data = netcdf.Dataset(filein)
        cs_lat = model_data.variables['LATITUDE'][0,0,:,0]
        cs_lon = model_data.variables['LONGITUDE'][0,0,:,0]
        model_data.close()
        num_pts=len(cs_lat)
    # ax = plt.axes(projection=ccrs.PlateCarree())
    # ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    
    ##ax = plt.axes(projection=ccrs.LambertConformal(central_longitude=-96.0, central_latitude=39.0, false_easting=0.0, false_northing=0.0, secant_latitudes=None, standard_parallels=None, globe=None, cutoff=-30)
        plt.figure(figsize=(12, 6))
        for i in range(0,ilen):
            if int(iplot[i]) == 1: 
                ## print("plot "+title[i])
                figarea=reg[i]
                extent = [ rlon0[i], rlon1[i], rlat0[i], rlat1[i] ]
                clon=0.5*(rlon0[i]+rlon1[i])
                clat=0.5*(rlat0[i]+rlat1[i])
                ## ax = plt.axes(projection=ccrs.LambertConformal(central_longitude=-120.628, central_latitude=21.821, false_easting=-58.775, false_northing=48.772, standard_parallels=(33, 45), globe=None))
                if figarea == "ak":
                    aqmproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, false_easting=-58.775, false_northing=48.772, standard_parallels=(57, 63), globe=None)
                elif figarea == "hi":
                    aqmproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, standard_parallels=(19, 21), globe=None)
                else:
                    aqmproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, standard_parallels=(33, 45), globe=None)
                ax = plt.axes(projection=aqmproj)
                ## ax = plt.axes(projection=ccrs.PlateCarree())
                ax.set_extent(extent)
                states_provinces = cfeature.NaturalEarthFeature(
                    category='cultural',
                    name='admin_1_states_provinces_lines',
                    scale='50m',
                    facecolor='none')
                rivers_50m = cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '50m')
                ax.add_feature(states_provinces, edgecolor='gray')
                ## ax.coastlines('50m')
                ax.add_feature(cfeature.BORDERS, linestyle=':')
                ax.add_feature(cfeature.OCEAN)
                ax.add_feature(cfeature.LAND, edgecolor='black')
                ax.add_feature(cfeature.LAKES, edgecolor='black')
                ax.set_title(date.strftime(YMD_date_format)+" "+envir.upper()+" run fire location")
                ## ax.add_feature(rivers_50m, facecolor='None', edgecolor='b')
                ## ax.add_feature(cfeature.RIVERS)
                ## plt.show()
                for x in range(0,num_pts):
                  ## ax.plot(lon[x], lat[x], 'ro', markersize=3, transform=ccrs.Geodetic())
                  ax.plot(cs_lon[x], cs_lat[x], 'ro', markersize=3, transform=ccrs.PlateCarree())
                ##ax.text(-117, 33, 'San Diego', transform=ccrs.Geodetic())
                fileout=figout+"/gbbepxfire."+figarea+"."+envir+"."+date.strftime(YMD_date_format)+".t06z.location.day0.k1.png"
                plt.savefig(fileout, bbox_inches='tight') 
                for j in range(1,3):
                    newfile=figout+"/gbbepxfire."+figarea+"."+envir+"."+date.strftime(YMD_date_format)+".t06z.location.day"+str(j)+".k1.png"
                    shutil.copyfile(fileout,newfile)
            ## else:
                ## print("skip "+title[i])
        os.chdir(figout)
        parta=os.path.join("/usr", "bin", "scp")
        partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", date.strftime(Y_date_format), date.strftime(YMD_date_format), "t06z" )
        ##partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
        subprocess.call(["scp -p * "+partb], shell=True)
    else:
        print("Can not find "+filein)
    date = date + date_inc
