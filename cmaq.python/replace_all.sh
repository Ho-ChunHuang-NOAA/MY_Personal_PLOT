#!/bin/sh
#
ls daily.aqm.plot* > tlist
count=0
while read line
do
  shfile[$count]=$(echo $line | awk '{print $1}')
  ((count++))
done<tlist



old_ver='\-166.0, \-161.5, \-141.0, \-75.0 \]'
new_ver=' \-75.0, \-166.0, \-161.5, \-141.0 \]'
old_ver='\-132.0, \-153.1,  \-60.0, \-71.0 \]'
new_ver=' \-71.0, \-132.0, \-153.1, \-60.0 \]'
old_ver=' \-75.0, \-105.0, \-170.0, \-161.0, \-141.0'
new_ver='\-105.0,  \-75.0, \-170.0, \-161.0, \-141.0'
old_ver=' 8,      8,      8,  5 \]'
new_ver=' 5,      8,      8,     8 \]'
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
      chmod u+x ${i}
      diff ${i} ${i}.bak
   fi
done
/bin/rm xtest1 tlist
exit
