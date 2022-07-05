#!/bin/sh
##
## SCRIPT FOR SINGLE DAY PROCESSING AND MAP GENERATION
##
## YYYYMMDD is the start day of NAQFC PM   simulation
## Cycle_hr is the model run starting hour
##
module load prod_util
module use /apps/test/lmodules/core/
module load GrADS

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

MSG="USAGE : $0 model_grid [default:aqm|hysplit] YYYYMMDD_BEG YYYYMMDD_END"

obssat=viirs
mdlname=aqm
FIRSTDAY=${TODAY}
LASTDAY=${TODAY}

if [ $# -lt 1 ]; then
   echo $MSG
   exit
else
   mdlname=$1
fi
if [ $# -lt 2 ]; then
   FIRSTDAY=${TODAY}
   LASTDAY=${TODAY}
elif [ $# -lt 3 ]; then
   FIRSTDAY=$2
   LASTDAY=$2
else
   FIRSTDAY=$2
   LASTDAY=$3
fi
hl=`hostname | cut -c1`

capobssat=`echo ${obssat} | tr '[:lower:]' '[:upper:]'`
set -x
## echo " ${obssat} ${sel_cyc} ${FIRSTDAY} ${LASTDAY}"

remote_dir=/home/people/emc/www/htdocs/mmb/hchuang/web/fig
remote_host=emcrzdm.ncep.noaa.gov
remote_user=hchuang

grid_id2=148
grid_id=227

flag_update=no
if [ "${LASTDAY}" == "${TODAY}" ]; then flag_update=yes; fi

gs_dir=/gpfs/dell2/emc/modeling/save/${USER}/plot/viirs

declare -a reg=( dset conus east west  ne10  nw10  se10  swse  ak   hi   nyc   md    mdatl )
declare -a lon0=( -175 -133 -100 -130  -81   -125  -91   -125  -170 -162.5 -74.7 -79.3 -82   )
declare -a lon1=(   55  -60  -60  -90  -66   -105  -74   -100  -130 -152.5 -71.5 -75.3 -73   )
declare -a lat0=(    0   21   24   21   37     37   24     21    50   17.5  40.3  37.8 36    )
declare -a lat1=(   80   52   50   50   48     50   40     45    80   23.5  42.2  40.5 42.5  )
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
inyc=10
imd=11
imdatl=12

declare -a mchr=( JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC )
## declare -a qc_flag=( high )
## declare -a cyc_opt=( 20 )
declare -a cyc_opt=( 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 )
declare -a qc_flag=( high medium )

declare -a type=( ${mdlname} )
ntyp=${#type[@]}

ftpdir=/gpfs/dell1/stmp/${USER}/daily_plot_${obssat}_${mdlname}_aod
mkdir -p ${ftpdir}
   
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do

   comdir=/gpfs/dell2/emc/modeling/noscrub/${USER}/VIIRS_AOD/REGRID/${mdlname}.${NOW}
   if [ ! -d ${comdir} ]; then
      echo "////////////////////////////////////////"
      echo "${comdir} does not existed, program stop"
      echo "////////////////////////////////////////"
      exit
   else
      echo "////////////////////////////////////////"
      echo "/ Fetching PM data Data from ${comdir} /"
      echo "////////////////////////////////////////"
   fi
   outdir=${ftpdir}/${obssat}_aod_${mdlname}_${NOW}
   echo "Figure output in ${outdir}"
   if [ -d ${outdir} ]; then
      /bin/rm -f ${outdir}/*
   else
      mkdir -p ${outdir}
   fi
   
   tmpdir=/gpfs/dell1/stmp/${USER}/com_aod_${obssat}_${mdlname}.${NOW}
   if [ -d ${tmpdir} ]; then
      /bin/rm -f ${tmpdir}/*
   else
      mkdir -p ${tmpdir}
   fi
   cd ${tmpdir}

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

      if [ "${flag_test}" == "yes" ]; then
         continue
      fi
      for jfile in "${type[@]}"
      do
         case ${jfile} in
            aqm) aod_file=VIIRS-L3-AOD_AQM_${jfile}_${NOW}_${cych}.nc
               if [ ! -s ${comdir}/${aod_file} ]; then continue; fi
               if [ -e ${jfile}.ctl ]; then /bin/rm -f ${jfile}.ctl; fi
               cat >  ${jfile}.ctl <<EOF
dset ${comdir}/${aod_file}
undef  -9999.
dtype netcdf
PDEF 442 265 lccr 21.8210 -120.628 1 1 33 45 -97 12000. 12000.
xdef 614 linear -132.000 0.12
ydef 262 linear 22.0000 0.12
zdef    1 levels  1.000    
tdef  2 linear ${F1}:00Z${D1}${mchr[$M1-1]}${Y1}  01hr
vars  8
lat=>lat0   0 y,x aerosol optical depth (unitless)
lon=>lon0   0 y,x aerosol optical depth (unitless)
AOD_H_Quality=>highaod   0 y,x high quality aerosol optical depth (unitless)
AOD_HM_Quality=>medaod   0 y,x medium quality aerosol optical depth (unitless)
Dust_AOD_H_Quality=>highdustaod   0 y,x high quality aerosol optical depth (unitless)
Dust_AOD_HM_Quality=>meddustaod   0 y,x medium quality aerosol optical depth (unitless)
Smoke_AOD_H_Quality=>highsmokeaod   0 y,x high quality aerosol optical depth (unitless)
Smoke_AOD_HM_Quality=>medsmokeaod   0 y,x medium quality aerosol optical depth (unitless)
ENDVARS
EOF
                  ;;
            ak) aod_file=VIIRS-L3-AOD_AQM_${jfile}_${NOW}_${cych}.nc
               if [ ! -s ${comdir}/${aod_file} ]; then continue; fi
               if [ -e ${jfile}.ctl ]; then /bin/rm -f ${jfile}.ctl; fi
               cat >  ${jfile}.ctl <<EOF
dset ${comdir}/${aod_file}
undef  -9999.
dtype netcdf
pdef 199 163 lccr 53.0200 -166.477 1 1 57 63 -148.6 12000. 12000.
xdef 343 linear -179.631730 0.181353852478047
ydef 173 linear 53.020174 0.109090909090909
zdef    1 levels  1.000    
tdef  2 linear ${F1}:00Z${D1}${mchr[$M1-1]}${Y1}  01hr
vars  8
lat=>lat0   0 y,x aerosol optical depth (unitless)
lon=>lon0   0 y,x aerosol optical depth (unitless)
AOD_H_Quality=>highaod   0 y,x high quality aerosol optical depth (unitless)
AOD_HM_Quality=>medaod   0 y,x medium quality aerosol optical depth (unitless)
Dust_AOD_H_Quality=>highdustaod   0 y,x high quality aerosol optical depth (unitless)
Dust_AOD_HM_Quality=>meddustaod   0 y,x medium quality aerosol optical depth (unitless)
Smoke_AOD_H_Quality=>highsmokeaod   0 y,x high quality aerosol optical depth (unitless)
Smoke_AOD_HM_Quality=>medsmokeaod   0 y,x medium quality aerosol optical depth (unitless)
ENDVARS
EOF
                  ;;
            hi) aod_file=VIIRS-L3-AOD_AQM_${jfile}_${NOW}_${cych}.nc
               if [ ! -s ${comdir}/${aod_file} ]; then continue; fi
               if [ -e ${jfile}.ctl ]; then /bin/rm -f ${jfile}.ctl; fi
               cat >  ${jfile}.ctl <<EOF
dset ${comdir}/${aod_file}
undef  -9999.
dtype netcdf
pdef 80 52 lccr 17.7210 -161.973 1 1 19 21 -157.5 12000. 12000.
xdef 81 linear -162.132666 0.114525128341162
ydef 51 linear 17.721018 0.109090909090909
zdef    1 levels  1.000    
tdef  2 linear ${F1}:00Z${D1}${mchr[$M1-1]}${Y1}  01hr
vars  8
lat=>lat0   0 y,x aerosol optical depth (unitless)
lon=>lon0   0 y,x aerosol optical depth (unitless)
AOD_H_Quality=>highaod   0 y,x high quality aerosol optical depth (unitless)
AOD_HM_Quality=>medaod   0 y,x medium quality aerosol optical depth (unitless)
Dust_AOD_H_Quality=>highdustaod   0 y,x high quality aerosol optical depth (unitless)
Dust_AOD_HM_Quality=>meddustaod   0 y,x medium quality aerosol optical depth (unitless)
Smoke_AOD_H_Quality=>highsmokeaod   0 y,x high quality aerosol optical depth (unitless)
Smoke_AOD_HM_Quality=>medsmokeaod   0 y,x medium quality aerosol optical depth (unitless)
ENDVARS
EOF
                  ;;
            hysplit) aod_file=VIIRS-L3-AOD_AQM_${jfile}_${NOW}_${cych}.nc
               if [ ! -s ${comdir}/${aod_file} ]; then continue; fi
               if [ -e ${jfile}.ctl ]; then /bin/rm -f ${jfile}.ctl; fi
               cat >  ${jfile}.ctl <<EOF
dset ${comdir}/${aod_file}
undef  -9999.
dtype netcdf
xdef 801 linear -175.000 0.15000
ydef 534 linear 0.0000 0.15000
zdef    1 levels  1.000    
tdef  2 linear ${F1}:00Z${D1}${mchr[$M1-1]}${Y1}  01hr
vars  8
lat=>lat0   0 y,x aerosol optical depth (unitless)
lon=>lon0   0 y,x aerosol optical depth (unitless)
AOD_H_Quality=>highaod   0 y,x high quality aerosol optical depth (unitless)
AOD_HM_Quality=>medaod   0 y,x medium quality aerosol optical depth (unitless)
Dust_AOD_H_Quality=>highdustaod   0 y,x high quality aerosol optical depth (unitless)
Dust_AOD_HM_Quality=>meddustaod   0 y,x medium quality aerosol optical depth (unitless)
Smoke_AOD_H_Quality=>highsmokeaod   0 y,x high quality aerosol optical depth (unitless)
Smoke_AOD_HM_Quality=>medsmokeaod   0 y,x medium quality aerosol optical depth (unitless)
ENDVARS
EOF
                  ;;
            *) echo "case not found; ${regid}"
               exit ;;
         esac
         if [ ! -s ${comdir}/${aod_file} ]; then
            echo "can not find ${comdir}/${aod_file}"
            continue
         fi

         for qc in "${qc_flag[@]}"; do
            if [ "${jfile}" == "aqm" ]; then 
               gs_type=${jfile}
               if [ -e ${jfile}.${qc}.plots ]; then /bin/rm -f ${jfile}.${qc}.plots; fi
## 55 Medium brown 205 133 63
## 44 dark yellow  154 205 50
## 44 green Yellow 173 255 47
## 60 gold        255,215,0'
## 61 dark orange 255,140,0'
## 62 green        0   128 0
## 63 lime green   50,205,50
## 64 lawn green   142 252 0
## 65 Dark green   0   100 0
## 66 Yellow 255 255 0
## 67 Darker Yellow 230 230 0
## 68 crimson     220,20,60
## 69 dark red    139,0,0
## 70 violet      238,130,238
## 71 green-blue  0   204 204
                  cat >  ${jfile}.${qc}.plots <<EOF
'reinit'
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
*'set rgb 55 205 133 63'
*'set rgb 44 154 205 50'
'set rgb 60 255 215 0'
'set rgb 61 255 140 0'
'set rgb 62 0 128 0'
'set rgb 63 50 205 50'
'set rgb 64 142 252 0'
'set rgb 65 0   100 0'
*'set rgb 66 255 255 0'
'set rgb 67 230 230 0'
'set rgb 68 220 20  60'
'set rgb 69 139 0   0'
'set rgb 70 238 130 238'
'set rgb 71 0   204 204'
'set rgb 33  40  40  40'
'set rgb 44  80  80  80'
'set rgb 55 120 120 120'
'set rgb 66 160 160 160'
'set rgb 77 200 200 200'
'c'
'open ${jfile}.ctl'
'set lat ${lat0[${iconus}]} ${lat1[${iconus}]}'
'set lon ${lon0[${iconus}]} ${lon1[${iconus}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} conus'
'set lat ${lat0[${ieast}]} ${lat1[${ieast}]}'
'set lon ${lon0[${ieast}]} ${lon1[${ieast}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} east'
'set lat ${lat0[${iwest}]} ${lat1[${iwest}]}'
'set lon ${lon0[${iwest}]} ${lon1[${iwest}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} west'
'set lat ${lat0[${ine10}]} ${lat1[${ine10}]}'
'set lon ${lon0[${ine10}]} ${lon1[${ine10}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} ne'
'set lat ${lat0[${inw10}]} ${lat1[${inw10}]}'
'set lon ${lon0[${inw10}]} ${lon1[${inw10}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} nw'
'set lat ${lat0[${ise10}]} ${lat1[${ise10}]}'
'set lon ${lon0[${ise10}]} ${lon1[${ise10}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} se'
'set lat ${lat0[${iswse}]} ${lat1[${iswse}]}'
'set lon ${lon0[${iswse}]} ${lon1[${iswse}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} sw'
'set lat ${lat0[${inyc}]} ${lat1[${inyc}]}'
'set lon ${lon0[${inyc}]} ${lon1[${inyc}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} nyc'
'set lat ${lat0[${imd}]} ${lat1[${imd}]}'
'set lon ${lon0[${imd}]} ${lon1[${imd}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} md'
'set lat ${lat0[${imdatl}]} ${lat1[${imdatl}]}'
'set lon ${lon0[${imdatl}]} ${lon1[${imdatl}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} mdatl'
'quit'
EOF
            elif [ "${jfile}" == "ak" ]; then 
               gs_type=aqm
               if [ -e ${jfile}.${qc}.plots ]; then /bin/rm -f ${jfile}.${qc}.plots; fi
                  cat >  ${jfile}.${qc}.plots <<EOF
'reinit'
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
*'set rgb 55 205 133 63'
*'set rgb 44 154 205 50'
'set rgb 60 255 215 0'
'set rgb 61 255 140 0'
'set rgb 62 0 128 0'
'set rgb 63 50 205 50'
'set rgb 64 142 252 0'
'set rgb 65 0   100 0'
*'set rgb 66 255 255 0'
'set rgb 67 230 230 0'
'set rgb 68 220 20  60'
'set rgb 69 139 0   0'
'set rgb 70 238 130 238'
'set rgb 71 0   204 204'
'set rgb 33  40  40  40'
'set rgb 44  80  80  80'
'set rgb 55 120 120 120'
'set rgb 66 160 160 160'
'set rgb 77 200 200 200'
'c'
'open ${jfile}.ctl'
'set lat ${lat0[${iak}]} ${lat1[${iak}]}'
'set lon ${lon0[${iak}]} ${lon1[${iak}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} ak'
'quit'
EOF
            elif [ "${jfile}" == "hi" ]; then 
               gs_type=aqm
               if [ -e ${jfile}.${qc}.plots ]; then /bin/rm -f ${jfile}.${qc}.plots; fi
                  cat >  ${jfile}.${qc}.plots <<EOF
'reinit'
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
'set rgb 55 205 133 63'
'set rgb 44 154 205 50'
'set rgb 60 255 215 0'
'set rgb 61 255 140 0'
'set rgb 62 0 128 0'
'set rgb 63 50 205 50'
'set rgb 64 142 252 0'
'set rgb 65 0   100 0'
'set rgb 66 255 255 0'
'set rgb 67 230 230 0'
'set rgb 68 220 20  60'
'set rgb 69 139 0   0'
'set rgb 70 238 130 238'
'set rgb 71 0   204 204'
'c'
'open ${jfile}.ctl'
'set lat ${lat0[${ihi}]} ${lat1[${ihi}]}'
'set lon ${lon0[${ihi}]} ${lon1[${ihi}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} hi'
'quit'
EOF
            elif [ ${jfile} = 'hysplit' ]; then 
               gs_type=${jfile}
               if [ -e ${jfile}.${qc}.plots ]; then /bin/rm -f ${jfile}.${qc}.plots; fi
## 55 Medium brown 205 133 63
## 44 dark yellow  154 205 50
## 44 green Yellow 173 255 47
## 60 gold        255,215,0'
## 61 dark orange 255,140,0'
## 62 green        0   128 0
## 63 lime green   50,205,50
## 64 lawn green   142 252 0
## 65 Dark green   0   100 0
## 66 Yellow 255 255 0
## 67 Darker Yellow 230 230 0
## 68 crimson     220,20,60
## 69 dark red    139,0,0
## 70 violet      238,130,238
## 71 green-blue  0   204 204
               cat >  ${jfile}.${qc}.plots <<EOF
'reinit'
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
'set rgb 55 205 133 63'
'set rgb 44 154 205 50'
'set rgb 60 255 215 0'
'set rgb 61 255 140 0'
'set rgb 62 0 128 0'
'set rgb 63 50 205 50'
'set rgb 64 142 252 0'
'set rgb 65 0   100 0'
'set rgb 66 255 255 0'
'set rgb 67 230 230 0'
'set rgb 68 220 20  60'
'set rgb 69 139 0   0'
'set rgb 70 238 130 238'
'set rgb 71 0   204 204'
'c'
'open ${jfile}.ctl'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} dset'
'set lat ${lat0[${iconus}]} ${lat1[${iconus}]}'
'set lon ${lon0[${iconus}]} ${lon1[${iconus}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} conus'
'set lat ${lat0[${ieast}]} ${lat1[${ieast}]}'
'set lon ${lon0[${ieast}]} ${lon1[${ieast}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} east'
'set lat ${lat0[${iwest}]} ${lat1[${iwest}]}'
'set lon ${lon0[${iwest}]} ${lon1[${iwest}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} west'
'set lat ${lat0[${ine10}]} ${lat1[${ine10}]}'
'set lon ${lon0[${ine10}]} ${lon1[${ine10}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} ne'
'set lat ${lat0[${inw10}]} ${lat1[${inw10}]}'
'set lon ${lon0[${inw10}]} ${lon1[${inw10}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} nw'
'set lat ${lat0[${ise10}]} ${lat1[${ise10}]}'
'set lon ${lon0[${ise10}]} ${lon1[${ise10}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} se'
'set lat ${lat0[${iswse}]} ${lat1[${iswse}]}'
'set lon ${lon0[${iswse}]} ${lon1[${iswse}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} sw'
'set lat ${lat0[${inyc}]} ${lat1[${inyc}]}'
'set lon ${lon0[${inyc}]} ${lon1[${inyc}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} nyc'
'set lat ${lat0[${imd}]} ${lat1[${imd}]}'
'set lon ${lon0[${imd}]} ${lon1[${imd}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} md'
'set lat ${lat0[${imdatl}]} ${lat1[${imdatl}]}'
'set lon ${lon0[${imdatl}]} ${lon1[${imdatl}]}'
'${gs_dir}/draw.aod.${gs_type}.gs ${gs_dir} ${outdir} ${obssat} ${capobssat} ${NOW} ${cych} ${qc} mdatl'
'quit'
EOF
            fi
            grads -blc "run ${jfile}.${qc}.plots"
         done    ## quality flag loop
      done    ## type loop
      if [ ${flag_scp} == 'yes' ]; then  # for RZDM maintainence
         ##
         ## TRANSFER PLOTS TO RZDM
         ##
         scp ${outdir}/${mdlname}*.png ${remote_user}@${remote_host}:${remote_dir}/${Y1}/${NOW}
      fi
   done  ## end for loop cych in "${cyc_opt[@]}"
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
echo "${outdir}"

if [ "${flag_bsub}" == "yes" ]; then
   working_dir=/gpfs/dell1/stmp/${USER}/job_submit
   mkdir -p ${working_dir}
   cd ${working_dir}

   task_cpu='05:00'
   job_name=${mdlname}_aod_${obssat}
   batch_script=trans_${mdlname}_${obssat}.sh
   if [ -e ${batch_script} ]; then /bin/rm -f ${batch_script}; fi

   logdir=/gpfs/dell2/ptmp/${USER}/batch_logs
   if [ ! -d ${logdir} ]; then mkdir -p ${logdir}; fi

   logfile=${logdir}/${job_name}_${FIRSTDAY}_${LASTDAY}.out
   if [ -e ${logfile} ]; then /bin/rm -f ${logfile}; fi

   file_hd=${mdlname}
   if [ "${mdlname}" == "ak" ] || [ "${mdlname}" == "hi" ]; then file_hd=aqm; fi
   file_type=png
   cat > ${batch_script} << EOF
#!/bin/sh
#BSUB -o ${logfile}
#BSUB -e ${logfile}
#BSUB -n 1
#BSUB -J j${job_name}
#BSUB -q "dev_transfer"
#BSUB -P CMAQ-T2O
#BSUB -W ${task_cpu}
#BSUB -R affinity[core(1)]
#BSUB -M 100
####BSUB -R span[ptile=1]
##
##  Provide fix date daily Hysplit data processing
##
   module load prod_uitl
   FIRSTDAY=${FIRSTDAY}
   LASTDAY=${LASTDAY}
   ftpdir=${ftpdir}
   obssat=${obssat}
   remote_user=${remote_user}
   remote_host=${remote_host}
   remote_dir=${remote_dir}
   file_hd=${file_hd}
   file_type=${file_type}
   flag_update=${flag_update}
   declare -a type=( ${type[@]} )
EOF
   ##
   ##  Creat part 2 script : exact wording of scripts
   ##
   cat > ${batch_script}.add  << 'EOF'

   NOW=${FIRSTDAY}
   while [ ${NOW} -le ${LASTDAY} ]; do
      YY=`echo ${NOW} | cut -c1-4`
      YM=`echo ${NOW} | cut -c1-6`

      for j in "${type[@]}"; do
         data_dir=${ftpdir}/${obssat}_aod_${j}_${NOW}${i}
         if [ -d ${data_dir} ]; then
            scp ${data_dir}/${file_hd}*${file_type} ${remote_user}@${remote_host}:${remote_dir}/${YY}/${NOW}
         else
            echo "Can not find ${data_dir}, skip to next cycle"
         fi
      done  ## type
      cdate=${NOW}"00"
      NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
   done
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

