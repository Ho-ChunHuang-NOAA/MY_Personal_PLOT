#!/bin/sh
#PBS -o /lfs/h2/emc/ptmp/${USER}/batch_logs/gasp_all_aod_and_smoke_20171013.out
#PBS -e /lfs/h2/emc/ptmp/${USER}/batch_logs/gasp_all_aod_and_smoke_20171013.err
#PBS -l place=shared,select=1:ncpus=1:mem=4GB
#PBS -N jgasp_all_aod_and_smoke
#PBS -q dev_transfer
#PBS -A AQM-DEV
#PBS -l walltime=00:29
# 
# 
#### 
# 
##
##  Provide fix date daily GASP all aod and smoke conc data processing
##
   echo "submit job on dev machine g10a2"
   . ~/.bashrc
   bash /lfs/h2/emc/physics/noscrub/${USER}/gyre_hysplit_plot/conc/smoke/cron_daily_nesdis.sh
   bash /lfs/h2/emc/physics/noscrub/${USER}/gyre_hysplit_plot/aod/cmaq/cron_daily_nesdis.sh
exit
