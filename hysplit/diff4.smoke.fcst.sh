#!/bin/bash 
module use /apps/test/lmodules/core/
module load GrADS/2.2.2
module load prod_util

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

MSG="USAGE $0 exp1 exp2 [exp2-exp1] YYYYMMDD_BEG YYYYMMDD_END"

if [ $# -lt 2 ]; then
   echo $MSG
   exit
else
   opt1=$1
   opt2=$2
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

working_dir=/lfs/h2/emc/stmp/${USER}/job_submit
mkdir -p ${working_dir}
#
aqm=hysplit
capaqm=`echo ${aqm} | tr '[:lower:]' '[:upper:]'`
smlaqm=`echo ${aqm} | tr '[:upper:]' '[:lower:]'`
satellite=nesdis

##
## setting for exp1
##
opt=${opt1}
capopt=`echo ${opt} | tr '[:lower:]' '[:upper:]'`
smlopt=`echo ${opt} | tr '[:upper:]' '[:lower:]'`
capexp1=${capopt}
exp1=${smlopt}
comdir=${COMROOT}/${smlaqm}/${exp1}
comdir2=${comdir}
mydir=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp1}
mydir2=/lfs/h2/emc/ptmp/${USER}/com/${smlaqm}/${exp1}

## special setting
if [ ${exp1} == 'prod' ]; then
   mydir=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp1}
   mydir2=${mydir}
elif [ ${exp1} == 'ncopara' ]; then
   comdir=${COMROOT}/${smlaqm}/para
   comdir2=${comdir}
   mydir=${comdir}
   mydir2=${mydir}
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
opt=${opt2}
capopt=`echo ${opt} | tr '[:lower:]' '[:upper:]'`
smlopt=`echo ${opt} | tr '[:upper:]' '[:lower:]'`
capexp2=${capopt}
exp2=${smlopt}
comdir=${COMROOT}/${smlaqm}/${exp2}
comdir2=${comdir}
mydir=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp2}
mydir2=/lfs/h2/emc/ptmp/${USER}/com/${smlaqm}/${exp2}

## special setting
if [ ${exp2} == 'prod' ]; then
   mydir=/lfs/h2/emc/physics/noscrub/${USER}/com/${smlaqm}/${exp2}
   mydir2=${mydir}
elif [ ${exp2} == 'ncopara' ]; then
   comdir=${COMROOT}/${smlaqm}/para
   comdir2=${comdir}
   mydir=${comdir}
   mydir2=${mydir}
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
declare -a reg=( dset conus east west ne10 nw10 se10 swse   ak   hi can user )
declare -a lon0=( -175 -130 -100 -128  -81 -128  -91 -128 -170 -161 -141 -130 )
declare -a lon1=(   55  -60  -65  -90  -64 -110  -74 -100 -130 -154  -60  -90 )
declare -a lat0=(    0   20   24   25   37   38   24   28   50   18   40   45 )
declare -a lat1=(   80   55   47   55   48   55   40   40   80   23   70   65 )
nreg=${#reg[@]}
let max_ireg=${nreg}-3
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

declare -a aerosol=( dust smoke all )
iaero=1

declare -a mchr=( JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC )
declare -a cyc_opt=( 6 12 )
icyc=0
cyc=`printf %2.2d ${cyc_opt[${icyc}]}`
i=`expr ${cyc} + 1`
cycp1=`printf %2.2d ${i}`
cycle=t${cyc}z

declare -a area=( cs ak hi )
declare -a otyp=( pbl sfc )

NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do

   cdate=${NOW}"00"
   TOMORROW=$(${NDATE} +24 ${cdate}| cut -c1-8)
   THIRDDAY=$(${NDATE} +48 ${cdate}| cut -c1-8)

   if [ -d  ${comdir1_s1}/smokecs.${NOW} ]; then
      idir1=${comdir1_s1}
   elif [ -d ${comdir2_s1}/smokecs.${NOW} ]; then
      idir1=${comdir2_s1}
   elif [ -d  ${mydir1_s1}/smokecs.${NOW} ]; then
      idir1=${mydir1_s1}
   elif [ -d ${mydir2_s1}/smokecs.${NOW} ]; then
      idir1=${mydir2_s1}
   else
      echo " ${NOW} :: NO ${comdir1_s1}/smokecs.${NOW} & ${comdir2_s1}/smokecs.${NOW}, skip to nexy day"
      echo " ${NOW} :: NO ${mydir1_s1}/smokecs.${NOW} & ${mydir2_s1}/smokecs.${NOW}, skip to nexy day"
   fi

   if [ -d  ${comdir1_s2}/smokecs.${NOW} ]; then
      idir2=${comdir1_s2}
   elif [ -d ${comdir2_s2}/smokecs.${NOW} ]; then
      idir2=${comdir2_s2}
   elif [ -d  ${mydir1_s2}/smokecs.${NOW} ]; then
      idir2=${mydir1_s2}
   elif [ -d ${mydir2_s2}/smokecs.${NOW} ]; then
      idir2=${mydir2_s2}
   else
      echo " ${NOW} :: NO ${comdir1_s2}/smokecs.${NOW} & ${comdir2_s2}/smokecs.${NOW}, skip to nexy day"
      echo " ${NOW} :: NO ${mydir1_s2}/smokecs.${NOW} & ${mydir2_s2}/smokecs.${NOW}, skip to nexy day"
   fi

   YY=`echo ${NOW} | cut -c1-4`
   MX=`echo ${NOW} | cut -c5-5`
   if [ ${MX} == '0' ]; then
      MM=`echo ${NOW} | cut -c6-6`
   else
      MM=`echo ${NOW} | cut -c5-6`
   fi
   DD=`echo ${NOW} | cut -c7-8`

   data_dir=/lfs/h2/emc/stmp/${USER}/${aerosol[${iaero}]}_${exp}/${smlaqm}.${NOW}
   if [ -d ${data_dir} ]; then
      /bin/rm -f ${data_dir}/*
   else
      mkdir -p ${data_dir}
   fi
   cd ${data_dir}

   
   for layer in "${otyp[@]}"; do
      for loc in "${area[@]}"; do
         copyfile=smoke${loc}.${cycle}.${layer}.1hr.grib2
         if [ -s ${idir1}/smoke${loc}.${NOW}/${copyfile} ]; then
            /bin/cp -f ${idir1}/smoke${loc}.${NOW}/${copyfile} s1_${copyfile}
         else
           echo "can not find ${idir1}/smoke${loc}.${NOW}/${copyfile}"
         fi
         if [ -s ${idir2}/smoke${loc}.${NOW}/${copyfile} ]; then
            /bin/cp -f ${idir2}/smoke${loc}.${NOW}/${copyfile} s2_${copyfile}
         else
           echo "can not find ${idir2}/smoke${loc}.${NOW}/${copyfile}"
         fi
      done

      case ${layer} in
         pbl) plotvar=LIPMF5000_0m
              hgt=5000 ;;
         sfc) plotvar=LIPMF100_0m
              hgt=100 ;;
      esac
   s1_grib2_cs=s1_smokecs.${cycle}.${layer}.1hr.grib2
   s1_grib2_ak=s1_smokeak.${cycle}.${layer}.1hr.grib2
   s1_grib2_hi=s1_smokehi.${cycle}.${layer}.1hr.grib2

   s2_grib2_cs=s2_smokecs.${cycle}.${layer}.1hr.grib2
   s2_grib2_ak=s2_smokeak.${cycle}.${layer}.1hr.grib2
   s2_grib2_hi=s2_smokehi.${cycle}.${layer}.1hr.grib2
##
   flag_plot_cs=yes
   if [ -e ${data_dir}/${s1_grib2_cs} ] && [ -e ${data_dir}/${s2_grib2_cs} ]; then
cat > ${data_dir}/s1_smokecs.ctl <<EOF
dset ${data_dir}/${s1_grib2_cs}
index ${data_dir}/${s1_grib2_cs}.idx
undef 9.999E+20
title ${data_dir}/${s1_grib2_cs}
* produced by g2ctl v0.1.0
* command line options: smokecs.${cycle}.${layer}.1hr.grib2
* griddef=1:0:(801 x 534):grid_template=0:winds(N/S): lat-lon grid:(801 x 534) units 1e-06 input WE:SN output WE:SN res 48 lat 0.000000 to 80.000000 by 0.150000 lon 185.000000 to 305.000000 by 0.150000 #points=427734:winds(N/S)

dtype grib2
ydef 534 linear 0.000000 0.15
xdef 801 linear -175.000000 0.150000
tdef 48 linear ${cycp1}Z${DD}${mchr[$MM-1]}${YY} 1hr
zdef 1 linear 1 1
vars 1
${plotvar}  0,103,${hgt},0   0,13,195,0 ** ${hgt}-0 m above ground Integrated column particulate matter (fine) [log10(10-6gm-3)]
ENDVARS
EOF
cat > ${data_dir}/s2_smokecs.ctl <<EOF
dset ${data_dir}/${s2_grib2_cs}
index ${data_dir}/${s2_grib2_cs}.idx
undef 9.999E+20
title ${data_dir}/${s2_grib2_cs}
* produced by g2ctl v0.1.0
* command line options: smokecs.${cycle}.${layer}.1hr.grib2
* griddef=1:0:(801 x 534):grid_template=0:winds(N/S): lat-lon grid:(801 x 534) units 1e-06 input WE:SN output WE:SN res 48 lat 0.000000 to 80.000000 by 0.150000 lon 185.000000 to 305.000000 by 0.150000 #points=427734:winds(N/S)

dtype grib2
ydef 534 linear 0.000000 0.15
xdef 801 linear -175.000000 0.150000
tdef 48 linear ${cycp1}Z${DD}${mchr[$MM-1]}${YY} 1hr
zdef 1 linear 1 1
vars 1
${plotvar}  0,103,${hgt},0   0,13,195,0 ** ${hgt}-0 m above ground Integrated column particulate matter (fine) [log10(10-6gm-3)]
ENDVARS
EOF
         gribmap -i ${data_dir}/s1_smokecs.ctl
         gribmap -i ${data_dir}/s2_smokecs.ctl
   else
      flag_plot_cs=no
   fi

   ## For AK; if HYSPLIT_AK has NO data use HYSPLIT_FULL_DOMAIN
   flag_plot_ak=yes
   if [ -e ${data_dir}/${s1_grib2_ak} ] && [ -e ${data_dir}/${s2_grib2_ak} ]; then
cat > ${data_dir}/s1_smokeak.ctl <<EOF
dset ${data_dir}/${s1_grib2_ak}
index ${data_dir}/${s1_grib2_ak}.idx
undef 9.999E+20
title ${data_dir}/${s1_grib2_ak}
* produced by g2ctl v0.1.0
* command line options: smokeak.${cycle}.${layer}.1hr.grib2
* griddef=1:0:(401 x 301):grid_template=0:winds(N/S): lat-lon grid:(401 x 301) units 1e-06 input WE:SN output WE:SN res 48 lat 50.000000 to 80.000000 by 0.100000 lon 190.000000 to 230.000000 by 0.100000 #points=120701:winds(N/S)

dtype grib2
ydef 301 linear 50.000000 0.1
xdef 401 linear -170.000000 0.100000
tdef 48 linear ${cycp1}Z${DD}${mchr[$MM-1]}${YY} 1hr
zdef 1 linear 1 1
vars 1
${plotvar}  0,103,${hgt},0   0,13,195,0 ** ${hgt}-0 m above ground Integrated column particulate matter (fine) [log10(10-6gm-3)]
ENDVARS
EOF
cat > ${data_dir}/s2_smokeak.ctl <<EOF
dset ${data_dir}/${s2_grib2_ak}
index ${data_dir}/${s2_grib2_ak}.idx
undef 9.999E+20
title ${data_dir}/${s2_grib2_ak}
* produced by g2ctl v0.1.0
* command line options: smokeak.${cycle}.${layer}.1hr.grib2
* griddef=1:0:(401 x 301):grid_template=0:winds(N/S): lat-lon grid:(401 x 301) units 1e-06 input WE:SN output WE:SN res 48 lat 50.000000 to 80.000000 by 0.100000 lon 190.000000 to 230.000000 by 0.100000 #points=120701:winds(N/S)

dtype grib2
ydef 301 linear 50.000000 0.1
xdef 401 linear -170.000000 0.100000
tdef 48 linear ${cycp1}Z${DD}${mchr[$MM-1]}${YY} 1hr
zdef 1 linear 1 1
vars 1
${plotvar}  0,103,${hgt},0   0,13,195,0 ** ${hgt}-0 m above ground Integrated column particulate matter (fine) [log10(10-6gm-3)]
ENDVARS
EOF
         gribmap -i ${data_dir}/s1_smokeak.ctl
         gribmap -i ${data_dir}/s2_smokeak.ctl
   elif [ -s ${data_dir}/${s1_grib2_cs} ] && [ -s ${data_dir}/${s2_grib2_cs} ]; then
echo "replace ak"
      cp -p ${data_dir}/s1_smokecs.ctl ${data_dir}/s1_smokeak.ctl
      cp -p ${data_dir}/s2_smokecs.ctl ${data_dir}/s2_smokeak.ctl
      gribmap -i ${data_dir}/s1_smokeak.ctl
      gribmap -i ${data_dir}/s2_smokeak.ctl
   else
      flag_plot_ak=no
   fi

   ## For HI; if HYSPLIT_HI has NO data use HYSPLIT_FULL_DOMAIN
   flag_plot_hi=yes
   if [ -e ${data_dir}/${s1_grib2_hi} ] && [ -e ${data_dir}/${s2_grib2_hi} ]; then
cat > ${data_dir}/s1_smokehi.ctl <<EOF
dset ${data_dir}/${s1_grib2_hi}
index ${data_dir}/${s1_grib2_hi}.idx
undef 9.999E+20
title ${data_dir}/${s1_grib2_hi}
* produced by g2ctl v0.1.0
* command line options: smokehi.${cycle}.${layer}.1hr.grib2
* griddef=1:0:(401 x 201):grid_template=0:winds(N/S): lat-lon grid:(401 x 201) units 1e-06 input WE:SN output WE:SN res 48 lat 15.000000 to 25.000000 by 0.050000 lon 194.000000 to 214.000000 by 0.050000 #points=80601:winds(N/S)

dtype grib2
ydef 201 linear 15.000000 0.05
xdef 401 linear -166.000000 0.050000
tdef 48 linear ${cycp1}Z${DD}${mchr[$MM-1]}${YY} 1hr
zdef 1 linear 1 1
vars 1
${plotvar}  0,103,${hgt},0   0,13,195,0 ** ${hgt}-0 m above ground Integrated column particulate matter (fine) [log10(10-6gm-3)]
ENDVARS
EOF
cat > ${data_dir}/s2_smokehi.ctl <<EOF
dset ${data_dir}/${s2_grib2_hi}
index ${data_dir}/${s2_grib2_hi}.idx
undef 9.999E+20
title ${data_dir}/${s2_grib2_hi}
* produced by g2ctl v0.1.0
* command line options: smokehi.${cycle}.${layer}.1hr.grib2
* griddef=1:0:(401 x 201):grid_template=0:winds(N/S): lat-lon grid:(401 x 201) units 1e-06 input WE:SN output WE:SN res 48 lat 15.000000 to 25.000000 by 0.050000 lon 194.000000 to 214.000000 by 0.050000 #points=80601:winds(N/S)

dtype grib2
ydef 201 linear 15.000000 0.05
xdef 401 linear -166.000000 0.050000
tdef 48 linear ${cycp1}Z${DD}${mchr[$MM-1]}${YY} 1hr
zdef 1 linear 1 1
vars 1
${plotvar}  0,103,${hgt},0   0,13,195,0 ** ${hgt}-0 m above ground Integrated column particulate matter (fine) [log10(10-6gm-3)]
ENDVARS
EOF
         gribmap -i ${data_dir}/s1_smokehi.ctl
         gribmap -i ${data_dir}/s2_smokehi.ctl
   elif [ -s ${data_dir}/${s1_grib2_cs} ] && [ -s ${data_dir}/${s2_grib2_cs} ]; then
echo "replace hi"
      cp -p ${data_dir}/s1_smokecs.ctl ${data_dir}/s1_smokehi.ctl
      cp -p ${data_dir}/s2_smokecs.ctl ${data_dir}/s2_smokehi.ctl
      gribmap -i ${data_dir}/s1_smokehi.ctl
      gribmap -i ${data_dir}/s2_smokehi.ctl
   else
      flag_plot_hi=no
   fi

   t0=1
   t1=48
   let numi=t0
   while [ ${numi} -le ${t1} ]; do
      fcsti=`printf %3.3d ${numi}`
      i=`printf %2.2d ${numi}`

      let j=${numi}+${cyc}
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
      

## 'set clevs 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
## 'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
## 'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
## 'set clevs 1. 3. 15. 35. 50. 65. 85. 100. 150.'
## 'set clevs 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
## 'set ccols 79 78 76 17 18 19 20 3 10 7'
## 'set ccols 79 78 76 17 18 19 20 3 10 7 12 8 2 98'

      if [ "${flag_plot_cs}" == "yes" ]; then
cat > ${data_dir}/${i}_cs.plot << EOF
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
'set rgb 48 150   0   0'
'set rgb 49 200   0   0'
'set rgb 52 255  80  80'
'set rgb 53 255 120 120'
'set rgb 54 255 150 150'
'c'
'open ${data_dir}/s1_smokecs.ctl'
'open ${data_dir}/s2_smokecs.ctl'
'set t ${i}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${idset}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${iconus}]} ${lat1[${iconus}]}'
'set lon ${lon0[${iconus}]} ${lon1[${iconus}]}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${iconus}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ieast}]} ${lat1[${ieast}]}'
'set lon ${lon0[${ieast}]} ${lon1[${ieast}]}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${ieast}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${iwest}]} ${lat1[${iwest}]}'
'set lon ${lon0[${iwest}]} ${lon1[${iwest}]}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${iwest}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ine10}]} ${lat1[${ine10}]}'
'set lon ${lon0[${ine10}]} ${lon1[${ine10}]}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${ine10}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${inw10}]} ${lat1[${inw10}]}'
'set lon ${lon0[${inw10}]} ${lon1[${inw10}]}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${inw10}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ise10}]} ${lat1[${ise10}]}'
'set lon ${lon0[${ise10}]} ${lon1[${ise10}]}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${ise10}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${iswse}]} ${lat1[${iswse}]}'
'set lon ${lon0[${iswse}]} ${lon1[${iswse}]}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${iswse}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ican}]} ${lat1[${ican}]}'
'set lon ${lon0[${ican}]} ${lon1[${ican}]}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${ican}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'quit'
EOF
         grads -blc "run ${data_dir}/${i}_cs.plot"

      fi

      if [ "${flag_plot_ak}" == "yes" ]; then

## capaqm=HYSPLIT
cat > ${data_dir}/${i}_ak.plot << EOF
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
'set rgb 48 150   0   0'
'set rgb 49 200   0   0'
'set rgb 52 255  80  80'
'set rgb 53 255 120 120'
'set rgb 54 255 150 150'
'c'
'open ${data_dir}/s1_smokeak.ctl'
'open ${data_dir}/s2_smokeak.ctl'
'set t ${i}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${idset}]}_ak_${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${iak}]} ${lat1[${iak}]}'
'set lon ${lon0[${iak}]} ${lon1[${iak}]}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${iak}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'quit'
EOF
         grads -blc "run ${data_dir}/${i}_ak.plot"
      fi

      if [ "${flag_plot_hi}" == "yes" ]; then

## capaqm=HYSPLIT
cat > ${data_dir}/${i}_hi.plot << EOF
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
'set rgb 48 150   0   0'
'set rgb 49 200   0   0'
'set rgb 52 255  80  80'
'set rgb 53 255 120 120'
'set rgb 54 255 150 150'
'c'
'open ${data_dir}/s1_smokehi.ctl'
'open ${data_dir}/s2_smokehi.ctl'
'set t ${i}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${idset}]}_hi_${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ihi}]} ${lat1[${ihi}]}'
'set lon ${lon0[${ihi}]} ${lon1[${ihi}]}'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pow(10,${plotvar}.2)-pow(10,${plotvar}.1)'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${ihi}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'quit'
EOF
         grads -blc "run ${data_dir}/${i}_hi.plot"
      fi
      ((numi++))
   done   ## fcst hour loop

   done   ## layer loop

   if [ "${flag_scp}" == "yes" ]; then
      scp ${data_dir}/${smlaqm}*${ftype} ${remote_user}@${remote_host}:${remote_dir}/${YY}/${NOW}/${cycle}
   fi

   echo "INPUT DATA DIR 1 = ${idir1}"
   echo "INPUT DATA DIR 2 = ${idir2}"
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
if [ "${flag_qsub}" == "yes" ]; then
   cd ${working_dir}
   task_cpu='05:00:00'
   job_name=prtsmk${smlaqm}_${exp}
   batch_script=prtsmk_${smlaqm}_${exp}.sh
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
   aqm=${smlaqm}
   aerosol=${aerosol[${iaero}]}
   ftype=${ftype}
   remote_user=${remote_user}
   remote_host=${remote_host}
   remote_dir=${remote_dir}
EOF
      ##
      ##  Creat part 2 script : exact wording of scripts
      ##
cat > ${batch_script}.add  << 'EOF'

source ~/.bashrc

   declare -a cyc=( 06 )

   NOW=${FIRSTDAY}
   while [ ${NOW} -le ${LASTDAY} ]; do
      YY=`echo ${NOW} | cut -c1-4`
      YM=`echo ${NOW} | cut -c1-6`

      data_dir=/lfs/h2/emc/stmp/${USER}/${aerosol}_${exp}/${aqm}.${NOW}

      for i in "${cyc[@]}"; do
         cycle=t${i}z
         scp ${data_dir}/${aqm}*${ftype} ${remote_user}@${remote_host}:${remote_dir}/${YY}/${NOW}/${cycle}
      done  ## cycle time
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
      qsub < ${batch_script}
   else
      echo "test qsub < ${batch_script} completed"
   fi
fi
exit
