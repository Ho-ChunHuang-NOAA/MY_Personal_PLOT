import os
import numpy as np
import netCDF4 as netcdf
import re
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
if len(sys.argv) < 5:
    print("you must set 5 arguments as [g16|g18] [aodc|aodf] quality_flag[high|med|all] start_date end_date")
    sys.exit()
else:
    sat_sel = sys.argv[1]
    scan_sel = sys.argv[2]
    qc_sel = sys.argv[3]
    start_date = sys.argv[4]
    end_date = sys.argv[5]

mdl="aqm"
expid="aqmv7"

if qc_sel.lower() == "high":
    qc_list=[ "high" ]
elif qc_sel.lower() == "med" or qc_sel.lower() == "medium":
    qc_list=[ "medium" ]
elif qc_sel.lower() == "low":
    qc_list=[ "low" ]
    prints(f"QC Flag Low is not support at current time, program exit.")
    sys.exit()
else:
    qc_list=[ "high" ]

comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/GOES16_AOD/REGRID"
comout=f"/lfs/h2/emc/vpppg/noscrub/{user}/dcom/dev/abi_granule"
evsout=f"/lfs/h2/emc/vpppg/noscrub/{user}/evs/aqmaod_v2.0/prep/{mdl}"
comout=f"/lfs/h2/emc/vpppg/noscrub/{user}/point2grid_goes_abi/{mdl}"
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

py_code=sys.argv[0]
nfind=py_code.find("py")
if nfind == -1:
    workid=py_code
else:
    workid=py_code[0:nfind-1]
working_dir=f"{stmp_dir}/{sat_sel}_{scan_sel}_{qc_sel}_{expid}_{start_date}_{workid}"
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

os.chdir(working_dir)

msg_file=f"{working_dir}/msg_{sat_sel}_{scan_sel}_{qc_sel}_{expid}_{start_date}"
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
Julian_date_format = "%j"
Y_date_format = "%Y"
M_date_format = "%m"
D_date_format = "%d"
H_date_format = "%H"
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

if sat_sel == "all" or sat_sel == "ALL":
    satid=["g16", "g18", "g1618"]
elif sat_sel == "g16" or sat_sel == "g18" or sat_sel == "g1618":
    satid=[]
    satid.append(sat_sel)
else:
    print(f"Input sat ID = {sat_sel}, is not defined")
    sys.exit()

scan_check=scan_sel.upper()
if scan_check == "ALL":
    scanid=["AODC", "AODF"]
elif scan_check == "AODC" or scan_check == "AODF":
    scanid=[]
    scanid.append(scan_check)
else:
    print(f"Input Scan ID = {scan_sel}, is not defined")
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
cbar_num_format = "%.2f"
plt.close('all') # close all figures

msg=datetime.datetime.now()
msg=msg - date_inc

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
    rlon0 = [ -125., -120., -160.0, -120.4,   -95.0, -125.0,  -82.0, -125.0,  -90.0, -125.0, -103.0,  -98.0,  -75.0, -166.0, -161.5, -141.0 ]
    rlon1 = [  -110., -100., -60.0,  -70.6,   -67.0,  -95.0,  -67.0, -103.0,  -74.0, -100.0,  -83.0,  -78.0,  -71.0, -132.0, -153.1, -60.0 ]
    rlat0 = [   40., 30.0, 10.0,   22.2,    21.9,   24.5,   37.0,   38.0,   24.0,   30.0,   35.0,   23.5,   40.2,   53.2,   17.8,   38.0 ]
    rlat1 = [   45., 40., 47.0,   50.7,    50.0,   52.0,   48.0,   52.0,   40.0,   45.0,   50.0,   38.0,   41.8,   71.2,   23.1,   70.0 ]
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
    iplot = [    0,  0, 1,      1,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0,      0, 0 ]
num_reg=len(iplot)

flag_ak=False
for i in range(0,num_reg):
    if regname[i] == "ak" and iplot[i] == 1:
        flag_ak=True
flag_hi=False  ## depends on the type of scan

date=sdate
while date <= edate:
    YY=date.strftime(Y_date_format)
    YM=date.strftime(YM_date_format)
    YMD=date.strftime(YMD_date_format)
    JDAY=date.strftime(Julian_date_format)
    for scan in scanid:
        flag_hi=False
        for i in range(0,num_reg):
            if scan == "AODF" and regname[i] == "hi" and iplot[i] == 1:
                flag_hi=True
        scan_lower=scan.lower()
        evs_dir=f"{comout}/atmos.{YMD}/{mdl}"
        data_dir=f"{comout}/{mdl}.{YMD}"
        if not os.path.exists(data_dir):
            print(f"Can not find {data_dir} skip to next ABI scan")
            continue
        for goes in satid:
            goes_capt=goes.upper()
            goes_name="GOES OBS"
            if goes_capt == "G16":
                goes_name="GOES East"
            elif goes_capt == "G18":
                goes_name="GOES West"
            elif goes_capt == "G1618":
                goes_name=f"G16/18"

            figdir = f"{stmp_dir}/{goes}_{scan}_{expid}_{YMD}"
            print(f"FIGDIR={figdir}")
            if os.path.exists(figdir):
                shutil.rmtree(figdir)
            os.makedirs(figdir)

            ## for cyc in range(21,22):
            for cyc in range(0,24):
                str_obs_hr=str(cyc)
                fhh=str_obs_hr.zfill(2)
                for qc_now in qc_list:
                    qc=qc_now.lower()
                    if goes == "g1618":
                        checkfile1=f"{evs_dir}/abi_{scan}_{mdl}_join_{YMD}_{fhh}_{qc}.nc" 
                        checkfile=f"{data_dir}/abi_{scan}_{mdl}_join_{YMD}_{fhh}_{qc}.nc" 
                    else:
                        checkfile1=f"{evs_dir}/abi_{scan}_{mdl}_{goes}_{YMD}_{fhh}_{qc}.nc" 
                        checkfile=f"{data_dir}/abi_{scan}_{mdl}_{goes}_{YMD}_{fhh}_{qc}.nc" 
                    if not os.path.exists(checkfile):
                        print(f"Can not find {checkfile}")
                        if not os.path.exists(checkfile1):
                            print(f"Can not find {checkfile1} skip to next obsvered hour")
                            continue
                        else:
                            checkfile=checkfile1
                    aqmfilein=checkfile
                    if os.path.exists(aqmfilein):
                        print(aqmfilein+" exists")
                        cs_aqm = netcdf.Dataset(aqmfilein)
                        pvar_cs = cs_aqm.variables["AOD"][:,:]
                        cs_lat = cs_aqm.variables['lat'][:,:]
                        cs_lon = cs_aqm.variables['lon'][:,:]
                        fill_value_read=cs_aqm.variables["AOD"].getncattr("_FillValue")
                        cs_aqm.close()
                        imax=pvar_cs.shape[0]
                        jmax=pvar_cs.shape[1]
                        ## qc_title="$QC_{"+qc+"}$"
                        ## s1_title=goes_name+" ABI "+scan+" at 550nm "+qc_title+" "+YMD+" "+fhh+"Z"
                        s1_title=goes_name+" ABI "+scan+" at 550nm $QC_{"+qc+"}$ "+YMD+" "+fhh+"Z"
                        ## clevs = [ 0., 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0 ]
                        clevs = [ 0., 0.05, 0.1, 0.15, 0.2, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65 ]
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
                                if figarea == "ak" and flag_ak:
                                    aqmproj=ccrs.LambertConformal(central_longitude=clon, central_latitude=clat, standard_parallels=(57, 63), globe=None)
                                elif figarea == "hi" and flag_hi:
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

                                ## Matlab seems to have issue when plotting points with
                                #  longtitue with both positive and negative values
                                #  Matlab seems to be doing well if the area are smaller enough 
                                #  to have only the negative values (such as CONUS domain)
                                ## for consistency, turn the east-west system to 360. system

                                plot_lon=np.where(cs_lon>180., cs_lon-360., cs_lon)
                                ## ax.add_feature(cfeature.RIVERS)
                                try:
                                    cf1 = ax.contourf(
                                                 plot_lon, cs_lat, pvar_cs,
                                                 levels=clevs, cmap=cmap, norm=norm, extend='both',
                                                 transform=ccrs.PlateCarree() )
                                except ValueError:
                                    continue
                                ax.set_title(title)
                                ## cb2.set_label('Discrete intervals, some other units')
                                fig.colorbar(cf1,cmap=cmap,orientation='horizontal',pad=0.015,aspect=80,extend='both',ticks=clevs,norm=norm,shrink=1.0,format=cbar_num_format)
                                if goes_capt == "G1618":
                                    savefig_name = f"{figdir}/{mdl}.{figarea}.{goes}.{scan_lower}.{YMD}.{fhh}.aod.{qc}.png"
                                else:
                                    savefig_name = f"{figdir}/{mdl}.{figarea}.{goes}.{scan_lower}.{YMD}.{fhh}.aod.{qc}.png"
                                plt.savefig(savefig_name, bbox_inches='tight')
                                plt.close()
                    else:
                        print("Can not find "+aqmfilein)
            os.chdir(figdir)
            parta=os.path.join("/usr", "bin", "scp")
            if 1 == 1 :
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "web", "fig", YY, YMD)
            else:
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "transfer")
                partb=os.path.join("hchuang@rzdm:", "home", "www", "emc", "htdocs", "mmb", "hchuang", "ftp")
            subprocess.call(['scp -p * '+partb], shell=True)
            print("FIG DIR = "+figdir)
    msg=datetime.datetime.now()
    print("End   processing "+YMD+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    date = date + date_inc
