#!/bin/sh
TODAY=`date +%Y%m%d`

MSG="USAGE $0 obs_sat (default:g16|g17|) model_grid [default:aqm|hysplit|ngac] YYYYMMDD_BEG YYYYMMDD_END"
hname=`hostname`
hl=`hostname | cut -c1-1`
if [ -s prod_info_list ]; then /bin/rm -f prod_info_list; fi
cat /lfs/h1/ops/prod/config/prodmachinefile > prod_info_list
info_line=`head -n 1 prod_info_list`
echo ${info_line}
prodinfo=$(echo ${info_line} | awk -F":" '{print $1}')
if [ "${prodinfo}" == "primary" ]; then
    prodmachine=$(echo ${info_line} | awk -F":" '{print $2}')
else
    info_line=`head -n 2 prod_info_list | tail -n1`
    echo ${info_line}
    prodinfo=$(echo ${info_line} | awk -F":" '{print $1}')
    if [ "${prodinfo}" == "primary" ]; then
        prodmachine=$(echo ${info_line} | awk -F":" '{print $2}')
    else
	prodmachine="unknown"
    fi
fi
pm=`echo ${prodmachine} | cut -c1-1`
if [ -s prod_info_list ]; then /bin/rm -f prod_info_list; fi
##set -x

module purge
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/19.1.3.304/
module load intel
module load gsl
module load python/3.8.6
module load netcdf/4.7.4
module load met/10.1.1
module load metplus/4.1.1
export MET_BASE=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1/share/met
export MET_ROOT=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1
export PATH=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1/bin:${PATH}
module load prod_util
 
module list
TODAY=`date +%Y%m%d`
output_root=/lfs/h2/emc/physics/noscrub/${USER}/GOES16_AOD/REGRID
mkdir -p ${output_root}
OBSVDIR=/lfs/h2/emc/physics/noscrub/${USER}/GOES16_AOD/AOD
OBSVDIR_ADP=/lfs/h2/emc/physics/noscrub/${USER}/GOES16_AOD/ADP
hpss_root=/5year/NCEPDEV/emc-naqfc/${USER}
log_dir=/lfs/h2/emc/ptmp/${USER}/batch_logs
mkdir -p ${log_dir}
## mod_file=/naqfc/save/${USER}/plot/cmaq/parm/aqm.t06z.aot.f06.148.grib2
## Define G16 pixel Coordinate, without it MET will compute the coordinate in ${MET_TMP_DIR} from information contains AOD file 
## Take a minute to create, e.g., CONUS_2500_1500_56_-56_-101360_128240.nc
export MET_GEOSTATIONARY_DATA=/lfs/h2/emc/physics/noscrub/${USER}/GOES16_AOD/g16_conus_latlon_2km_20180620.dat

flag_hpss_archive=yes
flag_hpss_archive=no

if [ "${hl}" != "${pm}" ]; then
   obs_name=g16
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
   ## Store temporary map and G16 pixel netCDF file, e.g.,
   ## /lfs/h2/emc/ptmp/${USER}/METPLUS_TMP/CONUS_2500_1500_56_-56_-101360_128240_to_Lambert Conformal.grid_map or
   ## CONUS_2500_1500_56_-56_-101360_128240_to_LatLon.grid_map
   working_dir=/lfs/h2/emc/stmp/${USER}/working/g16aod2${mdl_name}
   mkdir -p ${working_dir}
   case ${mdl_name} in
      aqm) mod_file=/lfs/h2/emc/physics/noscrub/${USER}/plot/parm/aqm.aot.148.grid;;
      hysplit) mod_file=/lfs/h2/emc/physics/noscrub/${USER}/plot/parm/hysplit.smoke.cs.grid;;
      ngac) mod_file=/lfs/h2/emc/physics/noscrub/${USER}/plot/parm/ngac.aot.550nm.grid;;
      *) echo "model name ${mdl_name} is not defined"
         exit;;
   esac
   NOW=${FIRSTDAY}
   declare -a qc_flag=( all )
   declare -a qc_flag=( high medium low )
   while [ ${NOW} -le ${LASTDAY} ]; do
      export MET_TMP_DIR=/lfs/h2/emc/stmp/${USER}/METPLUS_TMP_${mdl_name}/${NOW}
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
      while [ ${ohr} -le ${tend} ]; do
         oh=`printf %2.2d ${ohr}`
         if [ -e aa1 ]; then /bin/rm -rf aa1; fi
         ##
         ##  WARNING
         ##  fhead has been changed from OR_ABI-L2-AODC-M3_G16_s* to OR_ABI-L2-AODC-M6_G16_s*
         ##  need to held fhead fixed for implementation
         ##
         ls ${OBSVDIR}/${NOW}/OR_ABI-L2-AODC-M6_G16_s${jday}${oh}*.nc > aa1
         if [ -s aa1 ]; then
            aod_file=`head -n1 aa1`
            element_1=$( echo ${aod_file} | awk -F"_" '{print $1}')
            element_2=$( echo ${aod_file} | awk -F"_" '{print $2}')
            element_3=$( echo ${aod_file} | awk -F"_" '{print $3}')
            element_4=$( echo ${aod_file} | awk -F"_" '{print $4}')
            element_5=$( echo ${aod_file} | awk -F"_" '{print $5}')
            ## which element depends on your directory structure and file name that contains the separation symbol, i.e., "_".
            ## echo ${element_5}
            if [ -e aa2 ]; then /bin/rm -rf aa2; fi
            ls ${OBSVDIR_ADP}/${NOW}/OR_ABI-L2-ADPC-M6_G16_${element_5}*.nc > aa2
            adp_file=`head -n1 aa2`
            echo "======================="
            echo ${aod_file}
            echo ${adp_file}
if [ 1 -eq 1 ]; then
            for i in "${qc_flag[@]}"; do
               case ${i} in
                  high) value="0"
                        ;;
                  medium) value="0,1"
                          ;;
                  low) value="0,1,2"
                       ;;
                  med_only) value="1"
                      ;;
                  low_only) value="2"
                      ;;
                  *) echo "qc_flag=${i} is not defined"
                     exit;;
               esac
               out_file=${OBSOUT}/OBS_DUSTAOD_${mdl_name}_${obs_name}_${NOW}_${oh}_${i}.nc
               if [ "${i}" == "99" ]; then
                  point2grid ${aod_file} ${mod_file} ${out_file} -field 'name="AOD_Dust"; level="(*,*)";' -method UW_MEAN -v 1 -qc ${value} -adp ${adp_file}
               else
                  point2grid ${aod_file} ${mod_file} ${out_file} -field 'name="AOD_Dust"; level="(*,*)";' -method UW_MEAN -v 1 -qc ${value} -adp ${adp_file}
               fi
               ## ps_file=OBS_AOD_aqm_${obs_name}_${NOW}_${oh}.ps
               ## plot_data_plane ${out_file} ${ps_file} 'name="AOD"; level="L0";' -title "${capsat} AOD mapped to CMAQ grid ${obs_date} ${obs_cyc}Z"
               if [ ! -s ${out_file} ]; then
                  echo "WARNING : Satellite Dust AOD regridding failed ${outfile} - point2grid"
               fi
            done
fi
         else
            echo "WARNING:  no Satellite Dust AOD observation data at ${NOW} hour ${oh}"
         fi
         ((ohr++))
      done
      if [ "${flag_hpss_archive}" == "yes" ]; then
         cd ${output_root}
         YY=`echo ${NOW} | cut -c1-4`
         YM=`echo ${NOW} | cut -c1-6`
         hpssdir=${hpss_root}/${YY}_GOES_16_Dust_AOD_REGRID/${YM}
         hsi mkdir  ${hpssdir}
         if [ -d ${mdl_name}.${NOW} ]; then
            htar -cf ${hpssdir}/${mdl_name}.${NOW}.tar ${mdl_name}.${NOW} > ${log_dir}/${mdl_name}.${NOW}.aod.regrid.tar.log 2>&1 &
         else
            echo "Can not find ${output_root}/${mdl_name}.${NOW}"
         fi
      fi
      cdate=${NOW}"00"
      NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
   done
fi
exit

