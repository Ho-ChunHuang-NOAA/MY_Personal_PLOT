#!/bin/sh
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
script=htar_plot_g16_adp_aod.sh
if [ ! -e ${script} ]; then
   echo "Can not find ${script}"
   exit
fi
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do
   logfile=${working_dir}/${script}.${NOW}.log
   if [ -e ${logfile} ]; then /bin/rm -rf ${logfile}; fi
   bash ${script} ${NOW} ${NOW} > ${logfile} 2>&1
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
