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
working_dir=os.path.join(run_root,envir,sel_var,sel_cyc,start_date)
if os.path.exists(working_dir):
    os.chdir(working_dir)
else:
    os.makedirs(working_dir)
    os.chdir(working_dir)

## subprocess.call(['cp -p * '+partb], shell=True)
## script_name = [ "daily.aqm.plot.py", "daily.aqm.plot_bc.py", "diff.aqm.plot.py", "diff.aqm.plot_bc.py" ]
diff_script="diff.aqm.plot_bc.py"   # difference of its own bias-correction solution
from_file=os.path.join(script_dir,diff_script)
to_file=os.path.join(working_dir,diff_script)
if os.path.exists(from_file):
    shutil.copyfile(from_file,to_file)
else:
    print("Can not find "+from_file)
    sys.exit()

diff_script2="diff.aqm.plot_48vs72.py"   # difference between prod and exp
from_file=os.path.join(script_dir,diff_script2)
to_file=os.path.join(working_dir,diff_script2)
if os.path.exists(from_file):
    shutil.copyfile(from_file,to_file)
else:
    print("Can not find "+from_file)
    sys.exit()

script_name = [ "daily.aqm.plot.py", "daily.aqm.plot_bc.py"]
for i in script_name:
    from_file=os.path.join(script_dir,i)
    to_file=os.path.join(working_dir,i)
    if os.path.exists(from_file):
        shutil.copyfile(from_file,to_file)
    else:
        print("Can not find "+from_file)
        sys.exit()

script_name_sp="daily.aqm.plot_spec.py"
from_file=os.path.join(script_dir,script_name_sp)
to_file=os.path.join(working_dir,script_name_sp)
if os.path.exists(from_file):
     shutil.copyfile(from_file,to_file)
else:
     print("Can not find "+from_file)
     sys.exit()

diff_name_sp="diff.aqm.plot_spec.py"
from_file=os.path.join(script_dir,diff_name_sp)
to_file=os.path.join(working_dir,diff_name_sp)
if os.path.exists(from_file):
     shutil.copyfile(from_file,to_file)
else:
     print("Can not find "+from_file)
     sys.exit()

script_name_met="daily.aqm.plot_met_v6.py"
from_file=os.path.join(script_dir,script_name_met)
to_file=os.path.join(working_dir,script_name_met)
if os.path.exists(from_file):
     shutil.copyfile(from_file,to_file)
else:
     print("Can not find "+from_file)
     sys.exit()

diff_name_met="diff.aqm.plot_met_v5_6.py"
from_file=os.path.join(script_dir,diff_name_met)
to_file=os.path.join(working_dir,diff_name_met)
if os.path.exists(from_file):
     shutil.copyfile(from_file,to_file)
else:
     print("Can not find "+from_file)
     sys.exit()

script_name_col="daily.aqm.col_v6.py"
from_file=os.path.join(script_dir,script_name_col)
to_file=os.path.join(working_dir,script_name_col)
if os.path.exists(from_file):
     shutil.copyfile(from_file,to_file)
else:
     print("Can not find "+from_file)
     sys.exit()
col_var = [ "pm25_col", "pm25c_col" ]

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
        for i in var:
            msg=datetime.datetime.now()
            print("    Start processing "+i)
            for j in script_name:
                msg="        python "+j+" "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                subprocess.call(["python "+j+" "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+j+"."+envir+"."+i+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            msg="        python "+diff_script+" "+envir+" "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
            print(msg)
            subprocess.call(["python "+diff_script+" "+envir+" "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+diff_script+"."+envir+"-"+envir+"bc."+i+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            msg="        python "+diff_script2+" prod "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
            print(msg)
            subprocess.call(["python "+diff_script2+" prod "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+diff_script2+".prod-"+envir+"."+i+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            if i == "pm25":
                msg="        python "+script_name_sp+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                subprocess.call(["python "+script_name_sp+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+script_name_sp+"."+envir+"."+i+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
                msg="        python "+diff_name_sp+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                subprocess.call(["python "+diff_name_sp+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+diff_name_sp+"."+envir+"."+i+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
                ## plot met variable only for pm25 cases; avoid duplicate when o3 and pm25 are called separately
                msg="        python "+script_name_met+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                subprocess.call(["python "+script_name_met+" "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+script_name_met+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
                for k in col_var:
                    msg="        python "+script_name_col+" "+envir+" "+k+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                    print(msg)
                    subprocess.call(["python "+script_name_col+" "+envir+" "+k+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+script_name_col+"."+envir+"."+k+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
        msg="        python "+diff_name_met+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
        print(msg)
        subprocess.call(["python "+diff_name_met+" prod "+envir+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+diff_name_met+"."+envir+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
        msg=datetime.datetime.now()
        print("End   processing "+date.strftime(YMD_date_format)+" "+cyc+"Z Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    msg=datetime.datetime.now()
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S"))
    print("LOG file location "+working_dir)
    date = date + date_inc
