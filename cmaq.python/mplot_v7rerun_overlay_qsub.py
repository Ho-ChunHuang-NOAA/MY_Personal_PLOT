import sys
import shutil
import subprocess
import os
import numpy as np
import netCDF4 as netcdf
import logging
import datetime

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

script_dir=os.getcwd()
print("Script directory is "+script_dir)

user=os.environ['USER']
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

script_name = [ "dev_aqm_plot_max_ave_overlay.py", "dev_rrfs_plot_bc_overlay.py" ]
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
    cycle=[ "06", "12" ]
elif sel_cyc == "06":
    cycle=[ "06" ]
elif sel_cyc == "12":
    cycle=[ "12" ]
else:
    print("seletced cycle"+sel_cyc+" can not be recongized.")
    sys.exit()

ic=0
date=sdate
while date <= edate:
    for cyc in cycle:
        msg=datetime.datetime.now()
        print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+"Z Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        for i in script_name:
            msg=datetime.datetime.now()
            if i == "dev_aqm_plot_max_ave_overlay.py":
                print("    Start processing bias correction "+i)
                jobid="plot_maxaveobs_"+envir+"bc_"+cyc+"_"+date.strftime(YMD_date_format)
                ftpid="ftp_maxaveobs_"+envir+"bc_"+cyc+"_"+date.strftime(YMD_date_format)
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
                with open(ftp_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+ftplog+"\n")
                    sh.write("#PBS -e "+ftplog+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=10GB:prepost=true\n")
                    sh.write("#PBS -N j"+ftpid+"\n")
                    sh.write("#PBS -q dev_transfer\n")
                    sh.write("#PBS -A AQM-DEV\n")
                    sh.write("#PBS -l walltime="+task_cpu1+"\n")
                    sh.write("###PBS -l debug=true\n")
                    sh.write("set -x\n")
                    sh.write("    cd "+working_dir+"\n")
                    sh.write("   python "+rzdm_file+" "+envir+"_bc "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash\n")
                    sh.write("#PBS -o "+logfile+"\n")
                    sh.write("#PBS -e "+logfile+"\n")
                    sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=10GB:prepost=true\n")
                    sh.write("#PBS -N j"+jobid+"\n")
                    sh.write("#PBS -q dev\n")
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
                    sh.write("    cat "+ftp_script+" | qsub\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("run_script = "+plot_script)
                print("log file   = "+logfile)
                subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                msg="        python "+i+" "+envir+"_bc "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "dev_rrfs_plot_bc_overlay.py":
                print("    Start processing "+i)
                for j in var:
                    jobid="plot_"+envir+"bcobs_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    ftpid="ftp_"+envir+"bcobs_"+j+"_"+cyc+"_"+date.strftime(YMD_date_format)
                    plot_script=os.path.join(os.getcwd(),jobid+".sh")
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    logfile=log_dir+"/"+jobid+".log"
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
                    with open(ftp_script, 'a') as sh:
                        sh.write("#!/bin/bash\n")
                        sh.write("#PBS -o "+ftplog+"\n")
                        sh.write("#PBS -e "+ftplog+"\n")
                        sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=10GB:prepost=true\n")
                        sh.write("#PBS -N j"+ftpid+"\n")
                        sh.write("#PBS -q dev_transfer\n")
                        sh.write("#PBS -A AQM-DEV\n")
                        sh.write("#PBS -l walltime="+task_cpu1+"\n")
                        sh.write("###PBS -l debug=true\n")
                        sh.write("set -x\n")
                        sh.write("    cd "+working_dir+"\n")
                        sh.write("   python "+rzdm_file+" "+envir+"_bc "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash\n")
                        sh.write("#PBS -o "+log_dir+"/"+jobid+".log\n")
                        sh.write("#PBS -e "+log_dir+"/"+jobid+".log\n")
                        sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=10GB:prepost=true\n")
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
                        sh.write("# \n")
                        sh.write("\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+"_bc "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("    cat "+ftp_script+" | qsub\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("run_script = "+plot_script)
                    print("log file   = "+logfile)
                    subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
                    msg="        python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
    date = date + date_inc
