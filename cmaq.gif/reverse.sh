#!/bin/sh
ls > tlist
count=0
while read line
do
  shfile[$count]=$(echo $line | awk '{print $1}')
  ((count++))
done<tlist

for i in "${shfile[@]}"
do
   echo ${i}
   if [ "${i}" == $0 ]; then continue; fi
   if [ "${i}" == "xtest1" ]; then continue; fi
   if [ -d ${i} ]; then continue; fi
   if [ -e ${i}.bak.bak ]; then
      mv ${i}.bak.bak ${i}
   fi
done
exit
