#!/bin/sh
#PBS -o /lfs/h2/emc/ptmp/${USER}/batch_logs/hyspt_hms_fire_dev_20170414.out
#PBS -e /lfs/h2/emc/ptmp/${USER}/batch_logs/hyspt_hms_fire_dev_20170414.err
#PBS -l place=shared,select=1:ncpus=1:mem=4GB
#PBS -N jhyspt_hms_fire_dev
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
   echo "submit job on dev machine t21a3"
   . ~/.bashrc
   cd /lfs/h2/emc/physics/noscrub/${USER}/IDL/hysplit_fire
   bash run.cron_hysplit_hms_fire_dev.sh 20170414 20170414 x x title
exit
