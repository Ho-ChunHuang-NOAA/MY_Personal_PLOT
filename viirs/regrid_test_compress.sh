#!/bin/sh
module use /gpfs/dell2/emc/verification/noscrub/emc.metplus/modulefiles ## Dell
hl=`hostname | cut -c1-1`
if [ "${hl}" == "v" ]; then
   module load met/10.0.0
else
   module load met/10.0.0
fi
module load prod_util/1.1.6
module load HPSS/5.0.2.5
module list
TODAY=`date +%Y%m%d`

MSG="USAGE $0 obs_sat (default:viirs) model_grid [default:aqm|hysplit|ngac] YYYYMMDD_BEG YYYYMMDD_END"
hl=`hostname | cut -c1-1`
pm=`cat /etc/prod | cut -c 1-1`
set -x
hl=`hostname | cut -c1`

TODAY=`date +%Y%m%d`
output_root=/gpfs/dell2/emc/modeling/noscrub/${USER}/VIIRS_AOD/REGRID
mkdir -p ${output_root}
OBSVDIR=/gpfs/dell2/emc/modeling/noscrub/${USER}/VIIRS_AOD/AOD
hpss_root=/5year/NCEPDEV/emc-naqfc/${USER}
log_dir=/gpfs/dell2/ptmp/${USER}/batch_logs
mkdir -p ${log_dir}
## mod_file=/naqfc/save/${USER}/plot/cmaq/parm/aqm.t06z.aot.f06.148.grib2
## Define G16 pixel Coordinate, without it MET will compute the coordinate in ${MET_TMP_DIR} from information contains AOD file 
## Take a minute to create, e.g., CONUS_2500_1500_56_-56_-101360_128240.nc

flag_hpss_archive=yes
flag_hpss_archive=no

if [ ${hl} != ${pm} ]; then
   set -x
   obs_name=viirs
   mdl_name=aqm
   if [ $# -lt 2 ]; then
      echo ${MSG}
      exit
   else
      obs_name=$1
      mdl_name=$2
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
echo "processing begin `date`"
   ## Store temporary map and G16 pixel netCDF file, e.g.,
   ## /gpfs/dell2/ptmp/${USER}/METPLUS_TMP/CONUS_2500_1500_56_-56_-101360_128240_to_Lambert Conformal.grid_map or
   ## CONUS_2500_1500_56_-56_-101360_128240_to_LatLon.grid_map
   working_dir=/gpfs/dell1/stmp/${USER}/working/viirsaod2${mdl_name}
   mkdir -p ${working_dir}
   case ${mdl_name} in
      aqm) mod_file=/gpfs/dell2/emc/modeling/save/${USER}/plot/parm/aqm.aot.148.grid;;
      hysplit) mod_file=/gpfs/dell2/emc/modeling/save/${USER}/plot/parm/hysplit.smoke.cs.grid;;
      ngac) mod_file=/gpfs/dell2/emc/modeling/save/${USER}/plot/parm/ngac.aot.550nm.grid;;
      *) echo "model name ${mdl_name} is not defined"
         exit;;
   esac
   NOW=${FIRSTDAY}
   while [ ${NOW} -le ${LASTDAY} ]; do
      export MET_TMP_DIR=/gpfs/dell1/stmp/${USER}/METPLUS_TMP_${mdl_name}/${NOW}
      if [ -d ${MET_TMP_DIR} ]; then
         /bin/rm -f ${MET_TMP_DIR}/*
      else
         mkdir -p ${MET_TMP_DIR}
      fi
      ## need module load prod_util
      jday=`${UTILROOT}/ush/date2jday.sh ${NOW}`

      mkdir -p ${working_dir}/${NOW}
      cd ${working_dir}/${NOW}

      OBSOUT=${output_root}/${mdl_name}.${NOW}
      mkdir -p ${OBSOUT}
      #
      let ohr=0
      let tend=23
      let ohr=20
      let tend=20
      while [ ${ohr} -le ${tend} ]; do
         oh=`printf %2.2d ${ohr}`
         ##
         ##  WARNING
         ##  fhead has been changed from OR_ABI-L2-AODC-M3_G16_s* to OR_ABI-L2-AODC-M6_G16_s*
         ##  need to held fhead fixed for implementation
         ##
         obsfile=${OBSVDIR}/${NOW}/VIIRS-L3-AOD_AQM_${NOW}_${oh}"0000"_C1.nc
         if [ -s ${obsfile} ]; then
            out_file=${OBSOUT}/VIIRS-L3-AOD_AQM_${mdl_name}_${NOW}_${oh}.nc
            if [ -s ${out_file} ]; then /bin/rm -f ${out_file}; fi
            regrid_data_plane ${obsfile} ${mod_file} ${out_file} -field 'name="AOD_H_Quality"; level="(*,*)";' -field 'name="AOD_HM_Quality"; level="(*,*)";' -field 'name="Dust_AOD_H_Quality"; level="(*,*)";' -field 'name="Dust_AOD_HM_Quality"; level="(*,*)";' -field 'name="Smoke_AOD_H_Quality"; level="(*,*)";' -field 'name="Smoke_AOD_HM_Quality"; level="(*,*)";' -method BUDGET -width 4  -v 9
            ## regrid_data_plane ${obsfile} ${mod_file} ${out_file} -field 'name="AOD_H_Quality"; level="(*,*)";' -field 'name="AOD_HM_Quality"; level="(*,*)";' -field 'name="Dust_AOD_H_Quality"; level="(*,*)";' -field 'name="Dust_AOD_HM_Quality"; level="(*,*)";' -field 'name="Smoke_AOD_H_Quality"; level="(*,*)";' -field 'name="Smoke_AOD_HM_Quality"; level="(*,*)";' -v 7
            ## regrid_data_plane ${obsfile} ${mod_file} ${out_file} -field 'name="AOD_H_Quality"; level="(*,*)";' -v 7
            ## ps_file=OBS_AOD_aqm_${obs_name}_${NOW}_${oh}.ps
            ## plot_data_plane ${out_file} ${ps_file} 'name="AOD"; level="L0";' -title "${capsat} AOD mapped to CMAQ grid ${obs_date} ${obs_cyc}Z"
            if [ ! -s ${out_file} ]; then
               echo "WARNING : Satellite AOD regridding failed ${outfile} - regrid_data_plane"
            fi
         else
            echo "WARNING:  no Satellite AOD observation data at ${NOW} hour ${oh}"
         fi
         ((ohr++))
      done
      if [ "${flag_hpss_archive}" == "yes" ]; then
         cd ${output_root}
         YY=`echo ${NOW} | cut -c1-4`
         YM=`echo ${NOW} | cut -c1-6`
         hpssdir=${hpss_root}/${YY}_VIIRS_AOD_REGRID/${YM}
         hsi mkdir  ${hpssdir}
         if [ -d ${mdl_name}.${NOW} ]; then
            htar -cf ${hpssdir}/${mdl_name}.${NOW}.tar ${mdl_name}.${NOW} > ${log_dir}/${mdl_name}.${NOW}.viirs.aod.regrid.tar.log 2>&1 &
         else
            echo "Can not find ${output_root}/${mdl_name}.${NOW}"
         fi
      fi
      cdate=${NOW}"00"
      NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
   done
fi
echo "processing finsih `date`"
exit

