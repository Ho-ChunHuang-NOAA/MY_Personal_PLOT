#!/bin/sh
#BSUB -o /gpfs/dell2/ptmp/${USER}/batch_logs/gasp_all_aod_and_smoke_20171013.out
#BSUB -e /gpfs/dell2/ptmp/${USER}/batch_logs/gasp_all_aod_and_smoke_20171013.err
#BSUB -n 1
#BSUB -J jgasp_all_aod_and_smoke
#BSUB -q debug
#BSUB -P HYS-T2O
#BSUB -W 00:29
#BSUB -M 100
#BSUB -x
####BSUB -R span[ptile=1]
###BSUB -a poe
##
##  Provide fix date daily GASP all aod and smoke conc data processing
##
   echo "submit job on dev machine g10a2"
   . ~/.bashrc
   bash /gpfs/dell2/emc/verification/noscrub/${USER}/gyre_hysplit_plot/conc/smoke/cron_daily_nesdis.sh
   bash /gpfs/dell2/emc/verification/noscrub/${USER}/gyre_hysplit_plot/aod/cmaq/cron_daily_nesdis.sh
exit
