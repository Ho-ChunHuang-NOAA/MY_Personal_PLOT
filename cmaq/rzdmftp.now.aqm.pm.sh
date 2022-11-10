#!/bin/bash
##
## SCRIPT FOR SINGLE DAY PROCESSING AND MAP GENERATION
##
## YYYYMMDD is the start day of NAQFC PM   simulation
## Cycle_hr is the model run starting hour
##
USAGE="USAGE : $0 YYYYMMDD_BEG YYYYMMDD_END Cycle_hr (default:06|12) NCO_run (default:prod|para)"
if [[ $# -lt 2 ]]; then
  echo $USAGE
  exit
fi
## background ftp to RZDM is handled by transfer queue
flag_ftp=no
flag_ftp=yes

flag_update=yes
flag_update=no

FIRSTDAY=$1
LASTDAY=$2
cych=06
cychr=t06z
if [ $# -gt 2 ]; then 
   let numhr=$3
   if [ ${numhr} -lt 0 ] || [ ${numhr} -gt  18 ]; then
      echo "AQM cycle hour should be in one of [00 06 12 18], PROGRAM EXIT"
      exit
   else
      if [ ${numhr} -lt 10 ]; then 
         sck=`echo $3 | cut -c1-1`
         if [ ${sck} == '0' ]; then
            cych=${sck}
         else
            cych="0${sck}"
         fi
      else
         cych=`echo $3 | cut -c1-2`
      fi
   fi
fi
cychr="t${cych}z"
echo " Perform operation on cych = ${cych}  cychr = ${cychr}"

exp=prod
if [ $# -gt 3 ]; then exp=$4; fi
capexp=`echo ${exp} | tr '[:lower:]' '[:upper:]'`

NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do

   Y1=`echo ${NOW} | cut -c1-4`
   MX=`echo ${NOW} | cut -c5-5`
   if [ ${MX} == '0' ]; then
      M1=`echo ${NOW} | cut -c6-6`
   else
      M1=`echo ${NOW} | cut -c5-6`
   fi
   D1=`echo ${NOW} | cut -c7-8`

   outdir=/stmpp1/${USER}/daily_plot/aqm_${exp}_pm_cron.${NOW}${cych}
   JOBHR=00
   JOBMIN=29
   FTPDAY=${NOW}
   FTPCYCLHR=${cychr}
   FTPDATADIR=${outdir}
   FTPFLAGUPDATE=${flag_update}
   FTPFILEHD=aqm
   FTPFILEDESC=png
   
   ##
   ## 12/19/2014
   ## For someday, 00:29 is not enought to transfer all of the figures, regional speciated PM e, sw, and w
   ## Thus, split the task into two transfer job
## Note all *base used default output to /ptmpp1/${USER}/batch_logs
## need to makdir -p /ptmpp1/${USER}/batch_logs in case machine switch and directory can not be found for the beginning
mkdir -p /ptmpp1/${USER}/batch_logs
   ##
   JOBHDR=trans_${NOW}${cychr}_cmaq_pm1_${exp}
   basefile=${HOME}/cronjob/batch.ftp.cmaq.pm1.base
   jobscript=${HOME}/cronjob/job_cmaq_pm1_ftp.sh
   if [ -e ${jobscript} ]; then /bin/rm -f ${jobscript}; fi
      sed -e "s!JOBHDR!${JOBHDR}!" -e "s!JOBHR!${JOBHR}!" -e "s!JOBMIN!${JOBMIN}!" -e "s!FTPDAY!${FTPDAY}!" -e "s!FTPDATADIR!${FTPDATADIR}!" -e "s!FTPCYCLHR!${FTPCYCLHR}!" -e "s!FTPFLAGUPDATE!${FTPFLAGUPDATE}!" -e "s!FTPFILEHD!${FTPFILEHD}!" -e "s!FTPFILEDESC!${FTPFILEDESC}!" ${basefile} > ${jobscript}
   
   if [ ${flag_ftp} == 'yes' ]; then qsub < ${jobscript}; fi
   
   JOBHDR=trans_${NOW}${cychr}_cmaq_pm2_${exp}
   JOBMIN=59
   basefile=${HOME}/cronjob/batch.ftp.cmaq.pm2.base
   jobscript=${HOME}/cronjob/job_cmaq_pm2_ftp.sh
   if [ -e ${jobscript} ]; then /bin/rm -f ${jobscript}; fi
      sed -e "s!JOBHDR!${JOBHDR}!" -e "s!JOBHR!${JOBHR}!" -e "s!JOBMIN!${JOBMIN}!" -e "s!FTPDAY!${FTPDAY}!" -e "s!FTPDATADIR!${FTPDATADIR}!" -e "s!FTPCYCLHR!${FTPCYCLHR}!" -e "s!FTPFLAGUPDATE!${FTPFLAGUPDATE}!" -e "s!FTPFILEHD!${FTPFILEHD}!" -e "s!FTPFILEDESC!${FTPFILEDESC}!" ${basefile} > ${jobscript}
   
   if [ ${flag_ftp} == 'yes' ]; then qsub < ${jobscript}; fi

   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
