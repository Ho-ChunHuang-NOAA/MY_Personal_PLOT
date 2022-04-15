#!/bin/ksh

#=============================================================================================
# script to create FVS.CTL file used by make-fvs.sh
# exported varbs for input: TRACES, PLOTHRS, VARB, PLVL, RGN, appstat, stno, strdate, endate
#=============================================================================================

#-- Next 2 lines are for debugging; comment out when done
# set -x
echo Entering cr8cfg.sh

set -A traces $TRACES
set -A plothrs $PLOTHRS
# if only one plot hour, set for all model traces
if [ ${#plothrs[*]} -eq 1 ];then 
   set -A phrs 
   for tr in ${traces[*]};do
     set -A phrs ${phrs[*]} $plothrs
   done
   set -A plothrs ${phrs[*]}
fi

set -A varb $VARB
set -A plvl $PLVL
set -A rgn $RGN
nhrs=${#plothrs[*]}
let ihr=1
while [ $ihr -lt $nhrs ];do
  if [ -z "${varb[ihr]}" ];then varb[ihr]=${varb[ihr-1]};fi
  if [ -z "${rgn[ihr]}" ];then rgn[ihr]=${rgn[ihr-1]};fi
  if [ -z "${plvl[ihr]}" ];then plvl[ihr]=${plvl[ihr-1]};fi
  let ihr=ihr+1
done

echo ${traces[*]}        "=" >FVS.CTL
echo ${rgn[*]}           "=" >>FVS.CTL 
echo ${varb[*]}          "=" >>FVS.CTL 
echo ${plvl[*]}          "=" >>FVS.CTL 
echo ${plothrs[*]}       "=" >>FVS.CTL 
echo $appstat ${stno[*]} "=" >>FVS.CTL 
echo $strdate $endate    "=" >>FVS.CTL 

#-- Next line is for debugging; comment out when done
echo Exiting cr8cfg.sh

