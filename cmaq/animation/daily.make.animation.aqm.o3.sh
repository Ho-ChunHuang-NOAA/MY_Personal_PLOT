#!/bin/sh
## module load imagemagick/7.0.8-7
## module load prod_util/1.1.0
module load imagemagick
module load prod_util
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
   declare -a cyc=( t12z )
## declare envir=( prod ncopara dev para1 )
## declare envir=( prod para para1 para-prod para1-prod para1-para )
## declare envir=( para-prod para1-prod )
declare envir=( prod )

anim_slow=1
anim_fast=0
slow=40
fast=20

beg_hour=1
end_hour=48
## declare -a ptype=( pbl sfc )
## declare -a reg=( full conus  east west nwus neus seus swus akus hius can )
## declare -a fig_reg=( dset conus east west ne10 nw10 se10 swse   ak   hi can )
declare -a fig_reg=( conus )
declare -a fig_reg=( nw )
declare -a fig_reg=( lis )

figure_type=png
anim_type=gif

if [[ $anim_fast == 1 ]]; then
   anim_time=${fast}
else
   anim_time=${slow}
fi
working_dir=/lfs/h2/emc/stmp/${USER}/cmaq_animation
odir=${working_dir}/anim_out
if [ -d ${odir} ]; then /bin/rm -rf ${odir}; fi
mkdir -p ${working_dir} ${odir}

#
## plotdir=outdir in daily.plot.hourly.cc.ksh
#


NOW=$FIRSTDAY
while [ ${NOW} -le ${LASTDAY} ]; do
   YR=`echo $NOW | cut -c 1-4`
   MON=`echo $NOW | cut -c 5-6`
   DAY=`echo $NOW | cut -c 7-8`

   for i in "${fig_reg[@]}"
   do
      for j in "${cyc[@]}"
      do
         for L in "${envir[@]}"
         do
            plotdir=${working_dir}/${L}_${j}_${i}
            if [ -d ${plotdir} ]; then /bin/rm -rf ${plotdir}; fi
            mkdir -p ${plotdir}
            cd ${plotdir}
            ## /bin/rm -f *.${figure_type}
            ## k=${beg_hour}
            ## while [ ${k} -le ${end_hour} ]; do
            ##    num=`printf %2.2d ${k}`
            ##    if [ "${L}" == "prod" ]; then
            ##       cp -p ${idir}/${NOW}/cmaq${i}smoke${j}_${num}.${figure_type} cmaq${i}smoke${j}_${num}_${L}.${figure_type}
            ##    else
            ##       cp -p ${idir}/${NOW}/cmaq${i}smoke${j}_${num}_${L}.${figure_type} .
            ##    fi
            ##    ((k++))
            ## done
            file_hd=aqm.${i}.${L}.${NOW}.${j}
            file_type=o3.k1.${figure_type}
            scp -p ${remote_user}@${remote_host}:${remote_dir}/${YR}/${NOW}/${j}/${file_hd}*${file_type} .
            ## convert -cache 1GB -delay ${anim_time} -loop 0 cmaq${i}smoke${j}_*.${figure_type} cmaq_${i}_$NOW.anim.${j}
            convert -delay ${anim_time} -loop 0 ${file_hd}*${file_type} ${file_hd}.anim.${anim_type}
            mv ${file_hd}.anim.${anim_type} ${odir}
	    echo "${odir}/${file_hd}.anim.${anim_type}"
         done
      done
   done

  if [[ 1 == 2 ]]; then  # for RZDM maintainence
    #
    ## TRANSFER PLOTS TO RZDM
    #
    cd ${working_dir}
    remote_dir=/home/people/emc/www/htdocs/mmb/hchuang
    remote_dir=/home/people/emc/www/htdocs/mmb/hchuang/web/fig
    cd ${odir}
    ## aqm.conus.para5-prod.20170805.t06z.anim.pm25.k1.${figure_type}
    ## file=aqm.conus.para5-prod.20170805.t06z.anim.o3.k1.${figure_type}
    file=aqm.nw.${envir[0]}.20170809.t12z.anim.o3.k1.${figure_type}
    scp ${file} hchuang@rzdm:/home/people/emc/hchuang/transfer
    file=aqm.conus.${envir[0]}.20170809.t12z.anim.o3.k1.${figure_type}
    ## mv ${file} new_${file}
    ## scp new_${file} hchuang@rzdm:${remote_dir}
    scp ${file} hchuang@rzdm:/home/people/emc/hchuang/transfer
  fi

  cdate=$NOW"00"
  tmp=`${NDATE} +24 $cdate`
  NOW=`echo $tmp | cut -c 1-8`

done

exit
