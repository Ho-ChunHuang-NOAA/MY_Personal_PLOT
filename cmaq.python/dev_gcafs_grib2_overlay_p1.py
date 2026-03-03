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
import pandas as pd

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
        if ver_name[1] == "gcafs_ver":
            gcafs_ver_prod=ver[1]
rfile.close()
if gcafs_ver_prod=="":
    gcafs_ver_prod="v1.0"
print("gcafs_ver="+gcafs_ver_prod)

wgrib2=os.environ['WGRIB2']
if wgrib2 == "":
    print("No definition of WGRIB2 can be found, please load module wgrib2/2.0.8")
    sys.exit()

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

flag_obs=False
flag_obs=True

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
working_dir=stmp_dir+"/"+envir+"_"+workid
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

os.chdir(working_dir)

msg_file=working_dir+"/msg_"+sel_var+"_"+start_date+"_"+sel_cyc
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

sdate = datetime.datetime.strptime(start_date, '%Y%m%d')
edate = datetime.datetime.strptime(end_date, '%Y%m%d')

obs_YMDH_date_format = "%Y%m%d%H"
YMDH_date_format = "%Y%m%d/%H"
YMD_date_format = "%Y%m%d"
YM_date_format = "%Y%m"
YY_date_format = "%Y"
Y_date_format = "%Y"
M_date_format = "%m"
D_date_format = "%d"
H_date_format = "%H"
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

##
grid148="148"
grid227="227"
grid198="198"
grid139="139"
grid196="196"
grid793="793"

gcafs = True
caseid="gcafs"
s1_lead="Inline GCAFS"
gcafs_ver="v1.0"
dataid=gcafs_ver.split('.')[0]

nfind=envir.find("_bc")
if nfind == -1:
    print("not a bias_correction cases")
    EXP=envir
    if caseid == "keep":
        n0=len(caseid)
        n1=len(EXP)
        expid=envir[n0:n1]
    expid="gcafs"   # after 4/1/2023 directory will be changed into gcafs.yyyymmdd
    BC_append=""
    BC_fig_append=BC_append
    print("exp="+EXP)
    print("expid="+expid)
    print("BC_append="+BC_append)
else:
    EXP=envir[0:nfind]
    if caseid == "keep":
        n0=len(caseid)
        n1=len(EXP)
        expid=EXP[n0:n1]
    expid="gcafs"   # after 4/1/2023 directory will be changed into gcafs.yyyymmdd
    BC_append="_bc"
    BC_fig_append="bc"
    print("exp="+EXP)
    print("expid="+expid)
    print("BC_append="+BC_append)

if EXP.lower() == "gcafs" or EXP.lower() == "gcafsv10":
    comout="/lfs/h1/ops/prod/com/gcafs/v1.0"
else:
    comout=f"/lfs/h2/emc/vpppg/noscrub/{user}/verification/{expid}/{expid}{dataid}"
usrout=f"/lfs/h2/emc/vpppg/noscrub/{user}/verification/{expid}/{expid}{dataid}"
if not os.path.exists(comout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
    if not os.path.exists(usrout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
        print(f"Can not find output dir with experiment id {expid}")
        sys.exit()

if EXP.lower() == "para":
    fig_exp="ncopara"+BC_fig_append
else:
    fig_exp=EXP.lower()+BC_fig_append

if sel_var == "all":
   var=[ "aod", "pm25" ]
elif sel_var == "aod":
   var=[ "aod" ]
elif sel_var == "pm25":
   var=[ "pm25" ]
else:
    print("input variable "+sel_var+" can not be recongized.")
    sys.exit()
num_var=len(var)
print("var length = "+str(num_var))

if sel_cyc == "all":
   cycle=[ "t00z", "t12z" ]
   cycle=[ "00", "12" ]
elif sel_cyc == "00":
   cycle=[ "t00z" ]
   cycle=[ "00" ]
elif sel_cyc == "12":
   cycle=[ "t12z" ]
   cycle=[ "12" ]
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

dcomdir="/lfs/h1/ops/prod/dcom"
obsdir="/lfs/h2/emc/vpppg/noscrub/"+os.environ['USER']+"/dcom/prod/airnow"
figout=stmp_dir

flag_ak=False
flag_hi=False
##
## new area need to be added ahead of ak.  The last three areas need to be fixed as "ak",   "hi",  "can"
## this is due to the code below remove plotting of ak and hi if no ak and hi input files ash been found
##
flag_proj="LambertConf"
## from 22.574179720000018 to 51.47512722912568
## from 228.37073225113136 to 296.6273160909873
# old -70.6 to -120.4
#     22.2 to 50.7
mksize= [  64,64, 121, 64, 64, 16,     36,      36,      36,     49,     49,     49,     49,     64,     64,    121,    100,    121,     36 ]
## mksize= [ 64,64, 64, 64, 16,      16,      25,     25,     36,     36,     36,     36,     49,     49,    121,    100,    121,     36 ]
if flag_proj == "LambertConf":
    regname = [ "LAfire", "LABasin", "ctdeep", "Mckinney",  "aznw", "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",  "lis",   "ak",   "hi",  "can" ]
    rlon0 = [ -130., -121., -75., -125., -120., -165.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0,  -75.0, -166.0, -161.5, -141.0 ]
    rlon1 = [  -112., -116.8, -71., -110., -100., -70.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0,  -71.0, -132.0, -153.1, -60.0 ]
    rlat0 = [   22.5, 32.2, 40.4, 40., 30.0, 10.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   40.2,   53.2,   17.8,   38.0 ]
    rlat1 = [   38.5, 35.5, 42.2, 45., 40., 75.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   41.8,   71.2,   23.1,   70.0 ]
xsize = [   8,8, 10, 10, 10, 10,     10,       8,      8,      8,      8,      8,      8,      8,      8,     10,      8,      8,     10 ]
ysize = [    8,8, 8, 5, 5, 8,      8,       8,      8,      8,      8,      8,      8,      8,      8,      5,      8,      8,     8 ]
if 1 == 2:
    iplot = [  0, 0, 1, 0, 0,   1,      1,       1,      1,      1,      1,      1,      1,      1,      1,      1,      0,      0, 1 ]
else:
    iplot = [ 0, 0, 0, 0,  0, 0,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0, 0 ]

num_reg=len(iplot)
if num_reg == 0:
    print(f"no region has been selected")
    sys.exit(0)

date=sdate
while date <= edate:
    YY  = date.strftime(YY_date_format)
    YM  = date.strftime(YM_date_format)
    YMD = date.strftime(YMD_date_format)
    if not flag_ak and iplot[num_reg-3] == 1:
        iplot[num_reg-3] = 0
    if not flag_hi and iplot[num_reg-2] == 1:
        iplot[num_reg-2] = 0

    for cyc in cycle:
        cycle_time="t"+cyc+"z"
        msg=datetime.datetime.now()
        print("Start processing "+YMD+" "+cyc+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        s1_title=s1_lead+" "+EXP.upper()+BC_append.upper()+" "+YMD+" t"+cyc+"z"
        fcst_ini=datetime.datetime(date.year, date.month, date.day, int(cyc[0:2]))

        for ivar in range(0,num_var):
            fcst_hour=fcst_ini
            if flag_obs:
                figdir = figout+"/gcafs"+"_"+EXP.lower()+"obs_"+YMD+"_"+var[ivar]+cycle_time+BC_append.lower()+"_hrlyp1"
            else:
                figdir = figout+"/gcafs"+"_"+EXP.lower()+"_"+YMD+"_"+var[ivar]+cycle_time+BC_append.lower()+"_p1"
            print(f"figure dir = {figdir}")
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)
            print("working on "+YMD+" t"+cyc+"z "+var[ivar])
            fcst_inc = 3
            fcst_beg = 0
            fcst_end = 3
            for fcst_hr in range(fcst_beg,fcst_end+1,fcst_inc):
                str_fcst_hr=str(fcst_hr)
                fhh=str_fcst_hr.zfill(3)
                ## READ hourly EPA AirNOW OBS data
                ## note obs is forward average and model is backward, so they are different by an hour
                hour_adv = datetime.timedelta(hours=fcst_hr)
                fcst_hour=fcst_ini+hour_adv
                obs_hour=fcst_hour-hour_inc

                ## Read in one hourly data one at a time
                flag_with_obs=True
                obsfile= "HourlyAQObs_"+obs_hour.strftime(obs_YMDH_date_format)+".dat"
                ifile=os.path.join(dcomdir,obs_hour.strftime(YMD_date_format),"airnow",obsfile)
                ifile2=os.path.join(obsdir,obs_hour.strftime(Y_date_format),obs_hour.strftime(YMD_date_format),obsfile)
                ifile2=os.path.join(obsdir,obs_hour.strftime(YMD_date_format),"airnow",obsfile)
                if os.path.exists(ifile):
                    infile=ifile
                    print(infile+" exists")
                elif os.path.exists(ifile2):
                    infile=ifile2
                    print(infile+" exists")
                else:
                    print("Can not find both "+ifile+" and "+ifile2)
                    flag_with_obs=False

                if flag_obs and flag_with_obs:
                    airnow = []
                    colnames = ['Latitude','Longitude','ValidDate','ValidTime','PM25','PM25_Unit']
    
                    df = pd.read_csv(infile,usecols=colnames)
    
                    df[df['PM25']<0]=np.nan # ignore negative PM2.5 values
    
                    df['Datetime'] = df['ValidDate'].astype(str)+' '+df['ValidTime'] # merge date and time columns
                    ## note 2020 epa time format is MM/DD/YY while 2022 timestamp is MM/DD/YYYY
                    if obs_hour.strftime(Y_date_format) == "2020":
                        df['Datetime'] = pd.to_datetime(df['Datetime'],format='%m/%d/%y %H:%M') # convert dates/times into datetime format
                    else:
                        df['Datetime'] = pd.to_datetime(df['Datetime'],format='%m/%d/%Y %H:%M') # convert dates/times into datetime format
                    colnames_dt = ['Latitude','Longitude','Datetime','PM25','PM25_Unit']
    # is there a similar command of pd.close_csv() ??
                    df = df[colnames_dt]
                    airnow.append(df)
    
                    airnow = pd.concat(airnow, ignore_index=True) # combine list of dataframes into one
    
                    lat = airnow['Latitude']
                    lon = airnow['Longitude']
                    dt = airnow['Datetime']
                    pm25_obs = airnow['PM25']
                    pmunit = airnow['PM25_Unit']

                if var[ivar] == "pm25":
                    gcafsfilein=f"{usrout}/{expid}.{YMD}/{cyc}/products/atmos/grib2/0p25/gcafs.atmos.{cycle_time}.0p25.f{fhh}.trim.grib2"
                    gcafsfilein2=f"{comout}/{expid}.{YMD}/{cyc}/products/atmos/grib2/0p25/gcafs.{cycle_time}.pres_a.0p25.f{fhh}.grib2"
                    wgrib2_exe = "wgrib2" # Path to your wgrib2 executable
                    if os.path.exists(gcafsfilein):
                        ## print(gcafsfilein+" exists")
                        outfile=working_dir+"/pm25."+fhh+"."+YMD+"."+cycle_time+".nc"
                        
                        ## subprocess.call([wgrib2+' -d 2 -netcdf '+outfile+' '+gcafsfilein], shell=True)
                        cmd = [
                            "wgrib2",
                            gcafsfilein,
                            "-match", "PMTF",
                            "-match", "aerosol=Total Aerosol",
                            "-match", "aerosol_size <2.5e-06",
                            "-netcdf", outfile
                        ]

                        print(outfile)
                        try:
                            subprocess.run(cmd, check=True)
                        except subprocess.CalledProcessError as e:
                            print(f"Error: wgrib2 failed for {gcafsfilein}")
                        gcafsfilein=outfile
                        cs_gcafs = netcdf.Dataset(gcafsfilein)
                        cs_lat = cs_gcafs.variables['latitude'][:]
                        cs_lon = cs_gcafs.variables['longitude'][:]
                        pm_cs = cs_gcafs.variables['PMTF_surface'][0,:,:]
                        cs_gcafs.close()
                    elif os.path.exists(gcafsfilein2):
                        ## print(gcafsfilein2+" exists")
                        outfile=working_dir+"/pm25."+fhh+"."+YMD+"."+cycle_time+".nc"
                        ## subprocess.call([wgrib2+' -d 40 -netcdf '+outfile+' '+gcafsfilein2], shell=True)
                        cmd = [
                            wgrib2_exe,
                            gcafsfilein2,
                            "-match", "PMTF",
                            "-match", "aerosol=Total Aerosol",
                            "-match", "aerosol_size <2.5e-06",
                            "-netcdf", outfile
                        ]

                        # Run it
                        try:
                            subprocess.run(cmd, check=True)
                        except subprocess.CalledProcessError as e:
                            print(f"Error: wgrib2 failed for {gcafsfilein}")
                        gcafsfilein2=outfile
                        cs_gcafs = netcdf.Dataset(gcafsfilein2)
                        cs_lat = cs_gcafs.variables['latitude'][:]
                        cs_lon = cs_gcafs.variables['longitude'][:]
                        pm_cs = cs_gcafs.variables['PMTF_surface'][0,:,:]
                        cs_gcafs.close()
                    else:
                        print("Can not find "+gcafsfilein)
                        print("Can not find "+gcafsfilein2)
                        continue
                        ## sys.exit()
                s2_title = fcst_hour.strftime(YMDH_date_format)+"00V"+fhh
                if var[ivar] == "pm25":
                    s3_title="PM25 sfc_conc ($\u03bcg/m^3$)"
                    scale=1.
                    clevs = [ 3., 6., 9., 12., 15., 35., 55., 75., 100., 125., 150., 250., 300., 400., 500., 600., 750. ]
                    var_cs=pm_cs
                    cmap = mpl.colors.ListedColormap([
                          (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                          (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000),
                          (1.0000,0.3840,0.3840), (1.0000,0.0000,0.0000), (0.8000,0.0000,0.0000), (0.7020,0.0000,0.0000),
                          (0.6120,0.5100,0.8120), (0.5180,0.3880,0.7650), (0.4310,0.2780,0.7250),(0.2980,0.1920,0.5020),
                          (0.4706,0.4706,0.4706), (0.7843,0.7843,0.7843)
                          ])
                    cmap.set_under((0.8627,0.8627,1.0000))
                    cmap.set_over((0.9412,0.9412,0.9412))
                elif var[ivar] == "pm25_nonseason":
                    s3_title="PM25 sfc_conc ($\u03bcg/m^3$)"
                    scale=1.
                    clevs = [ 0., 3., 6., 9., 12., 25., 35., 45., 55., 65., 75., 85., 95., 105. ]
                    var_cs=pm_cs
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

                title=s1_title+"\n"+s2_title+" "+s3_title
                pvar_cs = var_cs[:,:]
                for ireg in range(0,num_reg):
                    if iplot[ireg] == 1:
                        figarea=regname[ireg]
                        extent=[ rlon0[ireg], rlon1[ireg], rlat0[ireg], rlat1[ireg] ]
                        clat=0.5*(rlat0[ireg] + rlat1[ireg])
                        clon=0.5*(rlon0[ireg] + rlon1[ireg])
                        if figarea == "ak":
                            gcafsproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, standard_parallels=(57, 63), globe=None)
                        elif figarea == "hi":
                            gcafsproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, standard_parallels=(19, 21), globe=None)
                        else:
                            gcafsproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, false_easting=-58.775, false_northing=48.772, standard_parallels=(33, 45), globe=None)
                        fig, ax = plt.subplots(figsize=(xsize[ireg],ysize[ireg]))

                        ax = plt.axes(projection=gcafsproj)
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
                        try:
                            cf1 = ax.contourf(
                                 cs_lon, cs_lat, pvar_cs,
                                 levels=clevs, cmap=cmap, norm=norm, extend='both',
                                 transform=ccrs.PlateCarree() )
                        except ValueError:
                            continue
                        ax.set_title(title)
                        ## cb2.set_label('Discrete intervals, some other units')
                        fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,shrink=1.0,format=cbar_num_format)

                        if flag_obs and flag_with_obs:
                            #######################################################
                            ##########      PLOTTING OBS DATA            ##########
                            #######################################################
    
                            var_lat = []
                            var_lon = []
                            plot_var = []
                            var_unit = []
                            length = len(lat)
    
                            for row in range(length):
                                bool_nanpm = pd.isnull(pm25_obs[row])
    
                                if var[ivar] == 'pm25':
                                    if dt[row] == obs_hour and bool_nanpm == False:
                                        var_lon.append(lon[row])
                                        var_lat.append(lat[row])
                                        plot_var.append(pm25_obs[row])
                                        var_unit.append(pmunit[row])
                                        if pmunit[row]!='UG/M3':
                                            print('Uh oh! pm25 row '+str(row)+' is in units of '+str(pmunit[row]))
                                else:
                                    print('Chosen variable not recognized'+str(var))
    
                            if var[ivar] == 'pm25':
                                num_pm25=len(plot_var)
                                clevs = [ 3., 6., 9., 12., 15., 35., 55., 75., 100., 125., 150., 250., 300., 400., 500., 600., 750. ]
                                nlev=len(clevs)
                                ccols = [
                                        (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
                                        (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000),
                                        (1.0000,0.3840,0.3840), (1.0000,0.0000,0.0000), (0.8000,0.0000,0.0000), (0.7020,0.0000,0.0000),
                                        (0.6120,0.5100,0.8120), (0.5180,0.3880,0.7650), (0.4310,0.2780,0.7250),(0.2980,0.1920,0.5020),
                                        (0.4706,0.4706,0.4706), (0.7843,0.7843,0.7843)
                                        ]
                                ncols=len(ccols)
                                if ncols+1 != nlev:
                                    print("Warning: color interval does not match with color setting")
                                color=[]
                                for i in range(0,num_pm25):
                                    if plot_var[i] < clevs[0]:
                                        color.append((0.8627,0.8627,1.0000))
                                    elif plot_var[i] >= clevs[nlev-1]:
                                        color.append((0.9412,0.9412,0.9412))
                                    else:
                                        flag_find_color=False
                                        for j in range(0,nlev-1):
                                            if plot_var[i] >= clevs[j] and plot_var[i] < clevs[j+1]:
                                                color.append(ccols[j])
                                                flag_find_color=True
                                                break
                                        if not flag_find_color:
                                            print("Can not assign proper value for color, program stop")
                                            sys.exit()
    
                            else:
                                print('Chosen variable not recognized'+str(var))
                            ## s = [20*4**n for n in range(len(x))]
                            ## ax.scatter(var_lon,var_lat,c=color,cmap=cmap,marker='o',s=100,zorder=1, transform=ccrs.PlateCarree(), edgecolors='black')
                            ax.scatter(var_lon,var_lat,c=color,cmap=cmap,marker='o',s=mksize[ireg],zorder=1, transform=ccrs.PlateCarree(), edgecolors='black')

                        if flag_obs and flag_with_obs:
                            savefig_name = figdir+"/gcafs."+figarea+"."+fig_exp+"obs."+YMD+"."+cycle_time+"."+fhh+"."+var[ivar]+".k1.png"
                        else:
                            savefig_name = figdir+"/gcafs."+figarea+"."+fig_exp+"."+YMD+"."+cycle_time+"."+fhh+"."+var[ivar]+".k1.png"
                        plt.savefig(savefig_name, bbox_inches='tight')
                        plt.close()
            ## scp by cycle and variable
            ##
            os.chdir(figdir)
            parta=os.path.join("/usr", "bin", "scp")
            if 1 == 2 :
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", date.strftime(Y_date_format), YMD, cycle_time)
            else:
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "ftp")
            subprocess.call(['scp -p * '+partb], shell=True)
            msg=datetime.datetime.now()
            print("End   processing "+var[ivar])
            print("FIG DIR = "+figdir)
        msg=datetime.datetime.now()
        print("End   processing "+YMD+" "+cycle_time+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    print("End   processing "+YMD+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc
