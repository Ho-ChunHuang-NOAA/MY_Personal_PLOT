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

wgrib2=os.environ['WGRIB2']
if wgrib2 == "":
    print("No definition of WGRIB2 can be found, please load module wgrib2/2.0.8")
    sys.exit()

### PASSED AGRUEMENTS
if len(sys.argv) < 4:
    print("you must set 4 arguments as model[prod|para|...] cycle[06|12|all]  start_date end_date")
    sys.exit()
else:
    envir = sys.argv[1]
    sel_cyc = sys.argv[2]
    start_date = sys.argv[3]
    end_date = sys.argv[4]

if envir.lower() == "para":
    fig_exp="ncopara"
elif envir.lower() == "para_bc":
    fig_exp="ncoparabc"
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

working_dir=stmp_dir+"/"+envir+"_plot_working_aot"
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

os.chdir(working_dir)

msg_file=working_dir+"/msg_read_"+start_date"_"+sel_cyc
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

## aqmv7 (aod) and aqmv6 (aot)
if envir == "prod":
    var=[ "aot" ]
    comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/verification/aqm/"+envir
    comout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
else:
    var=[ "aod" ]
    comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/aqmv7_aod/"+envir
    comout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
    comout="/lfs/h2/emc/ptmp/jianping.huang/emc.para/com/aqm/v7.0"
num_var=len(var)
print("var length = "+str(num_var))

if sel_cyc == "all":
   cyc_opt=[ "06", "12" ]
elif sel_cyc == "06":
   cyc_opt=[ "06" ]
elif sel_cyc == "12":
   cyc_opt=[ "12" ]
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
## cbar_num_format = "%d"
cbar_num_format = "%.1f"
plt.close('all') # close all figures

msg=datetime.datetime.now()
msg=msg - date_inc
grdcro2d_date=msg.strftime("%Y%m%d")
##
## Current operational CMAQ does include runs for AK and HI domain
## Current EMC development CMAQ does not include runs for AK and HI domain
##
## ilen=len(envir)
## print("experiment is "+envir[0:ilen])
## sys.exit()

if not os.path.exists(comout):
    print("Can not find output dir "+comout)
    sys.exit()
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
    iplot = [    0, 0,   1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      0,      0, 1 ]
else:
    iplot = [    0,  0, 0,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0, 0 ]
num_reg=len(iplot)

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
    
    flag_ak = "no"
    flag_hi = "no"

    for cyc in cyc_opt:
        cycle="t"+cyc+"z"
        msg=datetime.datetime.now()
        print("Start processing "+YMD+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        s1_title="CMAQ "+fig_exp.upper()+" "+YMD+" "+cycle
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[0:2]))

        ## metfilein=metout+"/cs."+grdcro2d_date+"/aqm."+cyc+".grdcro2d.ncf"
        ## if os.path.exists(metfilein):
        ##     print(metfilein+" exists")
        ##     model_data = netcdf.Dataset(metfilein)
        ##     cs_lat = model_data.variables['LAT'][0,0,:,:]
        ##     cs_lon = model_data.variables['LON'][0,0,:,:]
        ##     model_data.close()
        ## else:
        ##     print("Can not find "+metfilein)

        for ivar in range(0,num_var):
            fcst_hour=fcst_ini
            figdir = figout+"/aqm"+"_"+envir+"_"+YMD+"_"+var[ivar]+"_"+cycle
            print(figdir)
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("working on "+YMD+" "+cycle+" "+var[ivar])
            flag_read_latlon="no"
            hour_beg = 1
            hour_end = 72
            if hour_beg != 1:
                set_hour=1
                while set_hour < hour_beg:
                    fcst_hour=fcst_hour+hour_inc
                    set_hour+=1
            for fcst_hr in range(hour_beg,hour_end+1):
                str_fcst_hr=str(fcst_hr)
                fhh=str_fcst_hr.zfill(2)
                fhh3=str_fcst_hr.zfill(3)
                flag_plot_aod=False
                if var[ivar] == "aod":
                    file_hdr="aqm."+cycle+"."+var[ivar]+".f"+fhh3
                    aqmfilein=comout+"/aqm."+YMD+"/"+cyc+"/"+file_hdr+".nc"
                    if os.path.exists(aqmfilein):
                        print(aqmfilein+" exists")
                        cs_aqm = netcdf.Dataset(aqmfilein)
                        cs_lat = cs_aqm.variables['lat'][:,:]
                        cs_lon = cs_aqm.variables['lon'][:,:]
                        aot_cs = cs_aqm.variables['aod'][0,:,:]
                        cs_aqm.close()
                        flag_plot_aod=True
                    else:
                        print("Can not find "+aqmfilein)
                flag_plot_aot=False
                if var[ivar] == "aot":
                    file_hdr="aqm."+cycle+"."+var[ivar]+".f"+fhh+".148"
                    aqmfilein=comout+"/cs."+YMD+"/"+file_hdr+".grib2"
                    outfile=working_dir+"/"+file_hdr+"."+YMD+"."+cycle+".nc"
                    subprocess.call([wgrib2+' -netcdf '+outfile+' '+aqmfilein], shell=True)
                    aqmfilein=outfile
                    if os.path.exists(aqmfilein):
                        ## print(aqmfilein+" exists")
                        cs_aqm = netcdf.Dataset(aqmfilein)
                        cs_lat = cs_aqm.variables['latitude'][:,:]
                        cs_lon = cs_aqm.variables['longitude'][:,:]
                        latmax=np.amax(cs_lat)
                        latmin=np.amin(cs_lat)
                        lonmax=np.amax(cs_lon)
                        lonmin=np.amin(cs_lon)
                        ## print("from "+str(latmin)+" to "+str(latmax))
                        ## print("from "+str(lonmin)+" to "+str(lonmax))
                        aot_cs = cs_aqm.variables['AOTK_1sigmalevel'][0,:,:]
                        cs_aqm.close()
                        flag_plot_aot=True
                    else:
                        print("Can not find "+aqmfilein)

                if flag_plot_aot or flag_plot_aod:
                    fcst_hour=fcst_hour+hour_inc
                    s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+fhh
                    msg=datetime.datetime.now()
                    s3_title="Total AOD"
                    clevs = [ 0., 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0 ]
                    var_cs=aot_cs
                    if flag_ak == "yes":
                        var_ak=aot_ak
                    if flag_hi == "yes":
                        var_hi=aot_hi
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
    
                    title=s1_title+"\n"+s2_title+" "+s3_title
                    pvar_cs = var_cs[:,:]
                    if flag_ak == "yes":
                        pvar_ak = var_ak[:,:]
                    if flag_hi == "yes":
                        pvar_hi = var_hi[:,:]
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
                            if figarea == "ak":
                                try:
                                    cf1 = ax.contourf(
                                         ak_lon, ak_lat, pvar_ak,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                                except ValueError:
                                    continue
                            elif figarea == "hi":
                                try:
                                    cf1 = ax.contourf(
                                         hi_lon, hi_lat, pvar_hi,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                                except ValueError:
                                    continue
                            else:
                                try:
                                    cf1 = ax.contourf(
                                         cs_lon, cs_lat, pvar_cs,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                                except ValueError:
                                    continue
                                if figarea == "dset":
                                    if flag_ak == "yes":
                                        try:
                                            ax.contourf(
                                             ak_lon, ak_lat, pvar_ak,
                                             levels=clevs, cmap=cmap, norm=norm, extend='both',
                                             transform=ccrs.PlateCarree() )
                                        except ValueError:
                                            continue
                                    if flag_hi == "yes":
                                        try:
                                            ax.contourf(
                                             hi_lon, hi_lat, pvar_hi,
                                             levels=clevs, cmap=cmap, norm=norm, extend='both',
                                             transform=ccrs.PlateCarree() )
                                        except ValueError:
                                            continue
                            ax.set_title(title)
                            ## cb2.set_label('Discrete intervals, some other units')
                            fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,shrink=1.0,format=cbar_num_format)
                            savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"."+YMD+"."+cycle+"."+fhh+".aod.k1.png"
                            plt.savefig(savefig_name, bbox_inches='tight')
                            plt.close()

            ##
            ## scp by cycle and variable
            ##
            os.chdir(figdir)
            parta=os.path.join("/usr", "bin", "scp")
            if 1 == 1 :
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", date.strftime(Y_date_format), YMD, cycle)
            else:
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "ftp")
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
            ## subprocess.call(['scp -p * '+partb], shell=True)
        msg=datetime.datetime.now()
        print("End   processing "+var[ivar])
        print("FIG DIR = "+figdir)
        msg=datetime.datetime.now()
        print("End   processing "+YMD+" "+cycle+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    print("End   processing "+YMD+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc
