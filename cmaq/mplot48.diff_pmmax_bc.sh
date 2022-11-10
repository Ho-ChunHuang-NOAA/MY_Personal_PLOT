#!/bin/bash
module load prod_util
## set -x
MSG="$0 EXP1 [prod|para5|...] EXP2 [prod|para5|...] CYC [all\06\12] StartDate EndDate"
if [ $# -lt 5 ]; then
   echo ${MSG}
   exit
fi
exp1=$1
exp2=$2
cycid=$3
FIRSTDAY=$4
LASTDAY=$5
working_dir=/lfs/h2/emc/ptmp/${USER}/batch_logs
mkdir -p ${working_dir}
scr=`pwd`
cd ${scr}
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do
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
   script1=diff48.aqm.pm.plot_max
   logfile=${working_dir}/diff48_pmmax.${exp2}_${exp1}.${NOW}.${cycid}.log
   if [ -e ${script1} ]; then
     if [ -e ${logfile} ]; then /bin/rm -rf ${logfile}; fi
      bash ${script1} ${exp1} ${exp2} ${cycid} ${NOW} ${NOW} bc > ${logfile} 2>&1 &
   else
      echo "Can not find ${script1}"
   fi
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
