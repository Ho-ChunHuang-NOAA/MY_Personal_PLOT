#!/bin/sh
#BSUB -o /lfs/h2/emc/ptmp/${USER}/batch_logs/hyspt_hms_fire_20170414.out
#BSUB -e /lfs/h2/emc/ptmp/${USER}/batch_logs/hyspt_hms_fire_20170414.err
#BSUB -n 1
#BSUB -J jhyspt_hms_fire
#BSUB -q debug
#BSUB -P HYS-T2O
#BSUB -W 00:29
#BSUB -M 100
####BSUB -R span[ptile=1]
#BSUB -x
###BSUB -a poe
##
##  Provide fix date daily Hysplit data processing
##
   echo "submit job on dev machine t21a3"
   . ~/.bashrc
   cd /lfs/h2/emc/physics/noscrub/${USER}/IDL/hysplit_fire
   bash run.cron_hysplit_hms_fire.sh 20170414 20170414 x x title
exit
