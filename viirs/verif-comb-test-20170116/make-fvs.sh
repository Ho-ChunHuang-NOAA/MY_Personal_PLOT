#!/bin/ksh

#=========================================================================
#  Script to compute (fvs s) and Create (p) fvs error plots on 1 graph 
#  for bias and rmse or threat score  at multiple forecast hours
#  Jeff McQueen 12/03
#=========================================================================

#==================================================================================================
# USAGE make-fvs.sh  plottype cycle
# plottype :
#	DIU :  average stats by forecast hours (x-axis is forecast hour, y-axis is error)
#       UPA :  average stats by upper air pressure levels (x-axis is error, yaxis is pressure)
#       DTS :  Average stats for 1 forecast hour and plot a daily time series error (xaxis is date)
#       FHO :  Average stats by excedence categories (xaxis is exc. cat, Y-axis is error)
#	       Currently only prcp and totcld have FHO stats

#  In FVS.CTL files:
# Vars : VARB, REGION, PLEVEL, STATS and str-end dates  are set in FVS.CTL
#  set VARB = T,VWND, RH, Z, MSLP, APCP/24,APCP/3,smoke,aod,OZON/1, TOTCLD
#  set region: G236, G245, G216, G218, G104/XXX sub regions, etc
#  set Pressure level (P850, P700, P500...)  
#  set stat type (1101, 1102..., FHO,RHNT, RHET, RHET5, ESL1L2) 
#==================================================================================================

# LIMITATIONS: 
#       prob histogram plots RHNT, RHET can only use DTS plottype
#       NO prob VSDB files for prcp varb or HREF

# HISTORY: 
# 3/05: added prob mdltype option to plot :
#	RHNT : Ranked histogram of ensemble members nearest truth for SREF/21
#	RHNT5 : Ranked histogram of ensemble members nearest truth for 5 member subsets
# 	RHET : Ranked histogram of percent of truth lieing w/in ensemble prediction
#	RHET5 : Ranked histogram of percent of truth lieing w/in ensemble prediction for subsets
#	OUTL : Outlier percentage 
#	MRE  : Missing Rate Error 
#	ESL1L2: trace lines for various model subsets (rmse, bias, Statistical consist)
#       Probabilistic Subsets are :  SREF/CTL, SREF/ETA, SREF/EKF, SREF/RSM, SREF/WRF, SREF/21
# 
# 9/20/05: East and west regions now also plotted with rhnt and rhet prob histograms
# 10/25/05 : Added VARB=totcld....should work with SFC and DTS plots
# 4/2/07:  Added C in front of region names to combine regional statistics fro one trace
# 12/07:  Now using FVS.CTL or export statements to set up user choices
#========================================================================

#-- Next 2 lines are for debugging; comment out when done
# set -x
echo Entering make-fvs.sh

machine=`hostname | cut -d'.' -f1`

if [ ${machine} = 'tempest' ]; then
 echo $machine
export VSDB=/mmb/wd20er/vsdb
if [ -z "$VSDB_DATA" ];then export VSDB_DATA=/mmb/wd20ps;fi

# TEST   tEST   TEST
#export VSDB_DATA=`pwd`

. $VSDB/scripts/for_fvs.sh

else  ## ON DEW OR MIST
  export VSDB=/u/wx20bf/vsdb
  . /nwprod/gempak/.gempak.profile
  if [ -z "$VSDB_DATA" ];then export VSDB_DATA=/meso/noscrub/wx20er/data/vsdb;fi
fi
export DDAPP=$VSDB/ddapp
export VSDB_TBL=$VSDB/tables
export VSDB_HLP=$VSDB/help
export VSDB_SCRIPTS=$VSDB/scripts/

if [ -z "$npltpg" ];then npltpg=1;fi
if [ -z "$iplot" ];then iplot=1;fi    # Set to 0 to turn off plotting
dev=psc
WIDTH=9
if [ $dev = GIF ];then WIDTH=3;fi
mwdt=1.8; mfrq=6

#   T_TEXT = title | trace legend | XY axis label
#   T_TEXT = size/font/width/hw flag
#   L_TEXT = tick label
TTEXT="1.6/21/1.6/sw|1.2/22/1.2/sw|1.6/22/1.6/sw"
LTEXT="1.2/23/1.0/sw"
witlin=1/3/3/0



# line = colr/type/width/lnmarker freq
#   blk;red;blue;grn;magn;cyn;magn;
set -A lcolbs 1 2 4 3 7 5 6 9 10 11 12 13 14 15 16 17 18
set -A ltypbs 1 2 5 6 10 4 7 8
set -A mtypbs 1 2 3 4 5 6 12 14


#===========READ IN CONTROL FILES===================================
if [ $# -ge 2 ];then
# SET plottype for "UPA" for vlvl binning or "DIU" for fhour binning
# or "dts" for daily time series  or FHO for threshold error  plotting
  export plottype=$1
  if [ $plottype = DTS ];then plottype=dts;fi
  export cycle=$2
  if [ -z "$mdltype" ];then export mdltype=mean; fi

if [ -f FVS.CTL ];then
  echo;echo Computing $PLVL $VARB STAT $STAT statistic for ${traces[*]} for Region $RGN FHR=$PLOTHRS
  echo OPENING FVS.CTL file
  linemax=`cat FVS.CTL |wc -l`
  let iline=1

  while [ $iline -le $linemax ];do
    head -n $iline FVS.CTL >tempfile
    line=`tail -n1 tempfile`
    let k=0
    for word in $line; do
      c1=`echo $word |cut -c1-1 `
      if [ $c1 != "=" ];then
        case $iline in
         1)  traces[k]=$word;;
         2)  rgn[k]=$word;;
         3)  varb[k]=$word;;
         4)  plotlvl[k]=$word
             if [ ${plotlvl[k]} = SFC ];then
               obsdat[k]=ONLYSF
             elif [ ${plotlvl[k]} = UPA ]; then
               obsdat[k]=ADPUPA
             elif [ ${plotlvl[k]} = ANYAIR ]; then
               obsdat[k]=ANYAIR
             elif [ ${plotlvl[k]} = AFWA ]; then
               obsdat[k]=AFWA
               plotlvl[k]=ATMOS
               plabel=afwa
             elif [ ${plotlvl[k]} = CLAVR ]; then
               obsdat[k]=CLAVR
               plotlvl[k]=ATMOS
               plabel=clavr
             elif [ ${plotlvl[k]} = H2 ] || [ ${plotlvl[k]} = H10 ]; then
               obsdat[k]=RTMA
             else
               echo Unknown value for ${plotlvl[k]} ... exit 1
               exit 1
             fi
#old             if [ ${varb[k]} = "APCP/24" ];then obsdat[k]=MC_PCP;fi;;
             if [ ${varb[k]} = "APCP/24" ];then obsdat[k]=CPCANL;fi;;
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

  export strdate=${date[0]}
  export endate=${date[1]}
  strdatep=`echo $strdate | cut -c1-8`
  endatep=`echo $endate | cut -c1-8`
  strdatet=`echo $strdate | cut -c1-10`
  endatet=`echo $endate | cut -c1-10`

# Set Verification hr for each trace
  export nhrs=${#plothrs[*]}
  typeset -Z4 vhr
  let i=0
  for hr in ${plothrs[*]};do
    let vhr[i]=$cycle+hr
    ((vhr[i]=${vhr[i]}*100))
    while [ ${vhr[i]} -ge 2400 ];do
      let vhr[i]=${vhr[$i]}-2400
    done
    let plothre[i]=99
    let vhre[i]=99
    let i=$i+1
  done

# Set Statistics Labels for FVS number codes
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
if [ $plottype = dts ];then
  plotdts=1
  xudl=
  xlabel="DATE ($cycle UTC Cycle)"
fi
dtrange=`echo $strdate |cut -c1-8`
dtrange=" $dtrange to `echo $endate |cut -c1-8` "
echo `date` In $0; echo `date` In $0 >>fvs.log

#==============================SET FVS PARAMETERS FOR VARIABLES==================================
nvarbs=${#varb[*]}
let iv=0
while [ $iv -lt $nvarbs ];do    
  vrb4=`echo ${varb[iv]} | cut -c 1-4 -`
  vbrt=`echo ${varb[iv]} | cut -c 1-2 -`
  if [ -z "${sttyp[iv]}" ];then
    if [ ${varb[iv]} = VWND ];then sttyp[iv]=VL1L2; else sttyp[iv]=SL1L2;fi
  fi
  prrt=`echo ${sttyp[iv]} |cut -c1-2`
  if [ $plottype = FHO ];then 
    echo
    echo iv, vrb4 = $iv $vrb4 
    echo varb = ${varb[*]}
    echo prrt = $prrt
    echo sttyp = ${sttyp[*]}
    echo
    if [ ${varb[iv]} = TOTCLD  -o $vrb4 = APCP -o ${varb[iv]} = smoke -o ${varb[iv]} = AOD -o $vbrt = OZ -o $prrt = PB ]; then 
       echo " ${varb[iv]} OK:  prcp, totcld, smoke, ozone & aod varbs have FHO VSDB files "
     else
       echo "Illegal entry" ${varb[iv]} $plottype;exit
    fi
  fi 

#  SET FVS PARAMETERS FOR SFC PLOTS
  if [ ${plotlvl[iv]}  = SFC ];then
    rltr[0]=C;rltr[1]=D;rltr[2]=E;rltr[3]=F;rltr[4]=G;rltr[5]=H
    hd=${rltr[iv]}
    if [ ${rgn[iv]} = G245 ];then
      rgn[iv]="${hd}G104/NEC ${hd}G104/SEC ${hd}G104/APL ${hd}G104/ECA ${hd}G104/MDW ${hd}G104/LMV ${hd}G104/GMC"
    elif [ ${rgn[iv]} = G246 ];then
      rgn[iv]="${hd}G104/NWC ${hd}G104/SWC ${hd}G104/GRB ${hd}G104/WCA ${hd}G104/NMT ${hd}G104/SMT ${hd}G104/SWD ${hd}G104/NPL ${hd}G104/SPL"
    fi
  fi
  if [ ${vrb4} = APCP ];then 
    if [ $machine = 'tempest' ];then export VSDB_DATA=/mmb/wd22yl/vsdb ;fi
    unitlbl="inches"
    witlin=1/3/3/1
    if [ ${rgn[iv]} = G245 ];then
     rgn[iv]="CG212/NEC CG212/SEC CG212/APL CG212/ECA CG212/MDW CG212/LMV CG212/GMC"
    elif [ ${rgn[iv]} = G246 ];then
     rgn[iv]="DG212/NWC DG212/SWC DG212/GRB DG212/WCA DG212/NMT DG212/SMT DG212/SWD DG212/NPL DG212/SPL";fi
  fi
# SET FVS PARAMS FOR Special non-met varbs
  if [ ${varb[iv]} = smoke ];then 
    export VSDB_DATA=/export-4/tempest/wd20ch/VSDB/hysplit4
    obsdat[iv]="NESDIS/255"
    unitlbl="ug-m3"
  elif [ ${varb[iv]} = AOD ];then
    export VSDB_DATA=/export-4/tempest/wd20ch/VSDB/aqm
    obsdat[iv]="NESDIS/148"
#   elif [ ${varb[iv]} = TOTCLD ];then
#     export VSDB_DATA=/mmb/wd20bz/g2g/vsdb/cloud
#     obsdat[iv]=AFWA 
  fi
  if [ $vbrt = OZ ];then
    obsdat[iv]=AIRNOW
    if [ $vrb4 = OZMX ];then export VSDB_DATA=~wd20mat/fvs/data_nco/vsdb/aqm_max;fi
  fi

# For RH probabilistic plots, reset slbl since only STLBL (RHNT, RHET) is unique 
  if [ "$prrt" = "RH" -o "$prrt" = "ES" ];then
    export mdltype=prob
    if [ $prrt = RH ];then 
      plotdts=1
      slbl=${sttyp[iv]}
    elif [ $prrt = ES ];then
      esno=`echo ${traces[iv]}|cut -d/ -f2 `
      trlt=`echo $esno|cut -c 1 `
      case $trlt in
        [A-Z] ) if [ $esno = WRF ];then esno=6;else esno=5;fi;;
      esac
      sttyp[iv]="ESL1L2/"${esno}
      if [ ${varb[iv]} = VWND ];then sttyp[iv]="EVL1L2/"${esno};fi
    elif [ "$prrt" = PB ];then
      slbl=${sttyp[iv]}
    fi
  fi  
  if [ -z "${sttyp[0]}" ];then
    if [ ${varb[iv]} = VWND ];then sttyp[iv]=VL1L2; else sttyp[iv]=SL1L2;fi
  fi
  if [ $plottype = FHO -a $prrt != PB ];then sttyp[iv]=FHO;fi
  echo $iv STTYP= $sttyp slbl = $slbl
  let iv=$iv+1
  if [ -z "${sttyp[iv]}" ];then sttyp[iv]=${sttyp[iv-1]};fi
done

# Set forecast hours for Diurnal plots
if [ $plottype = DIU ];then
  typeset -Z2 bhrs 
  bhrs[0]=`echo $PLOTHRS |cut -d/ -f1`
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
  ph=0
  set -A plothrs
  for p in ${traces[*]};do set -A plothrs ${plothrs[*]} $ph;done
  export nhrs=1

# In FVS, Run cycle is set by setting the verification hours
  let i=0
  typeset -Z4 bvhrs
  for ihr in ${bhrs[*]};do
    let temp=$cycle+$ihr
    let bvhrs[$i]=$temp*100
    while [ ${bvhrs[$i]} -ge 2400 ];do
      let bvhrs[$i]=${bvhrs[$i]}-2400
    done
    let i=$i+1
  done
  export binvhrs=${bvhrs[*]}
  for xl in ${bhrs[*]};do
   xudl=${xudl}"/"${xl}
  done
  xudl="`echo $xudl |cut -c 2-${#xudl} -`"
fi

#===================SET AXES============================================ 
if [ $plottype = DIU -o $plotlvl = SFC ];then
# yax = left/right/increment/labelfrq;gridfreq;tickfrq
  yaxrmseVWND="0/6/0.5/1;4;;"
  yaxbiasVWND="-5/5/1.0/1;2;;"
else
  if [ $mdltype != prob -o $plottype = UPA ];then
    yaxrmseVWND="0/20/2./1;4;;"
    yaxbiasVWND="-6/6/2.0/1;2;;"
  fi
fi
yaxrmseT="0/5/0.5/1;4;;"
yaxrmseRH="10/40/5/1;4;;"
yaxrmseSLP="0/6/0.5/1;4;;"
yaxrmseZ="10/75/5./1;4;;"
yaxrmseTOTCLD="30/60/5./1;2;;"
# Bias Axes
yaxbiasT="-5/5/0.5/1;4;;"
yaxbiasRH="-10/40/5.0/1;4;;"
yaxbiasZ="-20/75/5.0/1;4;;"
yaxbiasSLP="-6/6/0.5/1;4;;"
yaxbiasTOTCLD="-5/60/5/1;2;;"

if [ $plottype = FHO ];then 
  if [ $vrb4 = "APCP" ];then
    yaxrmse="0/.7/0.1/1;4;;"
    yaxbias="0/2/0.25/1;2;;"
  elif [ $varb = "TOTCLD" ];then
    yaxrmse="0/.4/0.1/1;1;;"
    yaxbias="0/2/0.25/1;2;;"
  fi 
else
  tempvar=$(echo yaxrmse$varb)
  yaxrmse=$(eval echo \$$tempvar)
  tempvar=$(echo yaxbias$varb)
  yaxbias=$(eval echo \$$tempvar)
fi
if [ $vbrt = OZ ];then
  yax=
  yaxbias="-15/26/05/1;1;;"
  yaxrmse="0/25/8/1;1;5;"
fi

#===================BEGIN STATISTICS CALCULATIONS FOR EACH FHR ==============

echo Beginning plot of $varb error for $plottype plottype and $mdltype VSDB files and $plotlvl level>>fvs.log
echo VSDB_DATA = $VSDB_DATA

# Fill traces array for each forecast hour 
#  To put two stats on one graph, set trace number to use for the graph for one forecast hour
#  In this case, Mdl-1 stat1 at fhr1, Mdl-2 stat1 at Fhr-1,Mdl-1 stat2, Mdl-2 stat2 at fhr1
let ih=0
let itr=0
while [ $ih -lt $nhrs ];do
  traces[$ih]=${traces[$itr]}
  rgn[$ih]=${rgn[$itr]}
  if [ "$prrt" = RH ];then sttyp[ih]=`echo ${sttyp[itr]} |cut -c1-4`;fi
  let ih=$ih+1
  let itr=$itr+1
  if [ $itr -gt $ntrbase-1 ];then itr=0;fi
done
echo  traces  ${traces[*]}
echo  rgn  ${rgn[*]}
echo  obsdat  ${obsdat[*]}
rm -f trace.ctl
rm -f trace.dat

#=====================CREATE TRACE FILE==============================================
  export plotdts
  export plottype
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
  $scrdir/cr8trace.sh 

#====================COMPUTE PARTIAL SUMS==============================================
  echo Computing STAT $STTYP for $varb with $plottype for $FHR forecast hr and $rgn region>>fvs.log

  fvs s 

  if [ ! -s trace.dat ];then
    echo " EMPTY TRACE.DAT ..PROGRAM ENDING"
    exit
  fi

#=================== PLOT ERROR STATS===========================
    if [ $iplot -eq 0 ];then exit;fi
    let nstats=${#stno[*]}
    let ntraces=${#traces[*]}

    let istat=0
    while [ $istat -lt $nstats ] ;do  
      computetype=1
      traceno=1
      tlabel=1
      stat[$istat]=${stno[istat]}    
      echo STAT $istat ${stat[istat]}

#     Fill arrays for each trace number to plot multiple stats on one plot
      let itr=1
      let iplot=0
      let ihr=0
      if [ $appstat -eq 1 ];then 
        let istat=0
        ((nplots=$ntraces*$nstats))
      else
        nplots=$ntraces
      fi
      while [ $iplot -lt $nplots ];do   

#       Set Line color, types and marker types for each trace
        if [ $iplot -eq 0 ];then 
          lcol="${lcolbs[0]}"
          ltyp="${ltypbs[0]}"
          mtyp="${mtypbs[0]}"
        else 
          if [ $appstat -eq 1 ];then
            lcol="$lcol;${lcolbs[$itr-1]}"
            ltyp="$ltyp;${ltypbs[$istat]}"
            mtyp="$mtyp;${mtypbs[$istat]}"
          else
            lcol="$lcol;${lcolbs[$itr-1]}"
            ltyp="$ltyp;${ltypbs[$ihr]}"
            mtyp="$mtyp;${mtypbs[$ihr]}"
          fi
        fi

#       Determine statistics label for each trace
        stat[$iplot]=${stno[istat]}
        sl=1 
        for s in ${STCFG[*]};do
          if [ ${stat[iplot]} = $s ];then 
            if [ "$prrt" != RH ];then slbl=${STLBL[sl]};fi
            if [ "$iplot" -le 0 ];then 
              ylabel="${STYLBL[sl]}"
            else
              if [ ${stat[$iplot]} -ne ${stat[$iplot-1]} ];then 
                ylabel="$ylabel and ${STYLBL[sl]}"
              fi
            fi
            break
          fi
          let sl=sl+1
        done
        

#       Determine region label for each trace
#        rlbl=CONUS
        rgb=`echo ${rgn[itr-1]}|cut -d/ -f1 `
        rge=`echo ${rgn[itr-1]}|cut -d/ -f2 `

#-- Script tests show that $rge is the same as $rgb even if no "/" is present

#        if [ $rgb = G104 ];then 
#          rg=$rge
#          rgfn=$rg
#        else
#          rg=$rgb
##-- Use the region from the first trace in filename
#          rgfn=$rgb
#        fi

        rg=$rge
        rgfn=$rg
        rlbl=$rg

        echo rg, rgfn = $rg  $rgfn
        rl=1 
        for r in ${RCFG[*]};do
          if [ $rg = $r ];then 
            rlbl=${RLBL[rl]}
            break
          fi
          let rl=rl+1
        done

#       Set forecast hour and pressure level labels
        if [ plottype = DIU ];then flbl=;else flbl="FHR: ${plothrs[itr-1]}";fi
        if [ plottype = UPA ];then plbl=;else flbl="LVL: ${plotlvl[itr-1]}";fi

#       Set trace number array which allows for multiple stats on one plot (when appstat=1)
#       Also create trace label
        if [ "$prrt" = RH -o "$prrt" = ES ];then
          tlbl=${traces[itr-1]}
        else
          tlbl=`echo ${traces[itr-1]} |cut -d/ -f1`
        fi
        if [ $appstat -eq 1 ];then
          computetype=2
          trace[$iplot]="$tlbl ${slbl}+"
          if [ $tlabel = 0 ];then trace[$iplot]=;fi
          let traceno[$iplot]=$itr
          slbl=cmb
        else
          trace[$iplot]="${tlbl}  VARB: ${varb[itr-1]} $plbl  RGN: ${rlbl}  $flbl  STAT: ${slbl}" 
        fi
        if [ "${plothrs[$itr]}" -ne "${plothrs[$itr-1]}" ];then
           let ihr=$ihr+1

#          Allow for same color but different line types for different forecast hours
           if [ $appstat -eq 0 ];then itr=0;fi
        fi
        let itr=$itr+1
        let iplot=$iplot+1
        if [ $itr -gt $ntraces ];then 
          if [ $appstat -eq 1 ];then
            let istat=$istat+1
            if [ $istat -gt $nstats-1 ];then
              istat=0
              tlabel=0
            fi
          fi
          ihr=0
          itr=1
        fi
      done
      if [ $appstat -eq 1 ];then let istat=$nstats-1;fi
      line="${lcol}/${ltyp}/${WIDTH}/"
      marker="${lcol}/${mtyp}/${mwdt}/${mfrq}/"
      if [ -z "${stat[istat]}" ];then exit;fi
      
      echo CREATING PLOT FOR $varb $istat STAT= ${stat[istat]} >>fvs.log
      echo CREATING $varb PLOT FOR $istat STAT= ${stat[istat]}

#     Set plotting fields for probabilistic stat types
      hstclr=
      if [ $plottype = FHO ]; then
         if [ $stat = 1001 ]; then
            yax="0/2./0.05/5;5;2"      #-- Fixed maximum bias of 2
         else
            yax="0/.7/0.01/10;10;2"    #-- Fixed maximum ETS of 0.7
         fi
      fi
      stroot=`echo ${stat[istat]} |cut -c1-2`
      if [ $mdltype = prob ];then
        if [ ${stat[istat]} -eq 1601 ];then stat[istat]=1600;fi
        if [ ${stroot} -eq 16 ]; then 
          yax="0/0.60/0.05/1;2;;"
          if [ $slbl = RHNT -o $slbl = RHET ];then yax="0/0.20/0.05/1;2;;";fi
          hstclr="1;2;3;4;5;6"
          line=0; marker=0
        fi
      fi

#   SET PLOT TITLE
    if [ ${plothrs[0]} -ne ${plothrs[$nhrs-1]} ];then
      phrlabel="${plothrs[0]}-${plothrs[$nhrs-1]}"
    else
      phrlabel=$plothrs
    fi

    REV=NO
    if [ $plottype = UPA ];then 
      title="$phrlabel h $varb over $rgnd for $strdatet to $endatet"
      ylabel="$ylabel (${cycle}Z cycles)"
      xlabel="Pressure (hPa)"
      REV=YES
      FHRCH=$phrlabel
    fi

    if [ $plotdts -eq 1 ];then
      FHRCH=
      hrav=`echo $varb |cut -c 6-6 `
      titlert="$plotlvl $varb Error Daily Time Series from $strdatep to $endatep"
      if [ $vrb4 = OZON ];then
        FHRCH=DTS
      elif [ $vrb4 = OZMX ];then
        titlert="CMAQ Ozone Error:$hrav Hr Max for day"
      fi
      if [ $vhre -ne 99 ];then 
       title=" $slbl $titlert Averaged from Forecast Hr: $plothrs to $plothre "
      else
       title=" $slbl $titlert for Forecast Hrs: $phrlabel VALID $vhr GMT "
      fi
    fi

    if [ $plottype = DIU ]; then 
      FHRCH=DIU
      phrlabel=
      FHR=
      if [ $vbrt = "TO" ]; then
        tlabl=`echo $plabel | dd conv=ucase`
        title="Forecast errors vs $tlabl analysis from $strdatet to $endatet"
      else
        title="Surface $varb over $rgnd for $strdatet to $endatet"
      fi
      xlabel="Forecast Hour (${cycle}Z cycles)"
    fi

    if [ $plottype = FHO ];then 
      FHRCH=FHO
      if [ $vbrt = "TO" ]; then
        tlabl=`echo $plabel | dd conv=ucase`
        title="$phrlabel h fcst errors vs $tlabl analysis valid $endatet"
        xlabel="Total Cloud Fraction Threshold (%)"
      else
        let tbegin=phrlabel-24
        title="$tbegin - $phrlabel h QPF over $rgnd for $strdatet to $endatet"
        xlabel="24-h precipitation in inches (${cycle}Z cycles)"
      fi
    fi

#   SET OUTPUT PLOT FILE NAME    
    flname=${varb}${plotlvl}_${FHRCH}.${rgfn}
    if [ $plotlvl = UPA ]; then flname=${varb}${FHRCH}_${rgfn};fi
    if [ $plotlvl = SFC ]; then flname=${varb}${plotlvl}_${rgfn};fi
    if [ $vrb4 = "APCP" ];then flname=pcp${phrlabel}_${rgfn};fi
    if [ $vbrt = "OZ" ];then flname=$vrb4-$hrav${plotlvl}_${slbl}${phrlabel}_${mdltype}${FHRCH}${rgfn};fi
    if [ $vbrt = "OZ" ];then flname=$vrb4-$hrav${plotlvl}_${slbl}${phrlabel}_${mdltype}${FHRCH}${rgfn};fi
    if [ $vbrt = "TO" ]; then 
      if [ $plottype = "DIU" ]; then
        flname=${plabel}.$rgfn
      else
        flname=${plabel}.${endatet}.$rgfn
      fi
    fi
    echo OUTPUT FILENAME $flname DEVICE: $dev STAT: $stat $trace1

    rm -f $flname.psc
    rm -f psc.plt
    if [ $appstat -eq 0 ];then
      TNO=${stat[istat]}
      SNO=
    else
      TNO="${traceno[*]}"
      SNO="${stat[*]}"
    fi

#   Plotting Key Follows:               
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
   fvs p <<ENDFVS >plot.list 2>&1 
1
1
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
yaxis= $yax
LABLEV=2
trace1=${trace[0]}
trace2=${trace[1]}
trace3=${trace[2]}
trace4=${trace[3]}
trace5=${trace[4]}
trace6=${trace[5]}
trace7=${trace[6]}
trace8=${trace[7]}
DEVICE=$dev|VSDB
WITLIN = $witlin
hstclr=$hstclr
panel=0
xudlbl=$xudl
xaxis=$xax
xlabel=$xlabel
ylabel=$ylabel
title=$title
l
r
 cp $flname.$dev
0
0
0
ENDFVS

     if [ -f $flname.$dev ];then
       echo "FVS PLOT complete for $flname.$dev"
     else
       echo "FVS PLOT Failed...plot file not created"
       exit
     fi

#    Convert to GIF for web page
     convert -rotate 90 $flname.$dev $flname.gif
     rm -f $flname.$dev

#    Combine all member plots onto 1 page
     if [ $npltpg -gt 1 ];then
       mv $flname.gif  ${flname}${ipltpg}.gif
       if [ $ipltpg -eq 3 ];then 
         montage -geometry 600x600 ${flname}1.gif ${flname}2.gif ${flname}3.gif $flname.gif
       fi 
     fi
     if [ "$iftp" -eq 1 ];then 
       scp -p $flname.gif wd22jm@rzdm:$rzdmdir
       scp -p $flname${ipltpg}.gif wd22jm@rzdm:$rzdmdir
     fi
   let istat=$istat+1
 done                                #statno loop

#-- Next line is for debugging; comment out when done
echo Exiting make-fvs.sh

exit
