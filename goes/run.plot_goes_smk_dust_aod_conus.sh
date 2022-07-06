#!/bin/sh
  
module load prod_util
hl=`hostname | cut -c1`

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

flag_test=yes
flag_test=no

working_dir=/lfs/h2/emc/stmp/${USER}/plot_goes_aod_adp
mkdir -p ${working_dir}
##
##      echo "${idir_adp}/OR_ABI-L2-AODC-M6_G16_s20190411002137_e20190411004510_c20190411005261.nc" > flist
##      echo "${idir_adp}/OR_ABI-L2-AODC-M6_G16_s20190541702138_e20190541704511_c20190541707211.nc" > flist
## New processing code produce hmshysplit in the same output directory as EMITIME/FIRES.NEW
NOW=${FIRSTDAY}
while [[ ${NOW} -le ${LASTDAY} ]]; do
   YY=`echo ${NOW} | cut -c1-4`
   YM=`echo ${NOW} | cut -c1-6`
   cdate=${NOW}"00"
   ## calday=`bash /u/${USER}/bin/jday2cald ${NOW}`
   jday=`bash /u/${USER}/bin/cald2jday ${NOW}`
   ## number of separator / is 8 print 8+2 in awk command below, arrary is from 1-10 with filename
   idir_adp=/lfs/h2/emc/physics/noscrub/${USER}/GOES16/AOD      ## switch to print $10
   ## number of separator / is 8 print 8+2 in awk command below, arrary is from 1-8 with filename
   idir_adp=/gpfs/gd1/emc/meso/noscrub/${USER}/GOES16_GEO/NAQFC_data ## witch to print $8
   ## number of separator / is 9 print 9+2 in awk command below, arrary is from 1-8 with filename
   idir_adp=/gpfs/${phase12_id}d3/emc/meso/noscrub/${USER}/GOES16_AOD/ADP/${NOW}        ## switch to print $8
   ## number of separator / is 9 print 9+2 in awk command below, arrary is from 1-8 with filename
   idir_aod=/lfs/h2/emc/physics/noscrub/${USER}/GOES16_AOD/AOD/${NOW}        ## switch to print $8
   idir_adp=/lfs/h2/emc/physics/noscrub/${USER}/GOES16_AOD/ADP/${NOW}        ## switch to print $8
   fhd_aod=OR_ABI-L2-AODC-M6_G16
   fhd_adp=OR_ABI-L2-ADPC-M6_G16
   if [ -s ${working_dir}/flist_aod.${NOW} ]; then /bin/rm -rf ${working_dir}/flist_aod.${NOW}; fi
   if [ -s ${working_dir}/flist_adp.${NOW} ]; then /bin/rm -rf ${working_dir}/flist_adp.${NOW}; fi
   if [ "${flag_test}" == "no" ]; then
      let ohr=0
      let tend=23
      while [ ${ohr} -le ${tend} ]; do
         oh=`printf %2.2d ${ohr}`
         if [ -e ${working_dir}/a1 ]; then /bin/rm -rf ${working_dir}/a1; fi
         ls ${idir_aod}/${fhd_aod}_s${jday}${oh}*.nc > ${working_dir}/a1
         if [ -s ${working_dir}/a1 ]; then
            select_aod_file=`head -n1 ${working_dir}/a1`  
            tmp_file=$(echo ${select_aod_file} | awk -F"/" '{print $11}')
            start_time=$(echo ${tmp_file} | awk -F"_" '{print $4}')
            if [ -e ${working_dir}/a1 ]; then /bin/rm -rf ${working_dir}/a1; fi
            ls ${idir_adp}/${fhd_adp}_${start_time}*.nc > ${working_dir}/a1
            if [ -s ${working_dir}/a1 ]; then
               select_adp_file=`head -n1 ${working_dir}/a1`  
               echo ${select_aod_file} >> ${working_dir}/flist_aod.${NOW}
               echo ${select_adp_file} >> ${working_dir}/flist_adp.${NOW}
            fi
         fi
         ((ohr++))
      done    
   else
      echo "${idir_adp}/OR_ABI-L2-ADPC-M6_G16_s20192471901118_e20192471903491_c20192471904528.nc" > ${working_dir}/flist.${NOW}
   fi
   count=0
   while read line
   do
     #echo $line
     if [ 1 -eq 1 ]; then
        file_aod[$count]=$(echo $line | awk -F"/" '{print $11}')
     else
        file_aod[$count]=$(echo $line | awk -F"/" '{print $10}')
        file_aod[$count]=$(echo $line | awk -F"/" '{print $8}')
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
   done<${working_dir}/flist_aod.${NOW}
   let count=${count}-1
   pstring_aod="[ "
   let i=0
   while [ ${i} -le ${count} ]; do
      if [ ${i} -ne ${count} ]; then
        pstring_aod=${pstring_aod}"'"${file_aod[${i}]}"', "
      else
        pstring_aod=${pstring_aod}"'"${file_aod[${i}]}"' ]"
      fi
      ((i++))
   done
   echo "AOD file list : ${pstring_aod}"

   count=0
   while read line
   do
     #echo $line
     if [ 1 -eq 1 ]; then
        file_adp[$count]=$(echo $line | awk -F"/" '{print $11}')
     else
        file_adp[$count]=$(echo $line | awk -F"/" '{print $10}')
        file_adp[$count]=$(echo $line | awk -F"/" '{print $8}')
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
   done<${working_dir}/flist_adp.${NOW}
   ##
   ## Area available
   ## data_area=['na', 'conus', 'se', 'sw', 'ne', 'nw', 'mdn', 'mds' ]
   ##
   let count=${count}-1
   pstring_adp="[ "
   let i=0
   while [ ${i} -le ${count} ]; do
      if [ ${i} -ne ${count} ]; then
        pstring_adp=${pstring_adp}"'"${file_adp[${i}]}"', "
      else
        pstring_adp=${pstring_adp}"'"${file_adp[${i}]}"' ]"
      fi
      ((i++))
   done
   
   echo "ADP file list : ${pstring_adp}"

   script_name=plot_goes_smk_dust_aod_conus
   start_date=${NOW}
   end_date=${NOW}
   #
   
   idlexe=`which idl`
   script_dir=`pwd`
   odir=/lfs/h2/emc/ptmp/${USER}/goes_16_plot/
   mkdir -p ${odir}
   
   remote_host=emcrzdm.ncep.noaa.gov
   remote_user=hchuang
   remote_dir=/home/people/emc/www/htdocs/mmb/${remote_user}/web/fig
   #
   # generate parameters setting for specific run
   #
   filename=run.${script_name}.h
   
   runlog=${working_dir}/$0.${start_date}.${end_date}.${qc_flag}.log
   if [ -e ${runlog} ]; then
     grep 'Successfully finish.  Exit plot_goes_smk_dust_aod_conus.pro' ${runlog} > ${working_dir}/a1
     if [ ! -s ${working_dir}/a1 ]; then
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
   echo "idir_aod='"${idir_aod}"'" >  ${filename}
   echo "idir_adp='"${idir_adp}"'" >>  ${filename}
   echo "odir='"${odir}"'" >> ${filename}
   echo "start_date='"${start_date}"'" >> ${filename}
   echo "end_date='"${end_date}"'" >> ${filename}
   echo "remote_dir='"${remote_dir}"'" >> ${filename}
   echo "remote_host='"${remote_host}"'" >> ${filename}
   echo "remote_user='"${remote_user}"'" >> ${filename}
   echo "aod_files="${pstring_aod} >> ${filename}
   echo "adp_files="${pstring_adp} >> ${filename}
   ## echo "adpqf="${qc_flag}"L     ; filter ADP QF >= max_qc_flag             " >> ${filename}
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
   
   runlog=${working_dir}/$0.${start_date}.${end_date}.${qc_flag}.log
   if [[ -e ${runlog} ]]; then
     /bin/rm -f  ${runlog}
   fi
   cronhost=`hostname`
   echo "running on host ${cronhost%%.*}" > ${runlog}

   ${idlexe} ${idlcmd} >> ${runlog} 2>&1 
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done

exit

