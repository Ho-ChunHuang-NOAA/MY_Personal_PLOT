#!/bin/bash
module load prod_util
set -x
MSG="$0 StartDate EndDate"
if [ $# -lt 2 ]; then
   echo ${MSG}
   exit
fi
FIRSTDAY=$1
LASTDAY=$2
log_dir=/lfs/h2/emc/ptmp/${USER}/batch_logs
mkdir -p ${log_dir}
scr=`pwd`
cd ${scr}
declare -a mdl=(aqm ak hi hysplit)
script=run.viirs_aqm_aod.sh
if [ ! -e ${script} ]; then
   echo "Can not find ${script}"
   exit
fi
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do
   for i in "${mdl[@]}"; do
      logfile=${log_dir}/${i}_viirs_aod.${NOW}.regrid.log
      if [ -e ${logfile} ]; then /bin/rm -rf ${logfile}; fi
      bash ${script} viirs ${i} ${NOW} ${NOW} > ${logfile} 2>&1 &
   done
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
