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
USAGE="USAGE : $0 BEG_DAY(YYYYMMDD) END_DAY(YYYYMMDD) fetch_from radm [default=yes]"
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

## declare envir=( prod ncopara dev para1 )
declare envir=( prod ncopara para2 )

anim_slow=1
anim_fast=0
slow=20
fast=10

beg_hour=1
end_hour=48
declare -a ptype=( pbl sfc )
## declare -a reg=( full conus  east west nwus neus seus swus akus hius can )
## declare -a fig_reg=( dset conus east west ne10 nw10 se10 swse   ak   hi can )
## declare -a fig_reg=( conus se10 nw10 can )
declare -a fig_reg=( conus can )

if [[ $anim_fast == 1 ]]; then
   anim_time=${fast}
else
   anim_time=${slow}
fi
echo "anim_time=$anim_time"
idir==/gpfs/${phase12_id}d2/emc/naqfc/Ho-Chun.Huang
if [ ! -d ${idir} ]; then 
   echo "Can not find ${idir}"
   exit
fi
odir=${idir}/animation
mkdir -p ${odir}

#
## plotdir=outdir in daily.plot.hourly.cc.ksh
#
plotdir=/gpfs/dell2/ptmp/${USER}/daily_hysplit_anim_plot
mkdir -p $plotdir
echo $plotdir

NOW=$FIRSTDAY
while [ ${NOW} -le ${LASTDAY} ]; do
   YR=`echo $NOW | cut -c 1-4`
   MON=`echo $NOW | cut -c 5-6`
   DAY=`echo $NOW | cut -c 7-8`

   mkdir -p ${idir}/${NOW}
   cd $idir/${NOW}
   #
   #  Get gif from RZDM
   #
   if [ "${flag_fect_fig}" == "yes" ]; then
      for i in "${fig_reg[@]}"
      do
         scp -p hchuang@rzdm:/home/www/emc/htdocs/mmb/hchuang/web/fig/${YR}/${NOW}/t06z/hysplit${i}smoke*.${figure_type} .
      done
   fi

   mkdir -p ${plotdir}/${NOW}
   cd $plotdir/${NOW}
   for i in "${fig_reg[@]}"
   do
      for j in "${ptype[@]}"
      do
         for L in "${envir[@]}"
         do
            ## /bin/rm -f *.${figure_type}
            k=${beg_hour}
            while [ ${k} -le ${end_hour} ]; do
               num=`printf %2.2d ${k}`
               if [ "${L}" == "prod" ]; then
                  cp -p ${idir}/${NOW}/hysplit${i}smoke${j}_${num}.${figure_type} hysplit${i}smoke${j}_${num}_${L}.${figure_type}
               else
                  cp -p ${idir}/${NOW}/hysplit${i}smoke${j}_${num}_${L}.${figure_type} .
               fi
               ((k++))
            done
            ## convert -cache 1GB -delay ${anim_time} -loop 0 hysplit${i}smoke${j}_*.${figure_type} hysplit_${i}_$NOW.anim.${j}
            convert -delay ${anim_time} -loop 0 hysplit${i}smoke${j}_*_${L}.${figure_type} hysplit_${i}_$NOW.anim.${j}.${L}.${figure_type}
            mv hysplit_${i}_$NOW.anim.${j}.${L}.${figure_type} ${odir}
         done
      done
   done
   cd ${odir}
   scp -p $hysplit_*_${NOW}.anim.*.${figure_type} hchuang@rzdm:/home/people/emc/hchuang/transfer
  if [[ 1 == 2 ]]; then  # for RZDM maintainence
    #
    ## TRANSFER PLOTS TO RZDM
    #
    remote_dir=/home/people/emc/www/htdocs/mmb/hchuang

    scp ${plotdir}/*g.$NOW.$resol.anim*.k1.cc.${figure_type} hchuang@rzdm:${remote_dir}/${YR}${MON}/$NOW
    /bin/rm -f ${plotdir}/*g.*.cc.${figure_type}
    ##
    cd =/gpfs/${phase12_id}d2/emc/naqfc/${USER}/GFS_GOCART/output/bb/${YR}/${resol}
    /bin/rm -r -f $NOW
  fi

  cdate=$NOW"00"
  tmp=`${NDATE} +24 $cdate`
  NOW=`echo $tmp | cut -c 1-8`

done

exit
