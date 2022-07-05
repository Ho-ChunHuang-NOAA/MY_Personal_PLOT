#!/bin/sh
#
# /naqfc/noscrub ==> /gpfs/${phase12_id}d2/emc/naqfc/noscrub
# /naqfc2/noscrub ==> /gpfs/${phase12_id}d3/emc/naqfc/noscrub
# /meso/noscrub ==> /gpfs/${phase12_id}d1/emc/meso/noscrub
# /meso2/noscrub ==> /gpfs/${phase12_id}d3/emc/meso/noscrub
# /naqfc/save ==> /gpfs/${phase12_id}d2/emc/naqfc/save
# /meso/save ==> /gpfs/${phase12_id}d1/emc/meso/save
if [ 1 -eq 2 ]; then
module load imagemagick/6.9.9-25
module load prod_util/1.1.6
module load GrADS/2.2.0
module load prod_envir/1.1.0
hl=`hostname | cut -c1`
if [ "${hl}" == "v" ]; then
  phase12_id='g'
else
  phase12_id='t'
fi
fi
#
ls > tlist
count=0
while read line
do
  shfile[$count]=$(echo $line | awk '{print $1}')
  ((count++))
done<tlist

old_ver='module load GrADS/2.2.0'
new_ver='module load GrADS'
old_ver='module load ips/18.0.5.274'
old_ver='module load HPSS/5.0.2.5'
old_ver='module load prod_util/1.1.6'
new_ver='module load prod_util'
for i in "${shfile[@]}"
do
   echo ${i}
   if [ "${i}" == $0 ]; then continue; fi
   if [ "${i}" == "xtest1" ]; then continue; fi
   if [ -d ${i} ]; then continue; fi
   ## mv ${i}.bak ${i}
   if [ -e xtest1 ]; then /bin/rm -f xtest1; fi
   grep "${old_ver}" ${i} > xtest1
   if [ -s xtest1 ]; then
      mv ${i} ${i}.bak
      sed -e "s!${old_ver}!${new_ver}!" ${i}.bak > ${i}
      ## echo "diff ${i} ${i}.bak"
      diff ${i} ${i}.bak
   fi
done
exit
