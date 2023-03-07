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
area_ref=['can',  'na', 'conus', 'se', 'sw', 'ne',  'nw', 'mdn', 'mds', 'ak', 'hi', 'east', 'west']
lat0_ref=[40.,   0.,   24.,     24.,  30.,  37.,   38.,  38.,   24.,   52.,  18.,  24.,     24.5]
lat1_ref=[70.,   70.,  50.,     38.,  45.,  48.,   52.,  52.,   40.,   72.,  23.,  50.,     54.5]
lon0_ref=[ -141., -141.,  -124.,   -95., -125, -82, -125.,-105., -105., -170.,-161.,-100.,     -128. ]
lon1_ref=[  -60., -60.,   -70.,    -79., -105.,-67.,-103.,-85.,  -85.,  -130.,-154.,-65.,     -90. ]
figdir="/lfs/h2/emc/stmp/"+os.environ['USER']
##
reg = [ "Mckinney",  "aznw", "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
rlon0 = [ -125., -120., -165.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0,  -75.0, -166.0, -161.5, -141.0 ]
rlon1 = [  -110., -100., -70.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0,  -71.0, -132.0, -153.1, -60.0 ]
rlat0 = [   40., 30.0, 10.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   40.2,   53.2,   17.8,   38.0 ]
rlat1 = [   45., 40., 75.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   41.8,   71.2,   23.1,   70.0 ]
xsize = [     10, 10, 10,     10,       8,      8,      8,      8,      8,      8,      8,      8,     10,      8,      8,     10 ]
ysize = [      5, 5, 8,      8,       8,      8,      8,      8,      8,      8,      8,      8,      5,      8,      8,     8 ]
if 1 == 1:
    iplot = [    1, 1,   1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1, 1 ]
else:
    iplot = [    0,  0, 0,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0, 0 ]
ilen=len(iplot)
print("iplot length = "+str(ilen))

model="aqm"
cycle=[]
cycle.append(cyc_in)
working_dir="/lfs/h2/emc/stmp/"+os.environ['USER']+"/working/fireemis/"+envir
metout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver+"/cs."+grdcro2d_date
hourly_fire_data="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/hourly_fire_emission/"+envir
if not os.path.exists(hourly_fire_data):
    os.mkdir(hourly_fire_data)
date = sdate
while date <= edate:
    hourly_fire_out=hourly_fire_data+"/"+date.strftime(YMD_date_format)
    if not os.path.exists(hourly_fire_out):
        os.mkdir(hourly_fire_out)
    find_dir=[
              "/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+envir+"/cs."+date.strftime(YMD_date_format),
              "/lfs/h2/emc/ptmp/"+user+"/com/aqm/"+envir+"/cs."+date.strftime(YMD_date_format),
              "/lfs/h1/ops/prod/com/aqm/"+aqm_ver+"/cs."+date.strftime(YMD_date_format)
             ]
    flag_find_idir="no"
    for idir in find_dir:
        datadir=idir
        print("check "+idir)
        flag_find_cyc="no"
        for cyc in cycle:
            check_file=model+".t"+cyc+"z.fireemis.d1.ncf"
            check_file2=model+".t"+cyc+"z.fireemis.ncf"
            aqmfilein=datadir+"/"+check_file
            aqmfilein2=datadir+"/"+check_file2
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                cycfind=cyc
                flag_find_cyc="yes"
            else:
                if os.path.exists(aqmfilein2):
                    print(aqmfilein2+" exists")
                    cycfind=cyc
                    flag_find_cyc="yes"
                else:
                    print("Can not find "+aqmfilein+" and "+aqmfilein2)
        if flag_find_cyc == "yes":
                print("Can not find "+aqmfilein)
        if flag_find_cyc == "yes":
            flag_find_idir="yes"
            break
    if flag_find_idir == "yes":
        print("datadir set to "+datadir)
    else:
        ## try 12z data, may not work in near realtime since 12Z has not been run
        ## but good for manauel re-run this graphic routine
        if cycle[0] == "06":
            cycle = [ "12" ]
        else:
            sys.exit()
        flag_find_idir="no"
        for idir in find_dir:
            datadir=idir
            print("check "+idir)
            flag_find_cyc="no"
            for cyc in cycle:
                check_file=model+".t"+cyc+"z.fireemis.d1.ncf"
                aqmfilein=datadir+"/"+check_file
                check_file2=model+".t"+cyc+"z.fireemis.ncf"
                aqmfilein2=datadir+"/"+check_file2
                if os.path.exists(aqmfilein):
                    print(aqmfilein+" exists")
                    cycfind=cyc
                    flag_find_cyc="yes"
                else:
                    if os.path.exists(aqmfilein2):
                        print(aqmfilein2+" exists")
                        cycfind=cyc
                        flag_find_cyc="yes"
                    else:
                        print("Can not find "+aqmfilein+" and "+aqmfilein2)
            if flag_find_cyc == "yes":
                flag_find_idir="yes"
                break
        if flag_find_idir == "yes":
            print("datadir set to "+datadir)
        else:
            sys.exit()

    figout=figdir+"/fireemis_"+envir+"_"+date.strftime(YMD_date_format)
    if os.path.exists(figout):
        shutil.rmtree(figout)
    os.mkdir(figout)

    for cyc in cycle:
        nselect=15
        if cyc == "06":
            nselect=15
        elif cyc == "12":
            nselect=9
        filein=metout+"/"+model+".t"+cyc+"z.grdcro2d.ncf"
        if os.path.exists(filein):
            print(filein+" exists")
            model_data = netcdf.Dataset(filein)
            mdl_lat = model_data.variables['LAT'][0,0,:,:]
            mdl_lon = model_data.variables['LON'][0,0,:,:]
            model_data.close()
            i=mdl_lat.shape[0]
            j=mdl_lat.shape[1]
            mdl_pts=i*j
            print('"Total number of grid is %d"' % (mdl_pts))
        else:
            print('"Can not find %s"' % (filein))
            sys.exit()

        aqmfilein=datadir+"/"+model+".t"+cyc+"z.fireemis.d1.ncf"
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
        else:
            aqmfilein2=datadir+"/"+model+".t"+cyc+"z.fireemis.ncf"
            if os.path.exists(aqmfilein2):
                print(aqmfilein2+" exists")
                aqmfilein=aqmfilein2
            else:
                print("Can not find "+aqmfilein+" and "+aqmfilein2)
        if os.path.exists(aqmfilein):
            ## print(aqmfilein+" exists")
            cs_aqm = netcdf.Dataset(aqmfilein)
            cs_var = cs_aqm.variables['TFLAG'][:,0,:]
            fire_cs = cs_aqm.variables['AECJ'][:,0,:,:]
            cs_aqm.close()
            nstep=len(cs_var)
            for n in range(nselect,nselect+1):
                pvar_cs = fire_cs[n,:,:]
                xnonzero=[]
                xnonzero=np.nonzero(pvar_cs)
                nrow=xnonzero[0]
                ncol=xnonzero[1]
                nx=len(nrow)
                plotrow=[]
                plotcol=[]
                for ii in range(0,nx):
                    plotrow.append(nrow[ii])
                    plotcol.append(ncol[ii])
            num_pts=len(plotrow)
            print('number of fire is %d' % (num_pts))
            if num_pts >= mdl_pts:
                sys.exit()
            cs_lat=[]
            cs_lon=[]
            cs_pvar=[]
            for i in range(0,num_pts):
                cs_lat.append(mdl_lat[plotrow[i],plotcol[i]])
                cs_lon.append(mdl_lon[plotrow[i],plotcol[i]])
                cs_pvar.append(pvar_cs[plotrow[i],plotcol[i]])
            
        ## plt.figure(figsize=(12, 6))
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
                fig, ax = plt.subplots(figsize=(xsize[i],ysize[i]))
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
                ax.set_title(date.strftime(YMD_date_format)+" "+envir.upper()+" run 20-21Z fire location - AECJ")
                ## ax.add_feature(rivers_50m, facecolor='None', edgecolor='b')
                ## ax.add_feature(cfeature.RIVERS)
                ## plt.show()
                for x in range(0,num_pts):
                    emis_scale=1.0
                    logvar=np.log(cs_pvar[x]*emis_scale)
                    ## print(str(logvar))
                    if logvar <= 0.5:
                        msize=0.5
                    else:
                        msize=np.log(cs_pvar[x]*emis_scale)
                    ## ax.plot(lon[x], lat[x], 'ro', markersize=3, transform=ccrs.Geodetic())
                    ax.plot(cs_lon[x], cs_lat[x], 'ro', markersize=msize, transform=ccrs.PlateCarree())
                ##ax.text(-117, 33, 'San Diego', transform=ccrs.Geodetic())
                fileout=figout+"/fireemisfire."+figarea+"."+envir+"."+date.strftime(YMD_date_format)+".t"+cyc+"z.location.day0.k1.png"
                plt.savefig(fileout, bbox_inches='tight') 
                for j in range(1,3):
                    newfile=figout+"/fireemisfire."+figarea+"."+envir+"."+date.strftime(YMD_date_format)+".t"+cyc+"z.location.day"+str(j)+".k1.png"
                    shutil.copyfile(fileout,newfile)
            ## else:
                ## print("skip "+title[i])
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
