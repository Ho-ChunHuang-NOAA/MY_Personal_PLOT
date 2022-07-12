#!/bin/sh
#PBS -o /lfs/h2/emc/ptmp/${USER}/batch_logs/hyspt_hms_fire_para1_20160831.out
#PBS -e /lfs/h2/emc/ptmp/${USER}/batch_logs/hyspt_hms_fire_para1_20160831.err
#PBS -l place=shared,select=1:ncpus=1:mem=4GB
#PBS -N jhyspt_hms_fire_para1
#PBS -q dev_transfer
#PBS -A AQM-DEV
#PBS -l walltime=00:29
# 
# 
#### 
# 
##
##  Provide fix date daily Hysplit data processing
##
   echo "submit job on dev machine g21a2"
   . ~/.bashrc
   cd /lfs/h2/emc/physics/noscrub/${USER}/IDL/hysplit_fire
   bash run.cron_hysplit_hms_fire_para1.sh 20160831 20160831 x x title
exit
