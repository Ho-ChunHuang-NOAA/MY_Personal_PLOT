#!/bin/sh
module load prod_util
MSG="$0 BEG_DATE END_DATE EXP1 [prod] EXP2 [para#]"
if [ $# -lt 1 ]; then
      echo ${MSG}
      exit
fi

MYBIN=/u/Ho-Chun.Huang/bin
FIRSTDAY=$1
if [ $# -gt 1 ]; then
   LASTDAY=$2
else
   LASTDAY=$1
fi

exp1=$3
exp2=$4

if [ $3 == "prod" ]; then
   idir1=/com2/hysplit/prod
   idir1=/meso/noscrub/Ho-Chun.Huang/com/hysplit/prod
else
   idir1=/meso2/noscrub/Ho-Chun.Huang/com2/hysplit/$3
fi

if [ $4 == "prod" ]; then
   idir2=/com2/hysplit/prod
else
   idir2=/meso2/noscrub/Ho-Chun.Huang/com2/hysplit/$4
fi

oldhms=/meso/noscrub/Ho-Chun.Huang/dcom/us007003/2018
newhms=/meso/noscrub/Ho-Chun.Huang/dcom/us007003/2018.new

working_dir=/stmpp2/Ho-Chun.Huang/working
if [ ! -d ${working_dir} ]; then mkdir -p ${working_dir}; fi
cd ${working_dir}
logfile=compare.${exp1}.${exp2}.fire.log
if [ -s ${logfile} ]; then /bin/rm -f ${logfile};fi
echo "DATE,HMS_${exp1},HMS_${exp2},HYSPLIT_${exp1},HYSPLIT_${exp2}" > ${logfile}

infile=EMITIMES
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do
   cdate=${NOW}"00"
   YY=`echo ${NOW} | cut -c1-4`
   YM=`echo ${NOW} | cut -c1-6`
   smkdir=smokecs.${NOW}
   dir1=${idir1}/${smkdir}
   dir2=${idir2}/${smkdir}
   if [ -s add1 ]; then /bin/rm add*; fi
   head -n3 ${dir1}/${infile} > add1
   tail -n1 add1 > add2
   hysplena=`cat add2 | awk -F" " '{print $6}'`
   /bin/rm add*
   head -n3 ${dir2}/${infile} > add1
   tail -n1 add1 > add2
   hysplenb=`cat add2 | awk -F" " '{print $6}'`
   /bin/rm add*

   cdate=${NOW}"00"
   HMS=$(${NDATE} -24 ${cdate}| cut -c1-8)
   hmsfile=hmshysplit${HMS}.prelim.txt
   bash ${MYBIN}/getline.sh ${oldhms}/${hmsfile} > add1
   hmslena=`cat add1 | awk -F" " '{print $5}'`
   /bin/rm add*
   bash ${MYBIN}/getline.sh ${newhms}/${hmsfile} > add1
   hmslenb=`cat add1 | awk -F" " '{print $5}'`
   /bin/rm add*
   let hms_old=${hmslena}-1
   let hms_new=${hmslenb}-1
   echo "${NOW},${hms_old},${hms_new},${hysplena},${hysplenb}" >> ${logfile}

   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
exit
