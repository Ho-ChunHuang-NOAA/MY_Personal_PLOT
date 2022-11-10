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

MSG="USAGE $0 exp_id[prod|para|para#] YYYYMMDD_BEG YYYYMMDD_END"

if [ $# -lt 1 ]; then
  echo $MSG
  exit
elif [ $# -lt 2 ]; then
   opt=$1
   FIRSTDAY=${TODAY}
   LASTDAY=${TODAY}
elif [ $# -lt 3 ]; then
   opt=$1
   FIRSTDAY=$2
   LASTDAY=$2
else
   opt=$1
   FIRSTDAY=$2
   LASTDAY=$3
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
   mydir2=${mydir}
elif [ ${smlopt} == 'ncopara' ]; then
   comdir=${COMROOT}/${smlaqm}/para
   comdir2=${comdir}
   mydir=${comdir}
   mydir2=${mydir}
else
   comdir=${mydir}
   comdir2=${mydir2}
fi

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

## DEFINE TIME
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do

   cdate=${NOW}"00"
   TOMORROW=$(${NDATE} +24 ${cdate}| cut -c1-8)
   THIRDDAY=$(${NDATE} +48 ${cdate}| cut -c1-8)

   if [ -d  ${comdir}/smokecs.${NOW} ]; then
      idir=${comdir}
   elif [ -d ${comdir2}/smokecs.${NOW} ]; then
      idir=${comdir2}
   elif [ -d  ${mydir}/smokecs.${NOW} ]; then
      idir=${mydir}
   elif [ -d ${mydir2}/smokecs.${NOW} ]; then
      idir=${mydir2}
   else
      echo " ${NOW} :: NO ${comdir}/smokecs.${NOW} & ${comdir2}/smokecs.${NOW}, skip to nexy day"
      echo " ${NOW} :: NO ${mydir}/smokecs.${NOW} & ${mydir2}/smokecs.${NOW}, skip to nexy day"
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
         if [ -s ${idir}/smoke${loc}.${NOW}/${copyfile} ]; then
            /bin/cp -f ${idir}/smoke${loc}.${NOW}/${copyfile} .
         else
           echo "can not find ${idir}/smoke${loc}.${NOW}/${copyfile}"
         fi
      done

      case ${layer} in
         pbl) plotvar=LIPMF5000_0m
              hgt=5000 ;;
         sfc) plotvar=LIPMF100_0m
              hgt=100 ;;
      esac
   grib2_cs=smokecs.${cycle}.${layer}.1hr.grib2
   grib2_ak=smokeak.${cycle}.${layer}.1hr.grib2
   grib2_hi=smokehi.${cycle}.${layer}.1hr.grib2
##
   flag_plot_cs=yes
   if [ -e ${data_dir}/${grib2_cs} ]; then
cat > ${data_dir}/smokecs.ctl <<EOF
dset ${data_dir}/${grib2_cs}
index ${data_dir}/${grib2_cs}.idx
undef 9.999E+20
title ${data_dir}/${grib2_cs}
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
         gribmap -i ${data_dir}/smokecs.ctl
   else
      flag_plot_cs=no
   fi

   ## For AK; if HYSPLIT_AK has NO data use HYSPLIT_FULL_DOMAIN
   flag_plot_ak=yes
   if [ -e ${data_dir}/${grib2_ak} ]; then
cat > ${data_dir}/smokeak.ctl <<EOF
dset ${data_dir}/${grib2_ak}
index ${data_dir}/${grib2_ak}.idx
undef 9.999E+20
title ${data_dir}/${grib2_ak}
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
         gribmap -i ${data_dir}/smokeak.ctl
   elif [ ! -s ${data_dir}/${grib2_ak} ] && [ -s ${data_dir}/${grib2_cs} ]; then
echo "replace ak"
      cp -p ${data_dir}/smokecs.ctl ${data_dir}/smokeak.ctl
      gribmap -i ${data_dir}/smokeak.ctl
   else
      flag_plot_ak=no
   fi

   ## For HI; if HYSPLIT_HI has NO data use HYSPLIT_FULL_DOMAIN
   flag_plot_hi=yes
   if [ -e ${data_dir}/${grib2_hi} ]; then
cat > ${data_dir}/smokehi.ctl <<EOF
dset ${data_dir}/${grib2_hi}
index ${data_dir}/${grib2_hi}.idx
undef 9.999E+20
title ${data_dir}/${grib2_hi}
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
         gribmap -i ${data_dir}/smokehi.ctl
   elif [ ! -s ${data_dir}/${grib2_hi} ] && [ -s ${data_dir}/${grib2_cs} ]; then
echo "replace hi"
      cp -p ${data_dir}/smokecs.ctl ${data_dir}/smokehi.ctl
      gribmap -i ${data_dir}/smokehi.ctl
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
## 'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
## 'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
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
'set rgb 70 30 30 30'
'set rgb 71 60 60 60'
'set rgb 72 80 80 80'
'set rgb 73 100 100 100'
'set rgb 74 120 120 120'
'set rgb 75 150 150 150'
'set rgb 76 180 180 180'
'set rgb 77 200 200 200'
'set rgb 78 220 220 220'
'set rgb 88 250 250 250'
'set rgb 98 255 105 180'
'set rgb 79 240 240 240'
'set rgb 17  55  55 255'
'set rgb 18 110 110 255'
'set rgb 19 165 165 255'
'set rgb 20 220 220 255'
'set rgb 89 238 220 220'
'c'
'open ${data_dir}/smokecs.ctl'
'set t ${i}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${idset}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${iconus}]} ${lat1[${iconus}]}'
'set lon ${lon0[${iconus}]} ${lon1[${iconus}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${iconus}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ieast}]} ${lat1[${ieast}]}'
'set lon ${lon0[${ieast}]} ${lon1[${ieast}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${ieast}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${iwest}]} ${lat1[${iwest}]}'
'set lon ${lon0[${iwest}]} ${lon1[${iwest}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${iwest}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ine10}]} ${lat1[${ine10}]}'
'set lon ${lon0[${ine10}]} ${lon1[${ine10}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${ine10}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${inw10}]} ${lat1[${inw10}]}'
'set lon ${lon0[${inw10}]} ${lon1[${inw10}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${inw10}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ise10}]} ${lat1[${ise10}]}'
'set lon ${lon0[${ise10}]} ${lon1[${ise10}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${ise10}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${iswse}]} ${lat1[${iswse}]}'
'set lon ${lon0[${iswse}]} ${lon1[${iswse}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${iswse}]}${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ican}]} ${lat1[${ican}]}'
'set lon ${lon0[${ican}]} ${lon1[${ican}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
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
'set rgb 70 30 30 30'
'set rgb 71 60 60 60'
'set rgb 72 80 80 80'
'set rgb 73 100 100 100'
'set rgb 74 120 120 120'
'set rgb 75 150 150 150'
'set rgb 76 180 180 180'
'set rgb 77 200 200 200'
'set rgb 78 220 220 220'
'set rgb 88 250 250 250'
'set rgb 98 255 105 180'
'set rgb 79 240 240 240'
'set rgb 17  55  55 255'
'set rgb 18 110 110 255'
'set rgb 19 165 165 255'
'set rgb 20 220 220 255'
'set rgb 89 238 220 220'
'c'
'open ${data_dir}/smokeak.ctl'
'set t ${i}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${idset}]}_ak_${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${iak}]} ${lat1[${iak}]}'
'set lon ${lon0[${iak}]} ${lon1[${iak}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
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
'set rgb 70 30 30 30'
'set rgb 71 60 60 60'
'set rgb 72 80 80 80'
'set rgb 73 100 100 100'
'set rgb 74 120 120 120'
'set rgb 75 150 150 150'
'set rgb 76 180 180 180'
'set rgb 77 200 200 200'
'set rgb 78 220 220 220'
'set rgb 88 250 250 250'
'set rgb 98 255 105 180'
'set rgb 79 240 240 240'
'set rgb 17  55  55 255'
'set rgb 18 110 110 255'
'set rgb 19 165 165 255'
'set rgb 20 220 220 255'
'set rgb 89 238 220 220'
'c'
'open ${data_dir}/smokehi.ctl'
'set t ${i}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
'${gs_dir}/cbar.gs'
'draw title ${capaqm} ${capexp} ${cycle} ${layer} ${aerosol[${iaero}]} ${date}/${numj}00V${fcsti} conc ug/m3'
'printim ${data_dir}/${smlaqm}${reg[${idset}]}_hi_${aerosol[${iaero}]}${layer}_${i}${ftype} png x800 y600 white'
'c'
'set lat ${lat0[${ihi}]} ${lat1[${ihi}]}'
'set lon ${lon0[${ihi}]} ${lon1[${ihi}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd pow(10,${plotvar})'
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

   echo "INPUT DATA DIR = ${idir}"
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
# 
# 
#### 
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
   flag_update=${flag_update}
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
   if [ "${flag_update}" == "yes" ]; then
      script_dir=/lfs/h2/emc/physics/noscrub/${USER}/WEB/base
      cd ${script_dir}

      script_name=wcoss.run.hysplit_bluesky_dev.sh
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
