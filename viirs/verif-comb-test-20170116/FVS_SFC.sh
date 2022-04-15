set -x

#===============================================================
#
#  Script:  FVS_SFC.sh => Used to plot surface bias & RMSE
#
#===============================================================

starttime=`date`      #-- For timing purposes

#***************************************************
#-- vars assigned from previous scrtip -------
#***************************************************

export VARB=$1
export strdate=$2

CYC=$3
runhrs=$4

export endate=$5
export scrdir=$6
export wrkdir=$7
export plotsdir=$8
export VSDB_DATA=$9
export iplot=${10}
export appstat=${11}

n1=${12}

#===================================================
#-- move to working dir for processing $CYC plots
#===================================================

wrkcyc=met_SFC_${CYC}_${VARB}

mkdir -p $wrkcyc
cd $wrkcyc

#------------------------------------------------------------
#-- Set up GEMPAK variables
#------------------------------------------------------------

set +x
echo Setting up GEMPAK variables without command echoing
. /nwprod/gempak/.gempak > /dev/null 2>&1
. ~wx20bf/vsdb/scripts/for_fvs.sh > /dev/null 2>&1
export PATH=${PATH}:/meso/save/wx20bf/vsdb_exe
set -x

echo VSDB=$VSDB     #-- /u/wx20bf/vsdb
echo VSDB_DATA=$VSDB_DATA

################################################################
#============== BEGIN THE PROCESS ==============================
################################################################

cp $scrdir/SLBL.CFG .            # statistics choice
cp $scrdir/RLBL.CFG .            # grid & regional choice
cp $scrdir/TLBL.CFG .            # operational model names
cp $scrdir/VARB.CFG .            # max/min values for variables

#-- Set line colors (LCOL), line types (LTYPE), and line markers (MTYP)

if [ $n1 -le 2 ]; then
   export LCOL="1;2;1;2;"
   export LTYP="1;1;2;2;"
   export MTYP="1;2;1;2;"
elif [ $n1 -le 3 ]; then
   export LCOL="1;2;4;1;2;4;"
   export LTYP="1;1;1;2;2;2;"
   export MTYP="1;2;3;1;2;3;"
elif [ $n1 -le 4 ]; then
   export LCOL="1;2;4;3;1;2;4;3;"
   export LTYP="1;1;1;1;2;2;2;2;"
   export MTYP="1;2;3;4;1;2;3;4;"
else
   echo Do not try to run combined verification statistics comparing
   echo than 4 runs ... exit
   exit
fi

#-- Set ldiff=1 to force all traces to have different line colors
# export ldiff=1

cp $wrkdir/sfc_fvs.ctl .         # associated vars & exports
TRACES="`head -1 sfc_fvs.ctl`"
sfc_reg=`tail -1 sfc_fvs.ctl`

let num_traces=n1-1
RGN=""
let j=0
while [ $j -le $num_traces ]; do
     RGN="$RGN $sfc_reg"
     let j=j+1
done
export RGN

#=========================================================

export TRACES
export PLVL=SFC

if [ $VARB != VWND ]; then
  export sttyp=SL1L2 stno="1101 1102"       #-- non-vector wind fields
else
  export sttyp=VL1L2 stno="1201 1202"       #-- vector wind speed fields
fi

export PLOTHRS="03/$runhrs/03"

$scrdir/cr8cfg_new.sh
$scrdir/make-fvs_new.sh DIU $CYC

#************************************************************
#-----------------------------------------------------------
# Move files to specific output directory
#-----------------------------------------------------------
#************************************************************

if [ $CYC -eq 99 ]; then
   cyclabl=all
else
   cyclabl=${CYC}Z
fi
mv ${VARB}SFC_rmsecmbDIU*.gif ${plotsdir}/${VARB}SFC_${cyclabl}.gif

echo Start time was $starttime and end time was `date`
