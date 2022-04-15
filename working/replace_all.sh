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
module load prod_util/1.1.0
module load GrADS/2.2.0
module load prod_envir/1.1.0
fi
#
ls > tlist
count=0
while read line
do
  shfile[$count]=$(echo $line | awk '{print $1}')
  ((count++))
done<tlist

old_ver='gif'
new_ver='png'
old_ver='\/${project}'
new_ver='${project}'
old_ver='\$ndate'
new_ver='\${NDATE}'
old_ver='\.gif'
new_ver='\.${figure_type}'
old_ver='flag_fect_gif'
new_ver='flag_fect_fig'
old_ver='grads -blc'
new_ver='grads -d Cairo -h GD -blc'
old_ver='module load idl'
new_ver='module load idl/8.6.1'
old_ver='\/naqfc\/save'
new_ver='\/gpfs\/dell2\/emc\/verification\/save'
old_ver='=\/com2'
new_ver='=${COMROOTp2}'
old_ver='/stmpp2'
new_ver='/gpfs/dell2/stmp'
old_ver='\/meso\/noscrub'
new_ver='\/gpfs/${phase12_id}d1\/emc\/meso\/noscrub'
old_ver='\/naqfc\/noscrub'
new_ver='\/gpfs/${phase12_id}d2\/emc\/naqfc'
old_ver='module load prod_util'
new_ver='module load prod_util/1.1.0'
old_ver='module load GrADS'
new_ver='module load GrADS/2.2.0'
old_ver='\-q transfer'
new_ver='\-q "dev_transfer"'
old_ver='#BSUB \-R span\[ptile=1\]'
new_ver='####BSUB \-R span\[ptile=1\]'
old_ver='\-R affinity\[core\]'
new_ver='\-R affinity\[core(1)\]'
old_ver='\-R rusage\[mem=200\]'
new_ver='\-M 100'
old_ver='=\/meso'
new_ver='=\/gpfs/${phase12_id}d1\/emc\/meso'
old_ver='=/stmpp2'
new_ver='=/gpfs/dell2/stmp'
old_ver='/ptmpp2'
new_ver='/gpfs/dell2/ptmp'
old_ver='=\/meso2'
new_ver='=\/gpfs/${phase12_id}d3\/emc\/meso'
old_ver='=meso'
new_ver='=\/gpfs/${phase12_id}d1\/emc\/meso'
old_ver='gif'
new_ver='png'
ld_ver='prod_envir\/1.0.3'
new_ver='prod_envir\/1.1.0'
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
