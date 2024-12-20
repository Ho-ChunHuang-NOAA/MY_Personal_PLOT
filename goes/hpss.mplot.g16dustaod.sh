#!/bin/bash
module load prod_util
# set -x
MSG="$0 StartDate EndDate"
if [ $# -lt 2 ]; then
   echo ${MSG}
   exit
fi
FIRSTDAY=$1
LASTDAY=$2
working_dir=/lfs/h2/emc/ptmp/${USER}/batch_logs
mkdir -p ${working_dir}
scr=`pwd`
cd ${scr}
declare -a mdl=(aqm hysplit)
script=daily3.g16.aqm.dustaod.plot
if [ ! -e ${script} ]; then
   echo "Can not find ${script}"
   exit
fi
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do
   for i in "${mdl[@]}"; do
      logfile=${working_dir}/${i}_g16_dustaod.${NOW}.log
      if [ -e ${logfile} ]; then /bin/rm -rf ${logfile}; fi
      bash ${script} g16 ${i} ${NOW} ${NOW} > ${logfile} 2>&1
   done
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
