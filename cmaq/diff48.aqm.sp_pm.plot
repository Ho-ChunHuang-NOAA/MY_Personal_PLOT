#!/bin/sh
##
## SCRIPT FOR SINGLE DAY PROCESSING AND MAP GENERATION
##
## YYYYMMDD is the start day of NAQFC PM   simulation
## Cycle_hr is the model run starting hour
##
module use /apps/test/lmodules/core/
module load GrADS/2.2.2
module load prod_util
module load prod_envir
wgrib=/apps/ops/prod/libs/intel/19.1.3.304/grib_util/1.2.2/bin/wgrib
wgrib2=/apps/ops/prod/libs/intel/19.1.3.304/wgrib2/2.0.8/bin/wgrib2
hl=`hostname | cut -c1`

flag_test=yes
flag_test=no

flag_qsub=no
flag_qsub=yes

if [ "${flag_qsub}" == "yes" ]; then
   flag_scp=no
else
   flag_scp=yes
fi

TODAY=`date +%Y%m%d`

MSG="USAGE : $0 exp1 exp2 [exp2-exp1] Cycle_hr (default:all|06|12) YYYYMMDD_BEG YYYYMMDD_END"

if [ $# -lt 3 ]; then
   echo $MSG
   exit
else
   opt1=$1
   opt2=$2
   sel_cyc=$3
fi
if [ $# -lt 4 ]; then
   FIRSTDAY=${TODAY}
   LASTDAY=${TODAY}
elif [ $# -lt 5 ]; then
   FIRSTDAY=$4
   LASTDAY=$4
else
   FIRSTDAY=$4
   LASTDAY=$5
fi

aqm=aqm
capaqm=`echo ${aqm} | tr '[:lower:]' '[:upper:]'`
smlaqm=`echo ${aqm} | tr '[:upper:]' '[:lower:]'`

case ${sel_cyc} in
   ''|*[!0-9]*) if [ "${sel_cyc}" == "all" ]; then
            declare -a cyc_opt=( 06 12 )
         else
            echo "input choice for cycle time is not defined $3, program stop"
            echo $MSG
            exit
         fi ;;
   *) cyc_in=`printf %2.2d ${sel_cyc}`
      if [ "${cyc_in}" == "06" ] || [ "${cyc_in}" == "12" ]; then
         declare -a cyc_opt=( ${cyc_in} )
      else
         echo "input choice for cycle time is not defined $3, program stop"
         echo $MSG
         exit
      fi ;;
esac
echo ${cyc_opt[@]}

opt=${opt1}
capopt=`echo ${opt} | tr '[:lower:]' '[:upper:]'`
smlopt=`echo ${opt} | tr '[:upper:]' '[:lower:]'`

project=naqfc
capexp1=${capopt}
exp1=${smlopt}
comdir=/lfs/h1/ops/${exp1}/com/${smlaqm}/v6.1
## comdir2=${comdir}
comdir2=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp1}
project2=meso
mydir2=/lfs/h2/emc/ptmp/${USER}/com/${smlaqm}/${exp1}
project2=meso
mydir=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp1}
mydir=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp1}
mydir2=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp1}
mydir12=/lfs/h2/emc/ptmp/Jianping.Huang/com/aqm/${exp1}

## special setting
if [ ${smlopt} == 'prod' ]; then
   mydir=${comdir}
   mydir2=${comdir2}
elif [ ${smlopt} == 'ncopara' ]; then
   mydir=${comdir}
   mydir2=${comdir}
elif [ ${smlopt} == 'para12' ]; then
   comdir=${mydir12}
   comdir2=${mydir12}
else
   comdir=${mydir}
   comdir2=${mydir2}
fi
comdir1_s1=${comdir}
comdir2_s1=${comdir2}
mydir1_s1=${mydir}
mydir2_s1=${mydir2}

##
## setting for exp2
##
project=naqfc
project2=meso
opt=${opt2}
capopt=`echo ${opt} | tr '[:lower:]' '[:upper:]'`
smlopt=`echo ${opt} | tr '[:upper:]' '[:lower:]'`
capexp2=${capopt}
exp2=${smlopt}
comdir=/lfs/h1/ops/${exp2}/com/${smlaqm}/v6.1
## comdir2=${comdir}
comdir2=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp2}
mydir2=/lfs/h2/emc/ptmp/${USER}/com/${smlaqm}/${exp2}
mydir=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp2}
mydir=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp2}
mydir2=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp2}
mydir12=/lfs/h2/emc/ptmp/Jianping.Huang/com/aqm/${exp2}

## special setting
if [ ${smlopt} == 'prod' ]; then
   mydir=${comdir}
   mydir2=${comdir2}
elif [ ${smlopt} == 'ncopara' ]; then
   mydir=${comdir}
   mydir2=${comdir}
elif [ ${smlopt} == 'para12' ]; then
   comdir=${mydir12}
   comdir2=${mydir12}
else
   comdir=${mydir}
   comdir2=${mydir2}
fi
comdir1_s2=${comdir}
comdir2_s2=${comdir2}
mydir1_s2=${mydir}
mydir2_s2=${mydir2}
##
capexp="${capexp2}-${capexp1}"
exp="${exp2}-${exp1}"
ftype="_${exp2}m${exp1}.png"

if [ ${exp} == 'para1' ]; then flag_update=no; fi
## no for sp_pm difference
flag_update=no

## echo " ${exp} ${sel_cyc} ${FIRSTDAY} ${LASTDAY}"

remote_dir=/home/people/emc/www/htdocs/mmb/hchuang/web/fig
remote_host=emcrzdm.ncep.noaa.gov
remote_user=hchuang

grid_id2=148
grid_id=227

flag_update=no
if [ "${LASTDAY}" == "${TODAY}" ]; then flag_update=yes; fi

gs_dir=`pwd`

declare -a reg=( dset conus east west  ne10  nw10  se10  swse  ak   hi   )
declare -a lon0=( -175 -133 -100 -130  -81   -125  -91   -125  -170 -161 )
declare -a lon1=(   55  -60  -60  -90  -66   -105  -74   -100  -130 -154 )
declare -a lat0=(    0   21   24   21   37     37   24     21    50   18 )
declare -a lat1=(   80   52   50   50   48     50   40     45    80   23 )
nreg=${#reg[@]}
let max_ireg=${nreg}-1
idset=0
iconus=1
ieast=2
iwest=3
ine10=4
inw10=5
ise10=6
iswse=7
iak=8
ihi=9
ican=10
iuser=11

declare -a mchr=( JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC )

declare -a typ=( sp_pm )
ntyp=${#typ[@]}

NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do

   flag_plot=yes
   if [ -d  ${comdir1_s1}/cs.${NOW} ]; then
      idir1=${comdir1_s1}/cs.${NOW}
      echo "FILE 1 from ${idir1}"
   elif [ -d ${comdir2_s1}/cs.${NOW} ]; then
      idir1=${comdir2_s1}/cs.${NOW}
      echo "FILE 1 from ${idir1}"
   elif [ -d  ${mydir1_s1}/cs.${NOW} ]; then
      idir1=${mydir1_s1}/cs.${NOW}
      echo "FILE 1 from ${idir1}"
   elif [ -d ${mydir2_s1}/cs.${NOW} ]; then
      idir1=${mydir2_s1}/cs.${NOW}
      echo "FILE 1 from ${idir1}"
   else
      flag_plot=no
      echo " ${NOW} :: NO ${comdir1_s1}/cs.${NOW} & ${comdir2_s1}/aqm.${NOW}, skip to nexy day"
      echo " ${NOW} :: NO ${mydir1_s1}/cs.${NOW} & ${mydir2_s1}/aqm.${NOW}, skip to nexy day"
   fi

   if [ -d  ${comdir1_s2}/cs.${NOW} ]; then
      idir2=${comdir1_s2}/cs.${NOW}
      echo "FILE 2 from ${idir2}"
   elif [ -d ${comdir2_s2}/cs.${NOW} ]; then
      idir2=${comdir2_s2}/cs.${NOW}
      echo "FILE 2 from ${idir2}"
   elif [ -d  ${mydir1_s2}/cs.${NOW} ]; then
      idir2=${mydir1_s2}/cs.${NOW}
      echo "FILE 2 from ${idir2}"
   elif [ -d ${mydir2_s2}/cs.${NOW} ]; then
      idir2=${mydir2_s2}/cs.${NOW}
      echo "FILE 2 from ${idir2}"
   else
      flag_plot=no
      echo " ${NOW} :: NO ${comdir1_s2}/cs.${NOW} & ${comdir2_s2}/aqm.${NOW}, skip to nexy day"
      echo " ${NOW} :: NO ${mydir1_s2}/cs.${NOW} & ${mydir2_s2}/aqm.${NOW}, skip to nexy day"
   fi

   if [ "${flag_plot}" == "no" ]; then continue; fi

   for cych in "${cyc_opt[@]}"; do
      cdate=${NOW}${cych}
      F1=$(${NDATE} +1 ${cdate}| cut -c9-10)
      TOMORROW=$(${NDATE} +24 ${cdate}| cut -c1-8)
      THIRDDAY=$(${NDATE} +48 ${cdate}| cut -c1-8)
      FOURTHDAY=$(${NDATE} +72 ${cdate}| cut -c1-8)
   
      Y1=`echo ${NOW} | cut -c1-4`
      MX=`echo ${NOW} | cut -c5-5`
      if [ ${MX} == '0' ]; then
         M1=`echo ${NOW} | cut -c6-6`
      else
         M1=`echo ${NOW} | cut -c5-6`
      fi
      D1=`echo ${NOW} | cut -c7-8`
      Y2=`echo ${TOMORROW} | cut -c1-4`
      MX=`echo ${TOMORROW} | cut -c5-5`
      if [ ${MX} == '0' ]; then
         M2=`echo ${TOMORROW} | cut -c6-6`
      else
         M2=`echo ${TOMORROW} | cut -c5-6`
      fi
      D2=`echo ${TOMORROW} | cut -c7-8`
      Y3=`echo ${THIRDDAY} | cut -c1-4`
      MX=`echo ${THIRDDAY} | cut -c5-5`
      if [ ${MX} == '0' ]; then
         M3=`echo ${THIRDDAY} | cut -c6-6`
      else
         M3=`echo ${THIRDDAY} | cut -c5-6`
      fi
      D3=`echo ${THIRDDAY} | cut -c7-8`
      Y4=`echo ${FOURTHDAY} | cut -c1-4`
      MX=`echo ${FOURTHDAY} | cut -c5-5`
      if [ ${MX} == '0' ]; then
         M4=`echo ${FOURTHDAY} | cut -c6-6`
      else
         M4=`echo ${FOURTHDAY} | cut -c5-6`
      fi
      range1=05Z${D1}${mchr[$M1-1]}${Y1}-04Z${D2}${mchr[$M2-1]}${Y2}
      range2=05Z${D2}${mchr[$M2-1]}${Y2}-04Z${D3}${mchr[$M3-1]}${Y3}
      range3=05Z${D3}${mchr[$M3-1]}${Y3}-04Z${D4}${mchr[$M4-1]}${Y4}

      tmpdir=/lfs/h2/emc/stmp/${USER}/com_aqm_${exp}_sp_pm.${NOW}${cych}
      if [ -d ${tmpdir} ]; then /bin/rm -rf ${tmpdir}; fi
      mkdir -p ${tmpdir}
      cd ${tmpdir}
   
      fig_dir=/lfs/h2/emc/stmp/${USER}/diff_plot_pm25_sp/aqm_${exp}_pm_sp

      outdir=${fig_dir}.${NOW}${cych}
      if [ ! -d ${outdir} ]; then mkdir -p ${outdir}; fi

      let end_hour=48   
      let numcyc=${cych}
      cychr="t${cych}z"
      echo " Perform operation on cych = ${cych}  cychr = ${cychr}"
      if [ "${flag_test}" == "yes" ]; then continue; fi
      for i in "${typ[@]}"
      do
        case ${i} in
           sp_pm) cp ${idir1}/aqm.${cychr}.aconc_sfc.ncf  ${tmpdir}/s1_aqm.${cychr}.aconc_sfc.ncf
                  cp ${idir2}/aqm.${cychr}.aconc_sfc.ncf  ${tmpdir}/s2_aqm.${cychr}.aconc_sfc.ncf;;
        esac
      done
   
      n0=0
      let n1=${ntyp}-1
      let ptyp=n0
      while [ ${ptyp} -le ${n1} ]; do

         if [ -e aqm1.ctl ]; then /bin/rm -f aqm1.ctl; fi
         if [ -e aqm2.ctl ]; then /bin/rm -f aqm2.ctl; fi
#
         cat >  aqm1.ctl <<EOF
dset ${tmpdir}/s1_aqm.${cychr}.aconc_sfc.ncf
undef  -9.99e33
dtype netcdf
PDEF 442 265 lccr 21.8212 -120.628 1 1 33 45 -97 12000. 12000.
xdef 614 linear -132.000 0.12
ydef 262 linear 22.0000 0.12
zdef    1 levels  1.000
tdef  48 linear  ${F1}Z${D1}${mchr[$M1-1]}${Y1}  01hr
vars  19
O3=>o3   0 t,z,y,x  (ppmV)
CO=>co   0 t,z,y,x  (ppmV)
NO=>no   0 t,z,y,x  (ppmV)
NO2=>no2   0 t,z,y,x  (ppmV)
NOY=>noy   0 t,z,y,x  (ppmV)
VOC=>voc   0 t,z,y,x  (ppmC)
PM25_TOT=>pm25_tot   0 t,z,y,x  (micrograms/m**3)
PM25_CL=>pm25_cl   0 t,z,y,x  (micrograms/m**3)
PM25_EC=>pm25_ec   0 t,z,y,x  (micrograms/m**3)
PM25_NA=>pm25_na   0 t,z,y,x  (micrograms/m**3)
PM25_MG=>pm25_mg   0 t,z,y,x  (micrograms/m**3)
PM25_K=>pm25_k   0 t,z,y,x  (micrograms/m**3)
PM25_CA=>pm25_ca   0 t,z,y,x  (micrograms/m**3)
PM25_NH4=>pm25_nh4   0 t,z,y,x  (micrograms/m**3)
PM25_NO3=>pm25_no3   0 t,z,y,x  (micrograms/m**3)
PM25_OC=>pm25_oc   0 t,z,y,x  (micrograms/m**3)
PM25_SOIL=>pm25_soil   0 t,z,y,x  (micrograms/m**3)
PM25_SO4=>pm25_so4   0 t,z,y,x  (micrograms/m**3)
PMC_TOT=>pmc_tot   0 t,z,y,x  (micrograms/m**3)
ENDVARS
EOF
         cat >  aqm2.ctl <<EOF
dset ${tmpdir}/s2_aqm.${cychr}.aconc_sfc.ncf
undef  -9.99e33
dtype netcdf
PDEF 442 265 lccr 21.8212 -120.628 1 1 33 45 -97 12000. 12000.
xdef 614 linear -132.000 0.12
ydef 262 linear 22.0000 0.12
zdef    1 levels  1.000
tdef  48 linear  ${F1}Z${D1}${mchr[$M1-1]}${Y1}  01hr
vars  19
O3=>o3   0 t,z,y,x  (ppmV)
CO=>co   0 t,z,y,x  (ppmV)
NO=>no   0 t,z,y,x  (ppmV)
NO2=>no2   0 t,z,y,x  (ppmV)
NOY=>noy   0 t,z,y,x  (ppmV)
VOC=>voc   0 t,z,y,x  (ppmC)
PM25_TOT=>pm25_tot   0 t,z,y,x  (micrograms/m**3)
PM25_CL=>pm25_cl   0 t,z,y,x  (micrograms/m**3)
PM25_EC=>pm25_ec   0 t,z,y,x  (micrograms/m**3)
PM25_NA=>pm25_na   0 t,z,y,x  (micrograms/m**3)
PM25_MG=>pm25_mg   0 t,z,y,x  (micrograms/m**3)
PM25_K=>pm25_k   0 t,z,y,x  (micrograms/m**3)
PM25_CA=>pm25_ca   0 t,z,y,x  (micrograms/m**3)
PM25_NH4=>pm25_nh4   0 t,z,y,x  (micrograms/m**3)
PM25_NO3=>pm25_no3   0 t,z,y,x  (micrograms/m**3)
PM25_OC=>pm25_oc   0 t,z,y,x  (micrograms/m**3)
PM25_SOIL=>pm25_soil   0 t,z,y,x  (micrograms/m**3)
PM25_SO4=>pm25_so4   0 t,z,y,x  (micrograms/m**3)
PMC_TOT=>pmc_tot   0 t,z,y,x  (micrograms/m**3)
ENDVARS
EOF
         t0=1
         t1=48
         let numi=t0
         while [ ${numi} -le ${t1} ]; do

            fcsti=${numi}
            if [ ${numi} -le 9 ]; then fcsti="00"${numi}; fi
            if [ ${numi} -gt 9 ] && [ ${numi} -le 99 ]; then fcsti="0"${numi}; fi
   
            i=${numi}
            if [ ${numi} -le 9 ]; then i="0"${numi}; fi

            let j=numi+${numcyc}
            if [ ${j} -ge 72 ]; then
               let j=j-72
               date=${FOURTHDAY}
            elif [ ${j} -ge 48 ]; then
               let j=j-48
               date=${THIRDDAY}
            elif [ ${j} -ge 24 ]; then
               let j=j-24
               date=${TOMORROW}
            else
               date=${NOW}
            fi
            numj=`printf %2.2d ${j}`
   
            YH=`echo ${date} | cut -c1-4`
            MX=`echo ${date} | cut -c5-5`
            if [ ${MX} == '0' ]; then
               MH=`echo ${date} | cut -c6-6`
            else
               MH=`echo ${date} | cut -c5-6`
            fi
            DH=`echo ${date} | cut -c7-8`

               Newdate=$(${NDATE} ${numi} ${NOW}${cych})
               Ynew=`echo ${Newdate} | cut -c1-4`
               Xnew=`echo ${Newdate} | cut -c5-5`
               if [ ${Xnew} == '0' ]; then
                 Mnew=`echo ${Newdate} | cut -c6-6`
               else
                 Mnew=`echo ${Newdate} | cut -c5-6`
               fi
               Dnew=`echo ${Newdate} | cut -c7-8`
               hnew=`echo ${Newdate} | cut -c9-10`

               if [ -e aqm.plots ]; then /bin/rm -f aqm.plots; fi

               cat >  aqm.plots <<EOF
'reinit'
'set gxout shaded'
'set gxout grfill'
'set display color white'
'set mpdset hires'
'set grads off'
'set rgb 99   0   0 150'
'set rgb 88   0   0 200'
'set rgb 16   0   0 255'
'set rgb 18  80  80 255'
'set rgb 19 120 120 255'
'set rgb 20 150 150 255'
'set rgb 25 220 220 255'
'set rgb 48 150   0   0'
'set rgb 49 200   0   0'
'set rgb 52 255  80  80'
'set rgb 53 255 120 120'
'set rgb 54 255 150 150'
'set rgb 55 255 220 220'
'set rgb 89 238 220 220'
'c'
'open aqm1.ctl'
'open aqm2.ctl'
'set t ${numi}'
'set lat ${lat0[${iconus}]} ${lat1[${iconus}]}'
'set lon ${lon0[${iconus}]} ${lon1[${iconus}]}'
'${gs_dir}/diff3.aqm.${typ[${ptyp}]}.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} conus'
'set lat ${lat0[${ieast}]} ${lat1[${ieast}]}'
'set lon ${lon0[${ieast}]} ${lon1[${ieast}]}'
'${gs_dir}/diff3.aqm.${typ[${ptyp}]}.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} east'
'set lat ${lat0[${iwest}]} ${lat1[${iwest}]}'
'set lon ${lon0[${iwest}]} ${lon1[${iwest}]}'
'${gs_dir}/diff3.aqm.${typ[${ptyp}]}.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} west'
'set lat ${lat0[${ine10}]} ${lat1[${ine10}]}'
'set lon ${lon0[${ine10}]} ${lon1[${ine10}]}'
'${gs_dir}/diff3.aqm.${typ[${ptyp}]}.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} ne'
'set lat ${lat0[${inw10}]} ${lat1[${inw10}]}'
'set lon ${lon0[${inw10}]} ${lon1[${inw10}]}'
'${gs_dir}/diff3.aqm.${typ[${ptyp}]}.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} nw'
'set lat ${lat0[${ise10}]} ${lat1[${ise10}]}'
'set lon ${lon0[${ise10}]} ${lon1[${ise10}]}'
'${gs_dir}/diff3.aqm.${typ[${ptyp}]}.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} se'
'set lat ${lat0[${iswse}]} ${lat1[${iswse}]}'
'set lon ${lon0[${iswse}]} ${lon1[${iswse}]}'
'${gs_dir}/diff3.aqm.${typ[${ptyp}]}.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} sw'
'quit'
EOF
                  grads -blc "run aqm.plots"
               ((numi++))
            done
         ((ptyp++))
      done
      if [ ${flag_scp} == 'yes' ]; then  # for RZDM maintainence
         ##
         ## TRANSFER PLOTS TO RZDM
         ##
         scp ${outdir}/aqm*.png ${remote_user}@${remote_host}:${remote_dir}/${Y1}/${NOW}/${cychr}
      fi
   done   ## end for loop cych in "${cyc_opt[@]}"
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
if [ "${flag_qsub}" == "yes" ]; then
   working_dir=/lfs/h2/emc/stmp/${USER}/job_submit
   mkdir -p ${working_dir}
   cd ${working_dir}

   task_cpu='05:00:00'
   job_name=cmaq_pm_sp_${exp}${sel_cyc}
   batch_script=trans_cmaqpm_sp_${exp}${FIRSTDAY}.${LASTDAY}.sh
   if [ -e ${batch_script} ]; then /bin/rm -f ${batch_script}; fi

   logdir=/lfs/h2/emc/ptmp/${USER}/batch_logs
   if [ ! -d ${logdir} ]; then mkdir -p ${logdir}; fi

   logfile=${logdir}/${job_name}_${FIRSTDAY}_${LASTDAY}.out
   if [ -e ${logfile} ]; then /bin/rm -f ${logfile}; fi

   file_hd=aqm
   file_type=png
   cat > ${batch_script} << EOF
#!/bin/sh
#PBS -o ${logfile}
#PBS -e ${logfile}
#PBS -l place=shared,select=1:ncpus=1:mem=4GB
#PBS -N j${job_name}
#PBS -q "dev_transfer"
#PBS -A AQM-DEV
#PBS -l walltime=${task_cpu}
# 
# 
#### 
##
##  Provide fix date daily Hysplit data processing
##
   module load prod_util

   FIRSTDAY=${FIRSTDAY}
   LASTDAY=${LASTDAY}
   exp=${exp}
   remote_user=${remote_user}
   remote_host=${remote_host}
   remote_dir=${remote_dir}
   file_hd=${file_hd}
   file_type=${file_type}
   flag_update=${flag_update}
   declare -a cyc=( ${cyc_opt[@]} )
   fig_dir=${fig_dir}
EOF
   ##
   ##  Creat part 2 script : exact wording of scripts
   ##
   cat > ${batch_script}.add  << 'EOF'

   NOW=${FIRSTDAY}
   while [ ${NOW} -le ${LASTDAY} ]; do
      YY=`echo ${NOW} | cut -c1-4`
      YM=`echo ${NOW} | cut -c1-6`

      for i in "${cyc[@]}"; do
         cycle=t${i}z
         data_dir=${fig_dir}.${NOW}${i}
         if [ -d ${data_dir} ]; then
            scp ${data_dir}/${file_hd}*${file_type} ${remote_user}@${remote_host}:${remote_dir}/${YY}/${NOW}/${cycle}
         else
            echo "Can not find ${data_dir}, skip to next cycle/day"
         fi
      done  ## cycle time
      cdate=${NOW}"00"
      NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
   done
   if [ "${flag_update}" == "yes" ]; then
      script_dir=/lfs/h2/emc/physics/noscrub/${USER}/WEB/base
      cd ${script_dir}

      script_name=wcoss.run.cmaq_pm25.sh
      bash ${script_name} ${LASTDAY}
   fi
exit
EOF
   ##
   ##  Combine both working script together
   ##
   cat ${batch_script}.add >> ${batch_script}
   ##
   ##  Submit run scripts
   ##
   if [ "${flag_test}" == "no" ]; then
      qsub < ${batch_script}
   else
      echo "test qsub < ${batch_script} completed"
   fi
fi
exit

