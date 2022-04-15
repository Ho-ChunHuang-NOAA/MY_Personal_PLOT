#!/bin/sh
module load prod_util/1.1.6
set -x
MSG="$0 StartDate EndDate"
if [ $# -lt 2 ]; then
   echo ${MSG}
   exit
fi
FIRSTDAY=$1
LASTDAY=$2
log_dir=/gpfs/dell1/ptmp/${USER}/batch.logs
mkdir -p ${log_dir}
scr=`pwd`
cd ${scr}
# declare -a mdl=(aqm ak hi hysplit)
declare -a mdl=(hysplit)
script=daily.viirs.aqm.aod.plot
if [ ! -e ${script} ]; then
   echo "Can not find ${script}"
   exit
fi
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do
   for i in "${mdl[@]}"; do
      logfile=${log_dir}/${i}_viirs_aod.${NOW}.log
      if [ -e ${logfile} ]; then /bin/rm -rf ${logfile}; fi
      bash ${script} ${i} ${NOW} ${NOW} > ${logfile} 2>&1 &
   done
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
