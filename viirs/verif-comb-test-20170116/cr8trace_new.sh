#! /bin/ksh
#set -x
#=========================================================================
#  Create FVS trace.ctl file for statistical calculations
#   cr8trace.sh 
#  jtm 11/04
# 9/05 added FHO for prcp option
#=========================================================================
rm -f  trace.ctl
set -A rgn    $REGION
set -A traces $TRACES
set -A obsdat $OBSDAT
set -A sttyp  $STTYP 
set -A VARB   $VARB
set -A fhr    $FHR
set -A fhre   $FHRE
set -A vhr    $VHR
set -A vhre   $VHRE
set -A plvl   $PLVL

echo In $0 "plotdts    :" $plotdts
echo In $0 "VARB       :" ${VARB[*]}
echo In $0 "plotlvl    :" ${plvl[*]}
echo In $0 "FHR        :" ${fhr[*]}
echo In $0 "VHR        :" ${vhr[*]}
echo In $0 "TRACES     :" ${TRACES[*]}
echo In $0 "STTYP      :" ${sttyp[*]}
echo In $0 "OBSDAT     :" ${OBSDAT[*]}
echo In $0 "Regions    :" ${REGION[0]}
echo In $0 "plottype   :" $plottype
echo In $0 "FHRE       :" ${fhre[*]}
echo In $0 "VHRE       :" ${vhre[*]}
echo In $0 "Dates      :" $strdate $endate
echo In $0 "binhrs     :" ${binhrs[*]}
echo In $0 "binvhrs    :" ${binvhrs[*]}
echo In $0 "NTRACES    :" ${#traces[@]}
echo In $0 "NREGIONS   :" ${#rgn[@]}
echo In $0 "NVARB      :" ${#VARB[@]}
echo In $0 "CYCLE      :" ${cycle}

# FHO Threat score stat type check
if [ $plottype = FHO ];then
  conchk="2 1 1 3 2/2/0/0"
  inddate=0
  indfhr=0
  indplvl=0
fi
# Bin by day for 1 forecast hour and model level
if [ $plotdts = 1 ];then
  conchk="2 1 1 1 0/0/0/0"
  inddate=1
  indfhr=0
  indplvl=0
else

# Bin by forecast hour for 1 model level
  if [ $plottype = DIU -a $sttyp != FHO ];then
#707 changed consist from 0010 to none
#TEST 0609    conchk="2 1 1 4 2/2/2/2"
#TEST 0609    conchki="2 $nbhrs 1 4 2/2/2/2"
    conchk="2 1 1 4 2/2/0/0"
    conchki="2 $nbhrs 1 4 2/2/0/0"
    inddate=0
    indfhr=1
    indplvl=0

# Bin by plot level for 1 forecast hour
  elif [ $plottype = UPA -a $sttyp != FHO ];then   
    set -A blvls P1000 P850 P700 P500 P400 P300 P250 P200 P150 P100
    if [ $VARB = RH ];then
      set -A blvls P1000 P850 P700 P500 P400 P300 
    fi
    nlvls=${#blvls[@]}
#   if multiple forecast hours on one graph, can use consistency checking
    conchk="2 1 1 4 2/2/0/0"
    conchki="2 $nlvls 1 4 2/2/0/0"
    inddate=0
    indfhr=0
    indplvl=1
  fi
fi

#=====================================================================
#    BEGIN CREATING FVS TRACE.CTL FILE
#=====================================================================

#  11 FHO Indicator(ind. varb)
if [ $plottype = FHO ]; then
  itrace=0
  for TRACE in ${traces[*]};do
    let itrace=itrace+1
    if [ $itrace -eq 1 ];then
      echo $itrace "11 1" $conchk >trace.ctl
    else
      echo $itrace "11 1" $conchk >>trace.ctl
    fi
    echo 0 0 0 0 0 >>trace.ctl
  done
fi

#   2 Trace name (model)
itrace=0
for TRACE in ${traces[*]};do
  let itrace=itrace+1
  if [ $itrace -eq 1 -a $plottype != FHO ];then 
    echo $itrace "2 0" $conchk >trace.ctl 
  else 
    echo $itrace "2 0" $conchk >>trace.ctl 
  fi
  echo 18 0 0 $TRACE 0 >>trace.ctl
done

#   3 Forecast hour
let itrace=0
let itr=0
for TRACE in ${traces[*]};do
  let itrace=itrace+1
  OUT=${fhr[$itr]}
  OUTE=${fhre[$itr]}

# if SREF file, Forecast hour is offset by 3 hours
  tracemdl=`echo $TRACE | cut -c1-2 -`
  case $tracemdl in 
    SR | EB | EK | ES | ED |AR | NM | RS |RR |EM )
    let OUT=${fhr[$itr]}+3
    let OUTE=${fhre[$itr]}+3;;
  esac

  if [ $indfhr -eq 0 ];then 
#   FHR = 99 will plot stats for all forecast hours
    if [ ${fhr[itr]} -ne 99 ];then 
#     FHRE allows for a range of forecast hrs to be combined
      echo $itrace "3 $indfhr" $conchk >>trace.ctl 

#     The following sets a forecast range:(id:6, if fhre>fhr)
      if [ ${fhre[$itr]} -eq 99 -o ${fhre[$itr]} -eq 102 ];then
        echo 9 $OUT 0 0 0 >>trace.ctl
      else
        echo 6 $OUT $OUTE 0 0 >>trace.ctl
      fi
    fi
  else
    echo $itrace "3 $indfhr" $conchki >>trace.ctl 
    for fbhr in ${binhrs[*]};do
      OUT=$fbhr
      case $tracemdl in 
	SR | EB | EK | ES | ED |AR | NM | RS |RR |EM )
	let OUT=$fbhr+3;;
      esac
      echo 9 $OUT 0 0 0 >>trace.ctl
    done
  fi
  let itr=$itr+1
done

#   15 verification hour
itrace=0
itr=0
for TRACE in ${traces[*]};do
  let itrace=itrace+1
  if [ $indfhr -eq 0 ];then 

#   vhre(end) allows for a range of hrs to be lumped together in the statistics
#   vhr=99 indicates that a forecast range is not being used.
#   Right now, the program will not categorize by verification hour when a range is used
#   To compute stats for all cycles, Do not write out verification hour if cycle or vhr = 99 

    if [ ${vhr[itr]} -ne 99 ];then
     if [ ${vhre[itr]} -ne 99 ];then
      echo $itrace "15 $indfhr" $conchk >>trace.ctl 
      echo 18 0 0 ${vhr[$itr]} ${vhre[$itr]} 0 >>trace.ctl
     else
      echo $itrace "15 $indfhr" $conchk >>trace.ctl
      echo 18 0 0 ${vhr[$itr]} 0 >>trace.ctl
     fi
    fi
  else
    if [ $cycle -ne 99 ];then
      echo In $0 "Bin by Forecast hour" TRACE $TRACE
      echo $itrace "15 $indfhr" $conchki >>trace.ctl 
      for bvhr in ${binvhrs[*]};do
        typeset -Z4 VBHR
        let VBHR=$bvhr
        echo 18 0 0 $VBHR 0 >>trace.ctl
      done
    fi
  fi
  let itr=$itr+1
done

#   14 plvl (SFC,ATMOS  or a Pressure level)
itrace=0
for TRACE in ${traces[*]};do
  let itrace=itrace+1
    if [ $indplvl -eq 0 ];then
      echo $itrace "14 $indplvl" $conchk >>trace.ctl 
      echo 18 0 0 ${plvl[itrace-1]} 0 >>trace.ctl
    else
      echo $itrace "14 $indplvl" $conchki >>trace.ctl 
      for pllvl in ${blvls[*]};do
	echo 18 0 0 $pllvl 0 >>trace.ctl
      done
    fi
done

#   8 Verifying observation dataset 
itrace=0
for TRACE in ${traces[*]};do
  if [ -n "${obsdat[$itrace]}" ];then OBS=${obsdat[$itrace]};fi
  let itrace=itrace+1
  echo $itrace "8 0" $conchk >>trace.ctl 
  echo 18 0 0 $OBS 0 >>trace.ctl
done

#   9 verifying region
itrace=0
irgn=0
ic=0
set -A cflag C D E F H I
for TRACE in ${traces[*]};do
  if [ -n "${rgn[$irgn]}" ];then RGN=${rgn[$irgn]};fi
    rgnltr=`echo $RGN | cut -c1`
    let itrace=itrace+1
    echo IN CR8TRACE $plottype TRACE $itrace $TRACE RGN $irgn ${rgn[irgn]}

    case $rgnltr in 
      C | D | E | F | H | I )
      set -A crgn 
       while [ $rgnltr = ${cflag[ic]} ];do
#        set -A crgn ${cflag[ic]} ${RGN#${rgnltr}}
        set -A crgn ${crgn[*]} ${RGN#${rgnltr}}
        let irgn=$irgn+1 
        RGN=${rgn[$irgn]}
        rgnltr=`echo $RGN | cut -c1`
        if [ -z "$rgnltr" ];then rgnltr=Z;fi
       done
      set -A CONCHK $conchk
      CONCHK[1]=${#crgn[@]}
      echo $itrace "9 0" ${CONCHK[*]}  >>trace.ctl 
      for CRGN in ${crgn[*]};do 
        echo 18 0 0 $CRGN 0 >>trace.ctl
      done
      let ic=$ic+1;;
   * )
      echo $itrace "9 0" $conchk >>trace.ctl
      echo 18 0 0 $RGN 0 >>trace.ctl
     let irgn=$irgn+1;;
   esac
done

#   10 Statistic type (SL1L2,VL1L2, FHO, ESL1L2, RHNT, RHET)
itrace=0
for TRACE in ${traces[*]};do
  if [ -n "${sttyp[$itrace]}" ];then STT=${sttyp[$itrace]};fi
  let itrace=itrace+1
  echo $itrace "10 0" $conchk >>trace.ctl 
  echo 18 0 0 $STT 0 >>trace.ctl
done

#   12 variable to plot
itrace=0
for TRACE in ${traces[*]};do
  if [ -n "${VARB[$itrace]}" ];then VAR=${VARB[$itrace]};fi
  let itrace=itrace+1
  echo $itrace "12 0" $conchk >>trace.ctl 
  echo 18 0 0 $VAR 0 >>trace.ctl
done

#   5 Date range
itrace=0
for TRACE in ${traces[*]};do
  let itrace=itrace+1
  echo $itrace "5 $inddate" $conchk >>trace.ctl 
  echo 15 0 0 $strdate $endate  >>trace.ctl
done
