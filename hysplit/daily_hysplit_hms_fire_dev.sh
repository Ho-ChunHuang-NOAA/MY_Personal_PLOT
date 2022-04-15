#!/bin/sh
#BSUB -o /gpfs/dell2/ptmp/${USER}/batch_logs/hyspt_hms_fire_dev_20170414.out
#BSUB -e /gpfs/dell2/ptmp/${USER}/batch_logs/hyspt_hms_fire_dev_20170414.err
#BSUB -n 1
#BSUB -J jhyspt_hms_fire_dev
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
   echo "submit job on dev machine t21a3"
   . ~/.bashrc
   cd /gpfs/dell2/emc/modeling/save/${USER}/IDL/hysplit_fire
   bash run.cron_hysplit_hms_fire_dev.sh 20170414 20170414 x x title
exit
