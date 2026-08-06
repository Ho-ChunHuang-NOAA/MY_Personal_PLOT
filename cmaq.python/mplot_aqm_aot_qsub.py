import sys
import shutil
import subprocess
import os
import numpy as np
import netCDF4 as netcdf
import logging
import datetime

user=os.environ['USER']

flag_ftp=False
flag_ftp=True

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
if len(sys.argv) < 4:
    print("you must set 4 arguments as model[prod|para|...] cycle[06|12|all]  start_date end_date")
    sys.exit()
else:
    envir = sys.argv[1]
    sel_cyc = sys.argv[2]
    start_date = sys.argv[3]
    end_date = sys.argv[4]

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

msg_file=working_dir+"/aod_msg_"+start_date+"_"+sel_cyc
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
working_dir=os.path.join(run_root,envir,start_date)
if os.path.exists(working_dir):
    os.chdir(working_dir)
else:
    os.makedirs(working_dir)
    os.chdir(working_dir)

if envir == "prod":
    script_name = [
                  "dev_plot_aot_aqmv7_p1.py",
                  "dev_plot_aot_aqmv7_p2.py",
                  "dev_plot_aot_aqmv7_p3.py",
                  "dev_plot_aot_aqmv7_p4.py",
                  "dev_plot_aot_aqmv7_p5.py"
                  ]
else:
    script_name = [
                  "dev_plot_aot_aqmv7_p1.py",
                  "dev_plot_aot_aqmv7_p2.py",
                  "dev_plot_aot_aqmv7_p3.py",
                  "dev_plot_aot_aqmv7_p4.py",
                  "dev_plot_aot_aqmv7_p5.py"
                  ]
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
    filein=i
    rzdm_file="rzdm"+filein[3:]
    print(rzdm_file)
    from_file=os.path.join(script_dir,rzdm_file)
    to_file=os.path.join(working_dir,rzdm_file)
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

sdate = datetime.datetime.strptime(start_date, '%Y%m%d')
edate = datetime.datetime.strptime(end_date, '%Y%m%d')
YMDH_date_format = "%Y%m%d/%H"
YMD_date_format = "%Y%m%d"
YM_date_format = "%Y%m"
Y_date_format = "%Y"
M_date_format = "%m"
D_date_format = "%d"
H_date_format = "%H"
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

var=[ "aod" ]
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
        YMD=date.strftime(YMD_date_format)
        msg=datetime.datetime.now()
        for i in script_name:
            if i in [ "dev_plot_aot_aqmv7_p1.py", "dev_plot_aot_aqmv7_p2.py", "dev_plot_aot_aqmv7_p3.py", "dev_plot_aot_aqmv7_p4.py", "dev_plot_aot_aqmv7_p5.py" ]:
                print("    Start processing "+i)
                # Splits by '_' to get 'p1.py', then splits by '.' to get 'p1'
                if i.startswith("dev_plot_aot_aqmv7_"):
                    sec_id = i.split("_")[-1].split(".")[0]
                else:
                    sec_id = np
                jobid=f"{sec_id}_plot_{envir}_{cyc}_{YMD}"
                ftpid=f"{sec_id}_ftp_{envir}_{cyc}_{YMD}"
                plot_script=os.path.join(os.getcwd(),jobid+".sh")
                logfile=log_dir+"/"+jobid+".log"
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                if os.path.exists(logfile):
                    os.remove(logfile)
                filein=i
                rzdm_file="rzdm"+filein[3:]
                ftp_script=os.path.join(os.getcwd(),ftpid+".sh")
                ftplog=log_dir+"/"+ftpid+".log"
                if os.path.exists(ftp_script):
                    os.remove(ftp_script)
                if os.path.exists(ftplog):
                    os.remove(ftplog)
                with open(ftp_script, 'a') as fsh:
                    fsh.write("#!/bin/bash\n")
                    fsh.write("#PBS -o "+ftplog+"\n")
                    fsh.write("#PBS -e "+ftplog+"\n")
                    fsh.write("#PBS -l place=shared,select=1:ncpus=1:mem=4GB\n")
                    fsh.write("#PBS -N j"+ftpid+"\n")
                    fsh.write("#PBS -q dev_transfer\n")
                    fsh.write("#PBS -A AQM-DEV\n")
                    fsh.write("#PBS -l walltime="+task_cpu1+"\n")
                    fsh.write("###PBS -l debug=true\n")
                    fsh.write("set -x\n")
                    fsh.write("    cd "+working_dir+"\n")
                    fsh.write(f"   python {rzdm_file} {cyc} {YMD} {YMD}\n")
                    fsh.write("\n")
                    fsh.write("exit\n")
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=10GB\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev\n")
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
                    sh.write(f"   python {i} {envir} {cyc} {YMD} {YMD}\n")
                    if flag_ftp:
                        sh.write("    cat "+ftp_script+" | qsub\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg=f"   python {i} {envir} {cyc} {YMD} {YMD}"
                print(msg)
    date = date + date_inc
