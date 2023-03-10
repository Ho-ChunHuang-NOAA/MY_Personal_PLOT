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
if aqm_ver_prod=="":
    aqm_ver_prod="v6.1"
print("aqm_ver="+aqm_ver_prod)

if len(sys.argv) < 5:
    print("you must set 5 arguments as model1[prod|para|...] variabels[o3|pm25|all] cycle[06|12|all]  start_date end_date")
    sys.exit()
else:
    envir = sys.argv[1]
    sel_var = sys.argv[2]
    sel_cyc = sys.argv[3]
    start_date = sys.argv[4]
    end_date = sys.argv[5]

if envir.lower() == "para":
    fig_exp1="ncopara"
else:
    fig_exp1=envir.lower()
fig_id=fig_exp1+"bc-"+fig_exp1
title_id=fig_exp1.upper()+"BC-"+fig_exp1.upper()

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

flag_ak=True
flag_hi=True
aqmv6 = False
aqmv7 = False
caseid="v70"
nfind=envir.find(caseid)
if nfind == -1:
    print("AQMv6 simulation")
    s1_lead="CMAQ"
    aqmv6 = True
    bcfilehdr_o3="ozone"
    bcfilehdr_pm25="pm2.5"
    nfind=envir.find("_bc")
    if nfind == -1:
        print("not a bias_correction cases")
        EXP=envir
        BC_append=""
        BC_fig_append=BC_append
        print("exp="+EXP)
        print("BC_append="+BC_append)
        flag_ak=True
        flag_hi=True
    else:
        print("A bias_correction cases")
        EXP=envir[0:nfind]
        BC_append="_bc"
        BC_fig_append="bc"
        print("exp="+EXP)
        print("BC_append="+BC_append)
        flag_ak=False
        flag_hi=False
    if EXP.lower() == "prod" or EXP.lower() == "para" or EXP.lower() == "firev4":
        aqm_ver=aqm_ver_prod
        exp_grid=grid148
        expid="cs"
        comout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
        comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+EXP.lower()
        comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/verification/aqm/"+EXP.lower()
    else:
        print("Experiement ID "+EXP.lower()+" not found for this code, Program exit")
        sys.exit()
    usrout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/verification/aqm/"+EXP.lower()
    usrout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+EXP.lower()
    biasdir="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/BiasCor_updated/"+EXP.lower()
    if not os.path.exists(comout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
        if not os.path.exists(usrout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
            print("Can not find output dir with experiment id "+EXP.lower())
            sys.exit()
else:
    print("AQMv7 simulation")
    print("The difference plot is not for AQMv7")
    sys.exit()
    s1_lead="Online CMAQ"
    aqmv7 = True
    aqm_ver="v7.0"
    exp_grid=grid793

    bcfilehdr_o3="ozone"
    bcfilehdr_pm25="pm2.5"
    nfind=envir.find("_bc")
    if nfind == -1:
        print("not a bias_correction cases")
        EXP=envir
        n0=len(caseid)
        n1=len(EXP)
        expid=envir[n0:n1]
        BC_append=""
        BC_fig_append=BC_append
        print("exp="+EXP)
        print("expid="+expid)
        print("BC_append="+BC_append)
        flag_ak=True
        flag_hi=True
    else:
        EXP=envir[0:nfind]
        n0=len(caseid)
        n1=len(EXP)
        expid=EXP[n0:n1]
        BC_append="_bc"
        BC_fig_append="bc"
        print("exp="+EXP)
        print("expid="+expid)
        print("BC_append="+BC_append)
        flag_ak=False
        flag_hi=False
    comout="/lfs/h2/emc/ptmp/jianping.huang/emc.para/com/aqm/"+aqm_ver+"/aqm."+aqm_ver+"."+expid
    comout="/lfs/h2/emc/aqmtemp/para/com/aqm/"+aqm_ver
    usrout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/verification/aqm/"+EXP.lower()
    if not os.path.exists(comout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
        if not os.path.exists(usrout+"/cs."+sdate.strftime(YMD_date_format)):
            print("Can not find output dir with experiment id "+EXP.lower())
            sys.exit()

if EXP.lower() == "para":
    fig_exp="ncopara"
else:
    fig_exp=EXP.lower()+BC_fig_append

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

msg=datetime.datetime.now()
msg=msg - date_inc
grdcro2d_date=msg.strftime("%Y%m%d")

##
## Current operational CMAQ does not apply Bias-Correction procedure for AK and HI domain
## Current EMC development CMAQ does not apply Bias-Correction procedure for AK and HI domain
##

metout1="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
metout2="/lfs/h1/ops/prod/com/aqm/"+aqm_ver

flag_ak = False
flag_hi = False

flag_biasdir=False
flag_find_idir=False
flag_find_cyc=True
for cyc in cycle:
    check_file1=comout+"/cs."+sdate.strftime(YMD_date_format)+"/aqm."+cyc+".aconc_sfc.ncf"
    check_file2=usrout+"/cs."+sdate.strftime(YMD_date_format)+"/aqm."+cyc+".aconc_sfc.ncf"
    if os.path.exists(check_file1):
        comout1=comout
    elif os.path.exists(check_file2):
        comout1=usrout
    else:
        flag_find_cyc=False
        print("Can not find "+check_file1)
        print("Can not find "+check_file2)
        break
    for ivar in range(0,num_var):
        if var[ivar] == "o3":
            check_file1=comout+"/cs."+sdate.strftime(YMD_date_format)+"/"+bcfilehdr_o3+".corrected."+sdate.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
            check_file2=usrout+"/cs."+sdate.strftime(YMD_date_format)+"/"+bcfilehdr_o3+".corrected."+sdate.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
            check_file_bias=biasdir+"/"+bcfilehdr_o3+".corrected."+sdate.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
        if  var[ivar] == "pm25":
            check_file1=comout+"/cs."+sdate.strftime(YMD_date_format)+"/"+bcfilehdr_pm25+".corrected."+sdate.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
            check_file2=usrout+"/cs."+sdate.strftime(YMD_date_format)+"/"+bcfilehdr_pm25+".corrected."+sdate.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
            check_file_bias=biasdir+"/"+bcfilehdr_pm25+".corrected."+sdate.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
        if os.path.exists(check_file1):
            comout2=comout
        elif os.path.exists(check_file2):
            comout2=usrout
        elif os.path.exists(check_file_bias):
            comout2=biasdir
            flag_biasdir=True
        else:
            flag_find_cyc=False
            print("Can not find "+check_file1)
            print("Can not find "+check_file2)
            print("Can not find "+check_bias)
            break
    if flag_find_cyc:
        flag_find_idir=True
        break
if flag_find_idir:
    print("comout1 set to "+comout1)
    print("comout2 set to "+comout2)
else:
    sys.exit()

## No bias correction fo AK and HI, thus no difference for Ak and HI
flag_ak = False
flag_hi = False

figout="/lfs/h2/emc/stmp/"+user

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
    iplot = [    0, 0,   1,      1,       1,      1,      1,      1,      1,      1,      0,      0,      1,      0,      0, 0 ]
else:
    iplot = [      1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1 ]
num_reg=len(iplot)

if not flag_ak and iplot[num_reg-3] == 1:
    iplot[num_reg-3] = 0
if not flag_hi and iplot[num_reg-2] == 1:
    iplot[num_reg-2] = 0
print("iplot length = "+str(num_reg))

date=sdate
while date <= edate:
    for cyc in cycle:
        msg=datetime.datetime.now()
        print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        s1_title=title_id+" "+date.strftime(YMD_date_format)+" "+cyc
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[1:3]))

        metfilein=metout1+"/cs."+grdcro2d_date+"/aqm."+cyc+".grdcro2d.ncf"
        if os.path.exists(metfilein):
            print(metfilein+" exists")
            model_data = netcdf.Dataset(metfilein)
            cs_lat = model_data.variables['LAT'][0,0,:,:]
            cs_lon = model_data.variables['LON'][0,0,:,:]
            model_data.close()
        else:
            print("Can not find "+metfilein)

        aqmfilein=comout1+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".aconc_sfc.ncf"
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm = netcdf.Dataset(aqmfilein)
            cs_var = cs_aqm.variables['TFLAG'][:,0,:]
            nstep=len(cs_var)
            for ivar in range(0,num_var):
                if var[ivar] == "o3":
                    o3_cs1 = cs_aqm.variables['O3'][:,0,:,:]*1000.
                elif var[ivar] == "pm25":
                    pm_cs1 = cs_aqm.variables['PM25_TOT'][:,0,:,:]
            cs_aqm.close()
        
        ##
        ## Read ozone bias correction
        ##
        if flag_biasdir:
            model_filein=comout2+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
        else:
            model_filein=comout2+"/cs."+date.strftime(YMD_date_format)+"/ozone.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
        if os.path.exists(model_filein):
            print(model_filein+" exists")
            model_data = netcdf.Dataset(model_filein)
            o3_cs2  = model_data.variables['O3'][:,0,:,:] * 1000.
            model_data.close()
        else:
            print("Can not find "+model_filein)
            sys.exit()

        ##
        ## Read ozone bias correction
        ##
        if flag_biasdir:
            model_filein=comout2+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
        else:
            model_filein=comout2+"/cs."+date.strftime(YMD_date_format)+"/pm2.5.corrected."+date.strftime(YMD_date_format)+"."+cyc[1:4]+".nc"
        if os.path.exists(model_filein):
            print(model_filein+" exists")
            model_data = netcdf.Dataset(model_filein)
            pm_cs2 = model_data.variables['pm25'][:,0,:,:]
            model_data.close()
        else:
            print("Can not find "+model_filein)
            sys.exit()

        for ivar in range(0,num_var):
            msg=datetime.datetime.now()
            print("Start processing "+var[ivar])
            figdir = figout+"/aqm"+"_"+envir+"bc-"+envir+"_"+date.strftime(YMD_date_format)+"_"+var[ivar]+"_"+cyc+"_diff"
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("working on "+date.strftime(YMD_date_format)+" "+cyc+" "+var[ivar])
            if var[ivar] == "o3":
                s3_title="Ozone sfc_conc (ppbV)"
                scale=1000.
                clevs = [ -60., -40., -20., -10., -5., -1., -0.05, 0.05, 1., 5., 10., 20., 40., 60. ]
            elif var[ivar] == "pm25":
                s3_title="PM25 sfc_conc ($\u03bcg/m^3$)"
                scale=1.
                clevs = [ -60., -40., -20., -10., -5., -1., -0.05, 0.05, 1., 5., 10., 20., 40., 60. ]
            ## cmap = plt.get_cmap('coolwarm')
            cmap = mpl.colors.ListedColormap([
                   (0.0000,0.0000,0.7843), (0.0000,0.0000,1.0000), (0.3137,0.3137,1.0000), (0.4706,0.4706,1.0000),
                   (0.5882,0.5882,1.0000), (0.8627,0.8627,1.0000), (1.0000,1.0000,1.0000), (1.0000,0.8627,0.8627),
                   (1.0000,0.5882,0.5882), (1.0000,0.4706,0.4706), (0.9804,0.3137,0.3137), (0.9804,0.2353,0.2353),
                   (0.7843,0.0000,0.0000)
                   ])
            cmap.set_over((0.5882,0.0000,0.0000))
            cmap.set_under((0.0000,0.0000,0.5882))
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
                if var[ivar] == "o3":
                    val1 = o3_cs1[n,:,:]
                    val2 = o3_cs2[n,:,:]
                    diff = []
                    for x, y in zip(val2, val1):
                        diff.append(x-y)
                    pvar_cs= diff 
                    if flag_ak:
                        val1 = o3_ak1[n,:,:]
                        val2 = o3_ak2[n,:,:]
                        diff = []
                        for x, y in zip(val2, val1):
                            diff.append(x-y)
                        pvar_ak= diff
                    if flag_hi:
                        val1 = o3_hi1[n,:,:]
                        val2 = o3_hi2[n,:,:]
                        diff = []
                        for x, y in zip(val2, val1):
                            diff.append(x-y)
                        pvar_hi= diff
                elif var[ivar] == "pm25":
                    val1 = pm_cs1[n,:,:]
                    val2 = pm_cs2[n,:,:]
                    diff = []
                    for x, y in zip(val2, val1):
                        diff.append(x-y)
                    pvar_cs= diff
                    if flag_ak:
                        val1 = pm_ak1[n,:,:]
                        val2 = pm_ak2[n,:,:]
                        diff = []
                        for x, y in zip(val2, val1):
                            diff.append(x-y)
                        pvar_ak= diff
                    if flag_hi:
                        val1 = pm_hi1[n,:,:]
                        val2 = pm_hi2[n,:,:]
                        diff = []
                        for x, y in zip(val2, val1):
                            diff.append(x-y)
                        pvar_hi= diff
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
                        if figarea == "ak" and flag_ak:
                            cf1 = ax.contourf(
                                     ak_lon, ak_lat, pvar_ak,
                                     levels=clevs, cmap=cmap, norm=norm, extend='both',
                                     transform=ccrs.PlateCarree() )
                        elif figarea == "hi" and flag_hi:
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
                                if flag_ak:
                                    ax.contourf(
                                         ak_lon, ak_lat, pvar_ak,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                                if flag_hi:
                                    ax.contourf(
                                         hi_lon, hi_lat, pvar_hi,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                        ax.set_title(title)
                        ## cb2.set_label('Discrete intervals, some other units')
                        fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,format=cbar_num_format)
                        ## fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,shrink=1.0,format=cbar_num_format)
                        savefig_name = figdir+"/aqm."+figarea+"."+fig_id+"."+date.strftime(YMD_date_format)+"."+cyc+"."+str(format(nout,'02d'))+"."+var[ivar]+".k1.png"
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
