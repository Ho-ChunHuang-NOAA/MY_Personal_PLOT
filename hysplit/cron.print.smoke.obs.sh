#!/bin/sh 
module load GrADS/2.2.0
module load prod_util/1.1.0
module load prod_envir/1.1.0
hl=`hostname | cut -c1`
if [ "${hl}" == "v" ]; then
  phase12_id='g'
else
  phase12_id='t'
fi
MSG="USAGE $0 YYYYMMDD_BEG YYYYMMDD_END aero_type[0:dust, 1:smoke, 2:all]"
if [ $# -lt 2 ]; then
  echo $MSG
  exit
fi
remote_dir=/home/people/emc/www/htdocs/mmb/hchuang/web/fig
remote_host=vm-lnx-dmznas1.ncep.noaa.gov
remote_host=emcrzdm.ncep.noaa.gov
user=hchuang
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
declare -a reg=( dset conus east west ne10 nw10 se10 swse   ak   hi can )
declare -a lon0=( -175 -130 -100 -128  -81 -128  -91 -128 -170 -161 -141 )
declare -a lon1=(   55  -60  -65  -90  -64 -110  -74 -100 -130 -154  -60 )
declare -a lat0=(    0   20   24   25   37   38   24   28   50   18   40 )
declare -a lat1=(   80   55   47   55   48   55   40   40   80   23   70 )
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

declare -a aerosol=( dust smoke all )
iaero=1
if [ $# -gt 3 ]; then iaero=$3; fi
layer=pbl
surface=sfc

aqm=hysplit
satellite=nesdis

gctl=${MYBIN}/grib2ctl.pl
idir=/gpfs/dell2/emc/modeling/noscrub/${USER}/aod_${aerosol[${iaero}]}/conc

declare -a mchr=( JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC )
FCST=06
ahd=hysplit_smoke.t06z.f

ohd=G13.t
ohd_ak=GW.t
ohd_hi=GWHI.t
afix=z.f00

## DEFINE TIME
## TODAY=`date +%Y%m%d`
FIRSTDAY=$1
LASTDAY=$2
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do

   cdate=${NOW}"00"
   TOMORROW=$(${NDATE} +24 ${cdate}| cut -c1-8)
   THIRDDAY=$(${NDATE} +48 ${cdate}| cut -c1-8)

   YY=`echo ${NOW} | cut -c1-4`
   MX=`echo ${NOW} | cut -c5-5`
   if [ ${MX} == '0' ]; then
      MM=`echo ${NOW} | cut -c6-6`
   else
      MM=`echo ${NOW} | cut -c5-6`
   fi
   DD=`echo ${NOW} | cut -c7-8`
##
## PLOT NESDIS SMOKE HOURLY
## 
data_dir=/gpfs/dell1/stmp/${USER}/${aerosol[${iaero}]}/${satellite}.${NOW}
if [ -d ${data_dir} ]; then
  /bin/rm -f ${data_dir}/*
else
  mkdir -p ${data_dir}
fi
cd ${data_dir}
if [ -d ${idir}/${satellite}.${NOW} ]; then /bin/cp -f ${idir}/${satellite}.${NOW}/${ohd}* .; fi
if [ -d ${idir}/${satellite}_west.${NOW} ]; then /bin/cp -f ${idir}/${satellite}_west.${NOW}/${ohd_ak}* .; fi
if [ -d ${idir}/${satellite}_hawaii.${NOW} ]; then /bin/cp -f ${idir}/${satellite}_hawaii.${NOW}/${ohd_hi}* .; fi
YY=`echo ${NOW} | cut -c1-4`
   MX=`echo ${NOW} | cut -c5-5`
   if [ ${MX} == '0' ]; then
      MM=`echo ${NOW} | cut -c6-6`
   else
      MM=`echo ${NOW} | cut -c5-6`
   fi
DD=`echo ${NOW} | cut -c7-8`
##
   t0=00
   t1=23
   let numi=t0
   while [ ${numi} -le ${t1} ]; do

     i=${numi}
     if [ ${numi} -le 9 ]; then i="0"${numi}; fi

     if [ -e ${data_dir}/${ohd}${i}${afix} ]; then

cat > ${data_dir}/${i}.ctl << EOF
dset ${data_dir}/${ohd}${i}${afix}
index ${data_dir}/${ohd}${i}${afix}.idx
undef 9.999E+20
title ${data_dir}/${ohd}${i}${afix}
dtype grib 255
ydef 534 linear 0.000000 0.15
xdef 801 linear -175.000000 0.150000
tdef 1 linear ${i}Z${DD}${mchr[$MM-1]}${YY} 1mo
zdef 1 linear 1 1
vars 2
PMTF0_5000m   0 157,106,12800 ** 0-5000 m above ground Particulate matter (fine) [ug/m^3]
MSLMAclm  0 129,200,0 ** atmos column Mean sea level pressure (MAPS) [Pa]
ENDVARS
EOF

      gribmap -0 -i ${data_dir}/${i}.ctl

      date=${NOW}

title_satellite=GASP
cat > ${data_dir}/${i}.plot << EOF
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
'open ${data_dir}/${i}.ctl'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${idset}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${iconus}]} ${lat1[${iconus}]}'
'set lon ${lon0[${iconus}]} ${lon1[${iconus}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${iconus}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${ieast}]} ${lat1[${ieast}]}'
'set lon ${lon0[${ieast}]} ${lon1[${ieast}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${ieast}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${iwest}]} ${lat1[${iwest}]}'
'set lon ${lon0[${iwest}]} ${lon1[${iwest}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${iwest}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${ine10}]} ${lat1[${ine10}]}'
'set lon ${lon0[${ine10}]} ${lon1[${ine10}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${ine10}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${inw10}]} ${lat1[${inw10}]}'
'set lon ${lon0[${inw10}]} ${lon1[${inw10}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${inw10}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${ise10}]} ${lat1[${ise10}]}'
'set lon ${lon0[${ise10}]} ${lon1[${ise10}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${ise10}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${iswse}]} ${lat1[${iswse}]}'
'set lon ${lon0[${iswse}]} ${lon1[${iswse}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${iswse}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${iak}]} ${lat1[${iak}]}'
'set lon ${lon0[${iak}]} ${lon1[${iak}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${iak}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${ihi}]} ${lat1[${ihi}]}'
'set lon ${lon0[${ihi}]} ${lon1[${ihi}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${ihi}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${ican}]} ${lat1[${ican}]}'
'set lon ${lon0[${ican}]} ${lon1[${ican}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${ican}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'quit'
EOF
## 'set clevs 0,02 0.05 0.1 0.2 0.4 0.6 0.8 1.0 1.2 1.6 2.0'
## 'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
## 'set clevs 0 0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0'
## 'set ccols 79 20 19 18 17  3 10  7 12 8 2 9'
        grads -blc "run ${data_dir}/${i}.plot"

     fi
## For AK; if GOES-WEST has NO data use GOES-EAST
     if [ -e ${data_dir}/${ohd_ak}${i}${afix} ] || [ -e ${data_dir}/${ohd}${i}${afix} ] ; then

if [ -e ${data_dir}/${ohd_ak}${i}${afix} ]; then
cat > ${data_dir}/${i}_ak.ctl << EOF
dset ${data_dir}/${ohd_ak}${i}${afix}
index ${data_dir}/${ohd_ak}${i}${afix}.idx
undef 9.999E+20
title ${data_dir}/${ohd_ak}${i}${afix}
dtype grib 255
ydef 534 linear 0.000000 0.15
xdef 801 linear -175.000000 0.150000
tdef 1 linear ${i}Z${DD}${mchr[$MM-1]}${YY} 1mo
zdef 1 linear 1 1
vars 2
PMTF0_5000m   0 157,106,12800 ** 0-5000 m above ground Particulate matter (fine) [ug/m^3]
MSLMAclm  0 129,200,0 ** atmos column Mean sea level pressure (MAPS) [Pa]
ENDVARS
EOF

else

cat > ${data_dir}/${i}_ak.ctl << EOF
dset ${data_dir}/${ohd}${i}${afix}
index ${data_dir}/${ohd}${i}${afix}.idx
undef 9.999E+20
title ${data_dir}/${ohd}${i}${afix}
dtype grib 255
ydef 534 linear 0.000000 0.15
xdef 801 linear -175.000000 0.150000
tdef 1 linear ${i}Z${DD}${mchr[$MM-1]}${YY} 1mo
zdef 1 linear 1 1
vars 2
PMTF0_5000m   0 157,106,12800 ** 0-5000 m above ground Particulate matter (fine) [ug/m^3]
MSLMAclm  0 129,200,0 ** atmos column Mean sea level pressure (MAPS) [Pa]
ENDVARS
EOF

fi

      gribmap -0 -i ${data_dir}/${i}_ak.ctl

      date=${NOW}

title_satellite=GASP
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
'open ${data_dir}/${i}_ak.ctl'
*'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
*'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
*'d PMTF0_5000m'
*'${gs_dir}/cbar.gs'
*'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
*'printim ${data_dir}/${satellite}${reg[${idset}]}_ak_${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
*'c'
'set lat ${lat0[${iak}]} ${lat1[${iak}]}'
'set lon ${lon0[${iak}]} ${lon1[${iak}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${iak}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'quit'
EOF
## 'set clevs 0,02 0.05 0.1 0.2 0.4 0.6 0.8 1.0 1.2 1.6 2.0'
## 'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
## 'set clevs 0 0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0'
## 'set ccols 79 20 19 18 17  3 10  7 12 8 2 9'
    grads -blc "run ${data_dir}/${i}_ak.plot"
  fi
## For HI
            if [ -e ${data_dir}/${ohd_hi}${i}${afix} ]; then

cat > ${data_dir}/${i}_hi.ctl << EOF
dset ${data_dir}/${ohd_hi}${i}${afix}
index ${data_dir}/${ohd_hi}${i}${afix}.idx
undef 9.999E+20
title ${data_dir}/${ohd_hi}${i}${afix}
dtype grib 255
ydef 201 linear 15.000000 0.05
xdef 401 linear -166.000000 0.050000
tdef 1 linear ${i}Z${DD}${mchr[$MM-1]}${YY} 1mo
zdef 1 linear 1 1
vars 2
PMTF0_5000m   0 157,106,12800 ** 0-5000 m above ground Particulate matter (fine) [ug/m^3]
MSLMAclm  0 129,200,0 ** atmos column Mean sea level pressure (MAPS) [Pa]
ENDVARS
EOF

      gribmap -0 -i ${data_dir}/${i}_hi.ctl

      date=${NOW}

title_satellite=GASP
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
'open ${data_dir}/${i}_hi.ctl'
*'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
*'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
*'d PMTF0_5000m'
*'${gs_dir}/cbar.gs'
*'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
*'printim ${data_dir}/${satellite}${reg[${idset}]}_hi_${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
*'c'
'set lat ${lat0[${ihi}]} ${lat1[${ihi}]}'
'set lon ${lon0[${ihi}]} ${lon1[${ihi}]}'
'set clevs 0.01 3. 6. 12. 25. 35. 55. 75. 105. 150. 200. 250. 350. 500.'
'set ccols 89 88 79 78 76 19 18 17 3 10 7 12 8 2 98'
'd PMTF0_5000m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${ihi}]}${aerosol[${iaero}]}${layer}_${i}.png png x800 y600 white'
'c'
'quit'
EOF
## 'set clevs 0,02 0.05 0.1 0.2 0.4 0.6 0.8 1.0 1.2 1.6 2.0'
## 'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
## 'set clevs 0 0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0'
## 'set ccols 79 20 19 18 17  3 10  7 12 8 2 9'
    grads -blc "run ${data_dir}/${i}_hi.plot"
  fi
  ((numi++))
done
## scp ${data_dir}/${satellite}*.png ${user}@${remote_host}:${remote_dir}/${YY}/${NOW}

   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
