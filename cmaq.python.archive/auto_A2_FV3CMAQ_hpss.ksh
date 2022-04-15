#!/bin/ksh

module load hpss
export std=20191001
export etd=20191031


export outdir=/scratch2/NCEPDEV/naqfc/Jianping.Huang/Python_Scripts/Data/FV3CMAQ
         
export case1=FV3CMAQ
export case=aqm

while [ $std -le $etd ] 

do 

 if [[ -e ${outdir}/${case}.${std} ]] ; then
 echo ${outdir}/${case}.${std} "exits"
else
 mkdir -p ${outdir}/${case}.${std}
fi

cd ${outdir}/${case}.${std}


hsi << EOF
prompt
#cd /NCEPDEV/emc-naqfc/5year/Jianping.Huang/FV3GFS_CMAQ/CMAQv5.2.3/${std}/
cd /NCEPDEV/emc-naqfc/5year/Jianping.Huang/FV3GFS_CMAQ/CMAQv5.2.2/${std}/
get aqm.t12z.aconc_sfc.ncf
#get aqm.t12z.ave_24hr_pm25.148.grib2
#get aqm.t12z.max_1hr_pm25.148.grib2
get aqm.t12z.metcro2d.ncf
#get aqm.t06z.max_8hr_o3.148.grib2
#get aqm.t12z.max_8hr_o3.148.grib2
bye
EOF


let "std=std+1"

done
 
