#!/bin/sh
module load prod_util
## set -x
MSG="$0 EXP1 [prod|para5|...] EXP2 [prod|para5|...] StartDate EndDate"
if [ $# -lt 3 ]; then
   echo ${MSG}
   exit
fi
exp1=$1
exp2=$2
FIRSTDAY=$3
if [ $# -gt 3 ]; then 
   LASTDAY=$4
else
   LASTDAY=${FIRSTDAY}
fi
working_dir=/lfs/h2/emc/ptmp/${USER}/batch_logs
mkdir -p ${working_dir}
scr=`pwd`
cd ${scr}
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do
cycid=cs
##    case ${cycid} in
##       cs)   script1=archive_run_pm_cs.sh
##             script2=archive_run_ic_cs.sh
##             ;;
##       akhi) script1=archive_run_pm_akhi.sh
##             script2=archive_run_ic_akhi.sh
##             ;;
##       *) echo "case not found; ${cycid}"
##          exit ;;
##    esac
   script1=diff4.dust.fcst.sh
   logfile=${working_dir}/diff_dust_${exp2}_${exp1}.${NOW}.${cycid}.log
   if [ -e ${script1} ]; then
     if [ -e ${logfile} ]; then /bin/rm -rf ${logfile}; fi
      bash ${script1} ${exp1} ${exp2} ${NOW} ${NOW} > ${logfile} 2>&1 &
   else
      echo "Can not find ${script1}"
   fi
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
