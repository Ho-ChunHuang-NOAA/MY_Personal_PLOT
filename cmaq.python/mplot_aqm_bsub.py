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

script_dir=os.getcwd()
print("Script directory is "+script_dir)

### if os.path.exists(figdir):
###     shutil.rmtree(figdir)
### os.makedirs(figdir)`
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

## set proper stmp and ptmp location.  can not access /gpfs/dell1 and  /gpfs/dell3 on production machine
working_dir="/gpfs/dell2/stmp/"+user
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

working_dir="/gpfs/dell2/stmp/"+user+"/test"
if not os.path.exists(working_dir):
    os.mkdir(working_dir)

msg_file=working_dir+"/devmachine"
subprocess.call(["cat /etc/dev > "+msg_file], shell=True)
if os.path.isfile(msg_file):
    with open(msg_file, 'r') as sh:
        line=sh.readline()
        dev_machine=line.rstrip()
    sh.close()

if dev_machine != "":
    if site.lower() == dev_machine.lower():
        print("DEV machine is "+dev_machine+"  Current machine is develop machine")
        stmp_dir="/gpfs/dell1/stmp/"+user
        if not os.path.exists(stmp_dir):
            os.mkdir(stmp_dir)
        ptmp_dir="/gpfs/dell1/ptmp/"+user
        if not os.path.exists(ptmp_dir):
            os.mkdir(ptmp_dir)
        log_dir=ptmp_dir+"/batch_logs"
    else:
        print("DEV machine is "+dev_machine+"  Current machine is production machine")
        stmp_dir="/gpfs/dell2/stmp/"+user
        if not os.path.exists(stmp_dir):
            os.mkdir(stmp_dir)
        ptmp_dir="/gpfs/dell2/ptmp/"+user
        if not os.path.exists(ptmp_dir):
            os.mkdir(ptmp_dir)
        log_dir=ptmp_dir+"/batch_logs"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

run_root=stmp_dir+"/run_python_script"
if not os.path.exists(run_root):
    os.mkdir(run_root)
## working_dir=os.path.join(run_root,envir,sel_var,sel_cyc,start_date)
working_dir=os.path.join(run_root,envir,start_date,sel_cyc)
if os.path.exists(working_dir):
    os.chdir(working_dir)
else:
    os.makedirs(working_dir)
    os.chdir(working_dir)

if envir == "prod":
    script_name = [
                  "daily.aqm.plot.py", "daily.aqm.plot_bc.py",
                  "daily.aqm.plot_specs1.py", "daily.aqm.plot_specs2.py",
                  "daily.aqm.plot_specs3.py", "daily.aqm.plot_specs4.py",
                  "daily.aqm.plot_met_v6s1.py", "daily.aqm.plot_met_v6s2.py",
                  "daily.aqm.plot_met_v6s3.py", "daily.aqm.plot_met_v6s4.py",
                  "daily.aqm.plot_met_v6s5.py",
                  "daily.aqm.plot_dustloc.py",
                  "gbbepx_fire_loc.py",
                  "diff.aqm.plot_bc.py"
                  ]
else:
    ## "diff.aqm.plot_48vs72.py",
    script_name = [
                  "daily.aqm.plot.py", "daily.aqm.plot_bc.py", 
                  "daily.aqm.plot_specs1.py", "daily.aqm.plot_specs2.py",
                  "daily.aqm.plot_specs3.py", "daily.aqm.plot_specs4.py",
                  "diff.aqm.plot.py",
                  "daily.aqm.plot_dustloc.py",
                  "fireemis_fire_loc.py",
                  "gbbepx_fire_loc.py",
                  "diff.aqm.plot_specs1.py", "diff.aqm.plot_specs2.py",
                  "diff.aqm.plot_specs3.py", "diff.aqm.plot_specs4.py",
                  "diff.aqm.plot_bc.py"
                  ]
    no_workk_script = [
                  "daily.aqm.plot_met_v6s1.py", "daily.aqm.plot_met_v6s2.py",
                  "daily.aqm.plot_met_v6s3.py", "daily.aqm.plot_met_v6s4.py",
                  "daily.aqm.plot_met_v6s5.py", 
                  "diff.aqm.plot_met_v6s1.py", "diff.aqm.plot_met_v6s2.py",
                  "diff.aqm.plot_met_v6s3.py", "diff.aqm.plot_met_v6s4.py",
                  "daily.aqm.plot_dustloc.py",
                  ]
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
            if i == "daily.aqm.plot.py" or i == "daily.aqm.plot_bc.py":
                print("    Start processing "+i)
                for j in var:
                    ic=ic+1
                    icnt=str(format(ic,'03d'))
                    plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                    print("Creating graphic script "+plot_script)
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash -l\n")
                        sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -n 1\n")
                        sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                        sh.write("#BSUB -q dev_transfer\n")
                        sh.write("#BSUB -P CMAQ-T2O\n")
                        sh.write("#BSUB -W 04:30\n")
                        sh.write("#BSUB -R affinity[core(1)]\n")
                        sh.write("#BSUB -M 3999\n")
                        sh.write("\n")
                        ## sh.write("#%include <head.h>\n")
                        ## sh.write("#%include <envir-xc40.h>\n")
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
                    print("submit "+plot_script)
                    subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                    msg="        python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == "daily.aqm.plot_specs1.py" or i == "daily.aqm.plot_specs2.py" or i == "daily.aqm.plot_specs3.py" or i == "daily.aqm.plot_specs4.py" or i == "daily.aqm.plot_spec_xsel.py":
                print("    Start processing "+i)
                ic=ic+1
                icnt=str(format(ic,'03d'))
                plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                print("Creating graphic script "+plot_script)
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash -l\n")
                    sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -n 1\n")
                    sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                    sh.write("#BSUB -q dev_transfer\n")
                    sh.write("#BSUB -P CMAQ-T2O\n")
                    sh.write("#BSUB -W 04:30\n")
                    sh.write("#BSUB -R affinity[core(1)]\n")
                    sh.write("#BSUB -M 3999\n")
                    sh.write("\n")
                    ## sh.write("#%include <head.h>\n")
                    ## sh.write("#%include <envir-xc40.h>\n")
                    sh.write("\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("submit "+plot_script)
                subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "diff.aqm.plot_bc.py":
                print("    Start processing "+i)
                for j in var:
                    ic=ic+1
                    icnt=str(format(ic,'03d'))
                    plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                    print("Creating graphic script "+plot_script)
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash -l\n")
                        sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"bc-"+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"bc-"+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -n 1\n")
                        sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                        sh.write("#BSUB -q dev_transfer\n")
                        sh.write("#BSUB -P CMAQ-T2O\n")
                        sh.write("#BSUB -W 04:30\n")
                        sh.write("#BSUB -R affinity[core(1)]\n")
                        sh.write("#BSUB -M 3999\n")
                        sh.write("\n")
                        ## sh.write("#%include <head.h>\n")
                        ## sh.write("#%include <envir-xc40.h>\n")
                        sh.write("\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("submit "+plot_script)
                    subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                    msg="        python "+i+" "+envir+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == ( "diff.aqm.plot_specs1.py" or i == "diff.aqm.plot_specs2.py" or i == "diff.aqm.plot_specs3.py" or i == "diff.aqm.plot_specs4.py" ) and envir != "prod":
                print("    Start processing "+i)
                ic=ic+1
                icnt=str(format(ic,'03d'))
                plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                print("Creating graphic script "+plot_script)
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash -l\n")
                    sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"-prod."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"-prod."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -n 1\n")
                    sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                    sh.write("#BSUB -q dev_transfer\n")
                    sh.write("#BSUB -P CMAQ-T2O\n")
                    sh.write("#BSUB -W 04:30\n")
                    sh.write("#BSUB -R affinity[core(1)]\n")
                    sh.write("#BSUB -M 8000\n")
                    sh.write("\n")
                    ## sh.write("#%include <head.h>\n")
                    ## sh.write("#%include <envir-xc40.h>\n")
                    sh.write("\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("submit "+plot_script)
                subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                msg="        python "+i+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                if envir == "para":
                    ic=ic+1
                    icnt=str(format(ic,'03d'))
                    plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                    print("Creating graphic script "+plot_script)
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash -l\n")
                        sh.write("#BSUB -o "+log_dir+"/"+i+".para6d-nco"+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -e "+log_dir+"/"+i+".para6d-nco"+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -n 1\n")
                        sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                        sh.write("#BSUB -q dev_transfer\n")
                        sh.write("#BSUB -P CMAQ-T2O\n")
                        sh.write("#BSUB -W 04:30\n")
                        sh.write("#BSUB -R affinity[core(1)]\n")
                        sh.write("#BSUB -M 3999\n")
                        sh.write("\n")
                        ## sh.write("#%include <head.h>\n")
                        ## sh.write("#%include <envir-xc40.h>\n")
                        sh.write("\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+" para6d "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("submit "+plot_script)
                    subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                    msg="        python "+i+" "+envir+" para6d "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                if envir == "para6z":
                    ic=ic+1
                    icnt=str(format(ic,'03d'))
                    plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                    print("Creating graphic script "+plot_script)
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash -l\n")
                        sh.write("#BSUB -o "+log_dir+"/"+i+".para6x-"+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -e "+log_dir+"/"+i+".para6x-"+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -n 1\n")
                        sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                        sh.write("#BSUB -q dev_transfer\n")
                        sh.write("#BSUB -P CMAQ-T2O\n")
                        sh.write("#BSUB -W 04:30\n")
                        sh.write("#BSUB -R affinity[core(1)]\n")
                        sh.write("#BSUB -M 3999\n")
                        sh.write("\n")
                        ## sh.write("#%include <head.h>\n")
                        ## sh.write("#%include <envir-xc40.h>\n")
                        sh.write("\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" para6x "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("submit "+plot_script)
                    subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                    msg="        python "+i+" para6 "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == "diff.aqm.plot.py" and envir == "para":
                print("    Start processing "+i)
                for j in var:
                    ic=ic+1
                    icnt=str(format(ic,'03d'))
                    plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                    print("Creating graphic script "+plot_script)
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash -l\n")
                        sh.write("#BSUB -o "+log_dir+"/"+i+".para6d-nco"+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -e "+log_dir+"/"+i+".para6d-nco"+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -n 1\n")
                        sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                        sh.write("#BSUB -q dev_transfer\n")
                        sh.write("#BSUB -P CMAQ-T2O\n")
                        sh.write("#BSUB -W 04:30\n")
                        sh.write("#BSUB -R affinity[core(1)]\n")
                        sh.write("#BSUB -M 3999\n")
                        sh.write("\n")
                        ## sh.write("#%include <head.h>\n")
                        ## sh.write("#%include <envir-xc40.h>\n")
                        sh.write("\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" "+envir+" para6d "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("submit "+plot_script)
                    subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                    msg="        python "+i+" "+envir+" para6d "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == "diff.aqm.plot.py" and envir == "para6z":
                print("    Start processing "+i)
                for j in var:
                    ic=ic+1
                    icnt=str(format(ic,'03d'))
                    plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                    print("Creating graphic script "+plot_script)
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash -l\n")
                        sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"-para6x."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"-para6x."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -n 1\n")
                        sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                        sh.write("#BSUB -q dev_transfer\n")
                        sh.write("#BSUB -P CMAQ-T2O\n")
                        sh.write("#BSUB -W 04:30\n")
                        sh.write("#BSUB -R affinity[core(1)]\n")
                        sh.write("#BSUB -M 3999\n")
                        sh.write("\n")
                        ## sh.write("#%include <head.h>\n")
                        ## sh.write("#%include <envir-xc40.h>\n")
                        sh.write("\n")
                        sh.write("##\n")
                        sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                        sh.write("##\n")
                        sh.write("set -x\n")
                        sh.write("\n")
                        sh.write("   cd "+working_dir+"\n")
                        sh.write("   python "+i+" para6x "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                        sh.write("\n")
                        sh.write("exit\n")
                    print("submit "+plot_script)
                    subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                    msg="        python "+i+" para6 "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if ( i == "daily.aqm.plot_met_v6s1.py" or i == "daily.aqm.plot_met_v6s2.py" or i == "daily.aqm.plot_met_v6s3.py" or i == "daily.aqm.plot_met_v6s4.py" or i == "daily.aqm.plot_met_v6s5.py" ):
                print("    Start processing "+i)
                ic=ic+1
                icnt=str(format(ic,'03d'))
                plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                print("Creating graphic script "+plot_script)
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash -l\n")
                    sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -n 1\n")
                    sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                    sh.write("#BSUB -q dev_transfer\n")
                    sh.write("#BSUB -P CMAQ-T2O\n")
                    sh.write("#BSUB -W 04:30\n")
                    sh.write("#BSUB -R affinity[core(1)]\n")
                    sh.write("#BSUB -M 8000\n")
                    sh.write("\n")
                    ## sh.write("#%include <head.h>\n")
                    ## sh.write("#%include <envir-xc40.h>\n")
                    sh.write("\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("submit "+plot_script)
                subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if ( i == "diff.aqm.plot_met_v6s1.py" or i == "diff.aqm.plot_met_v6s2.py" or i == "diff.aqm.plot_met_v6s3.py" or i == "diff.aqm.plot_met_v6s4.py" or i == "diff.aqm.plot_met_v6s5.py" ) and envir != "prod":
                print("    Start processing "+i)
                ic=ic+1
                icnt=str(format(ic,'03d'))
                plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                print("Creating graphic script "+plot_script)
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash -l\n")
                    sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"-para6x."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"-para6x."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -n 1\n")
                    sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                    sh.write("#BSUB -q dev_transfer\n")
                    sh.write("#BSUB -P CMAQ-T2O\n")
                    sh.write("#BSUB -W 04:30\n")
                    sh.write("#BSUB -R affinity[core(1)]\n")
                    sh.write("#BSUB -M 8000\n")
                    sh.write("\n")
                    ## sh.write("#%include <head.h>\n")
                    ## sh.write("#%include <envir-xc40.h>\n")
                    sh.write("\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("submit "+plot_script)
                subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                msg="        python "+i+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.col_v6.py":
                print("    Start processing "+i)
                for j in col_var:
                    ic=ic+1
                    icnt=str(format(ic,'03d'))
                    plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                    print("Creating graphic script "+plot_script)
                    if os.path.exists(plot_script):
                        os.remove(plot_script)
                    with open(plot_script, 'a') as sh:
                        sh.write("#!/bin/bash -l\n")
                        sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                        sh.write("#BSUB -n 1\n")
                        sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                        sh.write("#BSUB -q dev_transfer\n")
                        sh.write("#BSUB -P CMAQ-T2O\n")
                        sh.write("#BSUB -W 04:30\n")
                        sh.write("#BSUB -R affinity[core(1)]\n")
                        sh.write("#BSUB -M 3999\n")
                        sh.write("\n")
                        ## sh.write("#%include <head.h>\n")
                        ## sh.write("#%include <envir-xc40.h>\n")
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
                    print("submit "+plot_script)
                    subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                    msg="        python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
            if i == "daily.aqm.plot_dustemis.py":
                print("    Start processing "+i)
                ic=ic+1
                icnt=str(format(ic,'03d'))
                plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                print("Creating graphic script "+plot_script)
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash -l\n")
                    sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -n 1\n")
                    sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                    sh.write("#BSUB -q dev_transfer\n")
                    sh.write("#BSUB -P CMAQ-T2O\n")
                    sh.write("#BSUB -W 04:30\n")
                    sh.write("#BSUB -R affinity[core(1)]\n")
                    sh.write("#BSUB -M 3999\n")
                    sh.write("\n")
                    ## sh.write("#%include <head.h>\n")
                    ## sh.write("#%include <envir-xc40.h>\n")
                    sh.write("\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("submit "+plot_script)
                subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.plot_fireemis.py" and envir != "prod":
                print("    Start processing "+i)
                ic=ic+1
                icnt=str(format(ic,'03d'))
                plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                print("Creating graphic script "+plot_script)
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash -l\n")
                    sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -n 1\n")
                    sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                    sh.write("#BSUB -q dev_transfer\n")
                    sh.write("#BSUB -P CMAQ-T2O\n")
                    sh.write("#BSUB -W 04:30\n")
                    sh.write("#BSUB -R affinity[core(1)]\n")
                    sh.write("#BSUB -M 3999\n")
                    sh.write("\n")
                    ## sh.write("#%include <head.h>\n")
                    ## sh.write("#%include <envir-xc40.h>\n")
                    sh.write("\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("submit "+plot_script)
                subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "fireemis_fire_loc.py":
                print("    Start processing "+i)
                ic=ic+1
                icnt=str(format(ic,'03d'))
                plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                print("Creating graphic script "+plot_script)
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash -l\n")
                    sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -n 1\n")
                    sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                    sh.write("#BSUB -q dev_transfer\n")
                    sh.write("#BSUB -P CMAQ-T2O\n")
                    sh.write("#BSUB -W 04:30\n")
                    sh.write("#BSUB -R affinity[core(1)]\n")
                    sh.write("#BSUB -M 3999\n")
                    sh.write("\n")
                    ## sh.write("#%include <head.h>\n")
                    ## sh.write("#%include <envir-xc40.h>\n")
                    sh.write("\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("submit "+plot_script)
                subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                msg="        python "+i+" "+envir+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "gbbepx_fire_loc.py":
                print("    Start processing "+i)
                ic=ic+1
                icnt=str(format(ic,'03d'))
                plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                print("Creating graphic script "+plot_script)
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash -l\n")
                    sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -n 1\n")
                    sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                    sh.write("#BSUB -q dev_transfer\n")
                    sh.write("#BSUB -P CMAQ-T2O\n")
                    sh.write("#BSUB -W 04:30\n")
                    sh.write("#BSUB -R affinity[core(1)]\n")
                    sh.write("#BSUB -M 3999\n")
                    sh.write("\n")
                    ## sh.write("#%include <head.h>\n")
                    ## sh.write("#%include <envir-xc40.h>\n")
                    sh.write("\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("submit "+plot_script)
                subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                msg="        python "+i+" "+envir+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.plot_fireemis_r.py" and envir != "prod":
                print("    Start processing "+i)
                ic=ic+1
                icnt=str(format(ic,'03d'))
                plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                print("Creating graphic script "+plot_script)
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash -l\n")
                    sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -n 1\n")
                    sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                    sh.write("#BSUB -q dev_transfer\n")
                    sh.write("#BSUB -P CMAQ-T2O\n")
                    sh.write("#BSUB -W 04:30\n")
                    sh.write("#BSUB -R affinity[core(1)]\n")
                    sh.write("#BSUB -M 3999\n")
                    sh.write("\n")
                    ## sh.write("#%include <head.h>\n")
                    ## sh.write("#%include <envir-xc40.h>\n")
                    sh.write("\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("submit "+plot_script)
                subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
            if i == "daily.aqm.plot_dustloc.py":
                print("    Start processing "+i)
                ic=ic+1
                icnt=str(format(ic,'03d'))
                plot_script=os.path.join(os.getcwd(),"plot_cmaq_"+icnt+".sh")
                print("Creating graphic script "+plot_script)
                if os.path.exists(plot_script):
                    os.remove(plot_script)
                with open(plot_script, 'a') as sh:
                    sh.write("#!/bin/bash -l\n")
                    sh.write("#BSUB -o "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -e "+log_dir+"/"+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log\n")
                    sh.write("#BSUB -n 1\n")
                    sh.write("#BSUB -J jplot_"+envir+"_"+icnt+"\n")
                    sh.write("#BSUB -q dev_transfer\n")
                    sh.write("#BSUB -P CMAQ-T2O\n")
                    sh.write("#BSUB -W 04:30\n")
                    sh.write("#BSUB -R affinity[core(1)]\n")
                    sh.write("#BSUB -M 3999\n")
                    sh.write("\n")
                    ## sh.write("#%include <head.h>\n")
                    ## sh.write("#%include <envir-xc40.h>\n")
                    sh.write("\n")
                    sh.write("##\n")
                    sh.write("##  Plot EMC EXP "+envir+" using python script\n")
                    sh.write("##\n")
                    sh.write("set -x\n")
                    sh.write("\n")
                    sh.write("   cd "+working_dir+"\n")
                    sh.write("   python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+"\n")
                    sh.write("\n")
                    sh.write("exit\n")
                print("submit "+plot_script)
                subprocess.call(["cat "+plot_script+" | bsub"], shell=True)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
        msg=datetime.datetime.now()
        print("End   processing "+date.strftime(YMD_date_format)+" "+cyc+"Z Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    print("LOG file location "+working_dir)
    date = date + date_inc
