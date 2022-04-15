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
# set -x
USAGE="USAGE : $0 BEG_DAY(YYYYMMDD) END_DAY(YYYYMMDD)"
flag_fectch_gif=no
if [ $# -lt 1 ]; then
  echo $MSG
  exit
elif [ $# -lt 2 ]; then
   FIRSTDAY=$1
   LASTDAY=$1
   flag_fectch_gif=yes
elif [ $# -lt 3 ]; then
   FIRSTDAY=$1
   LASTDAY=$2
   flag_fectch_gif=yes
else
   FIRSTDAY=$1
   LASTDAY=$2
   flag_fectch_gif=$3
fi

## declare envir=( prod ncopara dev para1 )
declare envir=( para7.5 para7.6 )
declare envir=( para5 para8 )

anim_slow=1
anim_fast=0
slow=50
fast=20

## declare -a fcstday=( 0 1 2 )
declare -a fcstday=( 0 )
## declare -a reg=( na conus  east west nwus neus seus swus akus hius can )
## declare -a fig_reg=( dset conus east west ne10 nw10 se10 swse   ak   hi can )
declare -a fig_reg=( na conus )
declare -a fig_reg=( nyc )

if [[ $anim_fast == 1 ]]; then
   anim_time=${fast}
else
   anim_time=${slow}
fi
idir==/gpfs/${phase12_id}d2/emc/naqfc/Ho-Chun.Huang
if [ ! -d ${idir} ]; then 
   echo "Can not find ${idir}"
   exit
fi
ptmpplot=/gpfs/dell2/ptmp/Ho-Chun.Huang/fire_plot
odir=${idir}/animation
mkdir -p ${odir}

#
## plotdir=outdir in daily.plot.hourly.cc.ksh
#
let beg_hour=6
let end_hour=12
for L in "${envir[@]}"
do
   plotdir=/gpfs/dell2/ptmp/${USER}/cmaq_met_anim_plot/${envir}
   mkdir -p $plotdir
   cd $plotdir
   /bin/rm -rf *

   for i in "${fig_reg[@]}"
   do
      ## for j in "${fcstday[@]}"
      ## do
      NOW=$FIRSTDAY
      let k=${beg_hour}
      while [ ${NOW} -le ${LASTDAY} ]; do
         YR=`echo $NOW | cut -c 1-4`
         YM=`echo $NOW | cut -c 1-6`
         DAY=`echo $NOW | cut -c 7-8`

         while [ ${k} -le ${end_hour} ]; do
            num=`printf %2.2d ${k}`
            scp -p hchuang@rzdm:/home/www/emc/htdocs/mmb/hchuang/web/fig/${YR}/${NOW}/t12z/aqm.${i}.${L}.${NOW}.t12z.${num}.cldc.k1.${figure_type} cmaq_met_${i}.${L}.${num}.${figure_type}
            ## cp -p ${ptmpplot}/aqm.${i}.${L}.${NOW}.t12z.${num}.cldc.k1.${figure_type} cmaq_met_${i}.${L}.${num}.${figure_type}
         ((k++))
         done
         cdate=$NOW"00"
         tmp=`${NDATE} +24 $cdate`
         NOW=`echo $tmp | cut -c 1-8`
      done
      output_file=cmaq_met_${i}.${L}.${figure_type}
      ## done
      ## convert -cache 1GB -delay ${anim_time} -loop 0 hysplit${i}smoke${j}_*.${figure_type} hysplit_${i}_$NOW.anim.${j}
      convert -delay ${anim_time} -loop 0 cmaq_met_${i}.${L}.* ${output_file}
   done
   ftp_dir=/home/people/emc/www/htdocs/mmb/hchuang/transfer
   scp -p cmaq_met_*.${L}.${figure_type} hchuang@rzdm:${ftp_dir}
   ftp_dir=/home/people/emc/hchuang/transfer
   ftp_dir=/home/people/emc/www/htdocs/mmb/hchuang/emc_intern
   scp -p cmaq_met_*.${L}.${figure_type} hchuang@rzdm:${ftp_dir}
done

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


exit
