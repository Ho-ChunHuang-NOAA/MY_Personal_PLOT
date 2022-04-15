#!/bin/ksh -f

export in_dir1=/scratch2/NCEPDEV/naqfc/Jianping.Huang/Python_Scripts/Data/FV3CMAQ
export in_dir2=/scratch4/NCEPDEV/naqfc/noscrub/Jianping.Huang/Python_Scripts/Data/FV3CMAQ


export std=20190819
export etd=20190831


while [ $std -le $etd ]

do 

cp $in_dir2/aqm.$std/aqm.t06z.max_8hr_o3.148.grib2  $in_dir1/aqm.$std/
cp $in_dir2/aqm.$std/aqm.t12z.max_8hr_o3.148.grib2  $in_dir1/aqm.$std/

let "std=std+1"

done
