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
## 'm'            magent
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

user=os.environ['USER']

### PASSED AGRUEMENTS
if len(sys.argv) < 3:
    print("you must set 3 arguments as cycle_hour [06|12] start_date end_date in yyyymmdd")
    sys.exit()
else:
    sel_cyc = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

envir="v70"
envir_out="v70fire"

stmp_dir="/lfs/h2/emc/stmp/"+user
if not os.path.exists(stmp_dir):
    os.mkdir(stmp_dir)

ptmp_dir="/lfs/h2/emc/ptmp/"+user
if not os.path.exists(ptmp_dir):
    os.mkdir(ptmp_dir)

log_dir=ptmp_dir+"/batch_logs"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

working_dir=stmp_dir+"/working_rrfs_fireemis_"+envir
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
    remote_host="clogin01.wcoss2.ncep.noaa.gov"
elif machine.lower() == "cactus":
    remote="dogwood"
    remote_host="dlogin01.wcoss2.ncep.noaa.gov"
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

sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:]), 00, 00, 00 )
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:]), 00, 00, 00 )

date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)
YMD_date_format = "%Y%m%d"
YMDH_date_format = "%Y%m%d%H"
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
##
reg = [ "Mckinney",  "aznw", "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
rlon0 = [ -125., -120., -165.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0,  -75.0, -166.0, -161.5, -141.0 ]
rlon1 = [  -110., -100., -70.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0,  -71.0, -132.0, -153.1, -60.0 ]
rlat0 = [   40., 30.0, 10.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   40.2,   53.2,   17.8,   38.0 ]
rlat1 = [   45., 40., 75.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   41.8,   71.2,   23.1,   70.0 ]
xsize = [     10, 10, 10,     10,       8,      8,      8,      8,      8,      8,      8,      8,     10,      8,      8,     10 ]
ysize = [      5, 5, 8,      8,       8,      8,      8,      8,      8,      8,      8,      8,      5,      8,      8,     8 ]
if 1 == 1:
    ## with all 16 reg, it can not be finished in 4:30:00 wallcolck time
    iplot = [    1, 1,   0,      1,       1,      1,      0,      1,      1,      1,      0,      0,      0,      1,      0, 1 ]
else:
    iplot = [    1,  0, 0,      0,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0, 0 ]
ilen=len(iplot)
print("iplot length = "+str(ilen))

model="aqm"

if sel_cyc == "all":
   cycle=[ "06", "12" ]
   cycle=[ "t06z", "t12z" ]
elif sel_cyc == "06":
   cycle=[ "06" ]
   cycle=[ "t06z" ]
elif sel_cyc == "12":
   cycle=[ "12" ]
   cycle=[ "t12z" ]
else:
    print("seletced cycle"+sel_cyc+" can not be recongized.")
    sys.exit()

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
figdir="/lfs/h2/emc/stmp/"+user
if not os.path.exists(working_dir):
    os.mkdir(working_dir)
date = sdate
while date <= edate:
    find_dir=[
              "/lfs/h2/emc/physics/noscrub/jianping.huang/data/RRFS_CMAQ/emissions/GSCE/RAVE.in.C793/RAVE_new/"+date.strftime(YMD_date_format),
              "/lfs/h2/emc/physics/noscrub/"+user+"/rave_fire_emission/C793/"+date.strftime(YMD_date_format),
              "/lfs/h2/emc/ptmp/"+user+"/com/aqm/"+envir+"/cs."+date.strftime(YMD_date_format)
             ]
    flag_find_idir="no"
    for idir in find_dir:
        datadir=idir
        print("check "+idir)
        flag_find_cyc="no"
        for cyc in cycle:
            ## check_file="Hourly_Emissions_regrid_rrfs_13km_"+date.strftime(YMD_date_format)+"_"+cyc+"_h72.nc"
            check_file="Hourly_Emissions_regrid_NA_13km_"+date.strftime(YMD_date_format)+"_"+cyc+"_h72.nc"
            aqmfilein=datadir+"/"+check_file
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                cycfind=cyc
                flag_find_cyc="yes"
            else:
                print("Can not find "+aqmfilein)
        if flag_find_cyc == "yes":
            flag_find_idir="yes"
            break
    if flag_find_idir == "yes":
        print("datadir set to "+datadir)
    else:
        sys.exit()

    for cyc in cycle:
        figout=working_dir+"/"+date.strftime(YMD_date_format)+"_"+cyc
        if os.path.exists(figout):
            shutil.rmtree(figout)
        os.mkdir(figout)

        ini_time = date.replace(int(date.year), int(date.month), int(date.day), int(cyc[1:3]), 00, 00 )
        print("initial time is "+ini_time.strftime(YMDH_date_format))
        aqmfilein=datadir+"/Hourly_Emissions_regrid_NA_13km_"+date.strftime(YMD_date_format)+"_"+cyc+"_h72.nc"
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm = netcdf.Dataset(aqmfilein)
            mdl_lat = cs_aqm.variables['Latitude'][:,:]
            mdl_lon = cs_aqm.variables['Longitude'][:,:]
            i=mdl_lat.shape[0]
            j=mdl_lat.shape[1]
            print('"Dimension 0 is %d"' % (i))
            print('"Dimension 1 is %d"' % (j))
            mdl_pts=i*j
            print('"Total number of grid is %d"' % (mdl_pts))
            emis_var="PM2.5"
            fire_cs = cs_aqm.variables[emis_var][:,:,:]
            nstep=fire_cs.shape[0]
            nlat=fire_cs.shape[1]
            nlon=fire_cs.shape[2]
            print('"Dimension 0 is %d"' % (nstep))
            print('"Dimension 1 is %d"' % (nlat))
            print('"Dimension 2 is %d"' % (nlon))
            cs_aqm.close()
            
            for n in range(0,nstep):
                if n == 0:
                    beg_time=ini_time
                    end_time=ini_time + hour_inc
                else:
                    beg_time=beg_time + hour_inc
                    end_time=end_time + hour_inc
                pvar_cs = fire_cs[n,:,:]
                max_fire=np.amax(pvar_cs)
                min_fire=np.amin(pvar_cs)
                ## print('maximum/minimum  fire emission occurred is %f and %f' % ( max_fire, min_fire ) )
                result = np.where(pvar_cs == np.amax(pvar_cs))
                ## print('( %d , %d )' % (result[0],result[1]))
                idx_rows=result[0]
                idx_cols=result[1]
                ## print('( %d , %d )' % (result[0],result[1]))
    
                xnonzero=[]
                xnonzero=np.nonzero(pvar_cs)
                nrow=xnonzero[0]
                ncol=xnonzero[1]
                nx=len(nrow)
                ## print(nrow)
                ## print(ncol)
                print('number of fire emission is %d' % (nx))
                plotrow=[]
                plotcol=[]
                for ii in range(0,nx):
                    ## print('( %d , %d )' % (nrow[ii],ncol[ii]) )
                    plotrow.append(nrow[ii])
                    plotcol.append(ncol[ii])
                ## print(plotrow)
                ## print(plotcol)
                ## print('initial number of fire is %d ' % (nx) )
                num_pts=len(plotrow)
                ## print('final   number of fire is %d' % (num_pts))
                if num_pts >= mdl_pts:
                    sys.exit()
                cs_lat=[]
                cs_lon=[]
                cs_pvar=[]
                for i in range(0,num_pts):
                    cs_lat.append(mdl_lat[plotrow[i],plotcol[i]])
                    cs_lon.append(mdl_lon[plotrow[i],plotcol[i]])
                    cs_pvar.append(pvar_cs[plotrow[i],plotcol[i]])
                ## print(cs_lat)
                ## print(cs_lon)

                ## plt.figure(figsize=(12, 6))
                for i in range(0,ilen):
                    fcst_hr=n+1
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
                        if beg_time.strftime(YMD_date_format) == end_time.strftime(YMD_date_format):
                            ## ax.set_title(end_time.strftime(YMD_date_format)+" "+beg_time.strftime(H_date_format)+"-"+end_time.strftime(H_date_format)+"Z "+envir.upper()+" run fire location - "+emis_var.upper())
                            ax.set_title(end_time.strftime(YMD_date_format)+" "+beg_time.strftime(H_date_format)+"-"+end_time.strftime(H_date_format)+"Z V70 run NA_G793 fire location - "+emis_var.upper())
                        else:
                            ## ax.set_title(beg_time.strftime(YMD_date_format)+" "+beg_time.strftime(H_date_format)+"Z - "+end_time.strftime(YMD_date_format)+" "+end_time.strftime(H_date_format)+"Z "+envir.upper()+" run fire location - "+emis_var.upper())
                            ax.set_title(beg_time.strftime(YMD_date_format)+" "+beg_time.strftime(H_date_format)+"Z - "+end_time.strftime(YMD_date_format)+" "+end_time.strftime(H_date_format)+"Z V70 exp run fire location - "+emis_var.upper())
                        ## ax.add_feature(cfeature.RIVERS)
                        ## ax.add_feature(rivers_50m, facecolor='None', edgecolor='b')
                        ## plt.show()
                        for x in range(0,num_pts):
                            ## fisrt convert unit from kg/m2/s to g/s, assuming grid area is 13x13 km**2
                            emis_scale=1.69E+10   ## 1000 g * 13000 m * 13000 m * 0.1
                            logvar=np.log(cs_pvar[x]*emis_scale)
                            ## print(str(logvar))
                            if logvar <= 0.5:
                                msize=0.5
                            else:
                                msize=np.log(cs_pvar[x]*emis_scale)
                            ## ax.plot(lon[x], lat[x], 'ro', markersize=3, transform=ccrs.Geodetic())
                            ax.plot(cs_lon[x], cs_lat[x], 'ro', markersize=msize, transform=ccrs.PlateCarree())
                        ##ax.text(-117, 33, 'San Diego', transform=ccrs.Geodetic())
                        fileout=figout+"/rrfs_fireemisfire."+figarea+"."+envir_out+"."+date.strftime(YMD_date_format)+"."+cyc+".location."+str(format(fcst_hr,'02d'))+".k1.png"
                        plt.savefig(fileout, bbox_inches='tight') 
        else:
            print("Can not find "+aqmfilein)
            sys.exit()
            
        os.chdir(figout)
        subprocess.call("chmod 644 *", shell=True)
        parta=os.path.join("/usr", "bin", "scp")
        if 1 == 1 :
            partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", date.strftime(Y_date_format), date.strftime(YMD_date_format), cyc )
        else:
            partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
            partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "ftp")
        subprocess.call(["scp -p * "+partb], shell=True)
    date = date + date_inc
