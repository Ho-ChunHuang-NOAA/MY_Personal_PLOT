#!/bin/sh
##
## SCRIPT FOR SINGLE DAY PROCESSING AND MAP GENERATION
##
## YYYYMMDD is the start day of NAQFC PM   simulation
## Cycle_hr is the model run starting hour
##
module load GrADS/2.2.0
module load prod_envir/1.0.3
hl=`hostname | cut -c1`
if [ "${hl}" == "v" ]; then
  phase12_id='g'
else
  phase12_id='t'
fi

flag_test=yes
flag_test=no

flag_bsub=no
flag_bsub=yes

if [ "${flag_bsub}" == "yes" ]; then
   flag_scp=no
else
   flag_scp=yes
fi

TODAY=`date +%Y%m%d`

MSG="USAGE : $0 NCO_run (default:prod|para) Cycle_hr (default:all|06|12) YYYYMMDD_BEG YYYYMMDD_END"

exp=prod
sel_cyc=all
FIRSTDAY=${TODAY}
LASTDAY=${TODAY}

if [ $# -lt 2 ]; then
   echo $MSG
   exit
else
   exp=$1
   sel_cyc=$2
fi
if [ $# -lt 3 ]; then
   FIRSTDAY=${TODAY}
   LASTDAY=${TODAY}
elif [ $# -lt 4 ]; then
   FIRSTDAY=$3
   LASTDAY=$3
else
   FIRSTDAY=$3
   LASTDAY=$4
fi
case ${sel_cyc} in
   ''|*[!0-9]*) if [ "${sel_cyc}" == "all" ]; then
            declare -a cyc_opt=( 06 12 )
         else
            echo "input choice for cycle time is not defined $2, program stop"
            echo $MSG
            exit
         fi ;;
   *) cyc_in=`printf %2.2d $2`
      if [ "${cyc_in}" == "06" ] || [ "${cyc_in}" == "12" ]; then
         declare -a cyc_opt=( ${cyc_in} )
      else
         echo "input choice for cycle time is not defined $2, program stop"
         echo $MSG
         exit
      fi ;;
esac
echo ${cyc_opt[@]}

capexp=`echo ${exp} | tr '[:lower:]' '[:upper:]'`

## echo " ${exp} ${sel_cyc} ${FIRSTDAY} ${LASTDAY}"

remote_dir=/home/people/emc/www/htdocs/mmb/hchuang/web/fig
remote_host=emcrzdm.ncep.noaa.gov
remote_user=hchuang

grid_id2=148
grid_id=227

flag_update=no
if [ "${LASTDAY}" == "${TODAY}" ]; then flag_update=yes; fi

gs_dir=`pwd`

declare -a reg=( dset conus east west  ne10  nw10  se10  swse  ak   hi   nyc   md    mdatl )
declare -a lon0=( -175 -133 -100 -130  -81   -125  -91   -125  -170 -161 -74.7 -79.3 -82   )
declare -a lon1=(   55  -60  -60  -90  -66   -105  -74   -100  -130 -154 -71.5 -75.3 -73   )
declare -a lat0=(    0   21   24   21   37     37   24     21    50   18  40.3  37.8 36    )
declare -a lat1=(   80   52   50   50   48     50   40     45    80   23  42.2  40.5 42.5  )
nreg=${#reg[@]}
let max_ireg=${nreg}-1
idset=0
iconus=1
ieast=2
iwest=3
ine10=4
inw10=5
ise10=6
iswse=7
iak=8
ihi=9
inyc=10
imd=11
imdatl=12

declare -a mchr=( JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC )

## declare -a type=( metcro2d metcro3d metdot3d metbdy3d grdcro2d grddot2d )
declare -a type=( emission+fire  )
ntyp=${#type[@]}

ndate=/nwprod/util/exec/ndate
ftpdir=/gpfs/dell2/stmp/${USER}/daily_plot_aqm_met
mkdir -p ${ftpdir}
   
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do

   if [ ${exp} == 'prod' ]; then
      comdir=${COMROOTp2}/aqm/${exp}/aqm.${NOW}
      ## comdir2=/gpfs/${phase12_id}d1/emc/meso/noscrub/${USER}/com/aqm/${exp}/aqm.${NOW}
      comdir2=/gpfs/${phase12_id}d1/emc/meso/noscrub/${USER}/com/
      comdir=/gpfs/hps/nco/ops/com/aqm/${exp}/aqm.${NOW}
      ## comdir2=/gpfs/hps3/emc/naqfc/noscrub/${USER}/com/aqm/${exp}/aqm.${NOW}
      ## comdir2=/gpfs/hps3/emc/meso/noscrub/${USER}/com/aqm/${exp}/aqm.${NOW}
      if [ ! -d ${comdir} ]; then
         if [ -d ${comdir2} ]; then
            comdir=${comdir2}
         else
            echo "Can not find ${comdir} or ${comdir2}, program stop"
            exit
         fi
      fi
   elif [ ${exp} == 'para' ]; then
      comdir=${COMROOTp2}/aqm/${exp}/aqm.${NOW}
   elif [ ${exp} == 'para' ]; then
      comdir=${COMROOTp2}/aqm/${exp}/aqm.${NOW}
      comdir=/gpfs/hps/nco/ops/com/aqm/${exp}/aqm.${NOW}
      comdir=/naqfc/noscrub/Jianping.Huang/com/aqm/${exp}/aqm.${NOW}
   elif [ ${exp} == 'para1' ]; then
      ## comdir=/ptmpp1/Jianping.Huang/com/aqm/${exp}/aqm.${NOW}
      comdir=/gpfs/hps3/emc/naqfc/noscrub/${USER}/com/aqm/${exp}/aqm.${NOW}
   elif [ ${exp} == 'para2' ]; then
      ## comdir=/ptmpp1/Jianping.Huang/com/aqm/${exp}/aqm.${NOW}
      ## comdir=/naqfc/noscrub/Jianping.Huang/com/aqm/${exp}/aqm.${NOW}
      comdir=/gpfs/hps3/emc/naqfc/noscrub/${USER}/com/aqm/${exp}/aqm.${NOW}
   elif [ ${exp} == 'para5' ]; then
      comdir=/gpfs/${phase12_id}d1/emc/meso/noscrub/Ho-Chun.Huang/cmaq_emiss_tmp/${exp}/aqm.${NOW}
   elif [ ${exp} == 'para8' ]; then
      comdir=/gpfs/${phase12_id}d1/emc/meso/noscrub/Ho-Chun.Huang/cmaq_emiss_tmp/${exp}/aqm.${NOW}
   else
      echo " Experiments not defined for plotting schedule"
      exit
   fi
   if [ ! -d ${comdir} ]; then
      echo "////////////////////////////////////////"
      echo "${comdir} does not existed, program stop"
      echo "////////////////////////////////////////"
      exit
   else
      echo "////////////////////////////////////////"
      echo "/ Fetching PM data Data from ${comdir} /"
      echo "////////////////////////////////////////"
   fi
   for cych in "${cyc_opt[@]}"; do
      cdate=${NOW}${cych}
      F1=$(/nwprod/util/exec/ndate +1 ${cdate}| cut -c9-10)
      TOMORROW=$(/nwprod/util/exec/ndate +24 ${cdate}| cut -c1-8)
      THIRDDAY=$(/nwprod/util/exec/ndate +48 ${cdate}| cut -c1-8)
   
      Y1=`echo ${NOW} | cut -c1-4`
      MX=`echo ${NOW} | cut -c5-5`
      if [ ${MX} == '0' ]; then
         M1=`echo ${NOW} | cut -c6-6`
      else
         M1=`echo ${NOW} | cut -c5-6`
      fi
      D1=`echo ${NOW} | cut -c7-8`
      Y2=`echo ${TOMORROW} | cut -c1-4`
      MX=`echo ${TOMORROW} | cut -c5-5`
      if [ ${MX} == '0' ]; then
         M2=`echo ${TOMORROW} | cut -c6-6`
      else
         M2=`echo ${TOMORROW} | cut -c5-6`
      fi
      D2=`echo ${TOMORROW} | cut -c7-8`
      Y3=`echo ${THIRDDAY} | cut -c1-4`
      MX=`echo ${THIRDDAY} | cut -c5-5`
      if [ ${MX} == '0' ]; then
         M3=`echo ${THIRDDAY} | cut -c6-6`
      else
         M3=`echo ${THIRDDAY} | cut -c5-6`
      fi
      D3=`echo ${THIRDDAY} | cut -c7-8`

      let numcyc=${cych}
      cychr="t${cych}z"
      echo " Perform operation on cych = ${cych}  cychr = ${cychr}"
      if [ "${flag_test}" == "yes" ]; then continue; fi
      ## aqm.t06z.ave_24hr_pm25.148.grib2
      ## aqm.t06z.max_1hr_pm25.148.grib2
      ## use ncf to plot      sp_pm)         cp ${comdir}/aqm.${cychr}.chem_sfc.f*.${grid_id2}.grib2 ${tmpdir};;
      for jfile in "${type[@]}"
      do
         tmpdir=/gpfs/dell2/stmp/${USER}/com2_aqm_${exp}_${jfile}.${NOW}${cych}
         if [ -d ${tmpdir} ]; then
            /bin/rm -f ${tmpdir}/*
         else
            mkdir -p ${tmpdir}
         fi
         cd ${tmpdir}
#         if [ -s ${comdir}/aqm.${cychr}.${jfile}.ncf ]; then
#            cp ${comdir}/aqm.${cychr}.${jfile}.ncf  .
#         else
#            echo "can not find ${comdir}/aqm.${cychr}.${jfile}.ncf"
#            continue
#         fi

         outdir=${ftpdir}/aqm_${exp}_${jfile}_${NOW}${cych}
         if [ -d ${outdir} ]; then
            /bin/rm -f ${outdir}/*
         else
            mkdir -p ${outdir}
         fi
         if [ ${jfile} = 'emission+fire' ]; then 
            if [ -e aqm.ctl ]; then /bin/rm -f aqm.ctl; fi
            cat >  aqm.ctl <<EOF
dset ${comdir}/aqm.${cychr}.${jfile}.ncf
undef  -9.99e33
dtype netcdf
PDEF 442 265 lccr 21.8212 -120.628 1 1 33 45 -97 12000. 12000.
xdef 614 linear -132.000 0.12
ydef 262 linear 22.0000 0.12
zdef   35 levels  1.000 0.99467 0.98863 0.981796 0.974076 0.965373 0.955585 0.952585 0.950585 0.930895 0.910397 0.900404 0.880811 0.852914 0.829314 0.786714 0.735314 0.645814 0.614214 0.582114 0.549714 0.511711 0.484394 0.451894 0.419694 0.388094 0.356994 0.326694 0.297694 0.270694 0.245894 0.223694 0.203594 0.154394 0.127094 0.089794
tdef  49 linear ${F1}:00Z${D1}${mchr[$M1-1]}${Y1}  01hr
vars 53
ALD2=>ald2   0 t,z,y,x Model species ALD2 (moles/s)
ALD2_PRIMARY=>ald2pr   0 t,z,y,x  Model species ALD2_PRIMARY  (moles/s)
ALDX=>aldx   0 t,z,y,x  Model species ALDX (moles/s)
BENZENE=>benzene   0 t,z,y,x  Model species BENZ (moles/s)
CH4=>ch4   0 t,z,y,x  Model species CH4 (moles/s)
CL2=>cl2   0 t,z,y,x  Model species CL2 (moles/s)
CO=>co   0 t,z,y,x  Model species CO (moles/s)
ETH=>eth   0 t,z,y,x  Model species ETH (moles/s)
ETHA=>etha   0 t,z,y,x  Model species ETHA (moles/s)
ETOH=>etoh   0 t,z,y,x  Model species ETOH (moles/s)
FORM=>form   0 t,z,y,x  Model species FORM (moles/s)
FORM_PRIMARY=>formpr   0 t,z,y,x  Model species FORM_PRIMARY (moles/s)
HCL=>hcl   0 t,z,y,x  Model species HCL (moles/s)
HONO=>hono   0 t,z,y,x  Model species HONO (moles/s)
IOLE=>iole   0 t,z,y,x  Model species IOLE (moles/s)
ISOP=>isop   0 t,z,y,x  Model species ISOP (moles/s)
MEOH=>meoh   0 t,z,y,x  Model species MEOH (moles/s)
NH3=>nh3   0 t,z,y,x  Model species NH3 (moles/s)
NH3_FERT=>nh3fert   0 t,z,y,x  Model species NH3_FERT (moles/s)
NO=>no   0 t,z,y,x  Model species NO (moles/s)
NO2=>no2   0 t,z,y,x  Model species NO2 (moles/s)
NR=>nr   0 t,z,y,x  biogenic emissions of the indicated species (moles/s)
NVOL=>nvol   0 t,z,y,x  Model species NVOL (moles/s)
OLE=>ole   0 t,z,y,x  Model species OLE (moles/s)
PAL=>pal   0 t,z,y,x  Model species PAL (moles/s)
PAR=>par   0 t,z,y,x  Model species PAR (moles/s)
PCA=>pca   0 t,z,y,x  Model species PCA (g/s)
PCL=>pcl   0 t,z,y,x  Model species PCL (g/s)
PEC=>pec   0 t,z,y,x  Model species PEC (g/s)
PFE=>pfe   0 t,z,y,x  Model species PFE  (g/s)
PH2O=>ph2o   0 t,z,y,x  Model species PH2O (g/s)
PK=>pk   0 t,z,y,x  Model species PK (g/s)
PMC=>pmc   0 t,z,y,x  Model species PMC (g/s)
PMFINE=>pmfine   0 t,z,y,x  Model species PMFINE (g/s)
PMG=>pmg   0 t,z,y,x  Model species PMG (g/s)
PMN=>pmh   0 t,z,y,x  Model species PMN (g/s)
PMOTHR=>pmother   0 t,z,y,x  Model species PMOTHR (g/s)
PNA=>pna   0 t,z,y,x  Model species PNA (g/s)
PNCOM=>pncom   0 t,z,y,x  Model species PNCOM (g/s)
PNH4=>pnh4   0 t,z,y,x  Model species PNH4 (g/s)
PNO3=>pno3   0 t,z,y,x  Model species PNO3 (g/s)
POC=>poc   0 t,z,y,x  Model species POC (g/s)
PSI=>psi   0 t,z,y,x  Model species PSI (g/s)
PSO4=>pso4   0 t,z,y,x  Model species PSO4 (g/s)
PTI=>pti   0 t,z,y,x  Model species PTI (g/s)
SO2=>so2   0 t,z,y,x  Model species SO2 (moles/s)
SULF=>sulf   0 t,z,y,x  Model species SULF (moles/s)
TERP=>terp   0 t,z,y,x  Model species TERP (moles/s)
TOL=>tol   0 t,z,y,x  Model species TOL (moles/s)
UNK=>unk   0 t,z,y,x  Model species UNK (moles/s)
UNR=>unr   0 t,z,y,x  Model species UNR (moles/s)
VOC_INV=>vocinv   0 t,z,y,x  Model species VOC_INV (moles/s)
XYL=>xyl   0 t,z,y,x   XYL Model species XYLMN (moles/s)
ENDVARS
EOF
            t0=0
            t1=48
            let numi=t0
            while [ ${numi} -le ${t1} ]; do

               fcsti=`printf %3.3d ${numi}`
               i=`printf %2.2d ${numi}`
               tindx=`expr ${numi} + 1`

               let j=numi+${cych}
               if [ ${j} -ge 48 ]; then
                  let j=j-48
                  date=${THIRDDAY}
               elif [ ${j} -ge 24 ]; then
                  let j=j-24
                  date=${TOMORROW}
               else
                  date=${NOW}
               fi
               numj=`printf %2.2d ${j}`
   
               if [ -e aqm.plots ]; then /bin/rm -f aqm.plots; fi

## 55 Medium brown 205 133 63
## 44 dark yellow  154 205 50
## 44 green Yellow 173 255 47
## 60 gold        255,215,0'
## 61 dark orange 255,140,0'
## 62 green        0   128 0
## 63 lime green   50,205,50
## 64 lawn green   142 252 0
## 65 Dark green   0   100 0
## 66 Yellow 255 255 0
## 67 Darker Yellow 230 230 0
## 68 crimson     220,20,60
## 69 dark red    139,0,0
## 70 violet      238,130,238
## 71 green-blue  0   204 204
               cat >  aqm.plots <<EOF
'reinit'
'set gxout shaded'
'set gxout grfill'
'set display color white'
'set mpdset hires'
'set grads off'
'set rgb 98 255 105 180'
'set rgb 79 240 240 240'
'set rgb 17  55  55 255'
'set rgb 18 110 110 255'
'set rgb 19 165 165 255'
'set rgb 20 220 220 255'
'set rgb 55 205 133 63'
'set rgb 44 154 205 50'
'set rgb 60 255 215 0'
'set rgb 61 255 140 0'
'set rgb 62 0 128 0'
'set rgb 63 50 205 50'
'set rgb 64 142 252 0'
'set rgb 65 0   100 0'
'set rgb 66 255 255 0'
'set rgb 67 230 230 0'
'set rgb 68 220 20  60'
'set rgb 69 139 0   0'
'set rgb 70 238 130 238'
'set rgb 71 0   204 204'
'c'
'open aqm.ctl'
'set t ${tindx}'
'set lat ${lat0[${iconus}]} ${lat1[${iconus}]}'
'set lon ${lon0[${iconus}]} ${lon1[${iconus}]}'
'${gs_dir}/draw2.aqm.${jfile}.gs2 ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} conus'
'set lat ${lat0[${ieast}]} ${lat1[${ieast}]}'
'set lon ${lon0[${ieast}]} ${lon1[${ieast}]}'
'${gs_dir}/draw2.aqm.${jfile}.gs2 ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} east'
'set lat ${lat0[${iwest}]} ${lat1[${iwest}]}'
'set lon ${lon0[${iwest}]} ${lon1[${iwest}]}'
'${gs_dir}/draw2.aqm.${jfile}.gs2 ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} west'
'set lat ${lat0[${ine10}]} ${lat1[${ine10}]}'
'set lon ${lon0[${ine10}]} ${lon1[${ine10}]}'
'${gs_dir}/draw2.aqm.${jfile}.gs2 ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} ne'
'set lat ${lat0[${inw10}]} ${lat1[${inw10}]}'
'set lon ${lon0[${inw10}]} ${lon1[${inw10}]}'
'${gs_dir}/draw2.aqm.${jfile}.gs2 ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} nw'
'set lat ${lat0[${ise10}]} ${lat1[${ise10}]}'
'set lon ${lon0[${ise10}]} ${lon1[${ise10}]}'
'${gs_dir}/draw2.aqm.${jfile}.gs2 ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} se'
'set lat ${lat0[${iswse}]} ${lat1[${iswse}]}'
'set lon ${lon0[${iswse}]} ${lon1[${iswse}]}'
'${gs_dir}/draw2.aqm.${jfile}.gs2 ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} sw'
'set lat ${lat0[${inyc}]} ${lat1[${inyc}]}'
'set lon ${lon0[${inyc}]} ${lon1[${inyc}]}'
'${gs_dir}/draw2.aqm.${jfile}.gs2 ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} nyc'
'set lat ${lat0[${imd}]} ${lat1[${imd}]}'
'set lon ${lon0[${imd}]} ${lon1[${imd}]}'
'${gs_dir}/draw2.aqm.${jfile}.gs2 ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} md'
'set lat ${lat0[${imdatl}]} ${lat1[${imdatl}]}'
'set lon ${lon0[${imdatl}]} ${lon1[${imdatl}]}'
'${gs_dir}/draw2.aqm.${jfile}.gs2 ${gs_dir} ${outdir} ${exp} ${capexp} ${NOW} ${cychr} ${i} ${date}/${numj}00V${fcsti} mdatl'
'quit'
EOF
               grads -d Cairo -h GD -blc "run aqm.plots"
               ((numi++))
            done   ## fcst hour loop
         fi
      done    ## type loop
      if [ ${flag_scp} == 'yes' ]; then  # for RZDM maintainence
         ##
         ## TRANSFER PLOTS TO RZDM
         ##
         scp ${outdir}/aqm*.gif ${remote_user}@${remote_host}:${remote_dir}/${Y1}/${NOW}/${cychr}
      fi
   done  ## end for loop cych in "${cyc_opt[@]}"
   cdate=${NOW}"00"
   NOW=$(/nwprod/util/exec/ndate +24 ${cdate}| cut -c1-8)
done
if [ "${flag_bsub}" == "yes" ]; then
   working_dir=/gpfs/dell2/stmp/${USER}/job_submit
   mkdir -p ${working_dir}
   cd ${working_dir}

   task_cpu='05:00'
   job_name=cmaq_met_${exp}${sel_cyc}
   batch_script=trans_cmaqmet_${exp}.sh
   if [ -e ${batch_script} ]; then /bin/rm -f ${batch_script}; fi

   logdir=/gpfs/dell2/ptmp/${USER}/batch.logs
   if [ ! -d ${logdir} ]; then mkdir -p ${logdir}; fi

   logfile=${logdir}/${job_name}_${FIRSTDAY}_${LASTDAY}.out
   if [ -e ${logfile} ]; then /bin/rm -f ${logfile}; fi

   file_hd=aqm
   file_type=gif
   cat > ${batch_script} << EOF
#!/bin/sh
#BSUB -o ${logfile}
#BSUB -e ${logfile}
#BSUB -n 1
#BSUB -J j${job_name}
#BSUB -q "dev_transfer"
#BSUB -P HYS-T2O
#BSUB -W ${task_cpu}
#BSUB -R affinity[core(1)]
#BSUB -M 100
####BSUB -R span[ptile=1]
##
##  Provide fix date daily Hysplit data processing
##
   FIRSTDAY=${FIRSTDAY}
   LASTDAY=${LASTDAY}
   ftpdir=${ftpdir}
   exp=${exp}
   remote_user=${remote_user}
   remote_host=${remote_host}
   remote_dir=${remote_dir}
   file_hd=${file_hd}
   file_type=${file_type}
   flag_update=${flag_update}
   declare -a cyc=( ${cyc_opt[@]} )
   declare -a type=( ${type[@]} )
EOF
   ##
   ##  Creat part 2 script : exact wording of scripts
   ##
   cat > ${batch_script}.add  << 'EOF'

   NOW=${FIRSTDAY}
   while [ ${NOW} -le ${LASTDAY} ]; do
      YY=`echo ${NOW} | cut -c1-4`
      YM=`echo ${NOW} | cut -c1-6`

      for i in "${cyc[@]}"; do
         cycle=t${i}z
         for j in "${type[@]}"; do
            data_dir=${ftpdir}/aqm_${exp}_${j}_${NOW}${i}
            if [ -d ${data_dir} ]; then
               scp ${data_dir}/${file_hd}*${file_type} ${remote_user}@${remote_host}:${remote_dir}/${YY}/${NOW}/${cycle}
            else
               echo "Can not find ${data_dir}, skip to next cycle/day"
            fi
         done  ## type
      done  ## cycle time
      cdate=${NOW}"00"
      NOW=$(/nwprod/util/exec/ndate +24 ${cdate}| cut -c1-8)
   done
   if [ "${flag_update}" == "yes" ]; then
      script_dir=/naqfc/save/${USER}/WEB/base
      cd ${script_dir}

      script_name=wcoss.run.cmaq_pm.sh
      bash ${script_name} ${LASTDAY}

      script_name=wcoss.run.cmaq2_pm.sh
      bash ${script_name} ${LASTDAY}
   fi
exit
EOF
   ##
   ##  Combine both working script together
   ##
   cat ${batch_script}.add >> ${batch_script}
   ##
   ##  Submit run scripts
   ##
   if [ "${flag_test}" == "no" ]; then
      bsub < ${batch_script}
   else
      echo "test bsub < ${batch_script} completed"
   fi
fi
exit

