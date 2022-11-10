#!/bin/bash
#PBS -o /lfs/h2/emc/ptmp/${USER}/print_hyspt_smoke_conus_dev_dev.out
#PBS -e /lfs/h2/emc/ptmp/${USER}/print_hyspt_smoke_conus_dev_dev.err
#PBS -l place=shared,select=1:ncpus=1:mem=4GB
#PBS -N jprint_hyspt_smoke_conus_dev
#PBS -q dev_transfer
#PBS -A AQM-DEV
#PBS -l walltime=00:29
# 
#### 
# 
##
##  Provide fix date daily Hysplit data processing
##
   echo "submit job on dev machine t10a2"
   . ~/.bashrc
   cd /lfs/h2/emc/physics/noscrub/${USER}/gyre_hysplit_plot/conc/smoke/sorc
   bash cron.print.smoke.fcst_dev.sh 20150331 20150401
exit
