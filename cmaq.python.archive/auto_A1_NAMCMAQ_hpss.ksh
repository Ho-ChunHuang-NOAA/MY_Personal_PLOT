#!/bin/ksh

module load hpss
export std=20191001
export etd=20191031


#export outdir=/scratch4/NCEPDEV/naqfc/noscrub/Jianping.Huang/Python_Scripts/Data/NAMCMAQ
export outdir=/scratch2/NCEPDEV/naqfc/Jianping.Huang/Python_Scripts/Data/NAMCMAQ
export case1=NAMCMAQ
export case=aqm

while [ $std -le $etd ] 

do 

 if [[ -e ${outdir}/${case}.${std} ]] ; then
 echo ${outdir}/${case}.${std} "exits"
else
 mkdir -p ${outdir}/${case}.${std}
fi

cd ${outdir}/${case}.${std}


#hsi << EOF
#prompt
#cd /NCEPDEV/emc-naqfc/5year/Jianping.Huang/FV3GFS_CMAQ/CMAQv5.2.2/${std}/
#get aqm.t12z.aconc_sfc.ncf
#get aqm.t12z.ave_24hr_pm25.148.grib2
#get aqm.t12z.max_1hr_pm25.148.grib2
#get aqm.t12z.metcro2d.ncf
#bye
#EOF

yyyy=`echo $std|cut -c1-4`
mm=`echo $std|cut -c5-6`
dd=`echo $std|cut -c7-8`
ymd=`echo $std|cut -c1-8`
cyc=`echo $std|cut -c9-10`


#htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}06.input.tar -Hnostage  ./aqm.t06z.metcro2d.ncf
#htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}12.input.tar -Hnostage  ./aqm.t12z.metcro2d.ncf
#htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}12.input.tar -Hnostage  ./aqm.t12z.metcro3d.ncf
#htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}06.output.tar -Hnostage  ./aqm.t06z.aconc_sfc.ncf
htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}12.output.tar -Hnostage  ./aqm.t12z.aconc_sfc.ncf
#htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}12.output.tar -Hnostage  ./aqm.t12z.conc_1.ncf
#htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}06.post.tar -Hnostage  ./aqm.t06z.ave_24hr_pm25.148.grib2
htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}12.post.tar -Hnostage  ./aqm.t12z.ave_24hr_pm25.148.grib2
#htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}06.post.tar -Hnostage  ./aqm.t06z.max_1hr_pm25.148.grib2
htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}12.post.tar -Hnostage  ./aqm.t12z.max_1hr_pm25.148.grib2
#htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}06.post.tar -Hnostage  ./aqm.t06z.max_8hr_o3.148.grib2
#htar -x -f /NCEPPROD/5year/hpssprod/runhistory/rh${yyyy}/${yyyy}${mm}/${yyyy}${mm}${dd}/gpfs_hps_nco_ops_com_aqm_prod_aqm.${yyyy}${mm}${dd}12.post.tar -Hnostage  ./aqm.t12z.max_8hr_o3.148.grib2


let "std=std+1"

done
 
