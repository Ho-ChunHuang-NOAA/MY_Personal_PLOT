#!/bin/sh
#BSUB -o /lfs/h2/emc/ptmp/${USER}/print_hyspt_smoke_conus_dev_dev.out
#BSUB -e /lfs/h2/emc/ptmp/${USER}/print_hyspt_smoke_conus_dev_dev.err
#BSUB -n 1
#BSUB -J jprint_hyspt_smoke_conus_dev
#BSUB -q debug
#BSUB -P HYS-T2O
#BSUB -W 00:29
#BSUB -x
####BSUB -R span[ptile=1]
###BSUB -a poe
##
##  Provide fix date daily Hysplit data processing
##
   echo "submit job on dev machine t10a2"
   . ~/.bashrc
   cd /gpfs/dell2/emc/verification/noscrub/${USER}/gyre_hysplit_plot/conc/smoke/sorc
   bash cron.print.smoke.fcst_dev.sh 20150331 20150401
exit
