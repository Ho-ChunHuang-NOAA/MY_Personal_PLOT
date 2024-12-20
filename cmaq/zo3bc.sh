#!/bin/bash
module load prod_util
# set -x
MSG="$0 EXP [prod|para5|...] CYC [all\06\12] StartDate EndDate"
if [ $# -lt 4 ]; then
   echo ${MSG}
   exit
fi
envir=$1
cycid=$2
FIRSTDAY=$3
LASTDAY=$4
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
## for bc results add bc as last input argument
   script1=daily48.aqm.o3.plot_max_prod
   logfile=${working_dir}/daily48_o3maxbc${envir}.${NOW}.${cycid}.log
   if [ -e ${script1} ]; then
     if [ -e ${logfile} ]; then /bin/rm -rf ${logfile}; fi
      bash ${script1} ${envir} ${cycid} ${NOW} ${NOW} bc > ${logfile} 2>&1 &
   else
      echo "Can not find ${script1}"
   fi
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
