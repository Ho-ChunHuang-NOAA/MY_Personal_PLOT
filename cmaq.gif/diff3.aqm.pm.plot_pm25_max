#!/bin/sh
##
## SCRIPT FOR SINGLE DAY PROCESSING AND MAP GENERATION
##
## YYYYMMDD is the start day of NAQFC PM   simulation
## Cycle_hr is the model run starting hour
##
module load GrADS/2.2.0
module load prod_util/1.1.0
module load prod_envir/1.0.3
hl=`hostname | cut -c1`
if [ "${hl}" == "v" ]; then
  phase12_id='g'
else
  phase12_id='t'
fi

flag_test=yes
flag_test=no

flag_bsub=no
flag_bsub=yes

if [ "${flag_bsub}" == "yes" ]; then
   flag_scp=no
else
   flag_scp=yes
fi

TODAY=`date +%Y%m%d`

MSG="USAGE : $0 exp1 exp2 [exp2-exp1] Cycle_hr (default:all|06|12) YYYYMMDD_BEG YYYYMMDD_END"

if [ $# -lt 2 ]; then
   echo $MSG
   exit
else
   opt1=$1
   opt2=$2
fi
if [ $# -lt 3 ]; then
   sel_cyc=all
   FIRSTDAY=${TODAY}
   LASTDAY=${TODAY}
elif [ $# -lt 4 ]; then
   sel_cyc=$3
   FIRSTDAY=${TODAY}
   LASTDAY=${TODAY}
elif [ $# -lt 5 ]; then
   sel_cyc=$3
   FIRSTDAY=$4
   LASTDAY=$4
else
   sel_cyc=$3
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
project2=meso
capexp1=${capopt}
exp1=${smlopt}
comdir=/gpfs/hps/nco/ops/com/${smlaqm}/${exp1}
## comdir2=${comdir}
comdir2=/gpfs/hps3/emc/${project2}/noscrub/${USER}/com/${smlaqm}/${exp1}
comdir2=/gpfs/${phase12_id}d1/emc/meso/noscrub/${USER}/com/${smlaqm}/${exp1}
mydir=/gpfs/hps3/emc/${project}/noscrub/${USER}/com/${smlaqm}/${exp1}
mydir2=/gpfs/hps3/ptmp/${USER}/com/${smlaqm}/${exp1}
mydir=/gpfs/hps3/emc/${project2}/noscrub/${USER}/com/${smlaqm}/${exp1}

## special setting
if [ ${smlopt} == 'prod' ]; then
   mydir=${comdir}
   mydir2=${comdir2}
elif [ ${smlopt} == 'ncopara' ]; then
   mydir=${comdir}
   mydir2=${comdir}
elif [ ${smlopt} == 'para' ]; then
   comdir=${mydir}
   comdir2=${mydir2}
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
comdir=/gpfs/hps/nco/ops/com/${smlaqm}/${exp2}
comdir2=${comdir}
comdir2=/gpfs/${phase12_id}d1/emc/meso/noscrub/${USER}/com/${smlaqm}/${exp2}
comdir2=/gpfs/hps3/emc/${project2}/noscrub/${USER}/com/${smlaqm}/${exp2}
mydir=/gpfs/hps3/emc/${project}/noscrub/${USER}/com/${smlaqm}/${exp2}
mydir2=/gpfs/hps3/ptmp/${USER}/com/${smlaqm}/${exp2}
mydir=/gpfs/hps3/emc/${project2}/noscrub/${USER}/com/${smlaqm}/${exp2}

## special setting
if [ ${smlopt} == 'prod' ]; then
   mydir=${comdir}
   mydir2=${comdir2}
elif [ ${smlopt} == 'ncopara' ]; then
   mydir=${comdir}
   mydir2=${comdir}
elif [ ${smlopt} == 'para' ]; then
   comdir=${mydir}
   comdir2=${mydir2}
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
ftype="_${exp2}m${exp1}.gif"

if [ ${exp} == 'para1' ]; then flag_update=no; fi

## echo " ${exp} ${sel_cyc} ${FIRSTDAY} ${LASTDAY}"

remote_dir=/home/people/emc/www/htdocs/mmb/hchuang/web/fig
remote_host=emcrzdm.ncep.noaa.gov
remote_host=rzdm
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

declare -a mchr=( JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC )

## declare -a typ=( max_1hr_pm25 ave_24hr_pm25 pm25 sp_pm )
declare -a typ=( max_1hr_pm25 ave_24hr_pm25 pm25 )
## declare -a typ=( max_1hr_pm25 ave_24hr_pm25 )
## declare -a typ=( sp_pm )
ntyp=${#typ[@]}

capexp=`echo ${exp} | tr '[:lower:]' '[:upper:]'`
if [ ${exp} == 'para1' ]; then flag_update=no; fi

NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do

   flag_plot=yes
   echo "////////////////////////////////////////////////////"
   if [ -d  ${comdir1_s1}/aqm.${NOW} ]; then
      idir1=${comdir1_s1}/aqm.${NOW}
      echo "FILE 1 from ${idir1}"
   elif [ -d ${comdir2_s1}/aqm.${NOW} ]; then
      idir1=${comdir2_s1}/aqm.${NOW}
      echo "FILE 1 from ${idir1}"
   elif [ -d  ${mydir1_s1}/aqm.${NOW} ]; then
      idir1=${mydir1_s1}/aqm.${NOW}
      echo "FILE 1 from ${idir1}"
   elif [ -d ${mydir2_s1}/aqm.${NOW} ]; then
      idir1=${mydir2_s1}/aqm.${NOW}
      echo "FILE 1 from ${idir1}"
   else
      flag_plot=no
      echo " ${NOW} :: NO ${comdir1_s1}/aqm.${NOW} & ${comdir2_s1}/aqm.${NOW}, skip to nexy day"
      echo " ${NOW} :: NO ${mydir1_s1}/aqm.${NOW} & ${mydir2_s1}/aqm.${NOW}, skip to nexy day"
   fi

   echo "////////////////////////////////////////////////////"
   if [ -d  ${comdir1_s2}/aqm.${NOW} ]; then
      idir2=${comdir1_s2}/aqm.${NOW}
      echo "FILE 2 from ${idir2}"
   elif [ -d ${comdir2_s2}/aqm.${NOW} ]; then
      idir2=${comdir2_s2}/aqm.${NOW}
      echo "FILE 2 from ${idir2}"
   elif [ -d  ${mydir1_s2}/aqm.${NOW} ]; then
      idir2=${mydir1_s2}/aqm.${NOW}
      echo "FILE 2 from ${idir2}"
   elif [ -d ${mydir2_s2}/aqm.${NOW} ]; then
      idir2=${mydir2_s2}/aqm.${NOW}
      echo "FILE 2 from ${idir2}"
   else
      flag_plot=no
      echo " ${NOW} :: NO ${comdir1_s2}/aqm.${NOW} & ${comdir2_s2}/aqm.${NOW}, skip to nexy day"
      echo " ${NOW} :: NO ${mydir1_s2}/aqm.${NOW} & ${mydir2_s2}/aqm.${NOW}, skip to nexy day"
   fi
   echo "////////////////////////////////////////////////////"
   if [ "${flag_plot}" == "no" ]; then continue; fi

   for cych in "${cyc_opt[@]}"; do
      cdate=${NOW}${cych}
      F1=$(${NDATE} +1 ${cdate}| cut -c9-10)
      TOMORROW=$(${NDATE} +24 ${cdate}| cut -c1-8)
      THIRDDAY=$(${NDATE} +48 ${cdate}| cut -c1-8)
   
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
      range1=05Z${D1}${mchr[$M1-1]}${Y1}-04Z${D2}${mchr[$M2-1]}${Y2}
      range2=05Z${D2}${mchr[$M2-1]}${Y2}-04Z${D3}${mchr[$M3-1]}${Y3}

      ## tmpdir=/naqfc/noscrub/${USER}/com_aqm_${exp}_pm_max.${NOW}${cych}
      tmpdir=/gpfs/dell2/stmp/${USER}/com2_aqm_${exp}_pm_max.${NOW}${cych}
      if [ -d ${tmpdir} ]; then /bin/rm -rf ${tmpdir}; fi
      mkdir -p ${tmpdir}
   
      let numcyc=${cych}
      cychr="t${cych}z"
      echo " Perform operation on cych = ${cych}  cychr = ${cychr}"
      if [ "${flag_test}" == "yes" ]; then continue; fi
      ## aqm.t06z.ave_24hr_pm25.148.grib2
      ## aqm.t06z.max_1hr_pm25.148.grib2
      ## use ncf to plot      sp_pm)         cp ${comdir}/aqm.${cychr}.chem_sfc.f*.${grid_id2}.grib2 ${tmpdir};;
      for i in "${typ[@]}"
      do
        case ${i} in
           max_1hr_pm25)  cp ${idir1}/aqm.${cychr}.max_1hr_pm25.${grid_id}.grib2  ${tmpdir}/s1_aqm.${cychr}.max_1hr_pm25.${grid_id}.grib2
                          cp ${idir2}/aqm.${cychr}.max_1hr_pm25.${grid_id}.grib2  ${tmpdir}/s2_aqm.${cychr}.max_1hr_pm25.${grid_id}.grib2;;
           ave_24hr_pm25) cp ${idir1}/aqm.${cychr}.ave_24hr_pm25.${grid_id}.grib2 ${tmpdir}/s1_aqm.${cychr}.ave_24hr_pm25.${grid_id}.grib2
                          cp ${idir2}/aqm.${cychr}.ave_24hr_pm25.${grid_id}.grib2 ${tmpdir}/s2_aqm.${cychr}.ave_24hr_pm25.${grid_id}.grib2;;
           sp_pm)         cp ${idir1}/aqm.${cychr}.aconc_sfc.ncf                  ${tmpdir}/s1_aqm.${cychr}.aconc_sfc.ncf
                          cp ${idir2}/aqm.${cychr}.aconc_sfc.ncf                  ${tmpdir}/s2_aqm.${cychr}.aconc_sfc.ncf;;
           pm25)          mkdir -p ${tmpdir}/s1_pm25 ${tmpdir}/s2_pm25
                          cp ${idir1}/aqm.${cychr}.pm25.f*.${grid_id2}.grib2      ${tmpdir}/s1_pm25
                          cp ${idir2}/aqm.${cychr}.pm25.f*.${grid_id2}.grib2      ${tmpdir}/s2_pm25;;
         esac
      done
      cd ${tmpdir}
   
      outdir=/gpfs/dell2/stmp/${USER}/daily_plot_pm25_max/aqm_${exp}_pm_max.${NOW}${cych}
      if [ ! -d ${outdir} ]; then mkdir -p ${outdir}; fi
   
      n0=0
      let n1=${ntyp}-1
      let ptyp=n0
      while [ ${ptyp} -le ${n1} ]; do

         if [ -e aqm1.ctl ]; then /bin/rm -f aqm1.ctl; fi
         if [ -e aqm2.ctl ]; then /bin/rm -f aqm2.ctl; fi
         if [ ${typ[${ptyp}]} = 'max_1hr_pm25' ] || [ ${typ[${ptyp}]} = 'ave_24hr_pm25' ]; then 
            if [ ${typ[${ptyp}]} = 'max_1hr_pm25' ]; then 
               cat >  aqm1.ctl <<EOF
dset ${tmpdir}/s1_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
index ${tmpdir}/s1_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2.idx
undef 9.999E+20
title s1_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
* produced by g2ctl v0.1.0
* command line options: aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
* griddef=1:0:(1473 x 1025):grid_template=30:winds(grid): Lambert Conformal: (1473 x 1025) input WE:SN output WE:SN res 8 Lat1 12.190000 Lon1 226.541000 LoV 265.000000 LatD 25.000000 Latin1 25.000000 Latin2 25.000000 LatSP 0.000000 LonSP 0.000000 Nor
dtype grib2
pdef 1473 1025 lccr 12.190000 -133.459 1 1 25.000000 25.000000 -95 5079.000000 5079.000000
xdef 2191 linear -152.852997 0.0472378093784381
ydef 1063 linear 12.202469 0.0461727272727273
tdef 2 linear 04Z${D2}${mchr[$M2-1]}${Y2} 1dy
zdef 1 linear 1 1
vars 1
PDMAX1sig1000   0,104,1   0,14,202,0 ** 1 sigma level PM 2.5 Daily Max from 1-hour Average [ugm-3]
ENDVARS
EOF
               cat >  aqm2.ctl <<EOF
dset ${tmpdir}/s2_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
index ${tmpdir}/s2_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2.idx
undef 9.999E+20
title s2_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
* produced by g2ctl v0.1.0
* command line options: aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
* griddef=1:0:(1473 x 1025):grid_template=30:winds(grid): Lambert Conformal: (1473 x 1025) input WE:SN output WE:SN res 8 Lat1 12.190000 Lon1 226.541000 LoV 265.000000 LatD 25.000000 Latin1 25.000000 Latin2 25.000000 LatSP 0.000000 LonSP 0.000000 Nor
dtype grib2
pdef 1473 1025 lccr 12.190000 -133.459 1 1 25.000000 25.000000 -95 5079.000000 5079.000000
xdef 2191 linear -152.852997 0.0472378093784381
ydef 1063 linear 12.202469 0.0461727272727273
tdef 2 linear 04Z${D2}${mchr[$M2-1]}${Y2} 1dy
zdef 1 linear 1 1
vars 1
PDMAX1sig1000   0,104,1   0,14,202,0 ** 1 sigma level PM 2.5 Daily Max from 1-hour Average [ugm-3]
ENDVARS
EOF
               var=PDMAX1sig1000
            elif [ ${typ[${ptyp}]} = 'ave_24hr_pm25' ]; then 

##xdef 2191 linear -152.852997 0.0472378093784381
##ydef 1063 linear 12.202469 0.0461727272727273
##xdef 1473 linear -133.459000 0.0472378093784381
##ydef 1025 linear 12.190000 0.0461727272727273
               cat >  aqm1.ctl <<EOF
dset ${tmpdir}/s1_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
index ${tmpdir}/s1_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2.idx
undef 9.999E+20
title s1_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
* produced by g2ctl v0.1.0
* command line options: aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
* griddef=1:0:(1473 x 1025):grid_template=30:winds(grid): Lambert Conformal: (1473 x 1025) input WE:SN output WE:SN res 8 Lat1 12.190000 Lon1 226.541000 LoV 265.000000 LatD 25.000000 Latin1 25.000000 Latin2 25.000000 LatSP 0.000000 LonSP 0.000000 Nor
dtype grib2
pdef 1473 1025 lccr 12.190000 -133.459 1 1 25.000000 25.000000 -95 5079.000000 5079.000000
xdef 2191 linear -152.852997 0.0472378093784381
ydef 1063 linear 12.202469 0.0461727272727273
tdef 2 linear 04Z${D2}${mchr[$M2-1]}${Y2} 1dy
zdef 1 linear 1 1
vars 1
PMTFsig1000   0,104,1   0,13,193,0 ** 1 sigma level Particulate matter (fine) [10-6gm-3]
ENDVARS
EOF
               cat >  aqm2.ctl <<EOF
dset ${tmpdir}/s2_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
index ${tmpdir}/s2_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2.idx
undef 9.999E+20
title s2_aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
* produced by g2ctl v0.1.0
* command line options: aqm.${cychr}.${typ[${ptyp}]}.${grid_id}.grib2
* griddef=1:0:(1473 x 1025):grid_template=30:winds(grid): Lambert Conformal: (1473 x 1025) input WE:SN output WE:SN res 8 Lat1 12.190000 Lon1 226.541000 LoV 265.000000 LatD 25.000000 Latin1 25.000000 Latin2 25.000000 LatSP 0.000000 LonSP 0.000000 Nor
dtype grib2
pdef 1473 1025 lccr 12.190000 -133.459 1 1 25.000000 25.000000 -95 5079.000000 5079.000000
xdef 2191 linear -152.852997 0.0472378093784381
ydef 1063 linear 12.202469 0.0461727272727273
tdef 2 linear 04Z${D2}${mchr[$M2-1]}${Y2} 1dy
zdef 1 linear 1 1
vars 1
PMTFsig1000   0,104,1   0,13,193,0 ** 1 sigma level Particulate matter (fine) [10-6gm-3]
ENDVARS
EOF
               var=PMTFsig1000
            fi
            gribmap -i aqm1.ctl
            gribmap -i aqm2.ctl

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
'set lat ${lat0[${iconus}]} ${lat1[${iconus}]}'
'set lon ${lon0[${iconus}]} ${lon1[${iconus}]}'
'${gs_dir}/diff3.aqm.pm25max.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${typ[${ptyp}]} ${range1} ${range2} ${var} conus'
'set lat ${lat0[${ieast}]} ${lat1[${ieast}]}'
'set lon ${lon0[${ieast}]} ${lon1[${ieast}]}'
'${gs_dir}/diff3.aqm.pm25max.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${typ[${ptyp}]} ${range1} ${range2} ${var} east'
'set lat ${lat0[${iwest}]} ${lat1[${iwest}]}'
'set lon ${lon0[${iwest}]} ${lon1[${iwest}]}'
'${gs_dir}/diff3.aqm.pm25max.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${typ[${ptyp}]} ${range1} ${range2} ${var} west'
'set lat ${lat0[${ine10}]} ${lat1[${ine10}]}'
'set lon ${lon0[${ine10}]} ${lon1[${ine10}]}'
'${gs_dir}/diff3.aqm.pm25max.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${typ[${ptyp}]} ${range1} ${range2} ${var} ne'
'set lat ${lat0[${inw10}]} ${lat1[${inw10}]}'
'set lon ${lon0[${inw10}]} ${lon1[${inw10}]}'
'${gs_dir}/diff3.aqm.pm25max.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${typ[${ptyp}]} ${range1} ${range2} ${var} nw'
'set lat ${lat0[${ise10}]} ${lat1[${ise10}]}'
'set lon ${lon0[${ise10}]} ${lon1[${ise10}]}'
'${gs_dir}/diff3.aqm.pm25max.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${typ[${ptyp}]} ${range1} ${range2} ${var} se'
'set lat ${lat0[${iswse}]} ${lat1[${iswse}]}'
'set lon ${lon0[${iswse}]} ${lon1[${iswse}]}'
'${gs_dir}/diff3.aqm.pm25max.gs ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${typ[${ptyp}]} ${range1} ${range2} ${var} sw'
'quit'
EOF
               grads -d Cairo -h GD -blc "run aqm.plots"
         else   ## for hourly sp_pm and pm25
#
# create ctl prior to fcst loop , which is the same for fcst hours, do not need to delete and re-create
            if [ ${typ[${ptyp}]} = 'sp_pm' ]; then 
               if [ -e aqm1.ctl ]; then /bin/rm -f aqm1.ctl; fi
               if [ -e aqm2.ctl ]; then /bin/rm -f aqm2.ctl; fi
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
            fi   ## NCF contains 48 hours file
   
            t0=1
            t1=48
            let numi=t0
            while [ ${numi} -le ${t1} ]; do
   
               fcsti=${numi}
               if [ ${numi} -le 9 ]; then fcsti="00"${numi}; fi
               if [ ${numi} -gt 9 ] && [ ${numi} -le 99 ]; then fcsti="0"${numi}; fi
      
               i=${numi}
               if [ ${numi} -le 9 ]; then i="0"${numi}; fi
   
               ## older version of cmaq include IC as f01 and FCST 48hr as f49
               ## switch the index here for this case
               ## let ip1=${numi}+1
               ## dati=${ip1}
               ## if [ ${ip1} -le 9 ]; then dati="0"${ip1}; fi
               ## Oct 28, 2015 switch the dati to i in aqm.ctl below
   
               let j=numi+${numcyc}
               if [ ${j} -ge 48 ]; then
                  let j=j-48
                  date=${THIRDDAY}
               elif [ ${j} -ge 24 ]; then
                  let j=j-24
                  date=${TOMORROW}
               else
                  date=${NOW}
               fi
               numj=${j}
               if [ ${j} -le 9 ]; then numj="0"${j}; fi
      
               YH=`echo ${date} | cut -c1-4`
               MX=`echo ${date} | cut -c5-5`
               if [ ${MX} == '0' ]; then
                  MH=`echo ${date} | cut -c6-6`
               else
                  MH=`echo ${date} | cut -c5-6`
               fi
               DH=`echo ${date} | cut -c7-8`
   
               if [ ${typ[${ptyp}]} = 'sp_pm' ]; then 
   
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
                  grads -d Cairo -h GD -blc "run aqm.plots"
               elif [ ${typ[${ptyp}]} = 'pm25' ]; then 

## xdef 650 linear -133.628000 0.117510583392794
## ydef 295 linear 21.821000 0.109090909090909
## tdef 1 linear 07Z27oct2015 1mo
## tdef 1 linear 04Z29oct2015 1mo
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
                  if [ -e aqm1.ctl ]; then /bin/rm -f aqm1.ctl; fi
                  if [ -e aqm2.ctl ]; then /bin/rm -f aqm2.ctl; fi
   
                  cat >  aqm1.ctl <<EOF
dset ${tmpdir}/s1_pm25/aqm.${cychr}.${typ[${ptyp}]}.f${i}.${grid_id2}.grib2
index ${tmpdir}/s1_pm25/aqm.${cychr}.${typ[${ptyp}]}.f${i}.${grid_id2}.grib2.idx
undef 9.999E+20
title s1_aqm.${cychr}.${typ[${ptyp}]}.f${i}.${grid_id2}.grib2
* produced by g2ctl v0.1.0
* command line options: aqm.t06z.pm25.f${i}.${grid_id2}.grib2
* griddef=1:0:(442 x 265):grid_template=30:winds(grid): Lambert Conformal: (442 x 265) input WE:SN output WE:SN res 8 Lat1 21.821000 Lon1 239.372000 LoV 263.000000 LatD 33.000000 Latin1 33.000000 Latin2 45.000000 LatSP 0.000000 LonSP 0.000000 North P
dtype grib2
pdef 442 265 lccr 21.821000 -120.628 1 1 33.000000 45.000000 -97 12000.000000 12000.000000
xdef 620 linear -131.659038 0.117510583392794
ydef 293 linear 21.153709 0.109090909090909
tdef 1 linear ${hnew}Z${Dnew}${mchr[$Mnew-1]}${Ynew} 1mo
zdef 1 linear 1 1
vars 1
PMTFsig1000   0,104,1   0,13,193,0 ** 1 sigma level Particulate matter (fine) [10-6gm-3]
ENDVARS
EOF
                  cat >  aqm2.ctl <<EOF
dset ${tmpdir}/s2_pm25/aqm.${cychr}.${typ[${ptyp}]}.f${i}.${grid_id2}.grib2
index ${tmpdir}/s2_pm25/aqm.${cychr}.${typ[${ptyp}]}.f${i}.${grid_id2}.grib2.idx
undef 9.999E+20
title s2_aqm.${cychr}.${typ[${ptyp}]}.f${i}.${grid_id2}.grib2
* produced by g2ctl v0.1.0
* command line options: aqm.t06z.pm25.f${i}.${grid_id2}.grib2
* griddef=1:0:(442 x 265):grid_template=30:winds(grid): Lambert Conformal: (442 x 265) input WE:SN output WE:SN res 8 Lat1 21.821000 Lon1 239.372000 LoV 263.000000 LatD 33.000000 Latin1 33.000000 Latin2 45.000000 LatSP 0.000000 LonSP 0.000000 North P
dtype grib2
pdef 442 265 lccr 21.821000 -120.628 1 1 33.000000 45.000000 -97 12000.000000 12000.000000
xdef 620 linear -131.659038 0.117510583392794
ydef 293 linear 21.153709 0.109090909090909
tdef 1 linear ${hnew}Z${Dnew}${mchr[$Mnew-1]}${Ynew} 1mo
zdef 1 linear 1 1
vars 1
PMTFsig1000   0,104,1   0,13,193,0 ** 1 sigma level Particulate matter (fine) [10-6gm-3]
ENDVARS
EOF
                  gribmap -i aqm1.ctl
                  gribmap -i aqm2.ctl
   
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
                  grads -d Cairo -h GD -blc "run aqm.plots"
               fi
               ((numi++))
            done
         fi
         ((ptyp++))
      done
      if [ ${flag_scp} == 'yes' ]; then  # for RZDM maintainence
         ##
         ## TRANSFER PLOTS TO RZDM
         ##
         scp ${outdir}/aqm*.gif ${remote_user}@${remote_host}:${remote_dir}/${Y1}/${NOW}/${cychr}
      fi
   done   ## end for loop cych in "${cyc_opt[@]}"
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done

if [ "${flag_bsub}" == "yes" ]; then
   working_dir=/gpfs/dell2/stmp/${USER}/job_submit
   mkdir -p ${working_dir}
   cd ${working_dir}

   task_cpu='05:00'
   job_name=cmaq_pmmax_${exp}${sel_cyc}
   batch_script=trans_cmaqpmmax_${exp}.${FIRSTDAY}.${LASTDAY}.sh
   if [ -e ${batch_script} ]; then /bin/rm -f ${batch_script}; fi

   logdir=/gpfs/dell2/ptmp/${USER}/batch.logs
   if [ ! -d ${logdir} ]; then mkdir -p ${logdir}; fi

   logfile=${logdir}/${job_name}_${FIRSTDAY}_${LASTDAY}.out
   if [ -e ${logfile} ]; then /bin/rm -f ${logfile}; fi

   file_hd=aqm
   file_type=gif
   cat > ${batch_script} << EOF
#!/bin/sh
#BSUB -o ${logfile}
#BSUB -e ${logfile}
#BSUB -n 1
#BSUB -J j${job_name}
#BSUB -q "dev_transfer"
#BSUB -P HYS-T2O
#BSUB -W ${task_cpu}
#BSUB -R affinity[core(1)]
#BSUB -M 100
####BSUB -R span[ptile=1]
##
##  Provide fix date daily Hysplit data processing
##
   module load prod_util/1.1.0

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
         data_dir=/gpfs/dell2/stmp/${USER}/daily_plot_pm25_max/aqm_${exp}_pm_max.${NOW}${i}
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
      script_dir=/naqfc/save/${USER}/WEB/base
      cd ${script_dir}

      script_name=wcoss.run.cmaq_pm.sh
      bash ${script_name} ${LASTDAY}

      script_name=wcoss.run.cmaq2_pm.sh
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
      bsub < ${batch_script}
   else
      echo "test bsub < ${batch_script} completed"
   fi
fi
exit
