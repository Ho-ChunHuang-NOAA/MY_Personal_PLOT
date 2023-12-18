import os
import math
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

### PASSED AGRUEMENTS
if len(sys.argv) < 2:
    print("you must set 2 arguments as model[prod|para|...]  search_date")
    sys.exit()
else:
    envir = sys.argv[1]
    start_date = sys.argv[2]

end_date = start_date

if envir.lower() == "para":
    fig_exp="ncopara"+BC_fig_append
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

working_dir=ptmp_dir+"/aqm_find_gridij_working"
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

working_dir=stmp_dir+"/aqm_find_gridij_working"
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

grid148="148"
grid227="227"
grid198="198"
grid139="139"
grid196="196"
grid793="793"

aqmv6=False
aqmv7=False
caseid="v70"
nfind=envir.find(caseid)
if nfind == -1:
    print("AQMv6 simulation")
    aqmv6 = True
    EXP=envir
    expid="cs"
    exp_grid=grid148
    comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+EXP.lower()
    usrout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/verification/aqm/"+EXP.lower()
    comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+EXP.lower()
    usrout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/com/aqm/"+EXP.lower()
    comout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
    usrout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver
    if not os.path.exists(comout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
        if not os.path.exists(usrout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
            print("Can not find output dir with experiment id "+EXP.lower())
            sys.exit()
else:
    print("AQMv7 simulation")
    aqmv7 = True
    aqm_ver="v7.0"
    exp_grid=grid793
    EXP=envir
    n0=len(caseid)
    n1=len(EXP)
    expid=envir[n0:n1]
    expid="aqm"   # after 4/1/2023 directory will be changed into aqm.yyyymmdd
    comout="/lfs/h2/emc/ptmp/jianping.huang/emc.para/com/aqm/"+aqm_ver
    comout="/lfs/h2/emc/aqmtemp/para/com/aqm/"+aqm_ver
    comout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/rrfs_sfc_chem_met/"+EXP.lower()
    usrout="/lfs/h2/emc/physics/noscrub/"+os.environ['USER']+"/rrfs_sfc_chem_met/"+EXP.lower()
    if not os.path.exists(comout+"/"+expid+"."+sdate.strftime(YMD_date_format)):
        if not os.path.exists(usrout+"/cs."+sdate.strftime(YMD_date_format)):
            print("Can not find output dir with experiment id "+EXP.lower())
            sys.exit()
msg=datetime.datetime.now()
msg=msg - date_inc
grddot2d_date=msg.strftime("%Y%m%d")
##
## Current operational CMAQ does include runs for AK and HI domain
## Current EMC development CMAQ does not include runs for AK and HI domain
##
metout="/lfs/h1/ops/prod/com/aqm/"+aqm_ver

csvout=stmp_dir

obs_site_name=[ "Westport, CT", "Greenwich, CT", "Stratford, CT" ]
obs_site_id=[ "090019003", "090010017", "090013007"  ]
obs_site_id=[ "wpt-9003", "grn-0017", "str-3007"  ]
obs_site_lat= [ 41.118228, 41.004657, 41.15181 ]
obs_site_lon= [ -73.336753, -73.585128, -73.10334 ]
obs_site_name=[ "HU-Beltsville, MD", "HU-IRB, MD" ]
obs_site_id=[ "xxxxxxxxx", "xxxxxxxxx" ]
obs_site_id=[ "xxxxxxxx", "xxxxxxxx" ]
obs_site_lat= [ 39.05, 38.92 ]
obs_site_lon= [ -76.88, -77.02 ]
nsite=len(obs_site_lat)
obs_site_mdli=[]
obs_site_mdlj=[]
var=[ "o3", "pm25", "no2" ]
num_var=len(var)
#
# /lfs/h2/emc/physics/noscrub/ho-chun.huang/rrfs_sfc_chem_met/v70c55/aqm.20230404
# aqm.t06z.chem_sfc.f048.nc
#
fcst_hr="f024"
cyc="t12z"

date=sdate
while date <= edate:
    flag_find_idir="no"
    if aqmv6:
        check_file="aqm."+cyc+".aconc_sfc.ncf"
    if aqmv7:
        check_file="aqm."+cyc+".chem_sfc."+fcst_hr+".nc"
    aqmfilein=comout+"/"+expid+"."+date.strftime(YMD_date_format)+"/"+check_file
    if os.path.exists(aqmfilein):
        print(aqmfilein+" exists")
    else:
        print("Can not find "+aqmfilein)
        date = date + date_inc
        continue
    
    if aqmv7:
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            model_data = netcdf.Dataset(aqmfilein)
            dot_xt = model_data.variables['grid_xt'][:]
            dot_yt = model_data.variables['grid_yt'][:]
            cro_lat = model_data.variables['lat'][:,:]
            cro_lon = model_data.variables['lon'][:,:]
            ixt=dot_xt.shape[0]
            jyt=dot_yt.shape[0]
            print('"Dimension x is %d"' % (ixt))
            print('"Dimension y is %d"' % (jyt))
            jmax=cro_lat.shape[0]
            imax=cro_lat.shape[1]
            print('"Dimension 0 is %d"' % (jmax))
            print('"Dimension 1 is %d"' % (imax))
            model_data.close()
            jsample_b=200
            jsample_u=jsample_b+3
            isample_l=200
            isample_r=isample_l+3
            print(dot_xt[isample_l:isample_r])
            print(dot_yt[jsample_b:jsample_u])
            for j in range(jsample_b,jsample_u):
                print(str(j)+","+str(isample_l+1)+" lat = "+str(cro_lat[j][isample_l+1]))
            for i in range(isample_l,isample_r):
                print(str(jsample_b+1)+","+str(i)+" lon = "+str(cro_lon[jsample_b+1][i]))
        else:
            print("Can not find "+aqmfilein)
            sys.exit()

        for sid in range(0,nsite):
            sidlon=obs_site_lon[sid]+360.
            sidlat=obs_site_lat[sid]
            mdl_j=-999
            mdl_i=-999
            j0=0
            j1=jmax-1
            i0=0
            i1=imax-1
            for j in range(j0,j1):
                flag_ij=False
                for i in range(i0,i1):
                    ## if sidlon >= cro_lon[j][i] and sidlon < cro_lon[j][i+1] and sidlon >= cro_lon[j+1][i] and sidlon < cro_lon[j+1][i+1] and sidlat >= cro_lat[j][i] and sidlat >= cro_lat[j][i+1] and sidlat < cro_lat[j+1][i] and sidlat < cro_lat[j+1][i+1]:
                    if sidlon >= cro_lon[j][i] and sidlon < cro_lon[j+1][i+1] and sidlat >= cro_lat[j][i+1] and sidlat < cro_lat[j+1][i]:
                        mdl_i=i
                        mdl_j=j
                        flag_ij=True
                        break
                if flag_ij:
                    break
            ## Then find closest model grid from obs_site_lat and obs_site_lon
            if mdl_j == -999:
                print("Cannot find mdl_j "+str(mdl_j))
            if mdl_i == -999:
                print("Cannot find mdl_i "+str(mdl_i))
            if mdl_j == -999 or mdl_i == -999:
                sys.exit()
            findi=-999
            findj=-999
            min_latlon=99999999999999.
            for j in range(mdl_j-2,mdl_j+3):
                flag_ij="no"
                for i in range(mdl_i-2,mdl_i+3):
                     a=sidlon-cro_lon[j,i]
                     b=sidlat-cro_lat[j,i]
                     c=a*a+b*b
                     d=math.sqrt(c)
                     ## print(str(d))
                     if d < min_latlon:
                         ## print("find new shortest distance "+str(min_latlon)+"  to "+str(d) )
                         ## print("find new shortest mdl_j and mdl_i = ("+str(j)+","+str(i)+")")
                         min_latlon=d
                         findi=i
                         findj=j

            mdl_j=findj
            mdl_i=findi
            i0=findi-1
            i1=findi+2
            j0=findj-1
            j1=findj+2
            for j in range(j0,j1):
                for i in range(i0,i1):
                    print(str(j)+","+str(i)+" lat = "+str(cro_lat[j][i]))
            for i in range(i0,i1):
                for j in range(j0,j1):
                    print(str(j)+","+str(i)+" lon = "+str(cro_lon[j][i]))
            print( "obs lon = "+str(sidlon))
            print( "obs lat = "+str(sidlat))
            print( "model i = "+str(mdl_i)+" and model j = "+str(mdl_j))
            print( "lat UL = "+str(cro_lat[mdl_j+1][mdl_i])+" and lat UR = "+str(cro_lat[mdl_j+1][mdl_i+1]))
            print( "lat LL = "+str(cro_lat[mdl_j][mdl_i])+" and lat LR = "+str(cro_lat[mdl_j][mdl_i+1]))
            print( "lon UL = "+str(cro_lon[mdl_j+1][mdl_i])+" and lon UR = "+str(cro_lon[mdl_j+1][mdl_i+1]))
            print( "lon LL = "+str(cro_lon[mdl_j][mdl_i])+" and lon LR = "+str(cro_lon[mdl_j][mdl_i+1]))
            print( "mdl lon = "+str(cro_lon[mdl_j][mdl_i]))
            print( "mdl lat = "+str(cro_lat[mdl_j][mdl_i]))

        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm = netcdf.Dataset(aqmfilein)
            cs_var = cs_aqm.variables['time'][:]
            nstep=len(cs_var)
            for ivar in range(0,num_var):
                if var[ivar] == "o3":
                    o3_cs = cs_aqm.variables['o3'][0,:,:]
                if var[ivar] == "pm25":
                    pm_cs = cs_aqm.variables['PM25_TOT'][0,:,:]
                if var[ivar] == "no2":
                    no2_cs = cs_aqm.variables['no2'][0,:,:]
            cs_aqm.close()
            jmax=no2_cs.shape[0]
            imax=no2_cs.shape[1]
            print('"Dimension 0 is %d"' % (jmax))
            print('"Dimension 1 is %d"' % (imax))
            max_no2=np.amax(no2_cs)
            min_no2=np.amin(no2_cs)
            print('"MAX of NO2 is  %f"' % (max_no2))
            print('"MIN of NO2 is  %f"' % (min_no2))
            result = np.where(no2_cs == np.amax(no2_cs))
            jidx=result[0]   # is an array
            iidx=result[1]   # is an array
            print(jidx[0])   # only one will be found, can be more than if not unique
            print(iidx[0])   # only one will be found, can be more than if not unique
            mld_max_no2=no2_cs[0,0]   # to double check the number from result[*] number
            mld_max_no2=no2_cs[4,559]   # to double check the number from result[*] number
            print('"CONC of NO2 is            %f"' % (no2_cs[jidx[0],iidx[0]]))
            print('"Asssigned CONC of NO2 is  %f"' % (mld_max_no2))
        else:
            print("Can not find "+aqmfilein)
            sys.exit()

    if aqmv6:
        metfilein=comout+"/cs."+grddot2d_date+"/aqm."+cyc+".grdcro2d.ncf"
        if os.path.exists(metfilein):
            print(metfilein+" exists")
            model_data = netcdf.Dataset(metfilein)
            cro_lat = model_data.variables['LAT'][0,0,:,:]
            cro_lon = model_data.variables['LON'][0,0,:,:]
            jmax=cro_lat.shape[0]
            imax=cro_lat.shape[1]
            print('"Dimension 0 is %d"' % (jmax))
            print('"Dimension 1 is %d"' % (imax))
            model_data.close()
        else:
            print("Can not find "+metfilein)
            sys.exit()

        metfilein=comout+"/cs."+grddot2d_date+"/aqm."+cyc+".grddot2d.ncf"
        if os.path.exists(metfilein):
            print(metfilein+" exists")
            model_data = netcdf.Dataset(metfilein)
            dot_lat = model_data.variables['LATD'][0,0,:,:]
            dot_lon = model_data.variables['LOND'][0,0,:,:]
            jmax=dot_lat.shape[0]
            imax=dot_lat.shape[1]
            print('"Dimension 0 is %d"' % (jmax))
            print('"Dimension 1 is %d"' % (imax))
            model_data.close()
        else:
            print("Can not find "+metfilein)
            sys.exit()

        print( "lat LL = "+str(dot_lat[0][0])+" and lat UL = "+str(dot_lat[jmax-1][0]))
        print( "lat LR = "+str(dot_lat[0][imax-1])+" and lat UR = "+str(dot_lat[jmax-1][imax-1]))
        print( "lon LL = "+str(dot_lon[0][0])+" and lon UL = "+str(dot_lon[jmax-1][0]))
        print( "lon LR = "+str(dot_lon[0][imax-1])+" and lon UR = "+str(dot_lon[jmax-1][imax-1]))
        for sid in range(0,nsite):
            sidlon=obs_site_lon[sid]
            sidlat=obs_site_lat[sid]
            print( "obs lon = "+str(sidlon))
            print( "obs lat = "+str(sidlat))
            mdl_i=-999
            mdl_j=-999
            flag_ij=False
            for j in range(0,jmax-1):
                for i in range(0,imax-1):
                    ## if sidlon >= dot_lon[j][i] and sidlon < dot_lon[j][i+1] and sidlon >= dot_lon[j+1][i] and sidlon < dot_lon[j+1][i+1] and sidlat >= dot_lat[j][i] and sidlat >= dot_lat[j][i+1] and sidlat < dot_lat[j+1][i] and sidlat < dot_lat[j+1][i+1]:
                    if sidlon >= dot_lon[j][i] and sidlon < dot_lon[j+1][i+1] and sidlat >= dot_lat[j][i+1] and sidlat < dot_lat[j+1][i]:
                        mdl_i=i
                        mdl_j=j
                        flag_ij=True
                        break
                if flag_ij:
                    break
            if flag_ij:
                ## print( "obs lon = "+str(sidlon))
                ## print( "obs lat = "+str(sidlat))
                print( "model i = "+str(mdl_i)+" and model j = "+str(mdl_j))
                print( "lat UL = "+str(dot_lat[mdl_j+1][mdl_i])+" and lat UR = "+str(dot_lat[mdl_j+1][mdl_i+1]))
                print( "lat LL = "+str(dot_lat[mdl_j][mdl_i])+" and lat LR = "+str(dot_lat[mdl_j][mdl_i+1]))
                print( "lon UL = "+str(dot_lon[mdl_j+1][mdl_i])+" and lon UR = "+str(dot_lon[mdl_j+1][mdl_i+1]))
                print( "lon LL = "+str(dot_lon[mdl_j][mdl_i])+" and lon LR = "+str(dot_lon[mdl_j][mdl_i+1]))
                print( "mdl lon = "+str(cro_lon[mdl_j][mdl_i]))
                print( "mdl lat = "+str(cro_lat[mdl_j][mdl_i]))
            else:
                print("Can not fin model i,j for station #"+str(sid))
                # set guess i,j for shortest distance calculation
                mdl_i=371
                mdl_j=174

            ## Then find closest model grid from obs_site_lat and obs_site_lon
            findi=-999
            findj=-999
            min_latlon=99999999999999.
            for j in range(mdl_j-5,mdl_j+6):
                flag_ij="no"
                for i in range(mdl_i-5,mdl_i+6):
                     a=sidlon-cro_lon[j,i]
                     b=sidlat-cro_lat[j,i]
                     c=a*a+b*b
                     d=math.sqrt(c)
                     ## print(str(d))
                     if d < min_latlon:
                         ## print("find new shortest distance "+str(min_latlon)+"  to "+str(d) )
                         ## print("find new shortest mdl_j and mdl_i = ("+str(j)+","+str(i)+")")
                         min_latlon=d
                         findi=i
                         findj=j

            mdl_j=findj
            mdl_i=findi
            print( "obs lon = "+str(sidlon))
            print( "obs lat = "+str(sidlat))
            print( "model i = "+str(mdl_i)+" and model j = "+str(mdl_j))
            print( "lat UL = "+str(cro_lat[mdl_j+1][mdl_i])+" and lat UR = "+str(cro_lat[mdl_j+1][mdl_i+1]))
            print( "lat LL = "+str(cro_lat[mdl_j][mdl_i])+" and lat LR = "+str(cro_lat[mdl_j][mdl_i+1]))
            print( "lon UL = "+str(cro_lon[mdl_j+1][mdl_i])+" and lon UR = "+str(cro_lon[mdl_j+1][mdl_i+1]))
            print( "lon LL = "+str(cro_lon[mdl_j][mdl_i])+" and lon LR = "+str(cro_lon[mdl_j][mdl_i+1]))
            print( "mdl lon = "+str(cro_lon[mdl_j][mdl_i]))
            print( "mdl lat = "+str(cro_lat[mdl_j][mdl_i]))
        sys.exit()
        aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".aconc_sfc.ncf"
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm = netcdf.Dataset(aqmfilein)
            cs_var = cs_aqm.variables['TFLAG'][:,0,:]
            nstep=len(cs_var)
            for ivar in range(0,num_var):
                if var[ivar] == "o3":
                    o3_cs = cs_aqm.variables['O3'][:,0,:,:]
                if var[ivar] == "pm25":
                    pm_cs = cs_aqm.variables['PM25_TOT'][:,0,:,:]
                if var[ivar] == "no2":
                    no2_cs = cs_aqm.variables['NO2'][:,0,:,:]
            cs_aqm.close()
            tmax=no2_cs.shape[0]
            jmax=no2_cs.shape[1]
            imax=no2_cs.shape[2]
            print('"Dimension 0 is %d"' % (tmax))
            print('"Dimension 1 is %d"' % (jmax))
            print('"Dimension 2 is %d"' % (imax))
            max_no2=np.amax(no2_cs)
            min_no2=np.amin(no2_cs)
            print('"MAX of NO2 is  %f"' % (max_no2))
            print('"MIN of NO2 is  %f"' % (min_no2))
            result = np.where(no2_cs == np.amax(no2_cs))
            nidx=result[0]   # is an array
            jidx=result[1]   # is an array
            iidx=result[2]   # is an array
            print(nidx[0])   # only one will be found, can be more than if not unique
            print(jidx[0])   # only one will be found, can be more than if not unique
            print(iidx[0])   # only one will be found, can be more than if not unique
            mld_max_no2=no2_cs[0,0,0]   # to double check the number from result[*] number
            mld_max_no2=no2_cs[61,169,369]   # to double check the number from result[*] number
            print('"CONC of NO2 is            %f"' % (no2_cs[nidx[0],jidx[0],iidx[0]]))
            print('"Asssigned CONC of NO2 is  %f"' % (no2_cs[61,169,369]))
            for n in range(0,tmax):
                print("===================")
                no2_2d=no2_cs[n,:,:]
                print("n = "+str(n)+"  no2 = "+str(no2_2d[mdl_j,mdl_i]))
                max_no2_2d=np.amax(no2_2d)
                min_no2_2d=np.amin(no2_2d)
                print('"MAX of NO2 is  %f"' % (max_no2_2d))
                print('"MIN of NO2 is  %f"' % (min_no2_2d))
                result = np.where(no2_2d == np.amax(no2_2d))
                jidx=result[0]   # is an array
                iidx=result[1]   # is an array
                print(jidx[0])   # only one will be found, can be more than if not unique
                print(iidx[0])   # only one will be found, can be more than if not unique
                if n == 61:
                    mld_max_no2_2d=no2_2d[169,369]
                    print('"CONC of NO2 is           %f"' % (no2_2d[jidx[0],iidx[0]]))
                    print('"Assigned CONC of NO2 is  %f"' % mld_max_no2_2d)
                print('"MAX CONC of NO2 at time step %d is  %f"' % (n,no2_2d[jidx[0],iidx[0]]))

        else:
            print("Can not find "+aqmfilein)
            sys.exit()
    date = date + date_inc
