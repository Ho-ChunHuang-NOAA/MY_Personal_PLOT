#!/bin/bash
TODAY=`date +%Y%m%d`

MSG="USAGE $0 obs_sat (default:viirs) model_grid [default:aqm|hysplit|ngac] YYYYMMDD_BEG YYYYMMDD_END"
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
   HOMEevs=/lfs/h2/emc/vpppg/noscrub/ho-chun.huang/EVS
   source $HOMEevs/versions/run.ver

   module reset
   module load prod_envir/${prod_envir_ver}
   source $HOMEevs/dev/modulefiles/aqm/aqm_prep.sh

set -x

OBSVDIR=/lfs/h2/emc/physics/noscrub/${USER}/VIIRS_AOD/AOD
output_root=/lfs/h2/emc/physics/noscrub/${USER}/VIIRS_AOD/REGRID
mkdir -p ${output_root}
hpss_root=/5year/NCEPDEV/emc-naqfc/${USER}
log_dir=/lfs/h2/emc/ptmp/${USER}/batch_logs
mkdir -p ${log_dir}

## daily fron ftp includes hpss aracived of regrid output
flag_hpss_archive=no
flag_hpss_archive=yes

ftp_script_dir=/u/ho-chun.huang/trans_rsync_scp
ftp_script_name=w2h_viirs_regrid_aod.py

   ## Store temporary map and G16 pixel netCDF file, e.g.,
   ## /lfs/h2/emc/ptmp/${USER}/METPLUS_TMP/CONUS_2500_1500_56_-56_-101360_12.2.2_to_Lambert Conformal.grid_map or
   ## CONUS_2500_1500_56_-56_-101360_12.2.2_to_LatLon.grid_map
   working_dir=/lfs/h2/emc/stmp/${USER}/working/viirsaod2${mdl_name}
   mkdir -p ${working_dir}
   case ${mdl_name} in
      rrfs) value=4
           mod_file=/lfs/h2/emc/vpppg/save/${USER}/plot/parm/rrfs.aot.grid;;
      aqmv7) value=4
           mod_file=/lfs/h2/emc/vpppg/save/${USER}/plot/parm/aqm.aot.793.grid;;
      aqm) value=4
           mod_file=/lfs/h2/emc/vpppg/save/${USER}/plot/parm/aqm.aot.148.grid;;
      ak) value=4
           mod_file=/lfs/h2/emc/vpppg/save/${USER}/plot/parm/aqm.aot.140.grid;;
      hi) value=4
           mod_file=/lfs/h2/emc/vpppg/save/${USER}/plot/parm/aqm.aot.139.grid;;
      hysplit) value=5
           mod_file=/lfs/h2/emc/vpppg/save/${USER}/plot/parm/hysplit.smoke.cs.grid;;
      *) echo "model name ${mdl_name} is not defined"
         exit;;
   esac
   filehdr=VIIRS-L3-AOD_AQM
   NOW=${FIRSTDAY}
   while [ ${NOW} -le ${LASTDAY} ]; do
      mkdir -p ${working_dir}/${NOW}
      cd ${working_dir}/${NOW}

      FIRSTHOUR=${NOW}"01"
      LASTHOUR=$(${NDATE} +24 ${FIRSTHOUR})
      HRNOW=${FIRSTHOUR}
      while [ ${HRNOW} -le ${LASTHOUR} ]; do
         TDY=`echo ${HRNOW} | cut -c1-8`
         oh=`echo ${HRNOW} | cut -c9-10`
         # oh=`printf %2.2d ${ohr}`
         ##
         OBSOUT=${output_root}/${mdl_name}.${TDY}
         mkdir -p ${OBSOUT}
         #
         obsfile=${OBSVDIR}/${NOW}/${filehdr}_${TDY}_${oh}"0000".nc
         if [ -s ${obsfile} ]; then
            out_file=${OBSOUT}/${filehdr}_${mdl_name}_${TDY}_${oh}.nc
            if [ -s ${out_file} ]; then /bin/rm -f ${out_file}; fi
            regrid_data_plane ${obsfile} ${mod_file} ${out_file} -field 'name="AOD_H_Quality"; level="(*,*)";' -field 'name="AOD_HM_Quality"; level="(*,*)";' -field 'name="Dust_AOD_H_Quality"; level="(*,*)";' -field 'name="Dust_AOD_HM_Quality"; level="(*,*)";' -field 'name="Smoke_AOD_H_Quality"; level="(*,*)";' -field 'name="Smoke_AOD_HM_Quality"; level="(*,*)";' -method UW_MEAN -width ${value} -vld_thresh 0.001 -v 1
            ## ps_file=OBS_AOD_aqm_${obs_name}_${TDY}_${oh}.ps
            ## plot_data_plane ${out_file} ${ps_file} 'name="AOD"; level="L0";' -title "${capsat} AOD mapped to CMAQ grid ${obs_date} ${obs_cyc}Z"
            if [ ! -s ${out_file} ]; then
               echo "WARNING : Satellite AOD regridding failed ${outfile} - regrid_data_plane"
            fi
         else
            echo "WARNING:  no Satellite AOD observation data at ${TDY} hour ${oh}"
         fi
         HRNOW=$(${NDATE} +1 ${HRNOW})
      done
      if [ "${flag_hpss_archive}" == "yes" ]; then
          cd ${ftp_script_dir}
          python ${ftp_script_name} ${mdl_name} ${NOW} ${NOW}
      fi
      cdate=${NOW}"00"
      NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
   done
exit

