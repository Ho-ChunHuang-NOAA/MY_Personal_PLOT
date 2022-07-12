#!/bin/sh
module load prod_util
envir=para7
TODAY=`date +%Y%m%d`
if [ $# -lt 1 ]; then
  MSG="USAGE : $0 EXP[para1:...] START_DATE(YYYYMMDD) END_DATE(YYYYMMDD)"
  echo ${MSG}
  exit
elif [ $# -lt 2 ]; then
   envir=$1
   FIRSTDAY=${TODAY}
   LASTDAY=${TODAY}
elif [ $# -lt 3 ]; then
   envir=$1
   FIRSTDAY=$2
   LASTDAY=$2
else
   envir=$1
   FIRSTDAY=$2
   LASTDAY=$3
fi
echo "Program Start $0 ${FIRSTDAY} ${LASTDAY} for ${envir}"

flag_all_reg=no
flag_all_reg=yes   ## plot_area is a dummy input

flag_ftp=no
flag_ftp=yes

flag_title=no
flag_title=yes

##
## Area available
## data_area=['na', 'conus', 'se', 'sw', 'ne', 'nw', 'mdn', 'mds' ]
##
declare -a plot_area=( na conus )
pstring="[ "
let nplot_area=${#plot_area[@]}-1
for i in "${!plot_area[@]}"
do
   if [[ ${i} -ne ${nplot_area} ]]; then
     pstring=${pstring}"'"${plot_area[${i}]}"', "
   else
     pstring=${pstring}"'"${plot_area[${i}]}"' ]"
   fi
done

flag_rgb=no
flag_border=no
flag_cutoff=no
val_cutoff=0.0
if [ $# -gt 2 ]; then
   if [[ $3 == 'rgb' ]]; then flag_rgb=yes; fi
elif [ $# -gt 3 ]; then
   if [[ $4 == 'border' ]]; then flag_border=yes; fi
elif [ $# -gt 4 ]; then
   if [[ $5 == 'x' ]]; then flag_title=no; fi
elif [[ $# -gt 5 ]]; then
   flag_cutoff=yes
   val_cutoff=$6
fi

script_name=plot_hysplit_hms_fire_para
start_date=${FIRSTDAY}
end_date=${LASTDAY}
#

idlexe=`which idl`
script_dir=`pwd`
devdir=/lfs/h2/emc/physics/noscrub/${USER}/com/hysplit/${envir}
idir=/lfs/h2/emc/physics/noscrub/${USER}/gyre_hysplit_plot/fire_${envir}/
odir=/lfs/h2/emc/ptmp/${USER}/fire_plot/
mkdir -p ${odir} ${idir}
flag_dark=no
smlexp=`echo ${envir} | tr '[:upper:]' '[:lower:]'`
capexp=`echo ${envir} | tr '[:lower:]' '[:upper:]'`

remote_host=emcrzdm.ncep.noaa.gov
remote_user=hchuang
remote_dir=/home/people/emc/www/htdocs/mmb/${remote_user}/web/fig
#
# generate parameters setting for specific run
#
filename=run.${script_name}.h

runlog=$0.${start_date}.${end_date}.log
if [ -e ${runlog} ]; then
  grep 'Successfully finish.  Exit plot_hysplit_hms_fire_para.pro' ${runlog} > a1
  if [ -s a1 ]; then
     echo "previous run successfully finished.  proceed with current run"
  else
     echo "Previous run has not been finised, Job terminated"
     exit
  fi
else
  echo "no ${runlog}.  proceed with current run"
fi
if [ -e idlrcmdpara0499 ]; then
   /bin/rm -f idlrcmdpara*
fi
let i=1
while [ ${i} -le 500 ]; do
   numi=`printf %4.4d ${i}`
   if [ ! -e idlrcmdpara${numi} ]; then
      idlcmd=idlrcmdpara${numi}
      break
   fi
   ((i++))
done

max_match=12000
###############################################################
cd ${script_dir}
if [[ -e ${idlcmd} ]]; then
  /bin/rm -f ${idlcmd}
fi
if [[ -e ${filename} ]]; then
  /bin/rm -f ${filename}
fi
##echo "product="${pstring} >  ${filename}
echo "idir='"${idir}"'" >  ${filename}
echo "odir='"${odir}"'" >> ${filename}
echo "smlexp='"${smlexp}"'" >> ${filename}
echo "capexp='"${capexp}"'" >> ${filename}
echo "start_date='"${start_date}"'" >> ${filename}
echo "end_date='"${end_date}"'" >> ${filename}
echo "max_match = "${max_match}"L" >> ${filename}
echo "remote_dir='"${remote_dir}"'" >> ${filename}
echo "remote_host='"${remote_host}"'" >> ${filename}
echo "remote_user='"${remote_user}"'" >> ${filename}
echo "plot_area="${pstring} >> ${filename}
echo "cutoff = "${val_cutoff}"D" >> ${filename}
if [[ ${flag_dark} == 'yes' ]]; then
  echo "flag_dark_bkgrd=1B" >> ${filename}
else
  echo "flag_dark_bkgrd=0B" >> ${filename}
fi
if [[ ${flag_cutoff} == 'yes' ]]; then
  echo "flag_cutoff=1B" >> ${filename}
else
  echo "flag_cutoff=0B" >> ${filename}
fi
if [[ ${flag_border} == 'yes' ]]; then
  echo "flag_border=1B" >> ${filename}
else
  echo "flag_border=0B" >> ${filename}
fi
if [[ ${flag_rgb} == 'yes' ]]; then
  echo "flag_rgb=1B" >> ${filename}
else
  echo "flag_rgb=0B" >> ${filename}
fi
if [[ ${flag_title} == 'yes' ]]; then
  echo "flag_title=1B" >> ${filename}
else
  echo "flag_title=0B" >> ${filename}
fi
if [[ ${flag_ftp} == 'yes' ]]; then
  echo "flag_ftp=1B" >> ${filename}
else
  echo "flag_ftp=0B" >> ${filename}
fi
if [[ ${flag_all_reg} == 'yes' ]]; then
  echo "flag_all_reg=1B" >> ${filename}
else
  echo "flag_all_reg=0B" >> ${filename}
fi
##
## end runtime parameters setting
##
echo ".r ${script_name}.pro" > ${idlcmd}
echo "${script_name}" >> ${idlcmd}
echo "retall" >> ${idlcmd}
echo "exit" >> ${idlcmd}

runlog=$0.${start_date}.${end_date}.log
if [[ -e ${runlog} ]]; then
  /bin/rm -f  ${runlog}
fi
cronhost=`hostname`
echo "running on host ${cronhost%%.*}" > ${runlog}

if [ 1 -eq 2 ]; then  ## assuming all input files are in place

FIRSTDAY=${start_date}
LASTDAY=${end_date}

declare -a regid=( cs ak hi )
##
## New processing code produce hmshysplit in the same output directory as EMITIME/FIRES.NEW
NOW=${FIRSTDAY}
while [[ ${NOW} -le ${LASTDAY} ]]; do
   YY=`echo ${NOW} | cut -c1-4`
   YM=`echo ${NOW} | cut -c1-6`
   cdate=${NOW}"00"
   HMSDAY=$(${NDATE} -24 ${cdate}| cut -c1-8)
   data_dir=${idir}${YY}/${YM}
   if [ ! -d ${data_dir} ]; then mkdir -p  ${data_dir}; fi
   for i in "${regid[@]}"
   do
if [ "${envir}" == "prod" ]; then
   comout=/lfs/h2/emc/physics/noscrub/${USER}/com/hysplit/prod/smoke${i}.${NOW}
else
   comout=${devdir}/smoke${i}.${NOW}
fi
      if [ -e ${comout}/EMITIMES ]; then
         cp -p ${comout}/EMITIMES ${data_dir}/EMITIMES_${NOW}_${i}
         echo "FOUND & COPY ${comout}/EMITIMES to ${data_dir}"
      else
         echo "${comout}/EMITIMES can not be found" >> ${runlog}
      fi
      if [ -e ${comout}/FIRES.NEW ]; then
         cp -p ${comout}/FIRES.NEW ${data_dir}/FIRESNEW_${NOW}_${i}
         echo "FOUND & COPY ${comout}/FIRES.NEW to ${data_dir}"
      else
         echo "${comout}/FIRES.NEW can not be found" >> ${runlog}
      fi
   done
   YY=`echo ${HMSDAY} | cut -c1-4`
   YM=`echo ${HMSDAY} | cut -c1-6`
   data_dir=${idir}${YY}/${YM}
   if [ ! -d ${data_dir} ]; then mkdir -p  ${data_dir}; fi
   chkfile=hmshysplit${HMSDAY}.prelim.txt
if [ "${envir}" == "prod" ]; then
   comout=/lfs/h2/emc/physics/noscrub/${USER}/dcom/${YY}
else
   comout=${devdir}/smokecs.${NOW}
fi
   if [ -e ${comout}/${chkfile} ]; then
      cp -p ${comout}/${chkfile} ${data_dir}
      echo "FOUND & COPY ${comout}/${chkfile} to ${data_dir}"
   else
      echo "${comout}/${chkfile} can not be found"
   fi
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done

fi                    ## END assuming all input files are in place

${idlexe} ${idlcmd} >> ${runlog} 2>&1 &
exit
