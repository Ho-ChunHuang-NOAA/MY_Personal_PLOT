#!/bin/sh
#BSUB -o /gpfs/dell2/ptmp/${USER}/batch_logs/hyspt_hms_fire_para1_20160831.out
#BSUB -e /gpfs/dell2/ptmp/${USER}/batch_logs/hyspt_hms_fire_para1_20160831.err
#BSUB -n 1
#BSUB -J jhyspt_hms_fire_para1
#BSUB -q debug
#BSUB -P HYS-T2O
#BSUB -W 00:29
#BSUB -M 100
#BSUB -x
####BSUB -R span[ptile=1]
###BSUB -a poe
##
##  Provide fix date daily Hysplit data processing
##
   echo "submit job on dev machine g21a2"
   . ~/.bashrc
   cd /gpfs/dell2/emc/modeling/save/${USER}/IDL/hysplit_fire
   bash run.cron_hysplit_hms_fire_para1.sh 20160831 20160831 x x title
exit
