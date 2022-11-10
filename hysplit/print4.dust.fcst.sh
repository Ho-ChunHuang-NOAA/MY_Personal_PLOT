#!/bin/bash 
module use /apps/test/lmodules/core/
module load GrADS/2.2.2
module load prod_util
module load prod_envir
hl=`hostname | cut -c1`
if [ "${hl}" == "v" ]; then
  phase12_id='g'
else
  phase12_id='t'
fi

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

MSG="USAGE $0 exp_id[prod|para|para#] [default all|06|12] YYYYMMDD_BEG YYYYMMDD_END"
if [ $# -lt 1 ]; then
  echo $MSG
  exit
elif [ $# -lt 2 ]; then
   opt=$1
   cyc_input=all
   FIRSTDAY=${TODAY}
   LASTDAY=${TODAY}
elif [ $# -lt 3 ]; then
   opt=$1
   cyc_input=$2
   FIRSTDAY=${TODAY}
   LASTDAY=${TODAY}
elif [ $# -lt 4 ]; then
   opt=$1
   cyc_input=$2
   FIRSTDAY=$3
   LASTDAY=$3
else
   opt=$1
   cyc_input=$2
   FIRSTDAY=$3
   LASTDAY=$4
fi
if [ "${LASTDAY}" == "${TODAY}" ]; then flag_update=yes; fi
flag_update=no

working_dir=/lfs/h2/emc/stmp/${USER}/job_submit
mkdir -p ${working_dir}
#
aqm=hysplit
capaqm=`echo ${aqm} | tr '[:lower:]' '[:upper:]'`
smlaqm=`echo ${aqm} | tr '[:upper:]' '[:lower:]'`
satellite=nesdis
#
## general setting
capopt=`echo ${opt} | tr '[:lower:]' '[:upper:]'`
smlopt=`echo ${opt} | tr '[:upper:]' '[:lower:]'`
capexp=${capopt}
exp=${smlopt}
ftype="_${exp}.png"
comdir=${COMROOT}/${smlaqm}/${exp}
comdir2=${comdir}
mydir=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp}
mydir2=/lfs/h2/emc/ptmp/${USER}/com/${smlaqm}/${exp}
## special setting
if [ ${exp} == 'prod' ]; then
   mydir=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp}
   mydir2=/lfs/h1/ops/${exp}/com/${smlaqm}/v7.9
elif [ ${exp} == 'ncopara' ]; then
   comdir=${COMROOT}/${smlaqm}/para
   comdir2=${comdir}
   mydir=${comdir}
   mydir2=${mydir}
elif [ ${exp} == 'acorn' ] || [ ${exp} == 'cactus' ]; then
  mydir2=/lfs/h2/emc/ptmp/${USER}/com/${smlaqm}/${exp}
else
   comdir=${mydir}
   comdir2=${mydir2}
fi
#
# web server ftp information
remote_dir=/home/people/emc/www/htdocs/mmb/hchuang/web/fig
remote_host=vm-lnx-dmznas1.ncep.noaa.gov
remote_host=emcrzdm.ncep.noaa.gov
remote_user=hchuang
### !------------------------------------------------------------------------------
### !G      GEOG NAME           CENLAT  CENLON   LLLAT   LLLON   URLAT   URLON PROJ
### !(8)    (18)              (8)     (8)     (8)     (8)     (8)     (8)      (30)
### !------------------------------------------------------------------------------
### NCUS    NCEP US              35.00 -100.00   17.89 -124.20   47.39  -40.98 STR/90;-105;0
### USLCC   UNITED STATES LCC    35.50  -90.00   20.00 -118.00   51.00  -62.00 LCC
### WEST    WESTERN US           37.50 -114.00   25.00 -125.00   55.00  -90.00 STR/90;-105;0
### CENT    CENTRAL US           37.50  -96.00   24.30 -107.40   49.70  -75.30 NPS
### EAST    EASTERN US           37.50  -78.00   24.57 -100.55   47.20  -65.42 STR/90;-90;0
### NWSE    NW SECTOR            44.25 -114.00   38.25 -126.00   50.25 -102.00 NPS
### NW10    NWRFC 218 SUBSET     46.00 -112.00   38.41 -125.85   54.46 -109.99 LCC/25;-95;25
### SWSE    SW SECTOR            34.25 -114.00   28.25 -126.00   40.25 -100.00 NPS
### NCSE    NC SECTOR            44.25  -96.00   38.25 -108.00   50.25  -84.00 NPS
### SCSE    SC SECTOR            34.25  -96.00   24.00 -108.90   40.25  -84.00 NPS
### NESE    NE SECTOR            44.25  -78.00   37.25  -89.00   47.25  -64.00 NPS
### NE10    NERFC 218 SUBSET     43.00  -77.00   40.95  -80.11   47.62  -64.02 LCC/25;-95;25
### SESE    SE SECTOR            34.25  -78.00   28.25  -90.00   40.25  -66.00 NPS
### SE10    SERFC 218 SUBSET     31.00  -82.00   24.12  -90.60   37.91  -73.94 LCC/25;-95;25
### AK      ALASKA               63.00 -150.00   49.00 -179.00   69.00 -116.40 NPS
### HI      HAWAII               20.00 -157.00   17.00 -161.50   23.00 -152.50 MER

gs_dir=`pwd`
declare -a reg=( dset conus east west ne10 nw10 se10 swse   ak   hi )
declare -a lon0=( -125 -125 -100 -125  -81 -125  -91 -125 -170 -161 )
declare -a lon1=(  -65  -65  -65  -90  -65 -110  -74 -100 -130 -154 )
declare -a lat0=(   25   25   25   25   37   38   25   28   50   18 )
declare -a lat1=(   50   50   47   50   48   50   40   40   80   23 )
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

declare -a modtyp=( full   ak   hi )
declare -a xlon0=(  -125 -170 -166 )
declare -a ylat0=(    25   50   15 )
declare -a nxdef=(   601  401  401 )
declare -a nydef=(   251  301  201 )
declare -a resol=(  0.10 0.10 0.05 )
imod00=0
imodak=1
imodhi=2

declare -a area_opt=( cs ak hi )
declare -a aero_opt=( dust smoke all )
declare -a mchr=( JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC )
case ${cyc_input} in
   ''|*[!0-9]*) if [ "${cyc_input}" == "all" ]; then
            declare -a cyc_hour=( 06 12 )
         else
            echo "input choice for cycle time is not defined $2, program stop"
            echo $MSG
            exit
         fi ;;
   *) cyc_in=`printf %2.2d $2`
      if [ "${cyc_in}" == "06" ] || [ "${cyc_in}" == "12" ]; then
         declare -a cyc_hour=( ${cyc_in} )
      else
         echo "input choice for cycle time is not defined $2, program stop"
         echo $MSG
         exit
      fi ;;
esac
declare -a otyp=( pbl sfc )

iarea=0
area=${area_opt[${iarea}]}

iaero=0
aero=${aero_opt[${iaero}]}
case ${aero} in
   smoke) satellite=nesdis ;;
   dust)  satellite=aquamodis ;;
esac


NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do

   cdate=${NOW}"06"
   TOMORROW=$(${NDATE} +24 ${cdate}| cut -c1-8)
   THIRDDAY=$(${NDATE} +48 ${cdate}| cut -c1-8)

   if [ -d  ${comdir}/${aero}${area}.${NOW} ]; then
      idir=${comdir}
   elif [ -d ${comdir2}/${aero}${area}.${NOW} ]; then
      idir=${comdir2}
   elif [ -d  ${mydir}/${aero}${area}.${NOW} ]; then
      idir=${mydir}
   elif [ -d ${mydir2}/${aero}${area}.${NOW} ]; then
      idir=${mydir2}
   else
      echo " ${NOW} :: NO ${comdir}/${aero}${area}.${NOW} & ${comdir2}/${aero}${area}.${NOW}, skip to nexy day"
      echo " ${NOW} :: NO ${mydir}/${aero}${area}.${NOW} & ${mydir2}/${aero}${area}.${NOW}, skip to nexy day"
   fi

   YY=`echo ${NOW} | cut -c1-4`
   MX=`echo ${NOW} | cut -c5-5`
   if [ ${MX} == '0' ]; then
      MM=`echo ${NOW} | cut -c6-6`
   else
      MM=`echo ${NOW} | cut -c5-6`
   fi
   DD=`echo ${NOW} | cut -c7-8`

   for k in "${cyc_hour[@]}"; do
      cyc=`printf %2.2d ${k}`
      cycle="t${cyc}z"
      i=`expr ${k} + 1`
      cycp1=`printf %2.2d ${i}`

      data_dir=/lfs/h2/emc/stmp/${USER}/${aero}_${exp}/${aqm}_${area}.${NOW}.${cycle}
      if [ -d ${data_dir} ]; then
         /bin/rm -f ${data_dir}/*
      else
         mkdir -p ${data_dir}
      fi
      cd ${data_dir}

      for layer in "${otyp[@]}"; do
         grib2_cs=${aero}${area}.${cycle}.${layer}.1hr.grib2
         flag_plot_cs=yes
         if [ -s ${idir}/${aero}${area}.${NOW}/${grib2_cs} ]; then
            /bin/cp -f ${idir}/${aero}${area}.${NOW}/${grib2_cs} .
         else
            echo "can not find ${idir}/${aero}${area}.${NOW}/${grib2_cs}"
            flag_plot_cs=no
         fi

         if [ "${flag_plot_cs}" == "yes" ]; then
            case ${layer} in
               pbl) plotvar=LIPMF5000_0m
                    hgt=5000 ;;
               sfc) plotvar=LIPMF100_0m
                    hgt=100 ;;
            esac

## xdef ${nxdef[${imod}]} linear ${xlon0[${imod}]} ${resol[${imod}]}
## ydef ${nydef[${imod}]} linear ${ylat0[${imod}]} ${resol[${imod}]}
cat > ${data_dir}/${aero}${area}.ctl <<EOF
dset ${data_dir}/${grib2_cs}
index ${data_dir}/${grib2_cs}.idx
undef 9.999E+20
title ${data_dir}/${grib2_cs}
* produced by g2ctl v0.1.0
* command line options: ${aero}${area}.${cycle}.${layer}.1hr.grib2
* griddef=1:0:(601 x 251):grid_template=0:winds(N/S): lat-lon grid:(601 x 251) units 1e-06 input WE:SN output WE:SN res 48 lat 25.000000 to 50.000000 by 0.100000 lon 235.000000 to 295.000000 by 0.100000 #points=150851:winds(N/S)
dtype grib2
ydef 251 linear 25.000000 0.1
xdef 601 linear -125.000000 0.100000
tdef 48 linear ${cycp1}Z${DD}${mchr[$MM-1]}${YY} 1hr
zdef 1 linear 1 1
vars 1
${plotvar}  0,103,${hgt},0   0,13,195,0 ** ${hgt}-0 m above ground Integrated column particulate matter (fine) [log10(10-6gm-3)]
ENDVARS
EOF
         gribmap -i ${data_dir}/${aero}${area}.ctl
      ##
         t0=1
         t1=48
         let numi=t0
         while [ ${numi} -le ${t1} ]; do
            fcsti=`printf %3.3d ${numi}`
            i=`printf %2.2d ${numi}`
      
            let j=${numi}+${k}

            if [ ${j} -ge 48 ]; then
               let j=j-48
               date=${THIRDDAY}
            elif [ ${j} -ge 24 ]; then
               let j=j-24
               date=${TOMORROW}
            else
               date=${NOW}
            fi
            numj=`printf %2.2d ${j}`
            
cat > ${data_dir}/${i}.plot << EOF
'set gxout shaded'
'set gxout grfill'
'set display color white'
'set mpdset hires'
'set grads off'
'set rgb 98 255 105 180'
'set rgb 79 240 240 240'
'set rgb 17  55  55 255'
'set rgb 18 110 110 255'
'set rgb 19 165 165 255'
'set rgb 20 220 220 255'
'c'
'open ${data_dir}/${aero}${area}.ctl'
'set t ${i}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aero} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${idset}]}${aero}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${iconus}]} ${lat1[${iconus}]}'
'set lon ${lon0[${iconus}]} ${lon1[${iconus}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aero} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${iconus}]}${aero}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ieast}]} ${lat1[${ieast}]}'
'set lon ${lon0[${ieast}]} ${lon1[${ieast}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aero} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${ieast}]}${aero}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${iwest}]} ${lat1[${iwest}]}'
'set lon ${lon0[${iwest}]} ${lon1[${iwest}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aero} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${iwest}]}${aero}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ine10}]} ${lat1[${ine10}]}'
'set lon ${lon0[${ine10}]} ${lon1[${ine10}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aero} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${ine10}]}${aero}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${inw10}]} ${lat1[${inw10}]}'
'set lon ${lon0[${inw10}]} ${lon1[${inw10}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aero} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${inw10}]}${aero}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ise10}]} ${lat1[${ise10}]}'
'set lon ${lon0[${ise10}]} ${lon1[${ise10}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aero} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${ise10}]}${aero}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${iswse}]} ${lat1[${iswse}]}'
'set lon ${lon0[${iswse}]} ${lon1[${iswse}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aero} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${iswse}]}${aero}${layer}_${i}${ftype} png x800 y600 white'
'c'
'quit'
EOF
               grads -blc "run ${data_dir}/${i}.plot"
            ((numi++))
         done  ## loop forecast hour

         fi  ## end if flag_plot_cs
      
      done   ## loop layer
      if [ "${flag_scp}" == "yes" ]; then
         scp ${data_dir}/${smlaqm}*${ftype} ${remote_user}@${remote_host}:${remote_dir}/${YY}/${NOW}/${cycle}
      fi
   done  ## loop cycle time
   echo "INPUT DATA DIR = ${idir}"
   echo "OUTPUT FIG DIR = ${data_dir}"
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
if [ "${flag_qsub}" == "yes" ]; then
   cd ${working_dir}
   task_cpu='05:00:00'
   job_name=prtdst${smlaqm}_${exp}
   batch_script=prtdst_${smlaqm}_${exp}.sh
   if [ -e ${batch_script} ]; then /bin/rm -f ${batch_script}; fi

   logdir=/lfs/h2/emc/ptmp/${USER}/batch_logs
   if [ ! -d ${logdir} ]; then mkdir -p ${logdir}; fi

   logfile=${logdir}/${job_name}_${TODAY}.out
   if [ -e ${logfile} ]; then /bin/rm -f ${logfile}; fi
cat > ${batch_script} << EOF
#!/bin/bash
#PBS -o ${logfile}
#PBS -e ${logfile}
#PBS -l place=shared,select=1:ncpus=1:mem=4GB
#PBS -N j${job_name}
#PBS -q dev_transfer
#PBS -A AQM-DEV
#PBS -l walltime=${task_cpu}
#### 
# 
# 
##
##  Provide fix date daily Hysplit data processing
##

   FIRSTDAY=${FIRSTDAY}
   LASTDAY=${LASTDAY}
   exp=${exp}
   area=${area}  ## currently only conus for dust
   aqm=${smlaqm}
   aero=${aero}
   ftype=${ftype}
   remote_user=${remote_user}
   remote_host=${remote_host}
   remote_dir=${remote_dir}
   flag_update=${flag_update}
   declare -a cyc=( ${cyc_hour[@]} )
   data_dir=${data_dir}
EOF
      ##
      ##  Creat part 2 script : exact wording of scripts
      ##
cat > ${batch_script}.add  << 'EOF'

source ~/.bashrc


   NOW=${FIRSTDAY}
   while [ ${NOW} -le ${LASTDAY} ]; do
      YY=`echo ${NOW} | cut -c1-4`
      YM=`echo ${NOW} | cut -c1-6`

      for i in "${cyc[@]}"; do
         cycle=t${i}z
         ## data_dir=/lfs/h2/emc/stmp/${USER}/${aero}_${exp}/${aqm}_${area}.${NOW}.${cycle}
         scp ${data_dir}/${aqm}*${ftype} ${remote_user}@${remote_host}:${remote_dir}/${YY}/${NOW}/${cycle}
      done  ## cycle time
      cdate=${NOW}"00"
      NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
   done
   if [ "${flag_update}" == "yes" ]; then
      script_dir=/lfs/h2/emc/physics/noscrub/${USER}/WEB/base
      cd ${script_dir}

      script_name=wcoss.run.hysplit_emc_tcomp.sh
      bash ${script_name} ${LASTDAY}

      script_name=wcoss.run.hysplit_nco_tcomp.sh
      bash ${script_name} ${LASTDAY}

      script_name=wcoss.run.hysplit_nco_comp.sh
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
      echo "job script at ${working_dir}"
      echo "test qsub < ${batch_script} completed"
   fi
fi
exit
