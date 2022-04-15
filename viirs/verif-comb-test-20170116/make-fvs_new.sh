#!/bin/ksh
###set -x
#=========================================================================
#  Script to compute (fvs s) and Create (p) fvs error plots on 1 graph 
#  for bias and rmse or threat score  at multiple forecast hours
#  Jeff McQueen 12/03
#=========================================================================

#==================================================================================================
# USAGE make-fvs.sh  plottype cycle
#
# plottype :
#	DIU :  average stats by forecast hours (x-axis is forecast hour, y-axis is error)
#       UPA :  average stats by upper air pressure levels (x-axis is error, yaxis is pressure)
#       DTS :  Average stats for 1 forecast hour and plot a daily time series error (xaxis is date)
#       FHO :  Average stats by excedence categories (xaxis is exc. cat, Y-axis is error)

# cycle = 00, 06, 12, 18 or 99
# If cycle = 99, all model run cycles are used to compute statistics

#  In FVS.CTL files:
# Vars : VARB, REGION, PLEVEL, STATS and str-end dates  are set in FVS.CTL
#  set VARB = T,VWND, RH, Z, MSLP, APCP/24,APCP/3,smoke,aod,OZON/1, TOtCLD
#  NOTE: To plot different varbs on same plot, uncomment, ryaxis, rstrcs 
#        in the fvs p section (also denoted by MVARB)
#  set region: G236, G245, G216, G218, G104/XXX sub regions, CONUS, etc
#  set Pressure level (P850, P700, P500...)  
#  set stat type (1101, 102..., FHO,RHNT, RHET, RHET5, ESL1L2) 
#==================================================================================================

# LIMITATIONS: 
#       prob histogram plots RHNT, RHET can only use DTS plottype
#       NO prob VSDB files for prcp varb 

# HISTORY: 
# 3/05: added prob mdltype option to plot :
#	RHNT : Ranked histogram of ensemble members nearest truth for SREFENS/EMS
#	RHNT5 : Ranked histogram of ensemble members nearest truth for 5 member subsets
# 	RHET : Ranked histogram of percent of truth lieing w/in ensemble prediction
#	RHET5 : Ranked histogram of percent of truth lieing w/in ensemble prediction for subsets
#	OUTL : Outlier percentage 
#	MRE  : Missing Rate Error 
#	ESL1L2: trace lines for various model subsets (rmse, bias, Statistical consist)
#       Probabilistic Subsets: SREFENS/CTL, SREFENS/ETA, SREFENS/EKF, SREFENS/RSM, SREFENS/WRF SREFENS/ENS
# 
# 9/20/05: East and west regions now also plotted with rhnt and rhet prob histograms
# 10/25/05: Added VARB=totcld...should work with SFC and DTS plots
# 4/2/07  Added C in front of region names to combine regional statistics for one trace
# 12/07:  Now using FVS.CTL or export statements (cr8cfg.sh) to set up user choices
# 07/10:  Added option to compute xaxis label frequency for Daily Time Series (dts)  plots
#========================================================================

machine=`hostname | cut -d. -f1`
echo `date` $machine

if [ ${machine} = 'tempest' ]; then
  export VSDB=/mmb/wd20er/vsdb
  if [ -z "$VSDB_DATA" ];then export VSDB_DATA=/mmb/wd20ps;fi
  TTEXT="1.7/22/5.0/hw|1.2/22/1.2/hw|1.6/22/2.0/hw|1.4/22/1.2/hw"

else  ## ON CCS
  export VSDB=~wx32kb/vsdb
  . /nwprod/gempak/.gempak.profile
# if [ -z "$VSDB_DATA" ];then export VSDB_DATA=/meso/noscrub/wx20er/data/vsdb;fi
  if [ -z "$VSDB_DATA" ];then export VSDB_DATA=/com/verf/prod/vsdb/gridtobs;fi
  TTEXT="1.6/21/1.6/sw|1.2/22/1.2/sw|1.6/22/1.6/sw"
fi
$VSDB/scripts/for_fvs.sh

if [ -z "$npltpg" ];then npltpg=1;fi
if [ -z "$cr8plot" ];then cr8plot=1;fi    # Set to 0 to turn off plotting
dev=psc
# Line Width
 WIDTH=9
mwdt=1.8; mfrq=6
gtype=1

# L_TEXT = tick label
LTEXT="1.2/23/1.0/sw"  #  was "1.5/22/1.5/hw"
#witlin= colors/type/width/values of lines to be drawn
# witlin="1/1;10;1;10;1/1;2;3;2;1/-1;-0.5;0.0;0.5;1"
witlin=1/3/3/0

# line = colr/type/width/lnmarker freq
#   blk;red;blue;grn;magn;cyn
# was this: set -A lcolbs 1 2 4 3 6 7 9 10 11 12 13 14 15 16 17 18
set -A lcolbs 1 2 4 3 1 2 4 3
set -A ltypbs 1 1 1 1 2 2 2 2
set -A mtypbs 1 2 3 4 1 2 3 4
hcolbs="1;2;4;3;6;7;9;10;11;12"

#===========READ IN CONTROL FILES===================================
if [ $# -ge 2 ];then
# SET plottype for "UPA" for vlvl binning or "DIU" for fhour binning
# or "dts" for daily time series  or FHO for threshold error  plotting
  export plottype=$1
  plottrt=`echo $plottype |cut -c 1-3`
  if [ $plottype = DTS ];then plottype=dts;fi
  export cycle=$2

if [ -f FVS.CTL ];then
  echo;echo;echo Computing $PLVL $VARB STAT $STAT statistic for ${traces[*]}  FHR=$PLOTHRSi Cycle $cycle
  echo OPENING FVS.CTL file
  linemax=`cat FVS.CTL |wc -l`
  let iline=1

  while [ $iline -le $linemax ];do
    head -n $iline FVS.CTL >tempfile
    line=`tail -n1 tempfile`
    let k=0
    for word in $line; do
      c1=`echo $word |cut -c 1-1 `
      if [ $c1 != "=" ];then
        case $iline in
         1)  traces[k]=$word;;
         2)  rgn[k]=$word;;
         3)  varb[k]=$word;;
         4)  plotlvl[k]=$word;;
#TEST 12-10  if [ ${plotlvl[k]} = SFC ];then pl[k]=SFC;else pl[k]=UPA;fi;;
         5)  plothrs[k]=$word;;
         6)  stfld[k]=$word;;
         7)  date[k]=$word;;
        esac
        let k=$k+1
      else
        break
      fi
    done
    let iline=$iline+1
  done
  ntrbase=${#traces[*]}
  rgnd=$rgn
  
  appstat=${stfld[0]}
  let k=1
  while [ k -lt ${#stfld[*]} ];do
   stno[k-1]=${stfld[k]}
   let k=k+1
  done
  echo "================== APPSTAT =  $appstat ======================="

  if [ -z "$mdltype" ];then export mdltype=`echo $traces |cut -d/ -f1`; fi
  export strdate=${date[0]}
  export endate=${date[1]}
  strdatep=`echo $strdate | cut -c1-8`
  endatep=`echo $endate | cut -c1-8`

# Set Verification hr for each trace
  export nhrs=${#plothrs[*]}
  typeset -Z4 vhr
  let i=0
  for hr in ${plothrs[*]};do
    if [ $cycle = 99 -o $cycle = all ];then 
      let vhr[i]=99
    else
      let vhr[i]=$cycle+hr
      ((vhr[i]=${vhr[i]}*100))
      while [ ${vhr[i]} -ge 2400 ];do
        let vhr[i]=${vhr[$i]}-2400
      done
#     24 hour precip valid only at 12 UTC 
      if [ ${varb[i]} = "APCP/24" ];then vhr[i]=1200;fi
    fi
    let plothre[i]=99
    let vhre[i]=99
    let i=$i+1
  done

# Set Statistics Labels for corresponding FVS number codes
  linemax=`cat SLBL.CFG |wc -l`
  let iline=0
  while [ $iline -lt $linemax ];do
    head -n $iline SLBL.CFG >tempfile
    line=`tail -n1 tempfile`
    let k=1
      for word in $line; do
        case $k in
         1)  STCFG[iline]=$word;;
         2)  STLBL[iline]=$word;;
         3)  STYLBL[iline]=$word;;
        esac
        let k=k+1
     done
     let iline=iline+1
  done

# Set Region labels for grid2obs region codeS
  linemax=`cat RLBL.CFG |wc -l`
  let iline=0
  while [ $iline -lt $linemax ];do
    head -n $iline RLBL.CFG >tempfile
    line=`tail -n1 tempfile`
    let k=1
      for word in $line; do
        case $k in
         1)  RCFG[iline]=$word;;
         2)  RLBL[iline]=$word;;
        esac
        let k=k+1
     done
     let iline=iline+1
  done

# Set TRACE labels 
  linemax=`cat TLBL.CFG |wc -l`
  let iline=0
  while [ $iline -lt $linemax ];do
    head -n $iline TLBL.CFG >tempfile
    line=`tail -n1 tempfile`
    let k=1
      for word in $line; do
        case $k in
         1)  TCFG[iline]=$word;;
         2)  TLBL[iline]=$word;;
        esac
        let k=k+1
     done
     let iline=iline+1
  done

# Set VARB Fields (yaxis, obsdat, unitlbl)
    linemax=`cat VARB.CFG |wc -l`
    let iline=0
    while [ $iline -lt $linemax ];do
      head -n $iline VARB.CFG >tempfile
      line=`tail -n1 tempfile`
      let k=1
        for word in $line; do
          case $k in
		   1)  VCFG[iline]=$word;;
		   2)  VLVL[iline]=$word;;
		   3)  VBIAS[iline]=$word;;
		   4)  VRMSE[iline]=$word;;
		   5)  VDAT[iline]=$word;;
		   6)  VULBL[iline]=$word;;
		  esac
		  let k=k+1
       done
       let iline=iline+1
     done
else
  echo "FVS.CTL file not found...Program EXiting"
  exit
fi

else
  echo USAGE: "$0 PLOTTYPE Cycle-hour(00,06..)"
  echo 
  echo PLOTTYPE=DIU,UPA,dts,FHO
  exit 
fi

plotdts=0
# Set Xaxis tick mark labels xudlbl
if [ $plottype = dts ];then
  plotdts=1
  xudl=
  xlabel="DATE ($cycle UTC Cycle)"
fi
dtrange=`echo $strdate |cut -c1-8`
dtrange=" $dtrange to `echo $endate |cut -c1-8` "
echo ; echo `date`  >>runfvs.log
#==============================SET FVS PARAMETERS FOR VARIABLES============================
nvarbs=${#varb[*]}-1 
let iv=0
irstr=0

#=====================SET Stat Type & number============================
# For threshold stats, FHO>thresh can be plotted as a daily time series 
# by setting STTYP in parent script (e.g.: STTYP=FHO>75.) 
#=======================================================================
echo STAT $STAT
if [ -z "${sttyp[0]}" ];then set -A sttyp ${STAT};fi 
echo sttyp ${sttyp[*]}

while [ $iv -le $nvarbs ];do    
  hrav=`echo ${varb[iv]} |cut -d/ -f2`
  if [ ${varb[iv]} = PM25AV ];then hrav=24;fi
  if [ ${varb[iv]} = PM25MX ];then hrav=MX;fi
  vrb4=`echo ${varb[iv]} | cut -c 1-4 -`
  vbrt[iv]=`echo ${varb[iv]} | cut -c 1-2 -`
  prrt=`echo ${sttyp[iv]} | cut -c1-2`

# Determine appropriate variable fields from VARB.CFG file
  vl=1 
  nvcfg=${#VCFG[*]}
  yax=;
  for v in ${VCFG[*]};do 
     lfound=0
     yaxbias[iv]=
     yaxrmse[iv]=
     if [ ${varb[iv]} = $v -o ${vrb4} = $v ];then
       if [ ${plotlvl[iv]} = ${VLVL[vl]} -a $prrt != "FH" ];then lfound=1;fi
       if [ ${VLVL[vl]} = FHO ];then lfound=1;fi
       if [ ${VLVL[vl]} = UPA ];then lfound=1;fi
       if [ $lfound -eq 1 ];then
         obsdat[iv]=${VDAT[vl]}
         unitlbl[iv]=${VULBL[vl]}
         yaxbias[iv]=${VBIAS[vl]}
         yaxrmse[iv]=${VRMSE[vl]}
         if [ $plottype = DIU ];then
           yaxbias[iv]=
           yaxrmse[iv]=
         fi
         break
       fi
    fi
    let vl=vl+1
    if [ $vl -gt $nvcfg ];then
      echo  $iv ${varb[iv]} on lvl ${plotlvl[iv]}  not found in VARB.CFG file
      echo  MAKE-FVS ENDING; exit
    fi
  done  #VCFG Search

#====================================================
#  SET FVS PARAMETERS FOR SFC PLOTS
#====================================================
  if [ ${vrb4} = APCP ];then 
    if [ $machine = 'tempest' ];then export VSDB_DATA=/mmb/wd22yl/vsdb ;fi
    obsdat[iv]=CPCANL
    if [ ${rgn[iv]} = G245 ];then
      rlbl="EAST US"
      rgn[iv]="${hd}G212/NEC ${hd}G212/SEC ${hd}G212/APL ${hd}G212/ECA ${hd}G212/MDW ${hd}G212/LMV ${hd}G212/GMC"
    elif [ ${rgn[iv]} = G246 ];then
      rlbl="WEST US"
      rgn[iv]="${hd}G212/NWC ${hd}G212/SWC ${hd}G212/GRB ${hd}G212/WCA ${hd}G212/NMT ${hd}G212/SMT ${hd}G212/SWD ${hd}G212/NPL ${hd}G212/SPL"
    fi
  fi

# SET FVS PARAMS FOR Special non-met varbs
  if [ ${varb[iv]} = smoke ]; then export VSDB_DATA=/export-4/tempest/wd20ch/VSDB/hysplit4;fi
  if [ ${varb[iv]} = AOD ]; then export VSDB_DATA=/export-4/tempest/wd20ch/VSDB/aqm;fi
  if [ ${varb[iv]} = TOTCLD ]; then export VSDB_DATA=/mmb/wd20bz/g2g/vsdb/cloud;fi 

# Allow for more than one variable on a plot  (rstrcs=2/4...)
   if [ -n "${varb[iv+1]}" ];then 
     if [ "${varb[iv+1]}" != "${varb[iv]}" ];then 
       rstrcs="2/4/6/8/10"
       irstr=1
     fi
   fi
#====================================================
# Define FVS Statistics Type and label 
#====================================================
# Probabilistic stat types
  case "$prrt" in
    RH |OU |MR )
#   Define RHNT and RHET stat labels(slbls) since stat numbers are not unique
      export mdltype=prob
      plotdts=1

#     Should this be done later within iplot loop ?
      slblsv=${slbl[iv]} 
      slbl[iv]=${sttyp[iv]}
      if [ -z "$slblsv" ];then slbl[iv]=${sttyp[iv]};else slbl[iv]=${slblsv};fi
      if [ ${sttyp[iv]} = OUTL -o ${sttyp[iv]} = MRE ];then 
        sttyp[iv]=RHET
      fi;;
    ES |EV )
#   Build ESL1L2 Statistics type for ensemble sub-groups
      trmdl=`echo ${traces[iv]}|cut -d/ -f1 `
      esno=`echo ${traces[iv]}|cut -d/ -f2 `

#     Ensemble mean special case
      if [ $esno = ENS ];then esno=21;fi
      trlt=`echo $esno|cut -c 1 `
      case $trlt in
        [A-Z] ) 
          if [ $trlt = R ];then esno=5;fi
          if [ $trlt = W ];then esno=10;elif [ $trlt = E ];then esno=3;fi;;
      esac
      sttyp[iv]="ESL1L2/"${esno}
      if [ ${varb[iv]} = VWND ];then sttyp[iv]="EVL1L2/"${esno};fi;;

    PB )
#   DEFINE PBS_ENS stat label (remove non alpha-numeric characters)
      F1=`echo ${sttyp[iv]} |cut -d: -f1`
      F2=`echo ${sttyp[iv]} |cut -d/ -f2`
      f2c1=`echo $F2 |cut -c1`
      f2c2=`echo $F2 |cut -d. -f1`
      f2c2=`echo $f2c2 |cut -c2-3`
      echo $iv ${sttyp[iv]} F1 $F1 F2 $F2 f2c1 $f2c1 f2c2 $f2c2
      if [ $f2c1 = "<" ];then F2=LT${f2c2}_;else F2=GT${f2c2}_;fi
      slbl[iv]="${F1}${F2}"
      echo SLBL "${slbl[iv]}";;
    FH ) 
#   DEFINE FHO stat type label (remove non alpha-numeric characters, 6/09)
#   FHO stat number 3 equals fraction correct and not obs mean as w/ SL1L2 stat 
      if [ -n "${stno[iv]}" ];then
        if [ ${stno[iv]} -eq 30 ];then stno[iv]=3;fi
      fi
      F1=`echo ${sttyp[iv]} |cut -dO -f1`  
      F2=`echo ${sttyp[iv]} |cut -dO -f2` 
      f2c1=`echo $F2 |cut -c1`           
      f2c2=`echo $F2 |cut -d. -f1`      
      f2c2=`echo $f2c2 |cut -c2-3`     
      if [ "$f2c1" = "<" ];then 
        thresh="LT${f2c2}"
      elif [ "$f2c1" = ">" ];then 
        thresh="GT${f2c2}"
      else
        thresh=;
      fi

#     WARNING: may not be correct...slbl is not set for each variable but for each plot
#     unless appstat=2

      slbl[iv]="${F1}O${F2}"
      echo $iv SLBL ${slbl[iv]};;
   SL )
#     Define SL1L2 Deterministic Stats
      sttyp[iv]=SL1L2
      if [ ${varb[iv]} = VWND ];then sttyp[iv]=VL1L2; fi;; 
  esac

  let iv=$iv+1
  echo $iv ${traces[iv]} ${varb[iv]} ${plotlvl[iv]} STTYP= ${sttyp[iv]} 
   if [ -z "${sttyp[iv]}" ];then sttyp[iv]=${sttyp[iv-1]};fi
   if [ -z "${plotlvl[iv]}" ];then plotlvlvl[iv]=${plotlvl[iv-1]};fi 

done #NVARBS 

#====================================================
# SET XLABEL & FORECAST HOURS or DATES
#====================================================
if [ $plotdts -eq 1 ];then
  typeset -Z6 idate idatee
  typeset -Z2 im id
  
  iys=`echo $strdate |cut -c 3-4`
  ims=`echo $strdate |cut -c 5-6`
  ids=`echo $strdate |cut -c 7-8`
  iye=`echo $endate |cut -c 3-4`
  ime=`echo $endate |cut -c 5-6`
  ide=`echo $endate |cut -c 7-8`
# TO DO: add mn array

#=============Set xaxis labels & frequency===========

# First determine the number of days in time series (nbdys)
# Account for different end year
  if [ $iye -gt $iys ];then 
    ide=$(( 12 - ims + ime + (iye - iys - 1) * 12 ))
  fi
# Account for different end month 
  if [ $ime -gt $ims ];then 
    ide=$((31 - ids + 1 + ide + (ime - ims -1) * 31 ))
  fi
  nbdys=$((ide - ids + 1))
 
# Determine the label frequency 
  let dyfrq=1
  let i=$(( nbdys - 15 ))
  while [ $i -gt 0 ];do 
     dyfrq=$(( dyfrq + 1 )) 
     i=$(( i - 15 ))
  done
  echo DATE LABEL FREQ $nbdys $dyfrq

# Set xax= left/right/increment/lbfq;gdfq;tkfq
  symdh=`echo $strdate |cut -c 1-10`
  eymdh=`echo $endate |cut -c 1-10`
  xax="$symdh:$eymdh:${dyfrq}/1;0;1"

# Set Xaxis tick mark labels xudlbl 
# NOTE: Labeling frequency set above in xaxis variable
  let idate=`echo $strdatep | cut -c 3-8`
  let idatee=`echo $endatep | cut -c 3-8`
  while [ $idate -le $idatee ];do
    iy=`echo $idate |cut -c 1-2`
    im=`echo $idate |cut -c 3-4`
    id=`echo $idate |cut -c 5-6`
    if [ $id -gt 31 ];then id=01;let im=im+1;idate=$iy$im$id; fi
    if [ $im -gt 12 ];then im=01;let iy=iy+1;idate=$iyim$id; fi

    xudl=${xudl}"/"${idate}
    let idate=$idate+$dyfrq
  done
  xudl="`echo $xudl |cut -c 2-${#xudl} -`"
  echo $dyfrq $xudl
fi

if [ $plottype = DIU ];then
  typeset -Z2 bhrs 
  bhrs[0]=`echo $PLOTHRS |cut -d/ -f1`
  fhrb=${bhrs[0]}
  fhre=`echo $PLOTHRS |cut -d/ -f2`
  hrfrq=`echo $PLOTHRS|cut -d/ -f3`

  let fh=${bhrs[0]}
  let i=0
  while [ ${bhrs[i]} -lt $fhre ];do 
    let i=i+1
    let bhrs[i]=${bhrs[i-1]}+$hrfrq
  done
  export binhrs="${bhrs[*]}"
  export nbhrs=${#bhrs[*]}

# Space out xaxis labels if there are too many tick labels
  if [ $nbhrs -gt 30 ];then
      let hrfrq=$((hrfrq * 2))
#     Format: xax= left/right/increment/lbfq;gdfq;tkfq
      xax="$fhrb/$fhre//$hrfrq;;$hrfrq"
  fi
# Set Xaxis tick mark labels xudlb 
# Labeling frequency set above in xaxis variable
  for xl in ${bhrs[*]};do
    xudl=${xudl}"/"${xl}
  done
  xudl="`echo $xudl |cut -c 2-${#xudl} -`"

# Set plot hours for trace.ctl file
  ph=0
  set -A plothrs
  for p in ${traces[*]};do set -A plothrs ${plothrs[*]} $ph;done
  export nhrs=1

# In FVS, Run cycle is set by setting the verification hours in trace.ctl
  let i=0
  typeset -Z4 bvhrs
  if [ $cycle -ge 99 -o $cycle = all ];then
    let bvhrs[$i]=99
  else
    for ihr in ${bhrs[*]};do
      let temp=$cycle+$ihr
      let bvhrs[$i]=$temp*100
      while [ ${bvhrs[$i]} -ge 2400 ];do
        let bvhrs[$i]=${bvhrs[$i]}-2400
      done
      let i=$i+1
    done
  fi
  export binvhrs=${bvhrs[*]}
fi

#===================BEGIN STATISTICS CALCULATIONS FOR EACH FHR ==============

echo Beginning plot: $varb  PLOTTYPE:$plottype  MODELS:$mdltype  LEVEL:$plotlvl >>runfvs.log
echo VSDB_DATA = $VSDB_DATA

# Fill traces array for each forecast hour 
# To put two stats on one graph, set trace number for each graph for one forecast hour
# In this case, Mdl-1 stat1 at fhr1, Mdl-2 stat1 at Fhr-1,Mdl-1 stat2, Mdl-2 stat2 at fhr1 

let ih=0
let itr=0
while [ $ih -lt $nhrs ];do
  traces[ih]=${traces[itr]}
  rgn[ih]=${rgn[itr]}
  if [ "$prrt" = RH ];then sttyp[ih]=`echo ${sttyp[itr]} |cut -c1-4`;fi
  let ih=$ih+1
  let itr=$itr+1
  if [ $itr -gt $ntrbase-1 ];then itr=0;fi
done
echo  traces  ${traces[*]}
echo  rgn  ${rgn[0]}
echo  obsdat  ${obsdat[*]}

# Don't remove previous trace.dat file if replotting only with combined plots
# on one graph (eg: appstat=2)
#MAR 2011 : rm when overlaying any stats on one plot (appstat = 1 or 2)
if [ $appstat -lt 1 ];then rm -f trace.dat;fi

#=====================CREATE TRACE FILE==============================================
  export plotdts
  export plottype=$plottrt
  export VARB=${varb[*]}
  export TRACES=${traces[*]}
  export STTYP=${sttyp[*]}
  export REGION=${rgn[*]}
  export OBSDAT=${obsdat[*]}
  export FHR=${plothrs[*]}
  export FHRE=${plothre[*]}
  export VHR=${vhr[*]}
  export VHRE=${vhre[*]}
  export PLVL=${plotlvl[*]}
  $scrdir/cr8trace_new.sh 

#====================COMPUTE PARTIAL SUMS==============================================

#MAR 2011 : rm when overlaying any stats on one plot (appstat = 1 or 2)
if [ -s trace.dat -a $appstat -ge 1 ];then
  echo "Reusing previous trace.dat file for plotting new stats"
else
  echo COMPUTING STATS for STAT-TYPE: ${sttyp[0]}   FHRs:$FHR  >>runfvs.log
  echo RGN:${rgn[0]} >>runfvs.log
  fvs s >>runfvs.log
fi
if [ ! -s trace.dat ];then
  echo " EMPTY TRACE.DAT ..PROGRAM ENDING"
  exit
fi
#=================== BEGIN PLOTTING ERROR STATS=========================================
if [ $cr8plot -eq 0 ];then exit;fi
let nstats=${#stno[*]}
let ntraces=${#traces[*]}

let istat=0
while [ $istat -lt $nstats ];do  
  stat[istat]=${stno[istat]}    
  echo stat nmbr $istat stat ${stat[istat]}

  computetype=1
  let traceno=1
  let itrskip=0
  lcol="$lcolbs;"
  ltyp="$ltypbs;"
  if [ -n "$LCOL" ];then 
     lcol=$LCOL
     ltyp=$LTYP
     mtyp=$MTYP
  else
     mtyp=$mtypbs
  fi
  tlabel=1

#=========================================================================
#   Fill arrays for each trace number to plot multiple stats on one plot
#   Indices
#   iplot = index for each trace on graph that may include multiple stats
#   itr = index for each trace w/o counting for multipe stat traces
#=========================================================================
  let itr=1 
  let icol=0 
  let ityp=0
  let iplot=0
  let ihr=0
  let irgfn=0 
  if [ $appstat -ge 1 ];then 
#JAN11    if [ $appstat -eq 1 ];then let istat=0;fi
    computetype=2
    nplots=$((ntraces * nstats))
  else
    nplots=$ntraces
  fi
  echo appstat= $appstat NPLOTS $nplots

  while [ $iplot -lt $nplots ];do   

    if [ ${varb[itr-1]} = PM25AV ];then 
      varb[itr-1]=PM25
    elif [ ${varb[itr-1]} = PM25MX ];then 
      varb[itr-1]=PMMX;varb[itr]=PMMX
    elif [ $varb[itr-1]} = VWND ];then
      if [ ${stno[istat]} -ge 1100 -a ${stno[istat]} -lt 1200 ];then
	let stno[istat]=${stno[istat]}+100
     fi
   fi
#=============================================================================
#   Set Line color, types and marker types for each trace
#=============================================================================
    hstclr=0
    if [ $iplot -gt 0 ];then
      mtyp="$mtyp;${mtypbs[$ityp]}"
      if [ -z "$LCOL" ];then
#       Use the following color definition to keep colors the same for 
#       diff. model traces over same regions (eg: prod vs para)
#       eg: ldiff=0
        lcol[iplot]="${lcolbs[icol]};"
        ltyp[iplot]="${ltypbs[icol]};"

#       Use the following Color definition to set different colors for 
#       diff. model comparisons
        if [ $ldiff -eq 1 ];then
          lcol[iplot]="${lcolbs[itr]};"
          ltyp[iplot]="${ltypbs[ihr]};"
        fi 
      fi   

      if [ "$prrt" = PB ];then hstclr="${hstclr};0";fi
    fi #iplot

#====================================================
#   Determine statistics label for each trace
#====================================================

#  Set a stat number for each trace (stat[iplot])
   stat[iplot]=${stno[istat]}

   sl=0 
   for s in ${STCFG[*]};do
     if [ ${stat[iplot]} = $s ];then 
#       Set filename statistical label discriminator
        slbl[iplot]=${STLBL[sl+1]}
        stylbl[iplot]=${STYLBL[sl+1]}

#      left (yax) and right (ryaxis) set if plotting two different variables 	   
       if [ $itr -le 1 ];then 
         case ${stat[iplot]} in
         1001| 1101| 1201 )
            yax=${yaxbias[itr-1]}
            ryaxis=${yaxbias[itr]};;
         1002| 1003| 1102| 1202 )
           yax=${yaxrmse[itr-1]}
           ryaxis=${yaxrmse[itr]};;
         1004 |1021 )
#          FAR plots
           yax=" 0.0/0.4/.1/1;1;;"
           ryaxis=$yax;;
         1007 )
#          POD plots
           yax=" 0.0/1.02/.1/1;1;; "
           ryaxis=$yax;;
         1034 )
#          NWS/HQ hit rate plots
           yax=" 0.7/1.02/.1/1;1"
           ryaxis=$yax;;
         esac
         if [ $irstr -eq 0 ];then ryaxis=;fi
        fi 

#       Filename label includes stat type (eg. hit)
#       and threshold (eg. GT75)
        if [ "$prrt" = FH ];then slbl[iplot]=${slbl[iplot]}${thresh};fi

        ylabel=${slbl[iplot]}
        echo iplot $iplot slbl ${slbl[iplot]} $ylabel
        if [ "$iplot" -gt 0 ];then 
          if [ ${stat[iplot]} -ne ${stat[$iplot-1]} ];then 
            icmb=1
            yold=$ylabel
            ylabel=" $yold and ${stylbl[iplot]} "
          else
            icmb=0
            ylabel=${stylbl[iplot]}
          fi
        fi
        break
      fi  #STCFG
      if [ $irstr = 1 ];then yrlabel="${ylabel} $bias";fi
      let sl=sl+1
    done  #STCFG Loop to find and define slbl & yaxis

    if [ -z "${slbl[iplot]}" ];then slbl[iplot]=${slbl[iplot-1]};fi
    echo istat $istat iplot $iplot slbl $ylabel

#====================================================
#   Determine region label for each trace
#====================================================
#T909  Multiple varb labels not working so changed index from itr-1 to iplot

    rgo=$rgfn
    rgb=`echo ${rgn[iplot]}|cut -d/ -f1 `
    rge=`echo ${rgn[iplot]}|cut -d/ -f2 `
    if [ -z "$rgb" -o -z "$rge" ];then
      rgb=`echo ${rgn[itr-1]}|cut -d/ -f1 `
      rge=`echo ${rgn[itr-1]}|cut -d/ -f2 `
    fi
    if [ $rgb = G104 ];then 
      rgfn=$rge
    else
      rgfn=$rgb
    fi 
    if [ $iplot -eq 0 ];then rgo=$rgfn;fi
    rl=1 
    for r in ${RCFG[*]};do
      if [ $rgfn = $r ];then 
        rlbl=${RLBL[rl]}
        break
      fi
      let rl=rl+1
    done
#   Test if only using one rgn for all traces, then
#   do not use special rgfn labels to define plot file name below
    if [ $rgfn != $rgo ];then irgfn=1;fi

#====================================================
#   Set forecast hour and pressure level labels
#====================================================
    if [ $plottype = DIU ];then flbl=;else flbl="FHR: ${plothrs[itr-1]}";fi
    if [ $plottype = UPA ];then plbl=;else flbl="LVL: ${plotlvl[itr-1]}";fi

#====================================================
#   Create Trace Labels
#====================================================
    tl=1 
    tlbl=`echo ${traces[itr-1]} |cut -d/ -f1`
    for t in ${TCFG[*]};do
      if [ $tlbl = $t ];then 
        tlbl=${TLBL[tl]}
        break
      fi
      let tl=tl+1
    done
#   Special case of SREF members, include the full trace name
    case $prrt in
      RH |OU |MR |ES |EV )
        tlbl="${traces[iplot]}" ;;
    esac
    if [ ${stat[iplot]} -eq 3 ];then tlbl="Observed mean ";fi

#Feb11 trace[iplot]="${tlbl}  ${varb[iplot]} $plbl  over ${rlbl}  $flbl  ${slbl[iplot]}" 
    trace[iplot]=" $tlbl  $rlbl ${slbl[iplot]} "
    if [ $irgfn -eq 0 ];then trace[iplot]="${tlbl} ";fi 

#   Set colors and labels when overlaying traces on same plot
    if [ $appstat -ge 1 ];then
      if [ $tlabel = 0 ];then trace[iplot]=;fi
#Feb11 trace[iplot]=" ${tlbl} VARB: ${varb[itr-1]} $plbl  RGN: ${rlbl}  $flbl  STAT: ${stylbl[iplot]}"
      trace[iplot]="${tlbl}  $rlbl  ${stylbl[iplot]} "  
      if [ $irgfn -eq 0 ];then trace[iplot]=" ${tlbl} ${stylbl[iplot]} ";fi  

#     Special case to force only one observation trace to be plotted
      if [ $iplot -ge 1 ];then
        if [ ${stat[iplot]} -eq 3 ];then 
#         Set trace #, line characteristics for obs mean
          let iplot=$iplot-1
          let nplots=$nplots-1
          let ntracess=$ntraces-1
          ltyp[iplot]="$((traceno[iplot]+1));"
          ltyp[0]="${traceno[0]};"
        elif [ ${stat[iplot]} -eq 2 ];then 
#         Set trace #, line characteristics for forecast mean
          let traceno[iplot]=$iplot
          ltyp[iplot]="$((traceno[iplot]+1));"
          ltyp[0]="${traceno[0]};"
         else
          let traceno[iplot]=$itr
          ltyp[iplot]="${ltypbs[istat]};"
        fi
        lcol[iplot]="${traceno[iplot]};"
        stat[iplot]=${stno[istat]}
      fi
    fi 
    trace[iplot]="${trace[iplot]} + "
    echo $nplots iplot $iplot stat ${stat[iplot]} tno ${traceno[iplot]}  lcol ${lcol[iplot]}  ltyp ${ltyp[iplot]}
    let itrm1=$itr-1
  
    if [ "${plothrs[$itr]}" -ne "${plothrs[$itr-1]}" ];then
      let ihr=$ihr+1
      if [ $appstat -eq 0 ];then itr=0;fi
    fi
#==============================================================================
#   Reset icol to keep line color the same for different model traces
#   EG:For comparing an operational vs parallel run (same color but dashed)
#   SOLID:mdl-rgn1(Blk) mdl-rgn2(red)  DASHED:mdlpar-rgn1(blk) mdlpar-rgn2(red)
#==============================================================================
    if [ $itr -lt $ntraces -a $itr -gt 0 -a $ntraces -gt 2 ];then 
      thdrc=`echo ${traces[itr]} |cut -d/ -f1`
      thdrb=`echo ${traces[itr-1]} |cut -d/ -f1`
      if [ ${thdrc} != ${thdrb} ];then 
        let icol=0
        let ityp=$ityp+1
      else
        let icol=$icol+1
      fi
    fi

    let itr=$itr+1
    let iplot=$iplot+1
    if [ $itr -gt $ntraces ];then 
      if [ $appstat -ge 1 ];then
        let istat=$istat+1
        if [ $istat -gt $nstats-1 ];then
          istat=0
          tlabel=0
        fi
      fi
      ihr=0
      itr=1
    fi
  done  #iplot loop
  
#1-10 : Ensured that iplot index not out of bounds (gt nplots-1)
#       enabling slbl to be set correctly for file name creation below
  if [ $appstat -eq 1 ];then 
   slbl[iplot-1]=${slbl[iplot-1]}cmb
  elif [ $appstat -eq 2 ];then 
   slbl[iplot-1]=OvsF
 fi

  if [ -z "${stat[istat]}" ];then exit;fi

# Define line color and type for each trace either from above algorithm
# OR from parent script with LCOL and LTYP 
  line="${lcol[*]}/${ltyp[*]}/${WIDTH}/"
  marker="${lcol[*]}/${mtyp}/${mwdt}/${mfrq}/"
    
  echo CREATING PLOT FOR $varb $istat STAT= ${stat[istat]} >>runfvs.log
  echo CREATING $varb PLOT FOR $istat STAT nmb = ${stat[istat]} ${slbl[iplot-1]}


#=============================================================
# Set plotting fields for special probabilistic stat types
#=============================================================
  stroot=`echo ${stat[istat]} |cut -c1-2`
  stend=`echo ${stat[istat]} |cut -c3-4`
  if [ $mdltype = prob ];then
    case "$prrt" in
    RH |OU |MR )
      yax="0/0.15/0.05/1;2;;"
      xax=;
      xudl=;;

#   Consistency or spread plots
    ES |EV )
      if [ $stend -eq 07 -o $stend -eq 16 ];then yax=;fi;;
    esac 

#   Ranked Histograms
    if [ ${stroot} -eq 16 ]; then 
      yax="0/0.70/0.05/1;2;;"
      hstclr=${hcolbs}
      line="${hcolbs}/1/${WIDTH}/"

#     Equally-likely Ranked Histograms
      if [ ${stat[istat]} -eq 1601 ];then 
        stat[istat]=1600
        yax="0/0.30/0.05/1;2;;"
      fi
#     For MRE missing Rate Error, use lines and daily time series
      if [ ${stat[istat]} -eq 1606 ];then hstclr=;fi
      marker= 
    fi
#=========================================================
#   Set axis, labels for attribute reliability diagrams
#=========================================================
    if [ ${stat[istat]} -eq 1360 ];then 
      gtype=6
      hstclr="${hstclr} ; ${lcol[*]}"
      yax="-.02/1.02/.1"
      xax="-.03/1.03/.05/2"
      xlabel="FORECAST PROBABILITY"
      ylabel="OBSERVED FREQUENCY"
      ryaxis="-.02/1.02/.1/1;0;0"
      yrlbel="FREQUENCY OF FORECAST USE (HISTOGRAM)/2"
    fi
  fi    #mdltype

#===================== SET PLOT TITLE===============================
  REV=NO
  phrlabel=$plothrs
  if [ ${plothrs[0]} -ne ${plothrs[$nhrs-1]} ];then
    phrlabel="${plothrs[0]}-${plothrs[$nhrs-1]}"
  fi  
  cyclbl="(${cycle}Z cycles)"
  if [ $cycle = 99 -o $cycle = all ];then 
     cyclbl="(all cycles)"
  fi

  if [ $plottype = UPA ];then 
#   REV = YES so ylabel is actually horizontal axis label
    REV=YES; FHRCH=
    if [ $phrlabel = 99 ]; then
       timelabel=All
    else
       timelabel=$phrlabel
    fi
    title="$timelabel h $varb over $rlbl from $strdatep to $endatep"
    xlabel="Pressure (mb)"
    ylabel="Bias and RMSE $cyclbl"   #-- Override values defined above
  fi

  if [ $plotdts -eq 1 ];then
    FHRCH=
    titlert="$plotlvl $varb $ylabel Daily Time Series \ from $strdatep to $endatep"
    if [ $vrb4 = OZMX ];then
      titlert="CMAQ $hrav Hr Daily Max Ozone $ylabel $thresh \ "
    elif [ $vrb4 = OZON ];then
      titlert="CMAQ $hrav Hr Avg Ozone $ylabel $thresh \ "
    fi
    title=" $titlert Averaged from Fhr: $plothrs to $plothre "
  fi

  if [ $plottype = DIU ]; then 
    FHRCH=DIU
    phrlabel=
    FHR=
    title="$plotlvl $varb $ylabel \ averaged by fcst hrs from $strdatep to $endatep"
    if [ $stat -eq 2 -o $stat -eq 3 ];then
      title="$plotlvl $varb \ averaged by fcst hrs from $strdatep to $endatep"
    fi
    xlabel="Forecast Hour $cyclbl"
#-- Added 2 lines below to override values defined above
    title="Surface $varb over $rlbl from $strdatep to $endatep"
    ylabel="Bias and RMSE"
  fi

  if [ $plottype = FHO ];then 
    FHRCH=FHO
#    titlert="$plotlvl $varb $ylabel averaged by Threshold \ from $strdatep to $endatep"
#    title=" $titlert for $phrlabel Hour Forecasts "
#    xlabel=" $varb Threshold $unitlbl "
    let tbegin=phrlabel-24
    title="$tbegin - $phrlabel h QPF over $rgnd for $strdatep to $endatep"
    xlabel="24-h precipitation in inches $cyclbl"
  fi

#=======================================================================
# SET OUTPUT PLOT FILE NAME    
#==================+++++++++++++++++++==================================
  if [ "$rgfn" = G236 -o "$rgfn" = G212 -o "$rgfn" = G218 ];then rgfn=;fi
  if [ $vrb4 = APCP ];then varb=APCP;fi

  flname=${varb}${plotlvl}_${slbl[iplot-1]}${FHRCH}${phrlabel}_${mdltype}${rgfn}

  if [ $vbrt = "OZ" -o $vbrt = "PM" ];then 

#   Special file name region labels if plotting different regions on one plot
    echo $appstat RGFN $rgfn irgfn $irgfn

#  Modified for experiments

    if [ $irgfn -eq 0 ];then
     case $rgfn in 
#TEST      NEC | SEC ) rgfn=EC;;
#      ECA | APL ) rgfn=AP;;
#      NWC | SWC ) rgfn=WC;;
#      LMV | MDW ) rgfn=MW;;
#      NPL | SPL ) rgfn=PL;;
#      GMC | SWD ) rgfn=GM;;
#      G245 | G246 ) rgfn=EW;;
      G245 ) rgfn=ES;;
      G247 ) rgfn=CN;;
      G246 ) rgfn=WS;;
      G148 | G142 | G236 ) rgfn=CS;;
      G212 | G218 | G221 ) rgfn=NA;;
      G250 ) rgfn=HI;;
     esac
    fi
    flname=$vrb4-$hrav${plotlvl}_${slbl[iplot-1]}${FHRCH}${phrlabel}_${mdltype}${rgfn}
  fi
  echo OUTPUT FILENAME $flname DEVICE: $dev  $trace
  echo PLOTTYPE $plottype STAT ${stat[istat]}  YAX $yax RYAXIS $ryaxis

  rm -f $flname.psc
  rm -f psc.plt
  TNO=${stat[istat]}
  SNO=
  if [ $appstat -ge 1 ];then
    TNO="${traceno[*]}"
    SNO="${stat[*]}"
  fi
  echo TNO="${traceno[*]}" to plot
  echo lcol="${lcol[*]}"
  echo ltyp="${ltyp[*]}"
  echo SNO="${stno[*]}"
#=========================================================================
# Plotting Key Follows:               
# 1                        !Plot #
# 1                        !1=Graphical Display
# 1                        !Computational code for all plots =1, =2 mult stats on one plot
# 1                        !Trace number(s)
# 1202                     !Stat type(s)
# 0                        !LAG
# 0                        !smoother
# line = colr/type/width/lnmarker freq
# multi plot system 
# NOTE: Do not add returns in input or plot will fail
#==========================================================================
  fvs p <<ENDFVS >> runfvsp.log 2>&1 
1
$gtype
$computetype
$TNO
$SNO
0  
0 
REVERS=$REV
line=$line
marker=$marker
l_text=$LTEXT
t_text=$TTEXT
yaxis=$yax
trace1=${trace[0]}
trace2=${trace[1]}
trace3=${trace[2]}
trace4=${trace[3]}
trace5=${trace[4]}
trace6=${trace[5]}
trace7=${trace[6]}
trace8=${trace[7]}
trace9=${trace[8]}
trace10=${trace[9]}
DEVICE=$dev|VSDB
WITLIN=$witlin
hstclr=$hstclr
panel=0
xudlbl=$xudl
xaxis=$xax
xlabel=$xlabel
ylabel=$ylabel
#MPLOT rstrcs=$rstrcs
#MPLOT ryaxis=$ryaxis
yrlabel=$yrlabel
title=$title
l
r
  cp $flname.$dev
0
0
0
ENDFVS

gpend

#====================CONVERT PLOT TO OUTPUT GRAPHIC GIF AND FTP=====================
  if [ -f $flname.$dev ];then
    echo "FVS PLOT complete for $flname";echo;echo;echo
  else
    echo "FVS PLOT Failed...plot file $flname not created";echo;echo;echo;
    exit
  fi

# Convert to GIF for web page
  convert -rotate 90 $flname.$dev $flname.gif
  rm -f $flname.$dev VSDB

# Combine all member plots onto 1 page
  if [ $npltpg -gt 1 ];then
    mv $flname.gif  ${flname}${ipltpg}.gif
    if [ $ipltpg -eq 3 ];then 
      montage -geometry 600x600 ${flname}1.gif ${flname}2.gif ${flname}3.gif $flname.gif
    fi 
  fi
  if [ "$iftp" -eq 1 ];then 
    scp -p $flname.gif wd22jm@rzdm:$rzdmdir
    if [ -f $flname${ipltpg}.gif ];then scp -p $flname${ipltpg}.gif wd22jm@rzdm:$rzdmdir;fi
  fi

  let istat=$istat+1
  if [ $appstat -ge 1 ];then exit;fi
done                                #statno loop

if [ $appstat -ge 2 ];then rm trace.dat;fi
exit
