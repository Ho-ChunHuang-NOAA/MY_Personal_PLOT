#!/bin/sh
prod_util_ver=1.1.6
prod_envir_ver=1.1.0
grib_util_ver=1.1.1
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}
module load grib_util/${grib_util_ver}

MSG="USAGE : $0 RRFS_run (rrfs-cmaq|rrfs_cmaq-nofire) cycle(all|06|12) YYYYMMDD_BEG YYYYMMDD_END"
exp=prod
sel_cyc=all
FIRSTDAY=${TODAY}
LASTDAY=${TODAY}
if [ $# -lt 2 ]; then
   echo $MSG
   exit
else
   exp=$1
   sel_cyc=$2
fi
if [ $# -lt 3 ]; then
   FIRSTDAY=${TODAY}
   LASTDAY=${TODAY}
elif [ $# -lt 4 ]; then
   FIRSTDAY=$3
   LASTDAY=$3
else
   FIRSTDAY=$3
   LASTDAY=$4
fi
case ${sel_cyc} in
   ''|*[!0-9]*) if [ "${sel_cyc}" == "all" ]; then
            declare -a cyc_opt=( 06 12 )
         else
            echo "input choice for cycle time is not defined $2, program stop"
            echo $MSG
            exit
         fi ;;
   *) cyc_in=`printf %2.2d $2`
      if [ "${cyc_in}" == "06" ] || [ "${cyc_in}" == "12" ]; then
         declare -a cyc_opt=( ${cyc_in} )
      else
         echo "input choice for cycle time is not defined $2, program stop"
         echo $MSG
         exit
      fi ;;
esac
echo ${cyc_opt[@]}

rrfs_base=/gpfs/dell2/ptmp/${USER}/expt_dirs
rrfs_ver="rrfs_cmaq_6c73ae56_conus13"
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do
   DE=`echo ${LASTDAY} | cut -c5-8`
   if [ "${exp}" == "rrfs-cmaq" ]; then
      indir=${rrfs_base}/${rrfs_ver}-${FIRSTDAY}-${DE}
   elif [ "${exp}" == "rrfs-cmaq-nofire" ]; then
      indir=${rrfs_base}/${rrfs_ver}-${FIRSTDAY}-${DE}_nofire
   fi
   for cyc in "${cyc_opt[@]}"; do
      idir=${indir}/${NOW}${cyc}/postprd/POST_STAT
      if [ -d ${idir} ]; then
         odir=/gpfs/dell1/ptmp/${USER}/com/rrfs-cmaq/${exp}/${NOW}${cyc}/postprd
         mkdir -p ${odir}
         cp -pr ${idir} ${odir}
      else
         echo "Can not find ${idir}, skip moving data"
      fi
   done   ## end for loop cych in "${cyc_opt[@]}"
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done

