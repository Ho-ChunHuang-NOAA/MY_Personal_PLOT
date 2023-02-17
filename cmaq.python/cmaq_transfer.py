import sys
import datetime
import shutil
import os
import subprocess
import fnmatch

user=os.environ['USER']
site=os.environ['SITE']
current_dir=os.getcwd()
if site.upper() == 'MARS':
    remote="venus"
elif site.upper() == 'VENUS':
    remote="mars"
else:
    print("System name not defined for this script")
    sys.exit()

model="aqm"
envir = [ "para6" ]
print("Current location = "+current_dir)
data_dir="/gpfs/hps3/emc/meso/noscrub/"+user+"/com"
log_dir="/lfs/h2/emc/ptmp/"+user+"/batch_logs"
working_dir="/gpfs/dell2/"+user+"/transfer"
if not os.path.exists(working_dir):
    os.mkdir(working_dir)
os.chdir(working_dir)

if len(sys.argv) < 2:
    print("you must provide 2 arguments for start_date end_date")
    sys.exit()
else:
    start_date = sys.argv[1]
    end_date = sys.argv[2]

sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:]), 00)
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:]), 23)
date_inc = datetime.timedelta(hours=24)
hour_inc = datetime.timedelta(hours=1)

YMD_date_format = "%Y%m%d"
MD_date_format = "%m%d"
H_date_format = "%H"

date=sdate
ic=0
while date <= edate:
    for exp in envir:
        ic=ic+1
        if ic < 10:
           icnt=str(format(ic,'00d'))
        elif ic < 100:
           icnt=str(format(ic,'02d'))
        elif ic < 1000:
           icnt=str(format(ic,'3d'))
        else:
            print("exceed 999 maximum file limit")
            sys.exit()
        icnt=str(format(ic,'03d'))
        transfer_file=os.path.join(os.getcwd(),"trans_cmaq2"+remote+"_"+icnt+".sh")
        print("Creating transfer file "+transfer_file)
        if os.path.exists(transfer_file):
            os.remove(transfer_file)
        with open(transfer_file, 'a') as sh:
            root_dir=data_dir+"/"+model+"/"+exp
            sh.write("#!/bin/bash -l\n")
            sh.write("#PBS -o "+log_dir+"/"+model+"_"+icnt+"_scp.out\n")
            sh.write("#PBS -e "+log_dir+"/"+model+"_"+icnt+"_scp.out\n")
            sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=4500MB\n")
            sh.write("#PBS -N j"+model+"_"+icnt+"_scp\n")
            sh.write("#PBS -q dev_transfer\n")
            sh.write("#PBS -A AQM-DEV\n")
            sh.write("#PBS -l walltime="+task_cpu+"\n")
            sh.write("# \n")
            sh.write("#BSUB -M 3000\n")
            sh.write("\n")
            ## sh.write("#%include <head.h>\n")
            ## sh.write("#%include <envir-xc40.h>\n")
            sh.write("\n")
            sh.write("##\n")
            sh.write("##  Provide fix date daily "+model+" data transfer\n")
            sh.write("##\n")
            sh.write("set -x\n")
            sh.write("\n")
            sh.write("   root_dir="+root_dir+"\n")
            sh.write("   dir=${root_dir}/"+model+"."+date.strftime(YMD_date_format)+"\n")
            sh.write("   if [ -d ${dir} ]; then\n")
            sh.write("      echo \"FIND ${dir}\"\n")
            sh.write("      scp -pr ${dir}  "+user+"@"+remote+":${root_dir}\n")
            sh.write("   else\n")
            sh.write("       echo \"Can not find ${dir}\"\n")
            sh.write("   fi\n")
            sh.write("\n")
            sh.write("exit\n")
        print("submit "+transfer_file)
        subprocess.call(["cat "+transfer_file+" | qsub"], shell=True)
    date = date + date_inc
