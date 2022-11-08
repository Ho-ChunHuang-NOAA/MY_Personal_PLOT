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
else:
    fig_exp=envir.lower()

script_dir=os.getcwd()
print("Script directory is "+script_dir)

user=os.environ['USER']
wgrib2=os.environ['WGRIB2']
if wgrib2 == "":
    print("iNo definition of WGRIB2 can be found, please load module wgrib2/2.0.8")
    sys.exit()
## print(wgrib2)
grid148="148"
grid227="227"
grid198="198"
grid139="139"
grid196="196"
grid793="793"

stmp_dir="/lfs/h2/emc/stmp/"+user
if not os.path.exists(stmp_dir):
    os.mkdir(stmp_dir)

ptmp_dir="/lfs/h2/emc/ptmp/"+user
if not os.path.exists(ptmp_dir):
    os.mkdir(ptmp_dir)

log_dir=ptmp_dir+"/batch_logs"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

working_root=stmp_dir+"/aqm_plot_working_max_ave_"+envir+"_bc"
if os.path.exists(working_root):
    os.chdir(working_root)
else:
    os.makedirs(working_root)
    os.chdir(working_root)

msg_file=working_root+"/devmachine"
subprocess.call(["cat /etc/cluster_name > "+msg_file], shell=True)
if os.path.isfile(msg_file):
    with open(msg_file, 'r') as sh:
        line=sh.readline()
        dev_machine=line.rstrip()
        print("currently on "+dev_machine)
        sh.close()

msg_file=working_root+"/prodmachine"
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
Month_date_format = "%B"
D_date_format = "%d"
H_date_format = "%H"
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

var=[ "ozmax8", "ozmax1", "pmave24", "pmmax1" ]
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
          "/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/verification/aqm/"+envir,
          "/lfs/h1/ops/"+envir+"/com/aqm/"+aqm_ver,
          "/lfs/h2/emc/ptmp/"+os.environ['USER']+"/com/aqm/"+envir,
          "/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+envir
         ]
metout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver

figout=stmp_dir

##
## new area need to be added ahead of ak.  The last three areas need to be fixed as "ak",   "hi",  "can"
## this is due to the code below remove plotting of ak and hi if no ak and hi input files ash been found
##
flag_proj="LambertConf"
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
    iplot = [    1, 1,   1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      0,      0, 1 ]
else:
    iplot = [    0,  0, 1,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0, 0 ]
num_reg=len(iplot)

date=sdate
while date <= edate:
    flag_find_idir="no"
    for idir in find_dir:
        comout=idir
        print("check "+idir)
        flag_find_cyc="yes"
        for cyc in cycle:
            for ivar in range(0,num_var):
                if var[ivar] == "ozmax8":
                    fileid="max_8hr_o3"
                elif var[ivar] == "ozmax1":
                    fileid="max_1hr_o3"
                elif var[ivar] == "pmave24":
                    fileid="ave_24hr_pm25"
                elif var[ivar] == "pmmax1":
                    fileid="max_1hr_pm25"
                check_file="aqm."+cyc+"."+fileid+"_bc."+grid148+".grib2"
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
            break

    if flag_find_idir == "no":
        print("Can not define comout, program stop")
        sys.exit()

    
    # No bias_correction been applied to AK and HI domain
    flag_ak = "no"
    flag_hi = "no"

    for cyc in cycle:
        working_dir=working_root+"/"+date.strftime(YMD_date_format)+cyc
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)

        s1_title="CMAQ "+fig_exp.upper()+"_BC "+date.strftime(YMD_date_format)+" "+cyc
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[1:3]))
        for ivar in range(0,num_var):
            if var[ivar] == "ozmax8":
                fileid="max_8hr_o3"
                varid="OZMAX8_1sigmalevel"
            elif var[ivar] == "ozmax1":
                fileid="max_1hr_o3"
                varid="OZMAX1_1sigmalevel"
            elif var[ivar] == "pmave24":
                fileid="ave_24hr_pm25"
                varid="PMTF_1sigmalevel"
            elif var[ivar] == "pmmax1":
                fileid="max_1hr_pm25"
                varid="PDMAX1_1sigmalevel"
            msg=datetime.datetime.now()
            print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))

            file_hdr="aqm."+cyc+"."+fileid+"_bc."+grid148
            aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                outfile=working_dir+"/"+file_hdr+".nc"
                subprocess.call([wgrib2+' -netcdf '+outfile+' '+aqmfilein], shell=True)
                aqmfilein=outfile
                cs_aqm = netcdf.Dataset(aqmfilein)
                cs_lat = cs_aqm.variables['latitude'][:,:]
                cs_lon = cs_aqm.variables['longitude'][:,:]
                cs_var = cs_aqm.variables['time'][:]
                nstep=len(cs_var)
                ozpm_cs = cs_aqm.variables[varid][:,:,:]
                cs_aqm.close()
            else:
                print("Can not find "+aqmfilein)
                sys.exit()
    
            if flag_ak == "yes":
                file_hdr="aqm."+cyc+"."+fileid+"_bc."+grid198
                aqmfilein=comout+"/ak."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
                if os.path.exists(aqmfilein):
                    print(aqmfilein+" exists")
                    outfile=working_dir+"/"+file_hdr+".nc"
                    subprocess.call([wgrib2+' -netcdf '+outfile+' '+aqmfilein], shell=True)
                    aqmfilein=outfile
                    ak_aqm = netcdf.Dataset(aqmfilein)
                    ak_lat = ak_aqm.variables['latitude'][:,:]
                    ak_lon = ak_aqm.variables['longitude'][:,:]
                    ak_var = ak_aqm.variables['time'][:]
                    nstep_ak=len(ak_var)
                    if nstep_ak != nstep:
                        print("time step of AK domain "+str(nstep_ak)+" is different from CONUS domain "+str(nstep))
                        sys.exit()
                    ozpm_ak = ak_aqm.variables[varid][:,:,:]
                    ak_aqm.close()
                else:
                    print("Can not find "+aqmfilein)
                    flag_ak = "no"
                    iplot[num_reg-3] = 0
        
            if flag_hi == "yes":
                file_hdr="aqm."+cyc+"."+fileid+"_bc."+grid139
                aqmfilein=comout+"/hi."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
                if os.path.exists(aqmfilein):
                    print(aqmfilein+" exists")
                    outfile=working_dir+"/"+file_hdr+".nc"
                    subprocess.call([wgrib2+' -netcdf '+outfile+' '+aqmfilein], shell=True)
                    aqmfilein=outfile
                    hi_aqm = netcdf.Dataset(aqmfilein)
                    hi_lat = hi_aqm.variables['latitude'][:,:]
                    hi_lon = hi_aqm.variables['longitude'][:,:]
                    hi_var = hi_aqm.variables['time'][:]
                    nstep_hi=len(hi_var)
                    if nstep_hi != nstep:
                        print("time step of HI domain "+str(nstep_hi)+" is different from CONUS domain "+str(nstep))
                        sys.exit()
                    ozpm_hi = hi_aqm.variables[varid][:,:,:]
                    hi_aqm.close()
                else:
                    print("Can not find "+aqmfilein)
                    flag_hi = "no"
                    iplot[num_reg-2] = 0
    
            if flag_ak == "no" and iplot[num_reg-3] == 1:
                iplot[num_reg-3] = 0
            if flag_hi == "no" and iplot[num_reg-2] == 1:
                iplot[num_reg-2] = 0
            print("iplot length = "+str(num_reg))

            msg=datetime.datetime.now()
            print("Start processing "+var[ivar])
            jobid="aqm"+"_"+envir+"_bc_"+date.strftime(YMD_date_format)+"_"+var[ivar]+"_"+cyc
            figdir = figout+"/"+jobid
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("figdir = "+figdir)
            print("working on "+date.strftime(YMD_date_format)+" "+cyc+" "+var[ivar])
            if var[ivar] == "ozmax8" or var[ivar] == "ozmax1":
                ## s3_title="Max 8HR-AVG SFC Ozone CONC (ppbV)"
                s3_title=fileid+" (ppbV)"
                scale=1.
                clevs = [ 3., 6., 9., 12., 25., 35., 45., 55., 65., 70., 75., 85., 95., 105. ]
                var_cs=ozpm_cs*scale
                if flag_ak == "yes":
                    var_ak=ozpm_ak*scale
                if flag_hi == "yes":
                    var_hi=ozpm_hi*scale
                cmap = mpl.colors.ListedColormap([
                      (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000),
                      (0.0000,0.7490,1.0000), (0.0000,1.0000,1.0000),
                      (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                      (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000), (0.9412,0.5098,0.1569),
                      (1.0000,0.0000,0.0000), (0.7020,0.0000,0.0000)
                      ])
                cmap.set_under((0.8627,0.8627,1.0000))
                cmap.set_over((0.4310,0.2780,0.7250))
            elif var[ivar] == "pmave24" or var[ivar] == "pmmax1":
                ## s3_title="PM25 sfc_conc ($\u03bcg/m^3$)"
                s3_title=fileid+" ($\u03bcg/m^3$)"
                scale=1.
                clevs = [ 3., 6., 9., 12., 15., 35., 55., 75., 100., 125., 150., 250., 300., 400., 500., 600., 750. ]
                var_cs=ozpm_cs
                if flag_ak == "yes":
                    var_ak=ozpm_ak
                if flag_hi == "yes":
                    var_hi=ozpm_hi
                cmap = mpl.colors.ListedColormap([
                      (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                      (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000),
                      (1.0000,0.3840,0.3840), (1.0000,0.0000,0.0000), (0.8000,0.0000,0.0000), (0.7020,0.0000,0.0000),
                      (0.6120,0.5100,0.8120), (0.5180,0.3880,0.7650), (0.4310,0.2780,0.7250),(0.2980,0.1920,0.5020),
                      (0.4706,0.4706,0.4706), (0.7843,0.7843,0.7843)
                      ])
                cmap.set_under((0.8627,0.8627,1.0000))
                cmap.set_over((0.9412,0.9412,0.9412))
            elif var[ivar] == "pmave24_nonseason":
                ## s3_title="PM25 sfc_conc ($\u03bcg/m^3$)"
                s3_title=fig_var_name+" ($\u03bcg/m^3$)"
                scale=1.
                clevs = [ 0., 3., 6., 9., 12., 25., 35., 45., 55., 65., 75., 85., 95., 105. ]
                var_cs=ozpm_cs
                if flag_ak == "yes":
                    var_ak=ozpm_ak
                if flag_hi == "yes":
                    var_hi=ozpm_hi
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
                cmonth=fcst_hour.strftime(Month_date_format)[0:3]
                begdate="05Z"+fcst_hour.strftime(D_date_format)+cmonth.upper()+fcst_hour.strftime(Y_date_format)

                nout=n+1
                fcst_hour=fcst_hour+date_inc
                cmonth=fcst_hour.strftime(Month_date_format)[0:3]
                enddate="04Z"+fcst_hour.strftime(D_date_format)+cmonth.upper()+fcst_hour.strftime(Y_date_format)
                s2_title = begdate+"-"+enddate
                title=s1_title+"\n"+s2_title+" "+s3_title
                pvar_cs = var_cs[n,:,:]
                if flag_ak == "yes":
                    pvar_ak = var_ak[n,:,:]
                if flag_hi == "yes":
                    pvar_hi = var_hi[n,:,:]
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
                        fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,shrink=1.0,format=cbar_num_format)
                        savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"bc."+date.strftime(YMD_date_format)+"."+cyc+"."+fileid+".day"+str(format(nout,'01d'))+".k1.png"
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
