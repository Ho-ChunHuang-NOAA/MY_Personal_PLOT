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
    print("you must set 4 arguments as [g16|g18|g1618|all] quality_flag[high|med|all] start_date end_date")
    sys.exit()
else:
    sel_sat= sys.argv[1]
    sel_qc= sys.argv[2]
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
working_dir=stmp_dir+"/"+workid
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

os.chdir(working_dir)

msg_file=f"{working_dir}/msg_{sel_sat}_{sel_qc}_{start_date}"
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
working_dir=os.path.join(run_root,f"abi_aod_{sel_sat}_{sel_qc}",f"run_start_time_{start_date}")
if os.path.exists(working_dir):
    os.chdir(working_dir)
else:
    os.makedirs(working_dir)
    os.chdir(working_dir)

script_name = [
              "dev_dcomabi_plot_aot_aqmv7.py"
              "dev_dcomabi_plot_aot_gefs.py"
              ]
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

if sel_qc == "all":
    qc_list=[ "high", "medium", "low" ]
elif sel_qc == "high":
    qc_list=[ "high" ]
elif sel_qc == "medium":
    qc_list=[ "medium" ]
elif sel_qc == "low":
    qc_list=[ "low" ]
else:
    print("input qc_listiable "+sel_qc+" can not be recongized.")
    sys.exit()
num_qc_list=len(qc_list)

if sel_sat == "all":
    satid=["g16", "g18", "g1618" ]
elif sel_sat == "g16" or sel_sat == "g18" or sel_sat == "g1618":
    satid=[]
    satid.append(sel_sat)
else:
    print(f"Input sat ID = {sel_sat}, is not defined")
    sys.exit()

ic=0
date=sdate
while date <= edate:
    YMD=date.strftime(YMD_date_format)
    for i in script_name:
        if i == "dev_dcomabi_plot_aot_aqmv7.py":
            print("    Start processing "+i)
            scanid=[ "AODC" ]
            for qc in qc_list:
                for sat in satid:
                    for scan in scanid:
                        jobid=f"plot_dcomabi_aod_{sat}_{scan}_{qc}_{YMD}"
                        ftpid=f"ftp_dcomabi_aod_{sat}_{scan}_{qc}_{YMD}"
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
                            fsh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                            fsh.write("#PBS -N j"+ftpid+"\n")
                            fsh.write("#PBS -q dev_transfer\n")
                            fsh.write("#PBS -A AQM-DEV\n")
                            fsh.write("#PBS -l walltime="+task_cpu1+"\n")
                            fsh.write("###PBS -l debug=true\n")
                            fsh.write("set -x\n")
                            fsh.write("    cd "+working_dir+"\n")
                            fsh.write(f"    python {rzdm_file} {sat} {scan} {qc} {YMD} {YMD}\n")
                            fsh.write("\n")
                            fsh.write("exit\n")
                        with open(plot_script, 'a') as sh:
                            sh.write("#!/bin/bash\n")
                            sh.write("#PBS -o "+logfile+"\n")
                            sh.write("#PBS -e "+logfile+"\n")
                            sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=10GB:prepost=true\n")
                            sh.write("#PBS -N j"+jobid+"\n")
                            sh.write("#PBS -q dev\n")
                            sh.write("#PBS -A AQM-DEV\n")
                            sh.write("#PBS -l walltime="+task_cpu+"\n")
                            sh.write("###PBS -l debug=true\n")
                            sh.write("# \n")
                            sh.write("export OMP_NUM_THREADS=1\n")
                            sh.write("\n")
                            sh.write("##\n")
                            sh.write("##  Plot ABI AOD\n")
                            sh.write("##\n")
                            sh.write("set -x\n")
                            sh.write("\n")
                            sh.write("   cd "+working_dir+"\n")
                            sh.write(f"    python {i} {sat} {scan} {qc} {YMD} {YMD}\n")
                            if flag_ftp:
                                sh.write("    cat "+ftp_script+" | qsub\n")
                            sh.write("\n")
                            sh.write("exit\n")
                        print("run_script = "+plot_script)
                        print("log file   = "+logfile)
                        subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                        ## subprocess.call(["cat "+plot_script], shell=True)
        if i == "dev_dcomabi_plot_aot_gefs.py":
            print("    Start processing "+i)
            scanid=[ "AODF" ]
            for qc in qc_list:
                for sat in satid:
                    for scan in scanid:
                        jobid=f"plot_dcomabi_aod_{sat}_{scan}_{qc}_{YMD}"
                        ftpid=f"ftp_dcomabi_aod_{sat}_{scan}_{qc}_{YMD}"
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
                            fsh.write("#PBS -l place=shared,select=1:ncpus=1:mem=5GB\n")
                            fsh.write("#PBS -N j"+ftpid+"\n")
                            fsh.write("#PBS -q dev_transfer\n")
                            fsh.write("#PBS -A AQM-DEV\n")
                            fsh.write("#PBS -l walltime="+task_cpu1+"\n")
                            fsh.write("###PBS -l debug=true\n")
                            fsh.write("set -x\n")
                            fsh.write("    cd "+working_dir+"\n")
                            fsh.write(f"    python {rzdm_file} {sat} {scan} {qc} {YMD} {YMD}\n")
                            fsh.write("\n")
                            fsh.write("exit\n")
                        with open(plot_script, 'a') as sh:
                            sh.write("#!/bin/bash\n")
                            sh.write("#PBS -o "+logfile+"\n")
                            sh.write("#PBS -e "+logfile+"\n")
                            sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=10GB:prepost=true\n")
                            sh.write("#PBS -N j"+jobid+"\n")
                            sh.write("#PBS -q dev\n")
                            sh.write("#PBS -A AQM-DEV\n")
                            sh.write("#PBS -l walltime="+task_cpu+"\n")
                            sh.write("###PBS -l debug=true\n")
                            sh.write("# \n")
                            sh.write("export OMP_NUM_THREADS=1\n")
                            sh.write("\n")
                            sh.write("##\n")
                            sh.write("##  Plot ABI AOD\n")
                            sh.write("##\n")
                            sh.write("set -x\n")
                            sh.write("\n")
                            sh.write("   cd "+working_dir+"\n")
                            sh.write(f"    python {i} {sat} {scan} {qc} {YMD} {YMD}\n")
                            if flag_ftp:
                                sh.write("    cat "+ftp_script+" | qsub\n")
                            sh.write("\n")
                            sh.write("exit\n")
                        print("run_script = "+plot_script)
                        print("log file   = "+logfile)
                        subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                        ## subprocess.call(["cat "+plot_script], shell=True)
    date = date + date_inc
