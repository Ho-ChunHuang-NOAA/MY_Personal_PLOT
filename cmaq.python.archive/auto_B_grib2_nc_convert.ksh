#!/bin/ksh

export std=20190830
export etd=20190831

#export data_dir=/scratch4/NCEPDEV/naqfc/noscrub/Jianping.Huang/Python_Scripts/Data/FV3CMAQ/
export data_dir=/scratch2/NCEPDEV/naqfc/Jianping.Huang/Python_Scripts/Data/NAMCMAQ

while [ $std -le $etd ]
do

wgrib2 $data_dir/aqm.$std/aqm.t12z.ave_24hr_pm25.148.grib2  -netcdf  $data_dir/aqm.$std/aqm.t12z.ave_24hr_pm25.148.nc 
wgrib2 $data_dir/aqm.$std/aqm.t12z.max_1hr_pm25.148.grib2  -netcdf  $data_dir/aqm.$std/aqm.t12z.max_1hr_pm25.148.nc 

mv $data_dir/aqm.$std/aqm.t12z.aconc_sfc.ncf $data_dir/aqm.$std/aqm.t12z.aconc_sfc.nc

mv $data_dir/aqm.$std/aqm.t12z.metcro2d.ncf $data_dir/aqm.$std/aqm.t12z.metcro2d.nc


let "std=std+1"

done
