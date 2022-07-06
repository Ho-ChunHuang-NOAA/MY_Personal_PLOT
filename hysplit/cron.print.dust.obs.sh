#!/bin/sh 
module use /apps/test/lmodules/core/
module load GrADS/2.2.2
module load prod_util
module load prod_envir
hl=`hostname | cut -c1`
MSG="USAGE $0 YYYYMMDD_BEG YYYYMMDD_END aero_type[0:dust, 1:smoke, 2:all]"
if [ $# -lt 2 ]; then
  echo $MSG
  exit
fi
#
# Dust only for conus now
IREG_MAX=1
EXP=PARA
EXP=PROD
#
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

declare -a aerosol=( dust smoke all )
iaero=0
if [ $# -gt 3 ]; then iaero=$3; fi

echo ${aerosol[${iaero}]}
aqm=hysplit
if [ ${aerosol[${iaero}]} == 'smoke' ]; then
   satellite=nesdis
else
   satellite=aquamodis
fi

gctl=${MYBIN}/grib2ctl.pl
idir=/lfs/h2/emc/physics/noscrub/${USER}/aod_${aerosol[${iaero}]}/conc

declare -a mchr=( JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC )

declare -a FCST=( 6 12 )
n=${#FCST[@]}
i=1
while [ ${i} -le ${#FCST[@]} ]; do
   if [ ${FCST[${i}-1]} -lt 10 ]; then
      fcst_hr[${i}-1]="0"${FCST[${i}-1]}
   else
      fcst_hr[${i}-1]=${FCST[${i}-1]}
   fi
   cycle[${i}-1]="t"${fcst_hr[${i}-1]}"z"
   ((i++))
done
declare -a layer=( pbl sfc )
declare -a layer_hgt=( 5000 100 )
declare -a layer_oct=( 12800 256 )


ohd=MYDdust.t
ohd_ak=MYDdustW.t
ohd_hi=MYDdustWHI.t
afix=z.f00

## DEFINE TIME
## TODAY=`date +%Y%m%d`
FIRSTDAY=$1
LASTDAY=$2
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do

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
ilay=0     ## PBL only
data_dir=/lfs/h2/emc/stmp/${USER}/${aerosol[${iaero}]}/${satellite}.${NOW}
if [ -d ${data_dir} ]; then
  /bin/rm -f ${data_dir}/*
else
  mkdir -p ${data_dir}
fi
cd ${data_dir}
if [ -d ${idir}/${satellite}.${NOW} ]; then /bin/cp -f ${idir}/${satellite}.${NOW}/${ohd}* .; fi
if [ -d ${idir}/${satellite}_west.${NOW} ]; then /bin/cp -f ${idir}/${satellite}_west.${NOW}/${ohd_ak}* .; fi
if [ -d ${idir}/${satellite}_hawaii.${NOW} ]; then /bin/cp -f ${idir}/${satellite}_hawaii.${NOW}/${ohd_hi}* .; fi
##
   t0=00
   t1=23
   let numi=t0
   while [ ${numi} -le ${t1} ]; do

     i=${numi}
     if [ ${numi} -le 9 ]; then i="0"${numi}; fi

     if [ -e ${data_dir}/${ohd}${i}${afix} ]; then
        imod=imod00
cat > ${data_dir}/${i}.ctl << EOF
dset ${data_dir}/${ohd}${i}${afix}
index ${data_dir}/${ohd}${i}${afix}.idx
undef -9.999
title ${data_dir}/${ohd}${i}${afix}
dtype grib 255
ydef ${nydef[${imod}]} linear ${ylat0[${imod}]} ${resol[${imod}]}
xdef ${nxdef[${imod}]} linear ${xlon0[${imod}]} ${resol[${imod}]}
tdef 1 linear ${i}Z${DD}${mchr[$MM-1]}${YY} 1hr
zdef 1 linear 1 1
vars 2
AOD0_${layer_hgt[${ilay}]}m   0 129,106,${layer_oct[${ilay}]} ** 0-${layer_hgt[${ilay}]} m above ground Aerosol Optical Depth [-]
PMTF0_${layer_hgt[${ilay}]}m   0 157,106,${layer_oct[${ilay}]} ** 0-${layer_hgt[${ilay}]} m above ground Particulate matter (fine) [ug/m^3]
ENDVARS
EOF

      gribmap -0 -i ${data_dir}/${i}.ctl

      date=${NOW}

title_satellite='Aqua Modis'
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
'open ${data_dir}/${i}.ctl'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${idset}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${iconus}]} ${lat1[${iconus}]}'
'set lon ${lon0[${iconus}]} ${lon1[${iconus}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${iconus}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${ieast}]} ${lat1[${ieast}]}'
'set lon ${lon0[${ieast}]} ${lon1[${ieast}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${ieast}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${iwest}]} ${lat1[${iwest}]}'
'set lon ${lon0[${iwest}]} ${lon1[${iwest}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${iwest}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${ine10}]} ${lat1[${ine10}]}'
'set lon ${lon0[${ine10}]} ${lon1[${ine10}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${ine10}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${inw10}]} ${lat1[${inw10}]}'
'set lon ${lon0[${inw10}]} ${lon1[${inw10}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${inw10}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${ise10}]} ${lat1[${ise10}]}'
'set lon ${lon0[${ise10}]} ${lon1[${ise10}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${ise10}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${iswse}]} ${lat1[${iswse}]}'
'set lon ${lon0[${iswse}]} ${lon1[${iswse}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${iswse}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${iak}]} ${lat1[${iak}]}'
'set lon ${lon0[${iak}]} ${lon1[${iak}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${iak}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'set lat ${lat0[${ihi}]} ${lat1[${ihi}]}'
'set lon ${lon0[${ihi}]} ${lon1[${ihi}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${ihi}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'quit'
EOF
## 'set clevs 0,02 0.05 0.1 0.2 0.4 0.6 0.8 1.0 1.2 1.6 2.0'
## 'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
## 'set clevs 0 0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0'
## 'set ccols 79 20 19 18 17  3 10  7 12 8 2 9'
        grads -blc "run ${data_dir}/${i}.plot"

     fi
if [ 1 -eq 2 ]; then ## Only for conus dust
     if [ -e ${data_dir}/${ohd_ak}${i}${afix} ] || [ -e ${data_dir}/${ohd}${i}${afix} ] ; then
        imod=imod00             ## Nesdis Alaksa using the same grid format as Hysplit
if [ -e ${data_dir}/${ohd_ak}${i}${afix} ]; then
cat > ${data_dir}/${i}_ak.ctl << EOF
dset ${data_dir}/${ohd_ak}${i}${afix}
index ${data_dir}/${ohd_ak}${i}${afix}.idx
undef -9.999
title ${data_dir}/${ohd_ak}${i}${afix}
dtype grib 255
ydef ${nydef[${imod}]} linear ${ylat0[${imod}]} ${resol[${imod}]}
xdef ${nxdef[${imod}]} linear ${xlon0[${imod}]} ${resol[${imod}]}
tdef 1 linear ${i}Z${DD}${mchr[$MM-1]}${YY} 1hr
zdef 1 linear 1 1
vars 2
AOD0_${layer_hgt[${ilay}]}m   0 129,106,${layer_oct[${ilay}]} ** 0-${layer_hgt[${ilay}]} m above ground Aerosol Optical Depth [-]
PMTF0_${layer_hgt[${ilay}]}m   0 157,106,${layer_oct[${ilay}]} ** 0-${layer_hgt[${ilay}]} m above ground Particulate matter (fine) [ug/m^3]
ENDVARS
EOF

else
        imod=imod00
cat > ${data_dir}/${i}_ak.ctl << EOF
dset ${data_dir}/${ohd}${i}${afix}
index ${data_dir}/${ohd}${i}${afix}.idx
undef -9.999
title ${data_dir}/${ohd}${i}${afix}
dtype grib 255
ydef ${nydef[${imod}]} linear ${ylat0[${imod}]} ${resol[${imod}]}
xdef ${nxdef[${imod}]} linear ${xlon0[${imod}]} ${resol[${imod}]}
tdef 1 linear ${i}Z${DD}${mchr[$MM-1]}${YY} 1hr
zdef 1 linear 1 1
vars 2
AOD0_${layer_hgt[${ilay}]}m   0 129,106,${layer_oct[${ilay}]} ** 0-${layer_hgt[${ilay}]} m above ground Aerosol Optical Depth [-]
PMTF0_${layer_hgt[${ilay}]}m   0 157,106,${layer_oct[${ilay}]} ** 0-${layer_hgt[${ilay}]} m above ground Particulate matter (fine) [ug/m^3]
ENDVARS
EOF

fi

      gribmap -0 -i ${data_dir}/${i}_ak.ctl

      date=${NOW}

title_satellite='Aqua Modis'
cat > ${data_dir}/${i}_ak.plot << EOF
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
'open ${data_dir}/${i}_ak.ctl'
*'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
*'d PMTF0_${layer_hgt[${ilay}]}m'
*'${gs_dir}/cbar.gs'
*'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
*'printim ${data_dir}/${satellite}${reg[${idset}]}_ak_${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
*'c'
'set lat ${lat0[${iak}]} ${lat1[${iak}]}'
'set lon ${lon0[${iak}]} ${lon1[${iak}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${iak}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'quit'
EOF
## 'set clevs 0,02 0.05 0.1 0.2 0.4 0.6 0.8 1.0 1.2 1.6 2.0'
## 'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
## 'set clevs 0  0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0'
## 'set ccols 79 20  19  18  17  3   10  7   12  8   2   9'
    grads -blc "run ${data_dir}/${i}_ak.plot"
  fi
## For HI
     if [ -e ${data_dir}/${ohd_hi}${i}${afix} ]; then
        imod=imodhi
cat > ${data_dir}/${i}_hi.ctl << EOF
dset ${data_dir}/${ohd_hi}${i}${afix}
index ${data_dir}/${ohd_hi}${i}${afix}.idx
undef -9.999
title ${data_dir}/${ohd_hi}${i}${afix}
dtype grib 255
ydef ${nydef[${imod}]} linear ${ylat0[${imod}]} ${resol[${imod}]}
xdef ${nxdef[${imod}]} linear ${xlon0[${imod}]} ${resol[${imod}]}
tdef 1 linear ${i}Z${DD}${mchr[$MM-1]}${YY} 1hr
zdef 1 linear 1 1
vars 2
AOD0_${layer_hgt[${ilay}]}m   0 129,106,${layer_oct[${ilay}]} ** 0-${layer_hgt[${ilay}]} m above ground Aerosol Optical Depth [-]
PMTF0_${layer_hgt[${ilay}]}m   0 157,106,${layer_oct[${ilay}]} ** 0-${layer_hgt[${ilay}]} m above ground Particulate matter (fine) [ug/m^3]
ENDVARS
EOF

      gribmap -0 -i ${data_dir}/${i}_hi.ctl

      date=${NOW}

title_satellite='Aqua Modis'
cat > ${data_dir}/${i}_hi.plot << EOF
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
'open ${data_dir}/${i}_hi.ctl'
*'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
*'d PMTF0_${layer_hgt[${ilay}]}m'
*'${gs_dir}/cbar.gs'
*'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
*'printim ${data_dir}/${satellite}${reg[${idset}]}_hi_${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
*'c'
'set lat ${lat0[${ihi}]} ${lat1[${ihi}]}'
'set lon ${lon0[${ihi}]} ${lon1[${ihi}]}'
'set clevs 0.05 1.0 2.0 5.0 10. 20. 35. 50. 65.'
'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTF0_${layer_hgt[${ilay}]}m'
'${gs_dir}/cbar.gs'
'draw title ${title_satellite} ${layer[${ilay}]} ${aerosol[${iaero}]} ${date}/${i}00V00 conc ug/m3'
'printim ${data_dir}/${satellite}${reg[${ihi}]}${aerosol[${iaero}]}${layer[${ilay}]}_${i}.png png x800 y600 white'
'c'
'quit'
EOF
## 'set clevs 0,02 0.05 0.1 0.2 0.4 0.6 0.8 1.0 1.2 1.6 2.0'
## 'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
## 'set clevs 0 0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0'
## 'set ccols 79 20 19 18 17  3 10  7 12 8 2 9'
    grads -blc "run ${data_dir}/${i}_hi.plot"
  fi
fi   ## only for conus dust
  ((numi++))
done
## scp ${data_dir}/${satellite}*.png ${user}@${remote_host}:${remote_dir}/${YY}/${NOW}

   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
