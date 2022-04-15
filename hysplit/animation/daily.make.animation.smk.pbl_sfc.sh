#!/bin/sh
set -x
USAGE="USAGE : $0 BEG_DAY(YYYYMMDD) END_DAY(YYYYMMDD)"
flag_fect_gif=no
if [ $# -lt 1 ]; then
  echo $MSG
  exit
elif [ $# -lt 2 ]; then
   FIRSTDAY=$1
   LASTDAY=$1
   flag_fect_gif=yes
elif [ $# -lt 3 ]; then
   FIRSTDAY=$1
   LASTDAY=$2
   flag_fect_gif=yes
else
   FIRSTDAY=$1
   LASTDAY=$2
   flag_fect_gif=$3
fi

## declare envir=( prod ncopara dev para1 )
declare envir=( prod ncopara para2 )

anim_slow=1
anim_fast=0
slow=20
fast=10

beg_hour=1
end_hour=24
declare -a ptype=( pbl sfc )
## declare -a reg=( full conus  east west nwus neus seus swus akus hius can )
## declare -a fig_reg=( dset conus east west ne10 nw10 se10 swse   ak   hi can )
declare -a fig_reg=( conus can )

if [[ $anim_fast == 1 ]]; then
   anim_time=${fast}
else
   anim_time=${slow}
fi
idir=/naqfc/noscrub/Ho-Chun.Huang
if [ ! -d ${idir} ]; then 
   echo "Can not find ${idir}"
   exit
fi
odir=${idir}/animation
mkdir -p ${odir}

#
## plotdir=outdir in daily.plot.hourly.cc.ksh
#
plotdir=/ptmpp1/${USER}/daily_hysplit_anim_plot
mkdir -p $plotdir
echo $plotdir

GRADS=/usrx/local/grads/bin
ndate=/nwprod/util/exec/ndate

NOW=$FIRSTDAY
while [ ${NOW} -le ${LASTDAY} ]; do
   YR=`echo $NOW | cut -c 1-4`
   MON=`echo $NOW | cut -c 5-6`
   DAY=`echo $NOW | cut -c 7-8`

   mkdir -p ${plotdir}/${NOW}
   cd $plotdir/${NOW}

   for i in "${fig_reg[@]}"
   do
      for j in "${ptype[@]}"
      do
         for L in "${envir[@]}"
         do
            ## /bin/rm -f *.gif
            k=${beg_hour}
            while [ ${k} -le ${end_hour} ]; do
               num=`printf %2.2d ${k}`
               if [ "${L}" == "prod" ]; then
                  cp -p ${idir}/${NOW}/hysplit${i}smoke${j}_${num}.gif hysplit${i}smoke${j}_${num}_${L}.gif
               else
                  cp -p ${idir}/${NOW}/hysplit${i}smoke${j}_${num}_${L}.gif .
               fi
               ((k++))
            done
            ## convert -cache 1GB -delay ${anim_time} -loop 0 hysplit${i}smoke${j}_*.gif hysplit_${i}_$NOW.anim.${j}
            convert -delay ${anim_time} -loop 0 hysplit${i}smoke${j}_*_${L}.gif hysplit_${i}_$NOW.anim.${j}.${L}.gif
            mv hysplit_${i}_$NOW.anim.${j}.${L}.gif ${odir}
         done
      done
   done

  if [[ 1 == 2 ]]; then  # for RZDM maintainence
    #
    ## TRANSFER PLOTS TO RZDM
    #
    remote_dir=/home/people/emc/www/htdocs/mmb/hchuang

    scp ${plotdir}/*g.$NOW.$resol.anim*.k1.cc.gif hchuang@rzdm:${remote_dir}/${YR}${MON}/$NOW
    /bin/rm -f ${plotdir}/*g.*.cc.gif
    ##
    cd /naqfc/noscrub/${USER}/GFS_GOCART/output/bb/${YR}/${resol}
    /bin/rm -r -f $NOW
  fi

  cdate=$NOW"00"
  tmp=`$ndate +24 $cdate`
  NOW=`echo $tmp | cut -c 1-8`

done

exit
