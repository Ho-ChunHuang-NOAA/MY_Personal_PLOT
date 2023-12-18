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
            aqm_ver_prod=ver[1]
rfile.close()

### PASSED AGRUEMENTS
if len(sys.argv) < 3:
    print("you must set 3 arguments as quality_flag[high|med|all] start_date end_date")
    sys.exit()
else:
    qc = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

if qc.lower() == "high":
    var=[ "AOD_H_Quality" ]
    fig_index=[ "high" ]
elif qc.lower() == "med":
    var=[ "AOD_HM_Quality" ]
    fig_index=[ "medium" ]
else:
    var=[ "AOD_H_Quality", "AOD_HM_Quality" ]
    fig_index=[ "high", "medium" ]
num_var=len(var)

comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/VIIRS_AOD/REGRID"
if not os.path.exists(comout):
    print("Can not find output dir "+comout)
    sys.exit()

stmp_dir="/lfs/h2/emc/stmp/"+user
if not os.path.exists(stmp_dir):
    os.mkdir(stmp_dir)

ptmp_dir="/lfs/h2/emc/ptmp/"+user
if not os.path.exists(ptmp_dir):
    os.mkdir(ptmp_dir)

log_dir=ptmp_dir+"/batch_logs"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

working_dir=ptmp_dir+"/aqm_plot_working_aot"
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

working_dir=stmp_dir+"/aqm_plot_working_aot"
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

grid148="148"
grid227="227"
grid198="198"
grid139="139"
grid196="196"
grid793="793"

aqmv6 = True
aqmv7 = True

EXP="v70c84"
caseid="v70"
nfind=EXP.find(caseid)
if nfind == -1:
    print("AQMv6 simulation")
    aqmv7 = False
    if EXP.lower() == "prod":
        aqm_ver=aqm_ver_prod
        map_grid=grid148
        expid="aqm"
    else:
        print("Experiement ID "+EXP.lower()+" not found for this code, Program exit")
        sys.exit()
else:
    print("AQMv7 simulation")
    aqmv7 = True
    aqm_ver="v7.0"
    map_grid=grid793
    expid="aqmv7"

if not os.path.exists(comout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
    print("Can not find VIIRS regrid output dir with experiment id "+EXP.lower())
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
## cbar_num_format = "%d"
cbar_num_format = "%.1f"
plt.close('all') # close all figures

msg=datetime.datetime.now()
msg=msg - date_inc

figout=stmp_dir

##
## new area need to be added ahead of ak.  The last three areas need to be fixed as "ak",   "hi",  "can"
## this is due to the code below remove plotting of ak and hi if no ak and hi input files ash been found
##
flag_proj="LambertConf"
## from 22.574179720000018 to 51.47512722912568
## from 228.37073225113136 to 296.6273160909873
# old -70.6 to -120.4
#     22.2 to 50.7
mksize= [     64, 64, 16,     36,      36,      36,     49,     49,     49,     49,     64,     64,    121,    100,    121,     36 ]
## mksize= [  64, 64, 16,      16,      25,     25,     36,     36,     36,     36,     49,     49,    121,    100,    121,     36 ]
if flag_proj == "LambertConf":
    regname = [ "Mckinney",  "aznw", "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
    rlon0 = [ -125., -120., -165.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0,  -75.0, -166.0, -161.5, -141.0 ]
    rlon1 = [  -110., -100., -70.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0,  -71.0, -132.0, -153.1, -60.0 ]
    rlat0 = [   40., 30.0, 10.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   40.2,   53.2,   17.8,   38.0 ]
    rlat1 = [   45., 40., 75.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   41.8,   71.2,   23.1,   70.0 ]
else:
    regname = [   "Mckinney",  "aznw", "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
    rlon0 = [ -125., -120., -175.0, -124.0,  -100.0, -128.0,  -82.0, -125.0,  -95.0, -125.0, -105.0, -105.0,  -75.0, -170.0, -161.0, -141.0 ]
    rlon1 = [  -110., -100., -55.0,  -70.0,   -65.0,  -90.0,  -67.0, -103.0,  -79.0, -105.0,  -85.0,  -85.0,   -71.0, -130.0, -154.0,  -60.0 ]
    rlat0 = [    40., 30.0, 0.0,   22.0,    22.0,   24.5,   37.0,   38.0,   24.0,   30.0,   38.0,   24.0,   40.2,   52.0,   18.0,   38.0 ]
    rlat1 = [   45., 40., 70.0,   51.0,    50.0,   54.5,   48.0,   52.0,   38.0,   45.0,   52.0,   40.0,   41.8,   72.0,   23.0,   70.0 ]
xsize = [     10, 10, 10,     10,       8,      8,      8,      8,      8,      8,      8,      8,     10,      8,      8,     10 ]
ysize = [      5, 5, 8,      8,       8,      8,      8,      8,      8,      8,      8,      8,      5,      8,      8,     8 ]
if 1 == 1:
    iplot = [    0, 0,   1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1, 1 ]
else:
    iplot = [    0,  0, 0,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      1,      1, 0 ]
num_reg=len(iplot)

flag_ak=False
flag_hi=False
for i in range(0,num_reg):
    if regname[i] == "ak" and iplot[i] == 1:
        flag_ak=True
    if regname[i] == "hi" and iplot[i] == 1:
        flag_hi=True

date=sdate
while date <= edate:
    YY=date.strftime(Y_date_format)
    YM=date.strftime(YM_date_format)
    YMD=date.strftime(YMD_date_format)

    flag_find_idir = "yes"

    if flag_find_idir == "yes":
        print("comout set to "+comout)
    else:
        date = date + date_inc
        continue
    
    figdir = figout+"/viirs_"+expid+"_"+YMD
    print(figdir)
    if os.path.exists(figdir):
        shutil.rmtree(figdir)
    os.makedirs(figdir)

    for cyc in range(0,24):
        str_obs_hr=str(cyc)
        fhh=str_obs_hr.zfill(2)
        file_hdr="VIIRS-L3-AOD_AQM_"+expid+"_"+YMD+"_"+fhh
        aqmfilein=comout+"/"+expid+"."+YMD+"/"+file_hdr+".nc"
        flag_plot=True
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm = netcdf.Dataset(aqmfilein)
            cs_lat = cs_aqm.variables['lat'][:,:]
            cs_lon = cs_aqm.variables['lon'][:,:]
        else:
            flag_plot=False

        if flag_plot:
            for ivar in range(0,num_var):
                s1_title="VIIRS Total AOD at 550 nm QC"+fig_index[ivar]+" "+YMD+" "+fhh+"Z"
                clevs = [ 0., 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0 ]
                if flag_plot:
                    pvar_cs = cs_aqm.variables[var[ivar]][:,:]
                cmap = mpl.colors.ListedColormap([
                       (0.8627,0.8627,1.0000), (0.6471,0.6471,1.0000),
                       (0.0000,0.7843,0.7843), (0.0000,0.7843,0.0000),
                       (0.6275,0.9020,0.1961), (0.9020,0.8627,0.1961), (0.9061,0.6863,0.1765),
                       (0.9412,0.5098,0.1569), (0.9804,0.2353,0.2353), (1.0000,0.4118,0.7059), (0.1569,0.1569,0.1569),
                       (0.3137,0.3137,0.3137), (0.4706,0.4706,0.4706)
                       ])
                cmap.set_under((0.9412,0.9412,0.9412))
                cmap.set_over((0.6275,0.6275,0.6275))
                norm = mpl.colors.BoundaryNorm(boundaries=clevs, ncolors=cmap.N)
                gs = gridspec.GridSpec(1,1)

                ## title=s1_title+"\n"+s2_title+" "+s3_title
                title=s1_title
                for ireg in range(0,num_reg):
                    if iplot[ireg] == 1:
                        figarea=regname[ireg]
                        extent=[ rlon0[ireg], rlon1[ireg], rlat0[ireg], rlat1[ireg] ]
                        clat=0.5*(rlat0[ireg] + rlat1[ireg])
                        clon=0.5*(rlon0[ireg] + rlon1[ireg])
                        if figarea == "ak":
                            aqmproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, standard_parallels=(57, 63), globe=None)
                        elif figarea == "hi":
                            aqmproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, standard_parallels=(19, 21), globe=None)
                        else:
                            aqmproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, false_easting=-58.775, false_northing=48.772, standard_parallels=(33, 45), globe=None)
                        fig, ax = plt.subplots(figsize=(xsize[ireg],ysize[ireg]))
    
                        ax = plt.axes(projection=aqmproj)
                        ax.set_extent(extent)
                        ax.coastlines('50m')
                        states_provinces = cfeature.NaturalEarthFeature(
                            category='cultural',
                            name='admin_1_states_provinces_lines',
                            scale='50m',
                            facecolor='none')
                        ax.add_feature(states_provinces, facecolor='none', edgecolor='gray')
                        ## rivers_50m = cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '50m')
                        ## ax.add_feature(cfeature.LAND, edgecolor='black')
                        ## ax.add_feature(cfeature.OCEAN, edgecolor='black')
                        ## ax.add_feature(cfeature.COASTLINE)
                        ax.add_feature(cfeature.BORDERS, facecolor='none', linestyle=':')
                        ax.add_feature(cfeature.LAKES, facecolor='None', edgecolor='black', alpha=0.5)
                        ## ax.add_feature(cfeature.RIVERS)
                        cf1 = ax.contourf(
                                         cs_lon, cs_lat, pvar_cs,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                        ax.set_title(title)
                        ## cb2.set_label('Discrete intervals, some other units')
                        fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,shrink=1.0,format=cbar_num_format)
                        savefig_name = figdir+"/aqm."+figarea+".viirs."+YMD+"."+fhh+".aod."+fig_index[ivar]+".png"
                        plt.savefig(savefig_name, bbox_inches='tight')
                        plt.close()
            cs_aqm.close()
        else:
            print("Can not find "+aqmfilein)
    os.chdir(figdir)
    parta=os.path.join("/usr", "bin", "scp")
    if 1 == 2 :
        partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", YY, YMD)
    else:
        partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "ftp")
        partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
    ## subprocess.call(['scp -p * '+partb], shell=True)
    print("End   processing "+var[ivar])
    print("FIG DIR = "+figdir)
    msg=datetime.datetime.now()
    print("End   processing "+YMD+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc
