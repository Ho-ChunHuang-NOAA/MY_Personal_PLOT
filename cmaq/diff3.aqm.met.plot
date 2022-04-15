#!/bin/sh
##
## SCRIPT FOR SINGLE DAY PROCESSING AND MAP GENERATION
##
## YYYYMMDD is the start day of NAQFC PM   simulation
## Cycle_hr is the model run starting hour
##
module load GrADS/2.2.0
   module load prod_util/1.1.6
module load prod_envir/1.1.0
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
   *) cyc_in=`printf %2.2d ${sel_cyc}`
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
declare -a type=( metcro2d )
ntyp=${#type[@]}

ftpdir=/gpfs/dell1/stmp/${USER}/daily_plot_aqm_met
   
NOW=${FIRSTDAY}
while [ ${NOW} -le ${LASTDAY} ]; do

   if [ ${exp} == 'prod' ]; then
      comdir=${COMROOThps}/aqm/${exp}/aqm.${NOW}
      comdir=/gpfs/dell2/emc/modeling/noscrub/${USER}/com/aqm/${exp}/aqm.${NOW}
      comdir=/gpfs/hps/nco/ops/com/aqm/${exp}/aqm.${NOW}
   elif [ ${exp} == 'para' ]; then
      comdir=${COMROOThps}/aqm/${exp}/aqm.${NOW}
      comdir=/gpfs/hps/nco/ops/com/aqm/${exp}/aqm.${NOW}
      comdir=/gpfs/hps3/emc/naqfc/noscrub/${USER}/com/aqm/${exp}/aqm.${NOW}
   elif [ ${exp} == 'para12' ]; then
      comdir1=/gpfs/hps3/ptmp/Jianping.Huang/com/aqm/${exp}/aqm.${NOW}
   else
      comdir=/gpfs/hps3/emc/meso/noscrub/${USER}/com/aqm/${exp}/aqm.${NOW}
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
      F1=$(${NDATE} +1 ${cdate}| cut -c9-10)
      TOMORROW=$(${NDATE} +24 ${cdate}| cut -c1-8)
      THIRDDAY=$(${NDATE} +48 ${cdate}| cut -c1-8)
   
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
         tmpdir=/gpfs/dell1/stmp/${USER}/com2_aqm_${exp}_${jfile}.${NOW}${cych}
         if [ -d ${tmpdir} ]; then
            /bin/rm -f ${tmpdir}/*
         else
            mkdir -p ${tmpdir}
         fi
         cd ${tmpdir}
         cp ${comdir}/aqm.${cychr}.${jfile}.ncf  .

         outdir=${ftpdir}/aqm_${exp}_${jfile}_${NOW}${cych}
         if [ -d ${outdir} ]; then
            /bin/rm -f ${outdir}/*
         else
            mkdir -p ${outdir}
         fi
   
         if [ ${jfile} = 'metcro2d' ]; then 
            if [ -e aqm.ctl ]; then /bin/rm -f aqm.ctl; fi
            cat >  aqm.ctl <<EOF
dset ${tmpdir}/aqm.${cychr}.${jfile}.ncf
undef  -9.99e33
dtype netcdf
PDEF 442 265 lccr 21.8212 -120.628 1 1 33 45 -97 12000. 12000.
xdef 614 linear -132.000 0.12
ydef 262 linear 22.0000 0.12
zdef    1 levels  1.000    
tdef  49 linear ${F1}:00Z${D1}${mchr[$M1-1]}${Y1}  01hr
vars  75
PRSFC=>prsfc   0 t,z,y,x surface pressure (Pascal)
JACOBS=>jacobs   0 t,z,y,x total Jacobian at surface (M)
USTAR=>ustar   0 t,z,y,x cell averaged friction velocity (M/S)
WSTAR=>wstar   0 t,z,y,x convective velocity scale (M/S)
PBL=>pbl   0 t,z,y,x PBL height (M)
ZRUF=>zruf   0 t,z,y,x surface rouhness length (M)
MOLI=>moli   0 t,z,y,x inverse of Monin-Obukhov length (1/M)
HFX=>hfx   0 t,z,y,x sensible heat flux (WATTS/M**2)
QFX=>qfx   0 t,z,y,x latent heat flux (WATTS/M**2)
RADYNI=>radyni   0 t,z,y,x inverse of aerodynaic resistance (M/S)
RBNDYI=>rbndyi   0 t,z,y,x inverse laminar bnd layer resistance (M/S)
RSTOMI=>rstomi   0 t,z,y,x inverse of bulk stomatal resistance (M/S)
TEMPG=>tempg   0 t,z,y,x skin temperature at ground (K)
TEMP2=>temp2   0 t,z,y,x air temperature at 2 m (K)
WSPD10=>wspd10   0 t,z,y,x wind speed at 10 m (M/S)
WDIR10=>wdir10   0 t,z,y,x wind direction at 10 m (DEGREES)
GLW=>glw   0 t,z,y,x longwave radiation at ground (WATTS/M**2)
GSW=>gsw   0 t,z,y,x solar radiation absorbed at ground (WATTS/M**2)
RGRND=>rgrnd   0 t,z,y,x solar rad reaching sfc (WATTS/M**2)
RN=>rn   0 t,z,y,x nonconvec. pcpn per met TSTEP (CM)
RC=>rc   0 t,z,y,x convective pcpn per met TSTEP (CM)
CFRAC=>cfrac   0 t,z,y,x total cloud fraction (FRACTION)
CLDT=>cldt   0 t,z,y,x cloud top layer height (m) (M)
CLDB=>cldb   0 t,z,y,x cloud bottom layer height (m) (M)
WBAR=>wbar   0 t,z,y,x avg. liquid water content of cloud (G/M**3)
TROP=>trop   0 t,z,y,x tropopause height (Pascal)
ATTEN_X=>atten_x   0 t,z,y,x radiation attenuation fctr, off-line (DIM-LESS)
ATTEN=>atten   0 t,z,y,x radiation attenuation factor (DIM-LESS)
CSRAD=>csrad   0 t,z,y,x dnward srfc clear-sky SW, off-line (WATTS/M**2)
CSWTOA=>cswtoa   0 t,z,y,x dnward TOA SW, off-line (WATTS/M**2)
CSUSF=>csusf   0 t,z,y,x upward surface clear-sky SW (Eta) (WATTS/M**2)
CSDSF=>csdsf   0 t,z,y,x downward surface clear-sky SW (Eta) (WATTS/M**2)
PSCCB=>psccb   0 t,z,y,x shallow convective cloud bottom (Pascal)
PSCCT=>pscct   0 t,z,y,x shallow convective cloud top (Pascal)
PDCCB=>pdccb   0 t,z,y,x deep convective cloud bottom (Pascal)
PDCCT=>pdcct   0 t,z,y,x deep convective cloud top (Pascal)
PTCCB=>ptccb   0 t,z,y,x convective cloud bottom (Pascal)
PTCCT=>ptcct   0 t,z,y,x convective cloud top (Pascal)
PBL2=>pbl2   0 t,z,y,x PBL height, ACM2 based Richardson # (M)
PBLR=>pblr   0 t,z,y,x PBL height, NCEP based Richardson # (M)
MIXHT=>mixht   0 t,z,y,x Mixed layer depth [m] (M)
SOTYP=>sotyp   0 t,z,y,x soil type (DIM_LESS)
SOILW=>soilw   0 t,z,y,x volumetric soil moisture content (fraction)
LAI=>lai   0 t,z,y,x Leaf Area Index(non-dim) (DIM_LESS)
SNOWC=>snowc   0 t,z,y,x Snow Cover (fraction)
SNOCOV=>snocov   0 t,z,y,x Snow Cover (DECIMAL)
VEG=>veg   0 t,z,y,x Vegetaion (DECIMAL)
Q2=>q2   0 t,z,y,x mixing ratio at 2 m (KG/KG)
WR=>wr   0 t,z,y,x canopy moisture content (M)
SOIM1=>soim1   0 t,z,y,x volumetric soil moisture in top cm (M**3/M**3)
SOIM2=>soim2   0 t,z,y,x volumetric soil moisture in top m (M**3/M**3)
SOIT1=>soit1   0 t,z,y,x soil temperature in top cm (K)
SOIT2=>soit2   0 t,z,y,x soil temperature in top m (K)
SLTYP=>sltyp   0 t,z,y,x soil textture type by USDA category (DIM_LESS)
SEAICE=>seaice   0 t,z,y,x sea ice fraction (fraction)
VD_SO2=>vd_so2   0 t,z,y,x deposition velocity for species SO2 (M/S)
VD_SULF=>vd_sulf   0 t,z,y,x deposition velocity for species SULF (M/S)
VD_NO2=>vd_no2   0 t,z,y,x deposition velocity for species NO2 (M/S)
VD_NO=>vd_no   0 t,z,y,x deposition velocity for species NO (M/S)
VD_O3=>vd_o3   0 t,z,y,x deposition velocity for species O3 (M/S)
VD_HNO3=>vd_hno3   0 t,z,y,x deposition velocity for species HNO3 (M/S)
VD_H2O2=>vd_h2o2   0 t,z,y,x deposition velocity for species H2O2 (M/S)
VD_ALD=>vd_ald   0 t,z,y,x deposition velocity for species ALD (M/S)
VD_HCHO=>vd_hcho   0 t,z,y,x deposition velocity for species HCHO (M/S)
VD_OP=>vd_op   0 t,z,y,x deposition velocity for species OP (M/S)
VD_PAA=>vd_paa   0 t,z,y,x deposition velocity for species PAA (M/S)
VD_ORA=>vd_ora   0 t,z,y,x deposition velocity for species ORA (M/S)
VD_NH3=>vd_nh3   0 t,z,y,x deposition velocity for species NH3 (M/S)
VD_PAN=>vd_pan   0 t,z,y,x deposition velocity for species PAN (M/S)
VD_HONO=>vd_hono   0 t,z,y,x deposition velocity for species HONO (M/S)
VD_CO=>vd_co   0 t,z,y,x deposition velocity for species CO (M/S)
VD_METHANOL=>vd_methanol   0 t,z,y,x deposition velocity for species METHANOL (M/S)
VD_N2O5=>vd_n2o5   0 t,z,y,x deposition velocity for species N2O5 (M/S)
VD_NO3=>vd_no3   0 t,z,y,x deposition velocity for species NO3 (M/S)
VD_GEN_ALD=>vd_gen_ald   0 t,z,y,x deposition velocity for species GEN_ALD (M/S)
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
               grads -blc "run aqm.plots"
               ((numi++))
            done   ## fcst hour loop
         fi
      done    ## type loop
      if [ ${flag_scp} == 'yes' ]; then  # for RZDM maintainence
         ##
         ## TRANSFER PLOTS TO RZDM
         ##
         scp ${outdir}/aqm*.png ${remote_user}@${remote_host}:${remote_dir}/${Y1}/${NOW}/${cychr}
      fi
   done  ## end for loop cych in "${cyc_opt[@]}"
   cdate=${NOW}"00"
   NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
if [ "${flag_bsub}" == "yes" ]; then
   working_dir=/gpfs/dell1/stmp/${USER}/job_submit
   mkdir -p ${working_dir}
   cd ${working_dir}

   task_cpu='05:00'
   job_name=cmaq_met_${exp}${sel_cyc}
   batch_script=trans_cmaqmet_${exp}.sh
   if [ -e ${batch_script} ]; then /bin/rm -f ${batch_script}; fi

   logdir=/gpfs/dell1/ptmp/${USER}/batch_logs
   if [ ! -d ${logdir} ]; then mkdir -p ${logdir}; fi

   logfile=${logdir}/${job_name}_${FIRSTDAY}_${LASTDAY}.out
   if [ -e ${logfile} ]; then /bin/rm -f ${logfile}; fi

   file_hd=aqm
   file_type=png
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
   module load prod_util/1.1.6

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
      NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
   done
   if [ "${flag_update}" == "yes" ]; then
      script_dir=/gpfs/dell2/emc/modeling/save/${USER}/WEB/base
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

