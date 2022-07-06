#!/bin/sh
module load prod_util
set -x
MSG="$0 StartDate EndDate"
if [ $# -lt 2 ]; then
   echo ${MSG}
   exit
fi
FIRSTDAY=$1
LASTDAY=$2
data_dir=/lfs/h2/emc/physics/noscrub/${USER}/GOES16_AOD
declare -a goes_prod=( AOD ADP )
logdir=/lfs/h2/emc/ptmp/${USER}/batch_logs
mkdir -p ${logdir}
scr=`pwd`
cd ${scr}
declare -a adp=( smk dust )
declare -a mdl=(aqm hysplit)
declare -a satid=( g16 )
script_dir=/lfs/h2/emc/physics/noscrub/${USER}/plot/goes
flag_get_hpssdata=no
flag_get_hpssdata=yes
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do
   YY=` echo ${NOW} | cut -c1-4`
   for k in "${satid[@]}"; do
      id=`echo ${k} | cut -c2-3`
      hpssroot=/NCEPDEV/emc-naqfc/5year/Ho-Chun.Huang/${YY}_GOES_${id}_AOD_ADP
      if [ "${flag_get_hpssdata}" == "yes" ]; then
         for i in "${goes_prod[@]}"; do
            odir=${data_dir}/${i}
            mkdir -p ${odir}
            cd ${odir}
            htar -xf ${hpssroot}/${i}_${NOW}.tar
         done
      fi
      cd ${script_dir}
      for j in "${adp[@]}"; do
         var=${j}"aod"
         script=daily3.${k}.aqm.${var}.plot
         for i in "${mdl[@]}"; do
            bash run.${k}taqm_aod_${var}.sh ${k} ${i} ${NOW} ${NOW}
            bash ${script} ${k} ${i} ${NOW} ${NOW}
         done
      done

   done
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
