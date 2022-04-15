#!/bin/sh
ls > tlist
count=0
while read line
do
  shfile[$count]=$(echo $line | awk '{print $1}')
  ((count++))
done<tlist

## declare -a shfile=( ztest )

old_ver='/com2/aqm'
new_ver='${COMROOTp2}/aqm'
old_ver='=/meso/'
new_ver='=/gpfs/${phase2_id}d1/emc/meso/'
old_ver='=/ptmpp2'
new_ver='=/gpfs/dell1/ptmp'
old_ver='\-q transfer'
new_ver='\-q "dev_transfer"'
old_ver='\-R affinity[core(1)]'
new_ver='\-R affinity[core(1)]'
old_ver='\-M 100'
new_ver='\-M 100'
grepidx='#BSUB \-R span\[ptile=1\]'
old_ver='#BSUB \-R span\[ptile=1\]'
new_ver='####BSUB \-R span\[ptile=1\]'
old_ver='module load prod_util/1.1.0'
new_ver='module load prod_util/1.1.6'
set -x
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
