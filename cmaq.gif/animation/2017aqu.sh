#!/bin/sh
module load imagemagick/6.9.9-25
module load prod_util/1.1.0
module load GrADS/2.2.0
hl=`hostname | cut -c1`
if [ "${hl}" == "v" ]; then
  phase12_id='g'
else
  phase12_id='t'
fi
set -x
USAGE="USAGE : $0 BEG_DAY(YYYYMMDD) END_DAY(YYYYMMDD)"
flag_fect_fig=no
if [ $# -lt 1 ]; then
  echo $MSG
  exit
elif [ $# -lt 2 ]; then
   FIRSTDAY=$1
   LASTDAY=$1
   flag_fect_fig=yes
elif [ $# -lt 3 ]; then
   FIRSTDAY=$1
   LASTDAY=$2
   flag_fect_fig=yes
else
   FIRSTDAY=$1
   LASTDAY=$2
   flag_fect_fig=$3
fi

   remote_user=hchuang
   remote_host=emcrzdm.ncep.noaa.gov
   remote_dir=/home/people/emc/www/htdocs/mmb/hchuang/web/fig

   ## declare -a cyc=( t06z t12z )
   declare -a cyc=( t06z )
## declare envir=( prod ncopara dev para1 )
## declare envir=( prod para para1 para-prod para1-prod para1-para )
## declare envir=( para-prod para1-prod )
declare envir=( 2017agu )

anim_slow=1
anim_fast=0
slow=30
fast=10

beg_hour=1
end_hour=48
let hourly=3   ## 3 hourly
## declare -a ptype=( pbl sfc )
## declare -a reg=( full conus  east west nwus neus seus swus akus hius can )
## declare -a fig_reg=( dset conus east west ne10 nw10 se10 swse   ak   hi can )
## declare -a fig_reg=( conus west nw )
declare -a fig_reg=( conus )

if [[ $anim_fast == 1 ]]; then
   anim_time=${fast}
else
   anim_time=${slow}
fi
working_dir=/gpfs/dell2/ptmp/${USER}/cmaq_animation
odir=${working_dir}/anim_out
if [ -d ${odir} ]; then /bin/rm -rf ${odir}; fi
mkdir -p ${working_dir} ${odir}

#
## plotdir=outdir in daily.plot.hourly.cc.ksh
#

cd ${odir}
for i in "${fig_reg[@]}"
do
   for j in "${cyc[@]}"
   do
      for L in "${envir[@]}"
      do
         /bin/rm -f *.${figure_type}
         let k=1
         NOW=$FIRSTDAY
         while [ ${NOW} -le ${LASTDAY} ]; do
            YR=`echo $NOW | cut -c 1-4`
            MON=`echo $NOW | cut -c 5-6`
            DAY=`echo $NOW | cut -c 7-8`
            file_hd=aqm.${i}.${L}.${NOW}.${j}
            file_type=pm25.k1.${figure_type}
            let m=${hourly}
            while [ ${m} -le 24 ]; do
               n=`printf %2.2d ${m}`
               num=`printf %3.3d ${k}`
               ## scp -p ${remote_user}@${remote_host}:${remote_dir}/${YR}/${NOW}/${j}/${file_hd}.${n}.${file_type} plot${num}.${figure_type}
               cp -p /gpfs/dell2/stmp/${USER}/daily_plot_pm25_max/aqm_${L}_pm_max.${NOW}06/${file_hd}.${n}.${file_type} plot${num}.${figure_type}
               let m=${m}+${hourly}
               ((k++))
            done
            cdate=$NOW"00"
            tmp=`${NDATE} +24 $cdate`
            NOW=`echo $tmp | cut -c 1-8`
         done
         fileout=aqm.${i}.${L}.${FIRSTDAY}_${LASTDAY}.${j}.3hrly_anim.pm25.${figure_type}
         convert -delay ${anim_time} -loop 0 plot*.${figure_type} ${fileout}
         scp -p ${fileout}  hchuang@rzdm:/home/people/emc/hchuang/transfer
         mv ${fileout} ${odir}
      done
   done
done

exit
