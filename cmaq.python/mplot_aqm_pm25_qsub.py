import sys
import shutil
import subprocess
import os
import numpy as np
import netCDF4 as netcdf
import logging
import datetime

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
        if ver_name[1] == "envvar_ver":
            envvar_ver=ver[1]
        if ver_name[1] == "PrgEnv_intel_ver":
            PrgEnv_intel_ver=ver[1]
        if ver_name[1] == "intel_ver":
            intel_ver=ver[1]
        if ver_name[1] == "craype_ver":
            craype_ver=ver[1]
        if ver_name[1] == "cray_mpich_ver":
            cray_mpich_ver=ver[1]
        if ver_name[1] == "python_ver":
            python_ver=ver[1]
        if ver_name[1] == "netcdf_ver":
            netcdf_ver=ver[1]
## print("envvar_ver="+envvar_ver)
## print("PrgEnv_intel_ver="+PrgEnv_intel_ver)
## print("intel_ver="+intel_ver)
## print("craype_ver="+craype_ver)
## print("envvar_ver="+envvar_ver)
## print("cray_mpich_ver="+cray_mpich_ver)
## print("python_ver="+python_ver)
## print("netcdf_ver="+netcdf_ver)

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

task_cpu="04:30:00"
task_cpu1="01:00:00"
task_cpu2="02:00:00"
task_cpu3="03:00:00"

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
    remote_host="clogin01.wcoss2.ncep.noaa.gov"
elif machine.lower() == "cactus":
    remote="dogwood"
    remote_host="dlogin01.wcoss2.ncep.noaa.gov"
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

run_root=stmp_dir+"/run_python_script"
if not os.path.exists(run_root):
    os.mkdir(run_root)
## working_dir=os.path.join(run_root,envir,sel_var,sel_cyc,start_date)
working_dir=os.path.join(run_root,envir,start_date)
if os.path.exists(working_dir):
    os.chdir(working_dir)
else:
    os.makedirs(working_dir)
    os.chdir(working_dir)

if envir == "prod" or envir == "firev4":
    script_name = [
                  "daily.aqm.plot.py",
                  "daily.aqm.plot_overlay.py",
                  "daily.aqm.plot_bc.py",
                  "daily.aqm.plot_bc_overlay.py",
                  "diff_aqm_plot_bc.py",
                  "daily.aqm.plot_max_ave.py", "daily.aqm.plot_max_ave_bc.py",
                  "daily.aqm.plot_max_ave_overlay.py",
                  "diff.aqm.plot_max_ave_bc.py"
                  ]
    ## using bias_corrected grib2 file before 2022/08/26 (excep 202201-202202)
    ## "daily_aqm_grib2_overlay_p1.py", "daily_aqm_grib2_overlay_p2.py",
    ## using ozone.corrected.* and pm2.5.corrected.* starting 2022/08/26
    ## "daily.aqm.plot_bc_overlay.py",
    ## "daily.aqm.plot_bc.py",
    no_workk_script = [
                  "daily_aqm_grib2_overlay_p1.py",
                  "daily_aqm_grib2_overlay_p2.py",
                  "diff.aqm.plot_bc.py",
                  "gbbepx_fire_loc.py", "daily.aqm.plot_dustloc.py",
                  "daily.aqm.plot_max_ave_overlay.py",
                  "daily_aqm_grib2_overlay.py", "daily.aqm.plot_aot.py"
                  ]
else:
    print(" Not for experimental run, use *rrfs*")
    sys.exit()
    col_var = [ "pm25_col", "pm25c_col" ]
## subprocess.call(['cp -p * '+partb], shell=True)

for i in script_name:
    from_file=os.path.join(script_dir,i)
    to_file=os.path.join(working_dir,i)
    if os.path.exists(from_file):
        shutil.copyfile(from_file,to_file)
    else:
        print("Can not find "+from_file)
        sys.exit()

util_name="maps2d_plot_util.py"
from_file=os.path.join(script_dir,util_name)
to_file=os.path.join(working_dir,util_name)
if os.path.exists(from_file):
    shutil.copyfile(from_file,to_file)
else:
    print("Can not find "+from_file)
    sys.exit()

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

var=[ "pm25" ]
num_var=len(var)
print("var length = "+str(num_var))

if sel_cyc == "all":
    cycle=[ "06", "12" ]
elif sel_cyc == "06":
    cycle=[ "06" ]
elif sel_cyc == "12":
    cycle=[ "12" ]
else:
    print("seletced cycle"+sel_cyc+" can not be recongized.")
    sys.exit()

##  regname = [   "dset", "conus", "east", "west",   "ne",   "nw",   "se",   "sw",  "mdn",  "glf",   "ak",   "hi",  "can" ] 
##    rlon0 = [ -175.0, -124.0,  -100.0, -128.0,  -82.0, -125.0,  -95.0, -125.0, -105.0, -105.0, -170.0, -161.0, -141.0 ]
## xsize = [     10,     10,       8,      8,      8,      8,      8,      8,      8,      8,      8,      8,     10 ]
## num_reg=len(iplot)
## print("iplot length = "+str(num_reg))

ic=0
date=sdate
while date <= edate:
    for cyc in cycle:
        msg=datetime.datetime.now()
        print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+"Z Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        for i in script_name:
            msg=datetime.datetime.now()
            if i == "daily.aqm.plot.py" or i == "daily.aqm.plot_overlay.py" or i == "daily.aqm.plot_bc.py" or i == "daily.aqm.plot_bc_overlay.py":
                print("    Start processing "+i)
                for j in var:
                    if i == "daily.aqm.plot.py":
                      jobid="plot_"+envir+"_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    if i == "daily.aqm.plot_overlay.py":
                      jobid="plot_"+envir+"obs_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    if i == "daily.aqm.plot_bc.py":
                      jobid="plot_"+envir+"bc_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    if i == "daily.aqm.plot_bc_overlay.py":
                      jobid="plot_"+envir+"bcobs_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    plot_script=os.path.join(os.getcwd(),jobid+".sh")
                    logfile=log_dir+"/"+jobid+".log"
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    if os.path.exists(logfile):
                        os.remove(logfile)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash\n")
                        sh.write("#PBS -o "+logfile+"\n")
                        sh.write("#PBS -e "+logfile+"\n")
                        sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                        sh.write("#PBS -N j"+jobid+"\n")
                        sh.write("#PBS -q dev_transfer\n")
                        sh.write("#PBS -A AQM-DEV\n")
                        sh.write("#PBS -l walltime="+task_cpu+"\n")
                        sh.write("###PBS -l debug=true\n")
                        ## sh.write("module load envvar/"+envvar_ver+"\n")
                        ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                        ## sh.write("module load intel/"+intel_ver+"\n")
                        ## sh.write("module load craype/"+craype_ver+"\n")
                        ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                        ## sh.write("module load python/"+python_ver+"\n")
                        ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                        sh.write("# \n")
                        sh.write("export OMP_NUM_THREADS=1\n")
                        sh.write("# \n")
                        sh.write("\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("run_script = "+plot_script)
                    print("log file   = "+logfile)
                    subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                    msg="        python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == "daily_aqm_grib2_overlay_p1.py":
                print("    Start processing "+i)
                for j in var:
                    jobid="pgribp1_"+envir+"bcobs_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    plot_script=os.path.join(os.getcwd(),jobid+".sh")
                    logfile=log_dir+"/"+jobid+".log"
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    if os.path.exists(logfile):
                        os.remove(logfile)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash\n")
                        sh.write("#PBS -o "+logfile+"\n")
                        sh.write("#PBS -e "+logfile+"\n")
                        sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                        sh.write("#PBS -N j"+jobid+"\n")
                        sh.write("#PBS -q dev_transfer\n")
                        sh.write("#PBS -A AQM-DEV\n")
                        sh.write("#PBS -l walltime="+task_cpu+"\n")
                        sh.write("###PBS -l debug=true\n")
                        ## sh.write("module load envvar/"+envvar_ver+"\n")
                        ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                        ## sh.write("module load intel/"+intel_ver+"\n")
                        ## sh.write("module load craype/"+craype_ver+"\n")
                        ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                        ## sh.write("module load python/"+python_ver+"\n")
                        ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                        sh.write("# \n")
                        sh.write("export OMP_NUM_THREADS=1\n")
                        sh.write("# \n")
                        sh.write("\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+"_bc "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("run_script = "+plot_script)
                    print("log file   = "+logfile)
                    subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                    msg="        python "+i+" "+envir+"bcobs "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == "daily_aqm_grib2_overlay_p2.py":
                print("    Start processing "+i)
                for j in var:
                    jobid="pgribp2_"+envir+"bcobs_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    plot_script=os.path.join(os.getcwd(),jobid+".sh")
                    logfile=log_dir+"/"+jobid+".log"
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    if os.path.exists(logfile):
                        os.remove(logfile)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash\n")
                        sh.write("#PBS -o "+logfile+"\n")
                        sh.write("#PBS -e "+logfile+"\n")
                        sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                        sh.write("#PBS -N j"+jobid+"\n")
                        sh.write("#PBS -q dev_transfer\n")
                        sh.write("#PBS -A AQM-DEV\n")
                        sh.write("#PBS -l walltime="+task_cpu+"\n")
                        sh.write("###PBS -l debug=true\n")
                        ## sh.write("module load envvar/"+envvar_ver+"\n")
                        ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                        ## sh.write("module load intel/"+intel_ver+"\n")
                        ## sh.write("module load craype/"+craype_ver+"\n")
                        ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                        ## sh.write("module load python/"+python_ver+"\n")
                        ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                        sh.write("# \n")
                        sh.write("export OMP_NUM_THREADS=1\n")
                        sh.write("# \n")
                        sh.write("\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+"_bc "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("run_script = "+plot_script)
                    print("log file   = "+logfile)
                    subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                    msg="        python "+i+" "+envir+"bcobs "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
            if i == "daily_aqm_grib2_overlay.py":
                print("    Start processing "+i)
                for j in var:
                    jobid="pgrib_"+envir+"_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    plot_script=os.path.join(os.getcwd(),jobid+".sh")
                    logfile=log_dir+"/"+jobid+".log"
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    if os.path.exists(logfile):
                        os.remove(logfile)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash\n")
                        sh.write("#PBS -o "+logfile+"\n")
                        sh.write("#PBS -e "+logfile+"\n")
                        sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                        sh.write("#PBS -N j"+jobid+"\n")
                        sh.write("#PBS -q dev_transfer\n")
                        sh.write("#PBS -A AQM-DEV\n")
                        sh.write("#PBS -l walltime="+task_cpu+"\n")
                        sh.write("###PBS -l debug=true\n")
                        ## sh.write("module load envvar/"+envvar_ver+"\n")
                        ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                        ## sh.write("module load intel/"+intel_ver+"\n")
                        ## sh.write("module load craype/"+craype_ver+"\n")
                        ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                        ## sh.write("module load python/"+python_ver+"\n")
                        ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                        sh.write("# \n")
                        sh.write("export OMP_NUM_THREADS=1\n")
                        sh.write("# \n")
                        sh.write("\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("run_script = "+plot_script)
                    print("log file   = "+logfile)
                    subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                    msg="        python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == "daily.aqm.plot_specs1.py" or i == "daily.aqm.plot_specs2.py" or i == "daily.aqm.plot_specs3.py" or i == "daily.aqm.plot_specs4.py" or i == "daily.aqm.plot_spec_xsel.py":
                print("    Start processing "+i)
                if i == "daily.aqm.plot_specs1.py":
                    jobid="plot_sp1_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "daily.aqm.plot_specs2.py":
                    jobid="plot_sp2_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "daily.aqm.plot_specs3.py":
                    jobid="plot_sp3_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "daily.aqm.plot_specs4.py":
                    jobid="plot_sp4_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "diff_aqm_plot_bc.py":
                print("    Start processing "+i)
                for j in var:
                    jobid="plot_diffbc_"+envir+"_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    plot_script=os.path.join(os.getcwd(),jobid+".sh")
                    logfile=log_dir+"/"+jobid+".log"
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    if os.path.exists(logfile):
                        os.remove(logfile)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash\n")
                        sh.write("#PBS -o "+logfile+"\n")
                        sh.write("#PBS -e "+logfile+"\n")
                        sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                        sh.write("#PBS -N j"+jobid+"\n")
                        sh.write("#PBS -q dev_transfer\n")
                        sh.write("#PBS -A AQM-DEV\n")
                        sh.write("#PBS -l walltime="+task_cpu+"\n")
                        sh.write("###PBS -l debug=true\n")
                        ## sh.write("module load envvar/"+envvar_ver+"\n")
                        ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                        ## sh.write("module load intel/"+intel_ver+"\n")
                        ## sh.write("module load craype/"+craype_ver+"\n")
                        ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                        ## sh.write("module load python/"+python_ver+"\n")
                        ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                        sh.write("# \n")
                        sh.write("export OMP_NUM_THREADS=1\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("run_script = "+plot_script)
                    print("log file   = "+logfile)
                    subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                    msg="        python "+i+" "+envir+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == "diff.aqm.plot_bc.py":
                print("    Start processing "+i)
                for j in var:
                    jobid="plot_diffbc_"+envir+"_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    plot_script=os.path.join(os.getcwd(),jobid+".sh")
                    logfile=log_dir+"/"+jobid+".log"
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    if os.path.exists(logfile):
                        os.remove(logfile)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash\n")
                        sh.write("#PBS -o "+logfile+"\n")
                        sh.write("#PBS -e "+logfile+"\n")
                        sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                        sh.write("#PBS -N j"+jobid+"\n")
                        sh.write("#PBS -q dev_transfer\n")
                        sh.write("#PBS -A AQM-DEV\n")
                        sh.write("#PBS -l walltime="+task_cpu+"\n")
                        sh.write("###PBS -l debug=true\n")
                        ## sh.write("module load envvar/"+envvar_ver+"\n")
                        ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                        ## sh.write("module load intel/"+intel_ver+"\n")
                        ## sh.write("module load craype/"+craype_ver+"\n")
                        ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                        ## sh.write("module load python/"+python_ver+"\n")
                        ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                        sh.write("# \n")
                        sh.write("export OMP_NUM_THREADS=1\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("run_script = "+plot_script)
                    print("log file   = "+logfile)
                    subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                    msg="        python "+i+" "+envir+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == ( "diff.aqm.plot_specs1.py" or i == "diff.aqm.plot_specs2.py" or i == "diff.aqm.plot_specs3.py" or i == "diff.aqm.plot_specs4.py" ) and envir != "prod":
                print("    Start processing "+i)
                if i == "diff.aqm.plot_specs1.py":
                    jobid="plot_diff_sp1_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "diff.aqm.plot_specs2.py":
                    jobid="plot_diff_sp2_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "diff.aqm.plot_specs3.py":
                    jobid="plot_diff_sp3_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "diff.aqm.plot_specs4.py":
                    jobid="plot_diff_sp4_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                if envir == "para":
                    if i == "diff.aqm.plot_specs1.py":
                        jobid="plot_diff_sp1_"+envir+"_6d_"+cyc+"_"+date.strftime(YMD_date_format)
                    if i == "diff.aqm.plot_specs2.py":
                        jobid="plot_diff_sp2_"+envir+"_6d_"+cyc+"_"+date.strftime(YMD_date_format)
                    if i == "diff.aqm.plot_specs3.py":
                        jobid="plot_diff_sp3_"+envir+"_6d_"+cyc+"_"+date.strftime(YMD_date_format)
                    if i == "diff.aqm.plot_specs4.py":
                        jobid="plot_diff_sp4_"+envir+"_6d_"+cyc+"_"+date.strftime(YMD_date_format)
                    plot_script=os.path.join(os.getcwd(),jobid+".sh")
                    logfile=log_dir+"/"+jobid+".log"
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    if os.path.exists(logfile):
                        os.remove(logfile)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash\n")
                        sh.write("#PBS -o "+logfile+"\n")
                        sh.write("#PBS -e "+logfile+"\n")
                        sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                        sh.write("#PBS -N j"+jobid+"\n")
                        sh.write("#PBS -q dev_transfer\n")
                        sh.write("#PBS -A AQM-DEV\n")
                        sh.write("#PBS -l walltime="+task_cpu+"\n")
                        sh.write("###PBS -l debug=true\n")
                        ## sh.write("module load envvar/"+envvar_ver+"\n")
                        ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                        ## sh.write("module load intel/"+intel_ver+"\n")
                        ## sh.write("module load craype/"+craype_ver+"\n")
                        ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                        ## sh.write("module load python/"+python_ver+"\n")
                        ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                        sh.write("# \n")
                        sh.write("export OMP_NUM_THREADS=1\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+" para6d "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("run_script = "+plot_script)
                    print("log file   = "+logfile)
                    subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                    msg="        python "+i+" "+envir+" para6d "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == "diff.aqm.plot.py" and envir == "para":
                print("    Start processing "+i)
                for j in var:
                    jobid="plot_diff_6d_"+envir+"_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    plot_script=os.path.join(os.getcwd(),jobid+".sh")
                    logfile=log_dir+"/"+jobid+".log"
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    if os.path.exists(logfile):
                        os.remove(logfile)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash\n")
                        sh.write("#PBS -o "+logfile+"\n")
                        sh.write("#PBS -e "+logfile+"\n")
                        sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                        sh.write("#PBS -N j"+jobid+"\n")
                        sh.write("#PBS -q dev_transfer\n")
                        sh.write("#PBS -A AQM-DEV\n")
                        sh.write("#PBS -l walltime="+task_cpu+"\n")
                        sh.write("###PBS -l debug=true\n")
                        ## sh.write("module load envvar/"+envvar_ver+"\n")
                        ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                        ## sh.write("module load intel/"+intel_ver+"\n")
                        ## sh.write("module load craype/"+craype_ver+"\n")
                        ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                        ## sh.write("module load python/"+python_ver+"\n")
                        ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                        sh.write("# \n")
                        sh.write("export OMP_NUM_THREADS=1\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+" para6d "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("run_script = "+plot_script)
                    print("log file   = "+logfile)
                    subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                    msg="        python "+i+" "+envir+" para6d "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if ( i == "daily.aqm.plot_met_v6s1.py" or i == "daily.aqm.plot_met_v6s2.py" or i == "daily.aqm.plot_met_v6s3.py" or i == "daily.aqm.plot_met_v6s4.py" or i == "daily.aqm.plot_met_v6s5.py" ):
                print("    Start processing "+i)
                if i == "daily.aqm.plot_met_v6s1.py":
                    jobid="plot_met1_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "daily.aqm.plot_met_v6s2.py":
                    jobid="plot_met2_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "daily.aqm.plot_met_v6s3.py":
                    jobid="plot_met3_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "daily.aqm.plot_met_v6s4.py":
                    jobid="plot_met4_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if ( i == "diff.aqm.plot_met_v6s1.py" or i == "diff.aqm.plot_met_v6s2.py" or i == "diff.aqm.plot_met_v6s3.py" or i == "diff.aqm.plot_met_v6s4.py" or i == "diff.aqm.plot_met_v6s5.py" ) and envir != "prod":
                print("    Start processing "+i)
                if i == "diff.aqm.plot_diff_met_v6s1.py":
                    jobid="plot_diff_met1_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "diff.aqm.plot_diff_met_v6s2.py":
                    jobid="plot_diff_met2_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "diff.aqm.plot_diff_met_v6s3.py":
                    jobid="plot_diff_met3_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                if i == "diff.aqm.plot_diff_met_v6s4.py":
                    jobid="plot_diff_met4_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.col_v6.py":
                print("    Start processing "+i)
                for j in col_var:
                    jobid="plot_col_"+envir+"_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    plot_script=os.path.join(os.getcwd(),jobid+".sh")
                    logfile=log_dir+"/"+jobid+".log"
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    if os.path.exists(logfile):
                        os.remove(logfile)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash\n")
                        sh.write("#PBS -o "+logfile+"\n")
                        sh.write("#PBS -e "+logfile+"\n")
                        sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                        sh.write("#PBS -N j"+jobid+"\n")
                        sh.write("#PBS -q dev_transfer\n")
                        sh.write("#PBS -A AQM-DEV\n")
                        sh.write("#PBS -l walltime="+task_cpu+"\n")
                        sh.write("###PBS -l debug=true\n")
                        ## sh.write("module load envvar/"+envvar_ver+"\n")
                        ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                        ## sh.write("module load intel/"+intel_ver+"\n")
                        ## sh.write("module load craype/"+craype_ver+"\n")
                        ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                        ## sh.write("module load python/"+python_ver+"\n")
                        ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                        sh.write("# \n")
                        sh.write("export OMP_NUM_THREADS=1\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("run_script = "+plot_script)
                    print("log file   = "+logfile)
                    subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                    msg="        python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == "daily.aqm.plot_dustemis.py":
                print("    Start processing "+i)
                jobid="plot_dustem_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.plot_fireemis.py" and envir != "prod":
                print("    Start processing "+i)
                jobid="plot_fireem_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "fireemis_fire_loc.py":
                print("    Start processing "+i)
                jobid="plot_fireloc_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "gbbepx_fire_loc.py":
                print("    Start processing "+i)
                jobid="plot_gbbepxloc_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.plot_fireemis_r.py" and envir != "prod":
                print("    Start processing "+i)
                jobid="plot_fireem_r_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.plot_dustloc.py":
                print("    Start processing "+i)
                jobid="plot_dustloc_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.plot_max_ave_overlay.py":
                print("    Start processing "+i)
                jobid="plot_maxave_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu2+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                print("    Start processing bias correction "+i)
                jobid="plot_maxave_"+envir+"bc_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu2+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+"_bc using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+"_bc "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+"_bc "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.plot_max_ave.py":
                print("    Start processing "+i)
                jobid="plot_maxave_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu2+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.plot_max_ave_bc.py":
                print("    Start processing "+i)
                jobid="plot_maxave_bc_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu2+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "diff.aqm.plot_max_ave_bc.py":
                print("    Start processing "+i)
                jobid="plot_diff_maxave_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu2+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.plot_aot.py":
                print("    Start processing "+i)
                jobid="plot_aot_"+envir+"_"+cyc+"_"+date.strftime(YMD_date_format)
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu+"\n")
                    sh.write("###PBS -l debug=true\n")
                    ## sh.write("module load envvar/"+envvar_ver+"\n")
                    ## sh.write("module load PrgEnv-intel/"+PrgEnv_intel_ver+"\n")
                    ## sh.write("module load intel/"+intel_ver+"\n")
                    ## sh.write("module load craype/"+craype_ver+"\n")
                    ## sh.write("module load cray-mpich/"+cray_mpich_ver+"\n")
                    ## sh.write("module load python/"+python_ver+"\n")
                    ## sh.write("module load netcdf/"+netcdf_ver+"\n")
                    sh.write("# \n")
                    sh.write("export OMP_NUM_THREADS=1\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
        ## msg=datetime.datetime.now()
        ## print("End   processing "+date.strftime(YMD_date_format)+" "+cyc+"Z Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    ## msg=datetime.datetime.now()
    ## print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    ## print("LOG file location "+working_dir)
    date = date + date_inc
