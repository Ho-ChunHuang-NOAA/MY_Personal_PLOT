#!/bin/ksh
#set -x
#=============================================================================================
# script to create FVS.CTL file used by make-fvs.sh
# exported varbs for input: TRACES, PLOTHRS, VARB, PLVL, RGN, appstat, stno, strdate, endate
#=============================================================================================
set -A traces $TRACES
set -A plothrs $PLOTHRS
nhrs=${#plothrs[*]}
ntraces=${#traces[*]}
# if only one plot hour, set for all model traces
if [ -z "${plothrs[0]}" ];then plothrs[0]=00;fi
let itr=1
if [ $nhrs -lt $ntraces ];then 
   while [ $itr -lt $ntraces ];do
     if [ -z "${plothrs[itr]}" ];then plothrs[itr]=${plothrs[itr-1]};fi
     let itr=$itr+1
   done
fi
set -A varb $VARB
set -A plvl $PLVL
set -A rgn $RGN
let ihr=1
nhrs=${#plothrs[*]}
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
