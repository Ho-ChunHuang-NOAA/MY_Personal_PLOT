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
    print("iNo definition of WGRIB2 can be found, please load module wgrib2/2.0.8")
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

py_code=sys.argv[0]
nfind=py_code.find("py")
if nfind == -1:
    workid=py_code
else:
    workid=py_code[0:nfind-1]
working_root=stmp_dir+"/"+envir+"_"+workid
if not os.path.exists(working_root):
    os.mkdir(working_root)

os.chdir(working_root)

msg_file=working_root+"/msg_"+start_date+"_"+sel_cyc
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
find_dir=[
          "/lfs/h1/ops/"+envir+"/com/aqm/"+aqm_ver,
          "/lfs/h2/emc/ptmp/"+os.environ['USER']+"/com/aqm/"+envir,
          "/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+envir,
          "/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/verification/aqm/"+envir
         ]
metout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver

figout=stmp_dir

##
## new area need to be added ahead of ak.  The last three areas need to be fixed as "ak",   "hi",  "can"
## this is due to the code below remove plotting of ak and hi if no ak and hi input files ash been found
##
flag_proj="LambertConf"
##
## marker size (s= in the scatter plot command) is the wxH. s=100 is the area of 10x10
## Thus increase and decrease by squrt(s) or using nxn wiht n from 1,....large integer
##
mksize= [ 121, 64, 64, 16,     36,      36,      36,     49,     49,     49,     49,     64,     64,    121,    100,    121,     36 ]
if flag_proj == "LambertConf":
    regname = [ "ctdeep", "Mckinney",  "aznw", "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
    rlon0 = [ -75., -125., -120., -165.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0,  -75.0, -166.0, -161.5, -141.0 ]
    rlon1 = [ -71., -110., -100., -70.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0,  -71.0, -132.0, -153.1, -60.0 ]
    rlat0 = [  40.4, 40., 30.0, 10.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   40.2,   53.2,   17.8,   38.0 ]
    rlat1 = [  42.2, 45., 40., 75.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   41.8,   71.2,   23.1,   70.0 ]
else:
    regname = [   "Mckinney",  "aznw", "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ] 
    rlon0 = [ -125., -120., -175.0, -124.0,  -100.0, -128.0,  -82.0, -125.0,  -95.0, -125.0, -105.0, -105.0,  -75.0, -170.0, -161.0, -141.0 ]
    rlon1 = [  -110., -100., -55.0,  -70.0,   -65.0,  -90.0,  -67.0, -103.0,  -79.0, -105.0,  -85.0,  -85.0,   -71.0, -130.0, -154.0,  -60.0 ]
    rlat0 = [    40., 30.0, 0.0,   22.0,    22.0,   24.5,   37.0,   38.0,   24.0,   30.0,   38.0,   24.0,   40.2,   52.0,   18.0,   38.0 ]
    rlat1 = [   45., 40., 70.0,   51.0,    50.0,   54.5,   48.0,   52.0,   38.0,   45.0,   52.0,   40.0,   41.8,   72.0,   23.0,   70.0 ]
xsize = [ 10, 10, 10, 10,     10,       8,      8,      8,      8,      8,      8,      8,      8,     10,      8,      8,     10 ]
ysize = [ 8,   5, 5, 8,      8,       8,      8,      8,      8,      8,      8,      8,      8,      5,      8,      8,     8 ]
if 1 == 1:
    iplot = [ 1, 0, 0,   1,      1,       1,      1,      1,      1,      1,      1,      0,      0,      1,      0,      0, 0 ]
else:
    iplot = [ 1, 1, 1,   1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1, 1 ]
num_reg=len(iplot)

date=sdate
while date <= edate:
    flag_find_idir=False
    for idir in find_dir:
        comout=idir
        print("check "+idir)
        flag_find_cyc=True
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
                check_file="aqm."+cyc+"."+fileid+"."+grid148+".grib2"
                aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/"+check_file
                if os.path.exists(aqmfilein):
                    print(aqmfilein+" exists")
                else:
                    flag_find_cyc=False
                    print("Can not find "+aqmfilein)
                    break
            if flag_find_cyc:
                flag_find_idir=True
                break
        if flag_find_idir:
            print("comout set to "+comout)
            break
        else:
            date = date + date_inc
            continue
    
    # NO Bias correction for AK and HI
    flag_ak = False
    flag_hi = False

    if not flag_ak and iplot[num_reg-3] == 1:
        iplot[num_reg-3] = 0
    if not flag_hi and iplot[num_reg-2] == 1:
        iplot[num_reg-2] = 0
    print("iplot length = "+str(num_reg))

    for cyc in cycle:
        working_dir=working_root+"/"+date.strftime(YMD_date_format)+cyc
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)

        s1_title="CMAQ "+fig_exp.upper()+"BC- "+fig_exp.upper()+" "+date.strftime(YMD_date_format)+" "+cyc
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
            fileidbc=fileid+"_bc"
            msg=datetime.datetime.now()
            print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))

            file_hdr="aqm."+cyc+"."+fileid+"."+grid148
            aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                outfile=working_dir+"/"+file_hdr+"."+date.strftime(YMD_date_format)+"."+cyc+".nc"
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

            file_hdr="aqm."+cyc+"."+fileidbc+"."+grid148
            aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/"+file_hdr+".grib2"
            if os.path.exists(aqmfilein):
                print(aqmfilein+" exists")
                outfile=working_dir+"/"+file_hdr+"."+date.strftime(YMD_date_format)+"."+cyc+".nc"
                subprocess.call([wgrib2+' -netcdf '+outfile+' '+aqmfilein], shell=True)
                aqmfilein=outfile
                cs_aqm = netcdf.Dataset(aqmfilein)
                ozpm_cs_bc = cs_aqm.variables[varid][:,:,:]
                cs_aqm.close()
            else:
                print("Can not find "+aqmfilein)
                sys.exit()
    
            msg=datetime.datetime.now()
            print("Start processing "+var[ivar])
            jobid="aqm"+"_"+envir+"bc-"+envir+"_"+date.strftime(YMD_date_format)+"_"+var[ivar]+"_"+cyc
            figdir = figout+"/"+jobid
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("figdir = "+figdir)
            print("working on "+date.strftime(YMD_date_format)+" "+cyc+" diffbc "+var[ivar])

            if var[ivar] == "ozmax8" or var[ivar] == "ozmax1":
                s3_title=fileid+" (ppbV)"
                scale=1.
                clevs = [ -60., -40., -20., -10., -5., -1., -0.05, 0.05, 1., 5., 10., 20., 40., 60. ]
            elif var[ivar] == "pmave24" or var[ivar] == "pmmax1":
                s3_title=fileid+" ($\u03bcg/m^3$)"
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
                cmonth=fcst_hour.strftime(Month_date_format)[0:3]
                begdate="05Z"+fcst_hour.strftime(D_date_format)+cmonth.upper()+fcst_hour.strftime(Y_date_format)
                nout=n+1
                fcst_hour=fcst_hour+date_inc
                cmonth=fcst_hour.strftime(Month_date_format)[0:3]
                enddate="04Z"+fcst_hour.strftime(D_date_format)+cmonth.upper()+fcst_hour.strftime(Y_date_format)
                s2_title = begdate+"-"+enddate
                title=s1_title+"\n"+s2_title+" "+s3_title
                val1 = ozpm_cs[n,:,:]
                val2 = ozpm_cs_bc[n,:,:]
                diff = []
                for x, y in zip(val2, val1):
                    diff.append(x-y)
                pvar_cs= diff 

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
                                if flag_ak:
                                    try:
                                        ax.contourf(
                                         ak_lon, ak_lat, pvar_ak,
                                         levels=clevs, cmap=cmap, norm=norm, extend='both',
                                         transform=ccrs.PlateCarree() )
                                    except ValueError:
                                        continue
                                if flag_hi:
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
                        savefig_name = figdir+"/aqm."+figarea+"."+fig_exp+"bc-"+fig_exp+"."+date.strftime(YMD_date_format)+"."+cyc+"."+fileid+".day"+str(format(nout,'01d'))+".k1.png"
                        plt.savefig(savefig_name, bbox_inches='tight')
                        copyfig_name = figdir+"/aqm."+figarea+"."+fig_exp+"bcobs-"+fig_exp+"obs."+date.strftime(YMD_date_format)+"."+cyc+"."+fileid+".day"+str(format(nout,'01d'))+".k1.png"
                        shutil.copyfile(savefig_name,copyfig_name)
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
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc
