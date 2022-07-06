#!/bin/sh
# module load idl/8.6.1
module load idl/8.7.3
module load prod_util
hl=`hostname | cut -c1`
if [ "${hl}" == "v" ]; then
  phase12_id='g'
else
  phase12_id='t'
fi

hl=`hostname | cut -c1`
if [ "${hl}" == "v" ]; then
  phase12_id='g'
else
  phase12_id='t'
fi

TODAY=`date +%Y%m%d`
if [ $# -lt 1 ]; then
  MSG="USAGE : $0 START_DATE(YYYYMMDD) END_DATE(YYYYMMDD) option[quality flag:0]"
  echo ${MSG}
  exit
elif [ $# -lt 2 ]; then
   FIRSTDAY=$1
   LASTDAY=${FIRSTDAY}
else
   FIRSTDAY=$1
   LASTDAY=$2
fi
echo "Program Start $0 ${FIRSTDAY} ${LASTDAY}"
qc_flag=0
if [ $# -gt 2 ]; then qc_flag=$3; fi

flag_ftp=no
flag_ftp=yes

flag_test=no
flag_test=yes

##
## New processing code produce hmshysplit in the same output directory as EMITIME/FIRES.NEW
NOW=${FIRSTDAY}
while [[ ${NOW} -le ${LASTDAY} ]]; do
   YY=`echo ${NOW} | cut -c1-4`
   YM=`echo ${NOW} | cut -c1-6`
   cdate=${NOW}"00"
   ## calday=`bash /u/${USER}/bin/jday2cald ${NOW}`
   jday=`bash /u/${USER}/bin/cald2jday ${NOW}`
   ## number of separator / is 8 print 8+2 in awk command below, arrary is from 1-10 with filename
   idir_aod=/gpfs/hps3/emc/meso/noscrub/${USER}/GOES16/AOD      ## switch to print $10
   ## number of separator / is 6 print 6+2 in awk command below, arrary is from 1-8 with filename
   idir_aod=/gpfs/${phase12_id}d3/emc/meso/noscrub/${USER}/GOES16_AOD/AOD/${NOW}        ## switch to print $8
   if [ "${flag_test}" == "no" ]; then
      ls ${idir_aod}/OR_ABI-L2-AODC-M3_G16_s${jday}*.nc > flist
   else
      echo "${idir_aod}/OR_ABI-L2-AODC-M3_G16_s20181341702215_e20181341704588_c20181341711418.nc" > flist
   fi
   count=0
   while read line
   do
     #echo $line
     if [ 1 -eq 2 ]; then
        file[$count]=$(echo $line | awk -F"/" '{print $10}')
     else
        file[$count]=$(echo $line | awk -F"/" '{print $8}')
     fi
     ## echo ${file[$count]}
     ## chr_abi[$count]=$(echo $line | awk -F"_" '{print $2}')
     ## chr_sat[$count]=$(echo $line | awk -F"_" '{print $3}')
     ## chr_beg[$count]=$(echo $line | awk -F"_" '{print $4}')
     ## chr_end[$count]=$(echo $line | awk -F"_" '{print $5}')
     ## echo "DR_${chr_abi[$count]}_${chr_sat[$count]}_${chr_beg[$count]}_${chr_end[$count]}"
     ## pids[$count]=$(echo $line | cut -c 1-8)
     ## echo "file[$count]"
     ((count++))
   done<flist
   ##
   ## Area available
   ## data_area=['na', 'conus', 'se', 'sw', 'ne', 'nw', 'mdn', 'mds' ]
   ##
   let count=${count}-1
   pstring="[ "
   let i=0
   while [ ${i} -le ${count} ]; do
      if [ ${i} -ne ${count} ]; then
        pstring=${pstring}"'"${file[${i}]}"', "
      else
        pstring=${pstring}"'"${file[${i}]}"' ]"
      fi
      ((i++))
   done
   
   echo "file list : ${pstring}"
   script_name=plot_goes_aod_conus
   start_date=${NOW}
   end_date=${NOW}
   #
   
   idlexe=`which idl`
   script_dir=`pwd`
   odir=/gpfs/dell1/ptmp/${USER}/goes_16_plot/
   
   remote_host=emcrzdm.ncep.noaa.gov
   remote_user=hchuang
   remote_dir=/home/people/emc/www/htdocs/mmb/${remote_user}/web/fig
   #
   # generate parameters setting for specific run
   #
   filename=run.${script_name}.h
   
   runlog=$0.${start_date}.${end_date}.log
   if [ -e ${runlog} ]; then
     grep 'Successfully finish.  Exit plot_goes_aod_conus.pro' ${runlog} > a1
     if [ ! -s a1 ]; then
     ##   echo "previous run successfully finished.  proceed with current run"
     ## else
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
   echo "idir='"${idir_aod}"'" >  ${filename}
   echo "odir='"${odir}"'" >> ${filename}
   echo "start_date='"${start_date}"'" >> ${filename}
   echo "end_date='"${end_date}"'" >> ${filename}
   echo "remote_dir='"${remote_dir}"'" >> ${filename}
   echo "remote_host='"${remote_host}"'" >> ${filename}
   echo "remote_user='"${remote_user}"'" >> ${filename}
   echo "aod_files="${pstring} >> ${filename}
   ## echo "aodqf="${qc_flag}"L     ; filter AOD QF >= max_qc_flag             " >> ${filename}
   echo "aodqf="${qc_flag}"L" >> ${filename}
   if [[ ${flag_dark} == 'yes' ]]; then
     echo "flag_dark_bkgrd=1B" >> ${filename}
   else
     echo "flag_dark_bkgrd=0B" >> ${filename}
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

   ${idlexe} ${idlcmd} >> ${runlog} 2>&1 &
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done

exit

