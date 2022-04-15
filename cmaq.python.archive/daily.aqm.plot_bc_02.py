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
if len(sys.argv) < 5:
    print("you must set 5 arguments as model[prod|para|...] variabels[o3|pm25|all] cycle[06|12|all]  start_date end_date")
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
cbar_num_format = "%d"
plt.close('all') # close all figures
##
## Current operational CMAQ does not apply Bias-Correction procedure for AK and HI domain
## Current EMC development CMAQ does not apply Bias-Correction procedure for AK and HI domain
##
if envir == "prod":
    comout="/gpfs/hps/nco/ops/com/aqm/"+envir
    usrout="/gpfs/hps/nco/ops/com/aqm/"+envir
    metout=comout
    flag_ak = "no"
    flag_hi = "no"
elif envir == "para6":
    ## comout="/gpfs/hps3/emc/naqfc/noscrub/Ho-Chun.Huang/com/aqm"+envir
    comout="/gpfs/hps3/ptmp/Ho-Chun.Huang/com/aqm/"+envir
    usrout="/gpfs/hps3/emc/naqfc/noscrub/Ho-Chun.Huang/com/aqm/"+envir
    metout="/gpfs/hps/nco/ops/com/aqm/prod"
    flag_ak = "no"
    flag_hi = "no"
else:
    comout="/gpfs/dell2/emc/modeling/noscrub/Ho-Chun.Huang/com/aqm/"+envir
    usrout="/gpfs/hps3/emc/naqfc/noscrub/Ho-Chun.Huang/com/aqm/"+envir
    metout="/gpfs/hps/nco/ops/com/aqm/prod"
    flag_ak = "no"
    flag_hi = "no"

figout="/gpfs/dell2/stmp/Ho-Chun.Huang"

flag_proj="LambertConf"
if flag_proj == "LambertConf":
    regname = [   "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",   "ak",   "hi",  "can" ] 
    rlon0 = [ -161.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0, -166.0, -161.5, -141.0 ]
    rlon1 = [  -73.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0, -132.0, -153.1,  -60.0 ]
    rlat0 = [   14.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   53.2,   17.8,   38.0 ]
    rlat1 = [   72.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   71.2,   23.1,   70.0 ]
else:
    regname = [   "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",   "ak",   "hi",  "can" ] 
    rlon0 = [ -175.0, -124.0,  -100.0, -128.0,  -82.0, -125.0,  -95.0, -125.0, -105.0, -105.0, -170.0, -161.0, -141.0 ]
    rlon1 = [  -55.0,  -70.0,   -65.0,  -90.0,  -67.0, -103.0,  -79.0, -105.0,  -85.0,  -85.0, -130.0, -154.0,  -60.0 ]
    rlat0 = [    0.0,   22.0,    22.0,   24.5,   37.0,   38.0,   24.0,   30.0,   38.0,   24.0,   52.0,   18.0,   38.0 ]
    rlat1 = [   70.0,   51.0,    50.0,   54.5,   48.0,   52.0,   38.0,   45.0,   52.0,   40.0,   72.0,   23.0,   70.0 ]
xsize = [     10,     10,       8,      8,      8,      8,      8,      8,      8,      8,      8,      8,     10 ]
ysize = [      8,      8,       8,      8,      8,      8,      8,      8,      8,      8,      8,      8,      8 ]
if 1 == 1:
    iplot = [      1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1 ]
else:
    iplot = [      0,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0 ]
num_reg=len(iplot)
if flag_ak == "no" and iplot[num_reg-3] == 1:
    iplot[num_reg-3] = 0
if flag_hi == "no" and iplot[num_reg-2] == 1:
    iplot[num_reg-2] = 0
print("iplot length = "+str(num_reg))

date=sdate
while date <= edate:
    for cyc in cycle:
        msg=datetime.datetime.now()
        print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        s1_title=envir.upper()+"_BC "+date.strftime(YMD_date_format)+" "+cyc
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[1:3]))

        for ivar in range(0,num_var):
            if var[ivar] == "o3":
                model_filein=comout+"/aqm."+date.strftime(YMD_date_format)+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                if os.path.exists(model_filein):
                    print(model_filein+" exists")
                    model_data = netcdf.Dataset(model_filein)
                    cs_lat = model_data.variables['ROW'][:,:]
                    cs_lon = model_data.variables['COL'][:,:]
                    o3_cs  = model_data.variables['O3'][:,0,:,:]
                    nstep=len(o3_cs)
                    model_data.close()
                else:
                    model_filein=usrout+"/aqm."+date.strftime(YMD_date_format)+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                    if os.path.exists(model_filein):
                        print(model_filein+" exists")
                        model_data = netcdf.Dataset(model_filein)
                        cs_lat = model_data.variables['ROW'][:,:]
                        cs_lon = model_data.variables['COL'][:,:]
                        o3_cs  = model_data.variables['O3'][:,0,:,:]
                        nstep=len(o3_cs)
                        model_data.close()
                    else:
                        print("Can not find "+model_filein)
                        sys.exit()
            elif var[ivar] == "pm25":
                model_filein=comout+"/aqm."+date.strftime(YMD_date_format)+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                if os.path.exists(model_filein):
                    print(model_filein+" exists")
                    model_data = netcdf.Dataset(model_filein)
                    cs_lat = model_data.variables['ROW'][:,:]
                    cs_lon = model_data.variables['COL'][:,:]
                    pm_cs = model_data.variables['pm25'][:,0,:,:]
                    nstep=len(pm_cs)
                    model_data.close()
                else:
                    model_filein=usrout+"/aqm."+date.strftime(YMD_date_format)+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                    if os.path.exists(model_filein):
                        print(model_filein+" exists")
                        model_data = netcdf.Dataset(model_filein)
                        cs_lat = model_data.variables['ROW'][:,:]
                        cs_lon = model_data.variables['COL'][:,:]
                        pm_cs = model_data.variables['pm25'][:,0,:,:]
                        nstep=len(pm_cs)
                        model_data.close()
                    else:
                        print("Can not find "+model_filein)
                        sys.exit()
            if flag_ak == "yes":
                if var[ivar] == "o3":
                    model_filein=comout+"/AK."+date.strftime(YMD_date_format)+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                    if os.path.exists(model_filein):
                        print(model_filein+" exists")
                        model_data = netcdf.Dataset(model_filein)
                        cs_lat = model_data.variables['ROW'][:,:]
                        cs_lon = model_data.variables['COL'][:,:]
                        o3_cs  = model_data.variables['O3'][:,0,:,:]
                        nstep=len(o3_cs)
                        model_data.close()
                    else:
                        model_filein=usrout+"/AK."+date.strftime(YMD_date_format)+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                        if os.path.exists(model_filein):
                            print(model_filein+" exists")
                            model_data = netcdf.Dataset(model_filein)
                            cs_lat = model_data.variables['ROW'][:,:]
                            cs_lon = model_data.variables['COL'][:,:]
                            o3_cs  = model_data.variables['O3'][:,0,:,:]
                            nstep=len(o3_cs)
                            model_data.close()
                        else:
                            print("Can not find "+model_filein)
                            sys.exit()
                elif var[ivar] == "pm25":
                    model_filein=comout+"/AK."+date.strftime(YMD_date_format)+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                    if os.path.exists(model_filein):
                        print(model_filein+" exists")
                        model_data = netcdf.Dataset(model_filein)
                        cs_lat = model_data.variables['ROW'][:,:]
                        cs_lon = model_data.variables['COL'][:,:]
                        pm_cs = model_data.variables['pm25'][:,0,:,:]
                        nstep=len(pm_cs)
                        model_data.close()
                    else:
                        model_filein=usrout+"/AK."+date.strftime(YMD_date_format)+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                        if os.path.exists(model_filein):
                            print(model_filein+" exists")
                            model_data = netcdf.Dataset(model_filein)
                            cs_lat = model_data.variables['ROW'][:,:]
                            cs_lon = model_data.variables['COL'][:,:]
                            pm_cs = model_data.variables['pm25'][:,0,:,:]
                            nstep=len(pm_cs)
                            model_data.close()
                        else:
                            print("Can not find "+model_filein)
                            sys.exit()
            if flag_hi == "yes":
                if var[ivar] == "o3":
                    model_filein=comout+"/HI."+date.strftime(YMD_date_format)+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                    if os.path.exists(model_filein):
                        print(model_filein+" exists")
                        model_data = netcdf.Dataset(model_filein)
                        cs_lat = model_data.variables['ROW'][:,:]
                        cs_lon = model_data.variables['COL'][:,:]
                        o3_cs  = model_data.variables['O3'][:,0,:,:]
                        nstep=len(o3_cs)
                        model_data.close()
                    else:
                        model_filein=usrout+"/HI."+date.strftime(YMD_date_format)+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                        if os.path.exists(model_filein):
                            print(model_filein+" exists")
                            model_data = netcdf.Dataset(model_filein)
                            cs_lat = model_data.variables['ROW'][:,:]
                            cs_lon = model_data.variables['COL'][:,:]
                            o3_cs  = model_data.variables['O3'][:,0,:,:]
                            nstep=len(o3_cs)
                            model_data.close()
                        else:
                            print("Can not find "+model_filein)
                            sys.exit()
                elif var[ivar] == "pm25":
                    model_filein=comout+"/HI."+date.strftime(YMD_date_format)+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                    if os.path.exists(model_filein):
                        print(model_filein+" exists")
                        model_data = netcdf.Dataset(model_filein)
                        cs_lat = model_data.variables['ROW'][:,:]
                        cs_lon = model_data.variables['COL'][:,:]
                        pm_cs = model_data.variables['pm25'][:,0,:,:]
                        nstep=len(pm_cs)
                        model_data.close()
                    else:
                        model_filein=usrout+"/HI."+date.strftime(YMD_date_format)+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
                        if os.path.exists(model_filein):
                            print(model_filein+" exists")
                            model_data = netcdf.Dataset(model_filein)
                            cs_lat = model_data.variables['ROW'][:,:]
                            cs_lon = model_data.variables['COL'][:,:]
                            pm_cs = model_data.variables['pm25'][:,0,:,:]
                            nstep=len(pm_cs)
                            model_data.close()
                        else:
                            print("Can not find "+model_filein)
                            sys.exit()

        for ivar in range(0,num_var):
            msg=datetime.datetime.now()
            print("Start processing "+var[ivar])
            figdir = figout+"/aqm"+"_"+envir+"_"+date.strftime(YMD_date_format)+"_"+var[ivar]+"_"+cyc+"_bc"
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("working on "+date.strftime(YMD_date_format)+" "+cyc+" "+var[ivar])
            if var[ivar] == "o3":
                s3_title="Ozone sfc_conc (ppbV)"
                scale=1000.
                clevs = [ 0., 3., 6., 9., 12., 25., 35., 45., 55., 65., 75., 85., 95., 105. ]
                var_cs=o3_cs*scale
                if flag_ak == "yes":
                    var_ak=o3_ak*scale
                if flag_hi == "yes":
                    var_hi=o3_hi*scale
            elif var[ivar] == "pm25":
                s3_title="PM25 sfc_conc ($\u03bcg/m^3$)"
                scale=1.
                clevs = [ 0., 3., 6., 9., 12., 25., 35., 45., 55., 65., 75., 85., 95., 105. ]
                var_cs=pm_cs
                if flag_ak == "yes":
                    var_ak=pm_ak
                if flag_hi == "yes":
                    var_hi=pm_hi
            cmap = mpl.colors.ListedColormap([
                  (0.9412,0.9412,0.9412), (0.8627,0.8627,1.0000), (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000),
                  (0.2157,0.2157,1.0000), (0.0000,0.7843,0.7843), (0.0000,0.8627,0.0000), (0.6275,0.9020,0.1961),
                  (0.9020,0.8627,0.1961), (0.9020,0.6863,0.1765), (0.9412,0.5098,0.1569), (0.9804,0.2353,0.2353),
                  (0.9412,0.0000,0.5098)
                  ])
            cmap.set_over('magenta')
            cmap.set_under('whitesmoke')
            norm = mpl.colors.BoundaryNorm(boundaries=clevs, ncolors=cmap.N)
            gs = gridspec.GridSpec(1,1)
            fcst_hour=fcst_ini
            ## for n in range(0,2):
            for n in range(0,nstep):
                nout=n+1
                fcst_hour=fcst_hour+hour_inc
                if nstep > 99:
                    s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+str(format(nout,'03d'))
                else:
                    s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+str(format(nout,'02d'))
                title=s1_title+"\n"+s2_title+" "+s3_title
                pvar_cs = var_cs[n,:,:]
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
                            cf1 = ax.contourf(
                                     ak_lon, ak_lat, pvar_ak,
                                     levels=clevs, cmap=cmap, norm=norm, extend='both',
                                     transform=ccrs.PlateCarree() )
                        elif figarea == "hi":
                            cf1 = ax.contourf(
                                     hi_lon, hi_lat, pvar_hi,
                                     levels=clevs, cmap=cmap, norm=norm, extend='both',
                                     transform=ccrs.PlateCarree() )
                        else:
                            cf1 = ax.contourf(
                                     cs_lon, cs_lat, pvar_cs,
                                     levels=clevs, cmap=cmap, norm=norm, extend='both',
                                     transform=ccrs.PlateCarree() )
                            if figarea == "dset":
                                if flag_ak == "yes":
                                    ax.contourf(
                                         ak_lon, ak_lat, pvar_ak,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                                if flag_hi == "yes":
                                    ax.contourf(
                                         hi_lon, hi_lat, pvar_hi,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                        ax.set_title(title)
                        ## cb2.set_label('Discrete intervals, some other units')
                        fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,shrink=0.8,format=cbar_num_format)
                        savefig_name = figdir+"/aqm."+figarea+"."+envir.lower()+"bc."+date.strftime(YMD_date_format)+"."+cyc+"."+str(format(nout,'02d'))+"."+var[ivar]+".k1.png"
                        plt.savefig(savefig_name, bbox_inches='tight')
                        plt.close()
            ##
            ## scp by cycle and variable
            ##
            os.chdir(figdir)
            parta=os.path.join("/usr", "bin", "scp")
            if 1 == 1 :
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", date.strftime(Y_date_format), date.strftime(YMD_date_format), cyc)
            else:
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
            subprocess.call(['scp -p * '+partb], shell=True)
            msg=datetime.datetime.now()
            print("End   processing "+var[ivar])
            print("FIG DIR = "+figdir)
        msg=datetime.datetime.now()
        print("End   processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc
