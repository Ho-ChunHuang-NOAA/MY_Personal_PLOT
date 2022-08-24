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

user=os.environ['USER']

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
working_dir=os.path.join(run_root,envir,start_date)
if os.path.exists(working_dir):
    os.chdir(working_dir)
else:
    os.makedirs(working_dir)
    os.chdir(working_dir)

if envir == "prod":
##                  "daily.aqm.plot.py", "daily.aqm.plot_bc.py", "daily.aqm.plot_spec.py",
##                  "gbbepx_fire_loc.py",
##                  "daily.aqm.plot_met_v6.py", "daily.aqm.plot_dustloc.py", "diff.aqm.plot_bc.py"
    script_name = [
                    "daily.aqm.plot_overlay.py", "daily.aqm.plot_bc_overlay.py"
                  ]
else:
    script_name = [
                  "daily.aqm.plot.py", "daily.aqm.plot_bc.py", "daily.aqm.plot_spec.py",
                  "daily.aqm.plot_met_v6.py", "diff.aqm.plot.py",
                  "diff.aqm.plot_bc.py", "diff.aqm.plot_spec.py",
                  "fireemis_fire_loc.py",
                  "gbbepx_fire_loc.py",
                  "daily.aqm.plot_dustloc.py"
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

date=sdate
while date <= edate:
    for cyc in cycle:
        msg=datetime.datetime.now()
        print("Start processing "+date.strftime(YMD_date_format)+" "+cyc+"Z Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
        for i in script_name:
            msg=datetime.datetime.now()
            if i == "daily.aqm.plot.py" or i == "daily.aqm.plot_bc.py" or i == "daily.aqm.plot_overlay.py" or i == "daily.aqm.plot_bc_overlay.py":
                print("    Start processing "+i)
                for j in var:
                    msg="        python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "daily.aqm.plot_spec.py" or i == "daily.aqm.plot_spec_xsel.py":
                print("    Start processing "+i)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                subprocess.call(["python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "diff.aqm.plot_bc.py":
                print("    Start processing "+i)
                for j in var:
                    msg="        python "+i+" "+envir+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+i+" "+envir+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"-"+envir+"bc."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "diff.aqm.plot_spec.py" and envir != "prod":
                print("    Start processing "+i)
                msg="        python "+i+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                subprocess.call(["python "+i+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"-prod."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
                if envir == "para6z":
                    msg="        python "+i+" para6x "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+i+" para6x "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"-para6a."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "diff.aqm.plot.py" and envir != "prod":
                print("    Start processing "+i)
                for j in var:
                    msg="        python "+i+" prod "+envir+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+i+" "+envir+" para6d "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+".para6d-"+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
                if envir == "para6z":
                    for j in var:
                        msg="        python "+i+" "+envir+" para6d "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                        print(msg)
                        subprocess.call(["python "+i+" "+envir+" para6d "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+".para6d-"+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "daily.aqm.plot_met_v6.py":
                print("    Start processing "+i)
                msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                subprocess.call(["python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "diff.aqm.plot_met_v6.py" and envir != "prod":
                print("    Start processing "+i)
                msg="        python "+i+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                subprocess.call(["python "+i+" para6a "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"-para6a."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "daily.aqm.col_v6.py":
                print("    Start processing "+i)
                for j in col_var:
                    msg="        python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+i+" "+envir+" "+j+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"."+j+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "daily.aqm.plot_dustemis.py":
                print("    Start processing "+i)
                for j in var:
                    msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "daily.aqm.plot_fireemis.py" and envir != "prod":
                print("    Start processing "+i)
                for j in var:
                    msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "daily.aqm.plot_fireemis_r.py" and envir != "prod":
                print("    Start processing "+i)
                for j in var:
                    msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "daily.aqm.plot_dustloc.py":
                print("    Start processing "+i)
                for j in var:
                    msg="        python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+i+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "fireemis_fire_loc.py":
                print("    Start processing "+i)
                for j in var:
                    msg="        python "+i+" "+envir+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+i+" "+envir+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "gbbepx_fire_loc.py":
                print("    Start processing "+i)
                for j in var:
                    msg="        python "+i+" "+envir+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+i+" "+envir+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+i+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
        msg=datetime.datetime.now()
        print("End   processing "+date.strftime(YMD_date_format)+" "+cyc+"Z Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    print("LOG file location "+working_dir)
    date = date + date_inc
