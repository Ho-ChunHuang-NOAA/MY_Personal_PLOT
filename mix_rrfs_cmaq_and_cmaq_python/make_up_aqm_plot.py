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

run_root="/gpfs/dell1/stmp/Ho-Chun.Huang/working/run_python"
working_dir=os.path.join(run_root,envir,sel_var,sel_cyc,start_date)
if os.path.exists(working_dir):
    shutil.rmtree(working_dir)
os.makedirs(working_dir)
os.chdir(working_dir)

## subprocess.call(['cp -p * '+partb], shell=True)
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

## script_name = [ "daily.aqm.plot.py", "daily.aqm.plot_bc.py", "diff.aqm.plot.py", "diff.aqm.plot_bc.py" ]
script_name = [ ]
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
        for i in var:
            msg=datetime.datetime.now()
            print("    Start processing "+i)
            for j in script_name:
                msg="        python "+j+" "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
                print(msg)
                subprocess.call(["python "+j+" "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+j+"."+envir+"."+i+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            ## msg="        python "+diff_script+" "+envir+" "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
            ## print(msg)
            ## subprocess.call(["python "+diff_script+" "+envir+" "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+diff_script+"."+envir+"-"+envir+"bc."+i+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
            msg="        python "+diff_script2+" prod "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)
            subprocess.call(["python "+diff_script2+" prod "+envir+" "+i+" "+cyc+" "+date.strftime(YMD_date_format)+" "+date.strftime(YMD_date_format)+" > "+diff_script2+".prod-"+envir+"."+i+"."+cyc+"."+date.strftime(YMD_date_format)+".log 2>&1 &"], shell=True)
        msg=datetime.datetime.now()
        print("End   processing "+date.strftime(YMD_date_format)+" "+cyc+"Z Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S")+"/n")
    msg=datetime.datetime.now()
    print("End   processing "+date.strftime(YMD_date_format)+" Current system time is :: "+msg.strftime("%Y-%m-%d %H:%M:%S")+"/n")
    print("LOG file location "+working_dir)
    date = date + date_inc
