#!/bin/ksh

# @ job_name = fvs_pcp
# @ step_name = all
# @ output = pcp.out
# @ error =  pcp.out
# @ job_type = serial
# @ resources = ConsumableCpus(1) ConsumableMemory(1000 MB)
# @ wall_clock_limit = 03:00:00
# @ class = dev
# @ group = dev
# @ account_no = NAM-MTN
# @ notification = never
# @ queue

set -x

starttime=`date`

#===============================================================
#-- Driving script for FVS plots of precipitation using 
#   Forecast-Hits-Observations (FHO) statistics
#
#---------------------------------------------------------------
#
# This script calls the following scripts developed by Jeff McQueen,
# which does most of the work:
#   o Calls cr8cfg.sh: Creates FVS.CTL file used by make-fvs.sh to set 
#     models, regions, forecast hours, fields, dates to verify.
#   o Calls make-fvs.sh: Creates FVS configuration files, creates 
#     statistics and plots
#     + It calls cr8trace.sh: Creates FVS configuration file (trace.ctl)
#===============================================================

#===============================================================
#-- Start of input:
#===============================================================

export iplot=1      #-- Set =0 to only create fvs stats without plotting

#-- Set erase_data to >0 if the user wants to remove existing /pvsdb directory 
#   (erases all vsdb records)
#
erase_data=1

#===  IMPORTANT!  IMPORTANT!  ==================================
#
#-- The following arrays must contain the same number of elements or values:
#   $newlabl - new names or labels of renamed model runs
#   $grid - grid number used for upper-air fields
#   $sfc_reg - regions for surface verification
#
#-- WARNING: No more than 4 different directories should be specified, since
#   each directory yields two traces.  No more than 8 traces can be
#   accomodated on the plots
#

dir[0]=`pwd`/pcp_vsdb/ctl
dir[1]=`pwd`/pcp_vsdb/nmmb
dir[2]=`pwd`/pcp_vsdb/nmmb02

#-- Original labels for each run (likely either "ctl" or "exp")
#
set -A oldlabl ctl nmmb nmmb02

#-- New labels used to rename each of the runs.
#
set -A newlabl nam parent nest

#-- Regions for surface verification
#
#-- Grid 218 ("CONUS-based" from $grid) contains:
#     o RFC - CONUS
#     o EA8 - Old 8-km eastern HRW nest
#     o CN8 - Old 8-km central HRW nest
#     o WS8 - Old 8-km western HRW nest
#     o Individual FVS regions are available for verification, if desired
set -A sfc_reg RFC EA8 CN8 WS8

#-- Launcher run total forecast hours (can be <= to actual length
#   of the launcher forecasts)
#
runhrs=84

#-- SET appstat =1 to apply all stats on one graph for all traces
#               =0 to apply one stat per graph for all traces
#
export appstat=1

#===============================================================
#-- End of input
#===============================================================

n1=${#dir[*]}
n2=${#oldlabl[*]}
n3=${#newlabl[*]}

if [[ $n1 -ne $n2 || $n2 -ne $n3 || $n2 -ne $n3 ]]; then
  echo ; echo
  echo n1=$n1  n2=$n2  n3=$n3  n4=$n4  ... all must be equal ... exit 1
  echo ; echo
  exit 1
fi

if [ $n1 -gt 4 ]; then
  echo ; echo
  echo No more than 4 runs can be compared, otherwise not all of the traces get
  echo plotted and the results are very confusing ... exit 2
  echo ; echo
  exit 2
fi
  
if [ ! -a list ]; then
   echo Cannot find the list file ... exit
   exit
fi
cycle_list=`pwd`/list

export scrdir=`pwd`
export wrkdir=`pwd`/pwork
if [ -d $wrkdir ]; then
  rm -rf $wrkdir
fi
mkdir -p $wrkdir

#-- Set up GEMPAK variables
set +x
echo Setting up GEMPAK variables without command echoing
. /nwprod/gempak/.gempak > /dev/null 2>&1
. ~wx20bf/vsdb/scripts/for_fvs.sh > /dev/null 2>&1
export PATH=${PATH}:/meso/save/wx20bf/vsdb_exe
set -x

export VSDB_DATA=`pwd`/pvsdb

echo VSDB=$VSDB and VSDB_DATA=$VSDB_DATA

if [[ -d $VSDB_DATA && $erase_data -gt 0 ]]; then
  rm -rf $VSDB_DATA
fi

make_new_data=0
if [ ! -d $VSDB_DATA ]; then
  make_new_data=1
fi

mkdir -p $VSDB_DATA
cd $VSDB_DATA

#-- Define TRACES variable

let num_traces=n1-1

let i=0
while [ $i -le $num_traces ]; do
   nname=${newlabl[i]}                 #-- New name
   New=`echo $nname | dd conv=ucase`
   export TRACES="$TRACES $New"
   if [ $make_new_data -gt 0 ]; then
#-- Copy & rename VSDB files if necessary
      cp -rp ${dir[i]} $nname
      cd $nname
      oname=${oldlabl[i]}              #-- Old name
      /u/wx20bf/vsdb/scripts/renamefls $oname $nname
      cd ..
   fi
   let i=i+1
done    #-- while [ $i -le $num_traces ]; do

cd $wrkdir
cp $scrdir/SLBL.CFG .
cp $scrdir/RLBL.CFG .

pltdir=../plots
if [ ! -d $pltdir ]; then
  mkdir -p $pltdir
fi

#-- Define variable and level in advance, unlike meteorological verification
export VARB="APCP/24"
export PLVL=SFC


#-- Loop through all 00Z cycles, then all 12Z cycles
#
#-- First make sure there is a mix of 00Z and 12Z cycles
#   that were run

set -A cyhr 99 99 99 99
for cycle in `cat $cycle_list`; do
  cyc=`echo $cycle | cut -c9-10`
  case $cyc in
     00) cyhr[0]=00;;
     06) cyhr[1]=06;;
     12) cyhr[2]=12;;
     18) cyhr[3]=18;;
   esac
done

i=0
j=0
while [ $j -le 3 ]; do
   if [ ${cyhr[$j]} -lt 99 ]; then
      CYCS[$i]=${cyhr[$j]}
      let i=i+1
   fi
   let j=j+1
done

numcyc=${#CYCS[*]}
let numcyc=numcyc-1

echo The following cycles will be verified: ${CYCS[*]}

num_sfcreg=${#sfc_reg[*]}
let num_sfcreg=num_sfcreg-1

typeset -Z2 fhr

let i=0

while [ $i -le numcyc ]; do

  typeset -Z10 first last
  first=9999999999
  last=0000000000
  CYC=${CYCS[$i]}
  for cycle in `cat $cycle_list`; do
     cyc=`echo $cycle | cut -c9-10`
     if [[ $cyc = $CYC || $CYC = all ]]; then
        if [ $cycle -lt $first ]; then
           first=$cycle
        elif [ $cycle -gt $last ]; then
           last=$cycle
        fi
     fi
  done     #-- for cycle in `cat $cycle_list`
  echo
  echo The first cycle is $first and the last cycle is $last
  echo
  export strdate=${first}00
  endate=`ndate $runhrs $last`
  export endate=${endate}00

  case $CYC in 
     00) shr=12 ;;
     06) shr=06 ;;
     12) shr=00 ;;
     18) shr=18 ;;
     *)  echo "Unknown cycle with CYC=$CYC ... exit"
         exit ;;
  esac

  let nrgn=0
  while [ $nrgn -le $num_sfcreg ]; do
     sfcregion=${sfc_reg[$nrgn]}
     RGN=""
     let j=0
     while [ $j -le $num_traces ]; do
        export RGN="$RGN G218/$sfcregion"
        let j=j+1
     done
     let fhr=shr+24      #-- truncated to 2 digits
     let fhour=fhr       #-- not truncated to 2 digits
     while [ $fhour -le $runhrs ]; do
        export PLOTHRS=$fhr
        edate=`ndate $fhr $last`
        export endate=${edate}00       #- Last valid date/time
        echo Start date is $strdate and last valid date is $endate
        export stno=1001     #-- FVS plot code for bias
        $scrdir/cr8cfg.sh
        $scrdir/make-fvs.sh FHO $CYC
        mv pcp${fhour}_${sfcregion}.gif pcpbias${fhour}_${sfcregion}.gif
        export stno=1002     #-- FVS plot code for ETS
        $scrdir/cr8cfg.sh
        $scrdir/make-fvs.sh FHO $CYC
        mv pcp${fhour}_${sfcregion}.gif pcpets${fhour}_${sfcregion}.gif
        montage -tile 1x2 -geometry 612x473 pcpets${fhour}_${sfcregion}.gif \
                pcpbias${fhour}_${sfcregion}.gif pcp${fhour}_${sfcregion}.gif
        rm pcpets${fhour}_${sfcregion}.gif pcpbias${fhour}_${sfcregion}.gif
        let fhr=fhr+24
        let fhour=fhour+24
     done     #-- while [ $fhr -le $runhrs ]
     let nrgn=nrgn+1
  done        #-- while [ $nrgn -le $numcyc ]

#--  Move gifs into precipitation+cycle, and then move that into the plots directory

  cycdir=pcp_${CYC}z
  mkdir -p $cycdir
  mv *.gif $cycdir
  mv $cycdir $pltdir

  let i=i+1

done    #-- while [ $i -le numcyc ]

echo Start time was $starttime and end time was `date`

exit
