#!/bin/bash
source /u/ho-chun.huang/versions/run.ver

flag_test=yes
flag_test=no

## module load prod_util
## module load prod_envir
## set -x
#
echo "program start `date`"
name=`hostname`
hl=`hostname | cut -c1-1`
if [ -s prod_info_list ]; then /bin/rm -f prod_info_list; fi
cat /lfs/h1/ops/prod/config/prodmachinefile > prod_info_list
info_line=`head -n 1 prod_info_list`
echo ${info_line}
prodinfo=$(echo ${info_line} | awk -F":" '{print $1}')
if [ "${prodinfo}" == "primary" ]; then
    prodmachine=$(echo ${info_line} | awk -F":" '{print $2}')
else
    info_line=`head -n 2 prod_info_list | tail -n1`
    echo ${info_line}
    prodinfo=$(echo ${info_line} | awk -F":" '{print $1}')
    if [ "${prodinfo}" == "primary" ]; then
        prodmachine=$(echo ${info_line} | awk -F":" '{print $2}')
    else
	prodmachine="unknown"
    fi
fi
pm=`echo ${prodmachine} | cut -c1-1`
if [ -s prod_info_list ]; then /bin/rm -f prod_info_list; fi
MSG="$0 envir beg_date end_date"
if [ "${hl}" != "${pm}" ]; then
    if [ $# -lt 3 ]; then
        echo ${MSG}
        exit
    fi
    if [ $# -eq 2 ]; then
        envir=$1
        FIRSTDAY=$2
        LASTDAY=$2
    else
        envir=$1
        FIRSTDAY=$2
        LASTDAY=$3
    fi

    script_dir=/lfs/h2/emc/vpppg/save/${USER}/plot/cmaq.python
    NOW=${FIRSTDAY}
    while [ ${NOW} -le ${LASTDAY} ]; do
        script_name=mplot_rrfs_exp_overlay_qsub.py
        declare -a exp=( ${envir} )
        cd ${script_dir}
	if [ -s ${script_name} ]; then
            for i in "${exp[@]}"; do
                python ${script_name} ${i} all all ${NOW} ${NOW}
            done
        else
            echo "Can not find ${script_dir}/${script_name}"
        fi

        ## script_name=mplot_aqm_max_ave_overlay_qsub.py
        ## declare -a exp=( prod v70c55 )
        ## cd ${script_dir}
	## if [ -s ${script_name} ]; then
        ##     for i in "${exp[@]}"; do
        ##         python ${script_name} ${i} all all ${NOW} ${NOW}
        ##     done
        ## else
        ##     echo "Can not find ${script_dir}/${script_name}"
        ## fi
    cdate=${NOW}"00"
    NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
fi
exit
