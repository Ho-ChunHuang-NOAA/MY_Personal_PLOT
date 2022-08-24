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
    print("# arguments ="+str(len(sys.argv)))
    print("you must set 4 arguments as model[prod|para|...] cycle[06|12|all]  start_date end_date")
    sys.exit()
else:
    envir = sys.argv[1]
    sel_cyc = sys.argv[2]
    start_date = sys.argv[3]
    end_date = sys.argv[4]

if envir.lower() == "para":
    fig_exp="ncopara"
else:
    fig_exp=envir.lower()

script_dir=os.getcwd()
print("Script directory is "+script_dir)

user=os.environ['USER']

stmp_dir="/lfs/h2/emc/stmp/"+user
if not os.path.exists(stmp_dir):
    os.mkdir(stmp_dir)

ptmp_dir="/lfs/h2/emc/ptmp/"+user
if not os.path.exists(ptmp_dir):
    os.mkdir(ptmp_dir)

log_dir=ptmp_dir+"/batch_logs"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

working_dir=stmp_dir+"/aqm_plot_working"
if os.path.exists(working_dir):
    os.chdir(working_dir)
else:
    os.makedirs(working_dir)
    os.chdir(working_dir)

msg_file=working_dir+"/devmachine"
subprocess.call(["cat /etc/cluster_name > "+msg_file], shell=True)
if os.path.isfile(msg_file):
    with open(msg_file, 'r') as sh:
        line=sh.readline()
        dev_machine=line.rstrip()
        print("currently on "+dev_machine)
        sh.close()

msg_file=working_dir+"/prodmachine"
subprocess.call(["cat /lfs/h1/ops/prod/config/prodmachinefile > "+msg_file], shell=True)
if os.path.isfile(msg_file):
    with open(msg_file, 'r') as sh:
        prod_machine="99"
        line=sh.readline()
        line1=line.rstrip()
        abc=line1.split(':')
        if abc[0] == 'primary':
            prod_machine=abc[1]
        else:
            line=sh.readline()
            line1=line.rstrip()
            abc=line1.split(':')
            if abc[0] == 'primary':
                prod_machine=abc[1]
        print(prod_machine)
        sh.close()

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

if envir == "prod":
    var=[ "pmcoarse_soil" ]
else:
    var=[ "pmcoarse_soil" ]
figid=[ "pmc_soil" ]
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

msg=datetime.datetime.now()
msg=msg - date_inc
grdcro2d_date=msg.strftime("%Y%m%d")
##
## Current operational CMAQ does include runs for AK and HI domain
## Current EMC development CMAQ does not include runs for AK and HI domain
##
aqm_ver="v6.1"
find_dir=[
          "/lfs/h1/ops/"+envir+"/com/aqm/"+aqm_ver,
          "/lfs/h2/emc/ptmp/"+user+"/com/aqm/"+envir+".met",
          "/lfs/h2/emc/physics/noscrub/"+user+"/com/aqm/"+envir,
          "/lfs/h2/emc/ptmp/"+user+"/com/aqm/"+envir
         ]
metout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver

figout=stmp_dir

flag_proj="LambertConf"
##mksize= [     16,     25,      36,      36,     49,     49,     49,     49,     64,     64,    100,    121,     25, 121 ]
mksize= [     16,      16,      25,     25,     36,     36,     36,     36,     49,     49,    100,    121,     25, 121 ]
if flag_proj == "LambertConf":
    regname = [   "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",   "ak",   "hi",  "can", "lis" ] 
    rlon0 = [ -161.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0, -166.0, -161.5, -141.0, -75.0 ]
    rlon1 = [  -73.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0, -132.0, -153.1,  -60.0, -71.0 ]
    rlat0 = [   14.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   53.2,   17.8,   38.0, 40.2 ]
    rlat1 = [   72.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   71.2,   23.1,   70.0, 41.8 ]
else:
    regname = [   "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",   "ak",   "hi",  "can", "lis" ] 
    rlon0 = [ -175.0, -124.0,  -100.0, -128.0,  -82.0, -125.0,  -95.0, -125.0, -105.0, -105.0, -170.0, -161.0, -141.0, -75.0 ]
    rlon1 = [  -55.0,  -70.0,   -65.0,  -90.0,  -67.0, -103.0,  -79.0, -105.0,  -85.0,  -85.0, -130.0, -154.0,  -60.0, -71.0 ]
    rlat0 = [    0.0,   22.0,    22.0,   24.5,   37.0,   38.0,   24.0,   30.0,   38.0,   24.0,   52.0,   18.0,   38.0, 40.2 ]
    rlat1 = [   70.0,   51.0,    50.0,   54.5,   48.0,   52.0,   38.0,   45.0,   52.0,   40.0,   72.0,   23.0,   70.0, 41.8 ]
xsize = [     10,     10,       8,      8,      8,      8,      8,      8,      8,      8,      8,      8,     10, 10 ]
ysize = [      8,      8,       8,      8,      8,      8,      8,      8,      8,      8,      8,      8,      8,  5 ]
if 1 == 2:
    iplot = [      1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1, 1 ]
else:
    iplot = [      0,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0, 0 ]
num_reg=len(iplot)

date=sdate
while date <= edate:
    flag_find_idir="no"
    for idir in find_dir:
        comout=idir
        print("check "+idir)
        flag_find_cyc="yes"
        for cyc in cycle:
            if envir == "prod":
                check_file="aqm."+cyc+".dustemis.ncf"
            else:
                check_file="aqm."+cyc+".dustemis.d1.ncf"
            aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/"+check_file
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
            else:
                flag_find_cyc="no"
                print("Can not find "+aqmfilein)
                break
        if flag_find_cyc == "yes":
            flag_find_idir="yes"
            break
    if flag_find_idir == "yes":
        print("comout set to "+comout)
    else:
        date = date + date_inc
        continue
    
    if envir == "prod" or envir == "para6x" or envir == "para6b":
        flag_ak = "yes"
        for cyc in cycle:
            if envir == "prod":
                check_file="aqm."+cyc+".dustemis.ncf"
            else:
                check_file="aqm."+cyc+".dustemis.d1.ncf"
            aqmfilein=comout+"/ak."+date.strftime(YMD_date_format)+"/"+check_file
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
            else:
                flag_ak="no"
                print("Can not find "+aqmfilein)
                break
        flag_hi = "yes"
        for cyc in cycle:
            if envir == "prod":
                check_file="aqm."+cyc+".dustemis.ncf"
            else:
                check_file="aqm."+cyc+".dustemis.d1.ncf"
            aqmfilein=comout+"/hi."+date.strftime(YMD_date_format)+"/"+check_file
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
            else:
                flag_hi="no"
                print("Can not find "+aqmfilein)
                break
    else:
        flag_ak = "no"
        flag_hi = "no"

    if flag_ak == "no" and iplot[num_reg-3] == 1:
        iplot[num_reg-3] = 0
    if flag_hi == "no" and iplot[num_reg-2] == 1:
        iplot[num_reg-2] = 0
    print("iplot length = "+str(num_reg))

    for cyc in cycle:
        msg=datetime.datetime.now()
        print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        s1_title=fig_exp.upper()+" "+date.strftime(YMD_date_format)+" "+cyc
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[1:3]))

        metfilein=metout+"/cs."+grdcro2d_date+"/aqm."+cyc+".grdcro2d.ncf"
        if os.path.exists(metfilein):
            print(metfilein+" exists")
            model_data = netcdf.Dataset(metfilein)
            mdl_lat = model_data.variables['LAT'][0,0,:,:]
            mdl_lon = model_data.variables['LON'][0,0,:,:]
            model_data.close()
        else:
            print("Can not find "+metfilein)

        if envir == "prod":
            aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".dustemis.ncf"
        else:
            aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".dustemis.d1.ncf"
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm = netcdf.Dataset(aqmfilein)
            cs_var = cs_aqm.variables['TFLAG'][:,0,:]
            nstep=len(cs_var)
        else:
            print("Can not find "+aqmfilein)

        flag_met3d="yes"
        met3dfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro3d.ncf"
        if os.path.exists(met3dfilein):
            print(met3dfilein+" exists")
            cs_3d_met = netcdf.Dataset(met3dfilein)
            cs_fhgt = cs_3d_met.variables['ZF'][:,0,:,:]
            cs_3d_met.close()
        else:
            print("Can not find "+met3dfilein)
            met3dfilein=comout+"/cs."+date.strftime(YMD_date_format)+".met/aqm."+cyc+".metcro3d.ncf"
            if os.path.exists(met3dfilein):
                print(met3dfilein+" exists")
                cs_3d_met = netcdf.Dataset(met3dfilein)
                cs_fhgt = cs_3d_met.variables['ZF'][:,0,:,:]
                cs_3d_met.close()
            else:
                print("Can not find "+met3dfilein)
                met3dfilein="/lfs/h2/emc/physics/noscrub/"+user+"/com/aqm/"+envir+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".metcro3d.ncf"
                if os.path.exists(met3dfilein):
                    print(met3dfilein+" exists")
                    cs_3d_met = netcdf.Dataset(met3dfilein)
                    cs_fhgt = cs_3d_met.variables['ZF'][:,0,:,:]
                    cs_3d_met.close()
                else:
                    print("Can not find "+met3dfilein)
                    print("no METCRO3D file, use genetic PM_SOIL dust emission")
                    flag_met3d="no"

        if flag_ak == "yes":
            metfilein=metout+"/ak."+grdcro2d_date+"/aqm."+cyc+".grdcro2d.ncf"
            if os.path.exists(metfilein):
                print(metfilein+" exists")
                model_data = netcdf.Dataset(metfilein)
                ak_lat = model_data.variables['LAT'][0,0,:,:]
                ak_lon = model_data.variables['LON'][0,0,:,:]
                model_data.close()
            else:
                print("Can not find "+metfilein)
                flag_ak = "no"
                iplot[num_reg-3] = 0

            if envir == "prod":
                aqmfilein=comout+"/ak."+date.strftime(YMD_date_format)+"/aqm."+cyc+".dustemis.ncf"
            else:
                aqmfilein=comout+"/ak."+date.strftime(YMD_date_format)+"/aqm."+cyc+".dustemis.d1.ncf"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                ak_aqm = netcdf.Dataset(aqmfilein)
                ak_var = ak_aqm.variables['TFLAG'][:,0,:]
                nstep_ak=len(ak_var)
                if nstep_ak != nstep:
                    print("time step of AK domain "+str(nstep_ak)+" is different from CONUS domain "+str(nstep))
                    sys.exit()
            else:
                print("Can not find "+aqmfilein)
                flag_ak = "no"
                iplot[num_reg-3] = 0
    
        if flag_hi == "yes":
            metfilein=metout+"/hi."+grdcro2d_date+"/aqm."+cyc+".grdcro2d.ncf"
            if os.path.exists(metfilein):
                print(metfilein+" exists")
                model_data = netcdf.Dataset(metfilein)
                hi_lat = model_data.variables['LAT'][0,0,:,:]
                hi_lon = model_data.variables['LON'][0,0,:,:]
                model_data.close()
            else:
                print("Can not find "+metfilein)
                flag_hi = "no"
                iplot[num_reg-2] = 0
    
            if envir == "prod":
                aqmfilein=comout+"/hi."+date.strftime(YMD_date_format)+"/aqm."+cyc+".dustemis.ncf"
            else:
                aqmfilein=comout+"/hi."+date.strftime(YMD_date_format)+"/aqm."+cyc+".dustemis.d1.ncf"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                hi_aqm = netcdf.Dataset(aqmfilein)
                hi_var = hi_aqm.variables['TFLAG'][:,0,:]
                nstep_hi=len(hi_var)
                nstep_hi= nstep
                if nstep_hi != nstep:
                    print("time step of HI domain "+str(nstep_hi)+" is different from CONUS domain "+str(nstep))
                    sys.exit()
            else:
                print("Can not find "+aqmfilein)
                flag_hi = "no"
                iplot[num_reg-2] = 0
        for ivar in range(0,num_var):
            plot_var=var[ivar]
            msg=datetime.datetime.now()
            print("Start processing "+plot_var)
            figdir = figout+"/aqm"+"_"+envir+"_"+date.strftime(YMD_date_format)+"_"+plot_var+"_"+cyc+"_dust_loc"
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("working on "+date.strftime(YMD_date_format)+" "+cyc+" "+plot_var)
            read_var=plot_var.upper()
            dust_cs = cs_aqm.variables[read_var][:,0,:,:]
            nrow_cs=dust_cs.shape[1]
            ncol_cs=dust_cs.shape[2]
            print('variable %s dimension is [i,j] = [ %d , %d ]' % (read_var, ncol_cs, nrow_cs))
            if flag_ak == "yes":
                dust_ak = ak_aqm.variables[read_var][:,0,:,:]
            if flag_hi == "yes":
                dust_hi = hi_aqm.variables[read_var][:,0,:,:]
            if plot_var == "pm25_oc":
                s3_title=plot_var.upper()+" sfc_conc ($\u03bcg/m^3$)"
                scale=1.
                clevs = [ 3., 6., 9., 12., 15., 35., 55., 75., 100., 125., 150., 250., 300., 400., 500., 600., 750. ]
                cmap = mpl.colors.ListedColormap([
                      (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                      (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000),
                      (1.0000,0.3840,0.3840), (1.0000,0.0000,0.0000), (0.8000,0.0000,0.0000), (0.7020,0.0000,0.0000),
                      (0.6120,0.5100,0.8120), (0.5180,0.3880,0.7650), (0.4310,0.2780,0.7250),(0.2980,0.1920,0.5020),
                      (0.4706,0.4706,0.4706), (0.7843,0.7843,0.7843)
                      ])
                cmap.set_under((0.8627,0.8627,1.0000))
                cmap.set_over((0.9412,0.9412,0.9412))
            elif plot_var == "anumk" :
                ## s3_title=plot_var.upper()+" sfc_conc ($\u03bcg/m^3$)"
                s3_title=plot_var.upper()+" coarse mode number ($*1x10^{-12} s^{-1}$)"
                scale=1.0E12
                clevs = [ 5., 10., 15., 35., 55., 75., 100., 125., 155., 205., 255., 305., 355., 425., 500., 604., 750. ]
                cmap = mpl.colors.ListedColormap([
                      (0.0000,0.6390,0.0000), (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                      (1.0000,1.0000,0.8784), (1.0000,1.0000,0.6000), (1.0000,1.0000,0.0000), (1.0000,0.8745,0.0000),
                      (1.0000,0.6471,0.0000), (0.9412,0.5098,0.1569),
                      (1.0000,0.0000,0.0000), (0.7020,0.0000,0.0000),
                      (0.6120,0.5100,0.8120), (0.4310,0.2780,0.7250),(0.2980,0.1920,0.5020),
                      (0.7843,0.7843,0.7843)
                      ])
                cmap.set_under((0.8627,0.8627,1.0000))
                cmap.set_over((0.9412,0.9412,0.9412))
            elif plot_var == "pmcoarse_soil" :
                ## s3_title=plot_var.upper()+" sfc_conc ($\u03bcg/m^3$)"
                s3_title=plot_var.upper()+" sfc_emis ($kg/hr$)"
                scale=1.
                clevs = [ 5., 10., 15., 35., 55., 75., 100., 125., 155., 205., 255., 305., 355., 425., 500., 604., 750. ]
                cmap = mpl.colors.ListedColormap([
                      (0.0000,0.6390,0.0000), (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                      (1.0000,1.0000,0.8784), (1.0000,1.0000,0.6000), (1.0000,1.0000,0.0000), (1.0000,0.8745,0.0000),
                      (1.0000,0.6471,0.0000), (0.9412,0.5098,0.1569),
                      (1.0000,0.0000,0.0000), (0.7020,0.0000,0.0000),
                      (0.6120,0.5100,0.8120), (0.4310,0.2780,0.7250),(0.2980,0.1920,0.5020),
                      (0.7843,0.7843,0.7843)
                      ])
                cmap.set_under((0.8627,0.8627,1.0000))
                cmap.set_over((0.9412,0.9412,0.9412))
            else:
                s3_title=plot_var.upper()+" sfc_conc ($\u03bcg/m^3$)"
                scale=1.
                clevs = [ 3., 6., 9., 12., 15., 35., 55., 75., 100. ]
                cmap = mpl.colors.ListedColormap([
                      (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                      (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000),
                      (1.0000,0.3840,0.3840), (1.0000,0.0000,0.0000)
                      ])
                cmap.set_under((0.8627,0.8627,1.0000))
                cmap.set_over((0.8000,0.0000,0.0000))
            var_cs = dust_cs*scale
            if flag_ak == "yes":
                var_ak = dust_ak*scale
            if flag_hi == "yes":
                var_hi = dust_hi*scale
            norm = mpl.colors.BoundaryNorm(boundaries=clevs, ncolors=cmap.N)
            gs = gridspec.GridSpec(1,1)
            fcst_hour=fcst_ini
            ## for n in range(nstep-1,nstep):
            ## dx=12 km=1.2E+04 m
            area=1.44E+08
            nday=nstep/24
            print('total number of day = %d' % (nday))
            plt.figure(figsize=(12, 6))
            for nd in range(0,int(nday)):
                nbeg=nd*24
                nend=(nd+1)*24
                plotrow=[]
                plotcol=[]
                title=date.strftime(YMD_date_format)+" "+envir.upper()+" run dust emission location - day "+str(nd+1)
                for n in range(nbeg,nend):
                    ## nout=n+1
                    ## fcst_hour=fcst_hour+hour_inc
                    ## if nstep > 99:
                    ##     s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+str(format(nout,'03d'))
                    ## else:
                    ##     s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+str(format(nout,'02d'))
                    ## title=s1_title+"\n"+s2_title+" "+s3_title
                    conc_cs = var_cs[n,:,:]
                    if flag_met3d == "yes":
                        zf_cs = cs_fhgt[n,:,:]
                        pvar_cs=[]
                        for j in range(0,nrow_cs):
                            col=[]
                            for i in range(0,ncol_cs):
                                sum=3.6*area*zf_cs[j,i]*conc_cs[j,i]
                                col.append(sum)
                            pvar_cs.append(col)
                    else:
                        pvar_cs = conc_cs
                    xnonzero=[]
                    xnonzero=np.nonzero(pvar_cs)
                    ## print(xnonzero)
                    nrow=xnonzero[0]
                    ncol=xnonzero[1]
                    nx=len(nrow)
                    ## print('number of dust emission at step %d is %d' % (n, nx))
                    nplot=len(plotrow)
                    for ii in range(0,nx):
                        find_new_dust=1
                        for ij in range(0,nplot):
                            if plotrow[ij] == nrow[ii] and plotcol[ij] == ncol[ii]:
                               find_new_dust=0
                               break
                        if find_new_dust == 1:
                            ## print('%s %d %d' % ("found new dust loc", nrow[ii], ncol[ii]))
                            plotrow.append(nrow[ii])
                            plotcol.append(ncol[ii])
                            ## nplotnow=len(plotrow)
                            ## print('current number of dust is %d'% (nplotnow))
                    num_pts=len(plotrow)
                    ## print('time step %d # of dust is %d' % (n,num_pts))
                num_pts=len(plotrow)
                print('Day %d # of dust is %d' % (int(nd),num_pts))
                if flag_ak == "yes":
                    pvar_ak = var_ak[n,:,:]
                if flag_hi == "yes":
                    pvar_hi = var_hi[n,:,:]
                ## turn (i,j) to (lon,lat)
                cs_lat=[]
                cs_lon=[]
                for i in range(0,num_pts):
                    cs_lat.append(mdl_lat[plotrow[i],plotcol[i]])
                    cs_lon.append(mdl_lon[plotrow[i],plotcol[i]])
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
                        states_provinces = cfeature.NaturalEarthFeature(
                             category='cultural',
                             name='admin_1_states_provinces_lines',
                             scale='50m',
                             facecolor='none')
                        rivers_50m = cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '50m')
                        ax.add_feature(states_provinces, facecolor='none', edgecolor='gray')
                        ## ax.coastlines('50m')
                        ax.add_feature(cfeature.BORDERS, facecolor='none', linestyle=':')
                        ax.add_feature(cfeature.OCEAN)
                        ax.add_feature(cfeature.LAND, edgecolor='black')
                        ax.add_feature(cfeature.LAKES, facecolor='None', edgecolor='black', alpha=0.5)
                        ## ax.add_feature(cfeature.COASTLINE)
                        ## ax.add_feature(rivers_50m, facecolor='None', edgecolor='b')
                        ## ax.add_feature(cfeature.RIVERS)
                        ax.set_title(title)
                        for x in range(0,num_pts):
                          ax.plot(cs_lon[x], cs_lat[x], 'ro', markersize=2, transform=ccrs.PlateCarree())
                        ##ax.text(-117, 33, 'San Diego', transform=ccrs.Geodetic())
                        savefig_name=figdir+"/dustemis."+figarea+"."+fig_exp+"."+date.strftime(YMD_date_format)+"."+cyc+".location.day"+str(nd+1)+".k1.png"
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
            print("End   processing "+plot_var)
            print("FIG DIR = "+figdir)
        cs_aqm.close()
        if flag_ak == "yes":
            ak_aqm.close()
        if flag_hi == "yes":
            hi_aqm.close()
        msg=datetime.datetime.now()
        print("End   processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc
