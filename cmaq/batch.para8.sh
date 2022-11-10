#!/bin/bash
FIRSTDAY=$1
LASTDAY=$2
bash mplot48.o3max.sh para8 all ${FIRSTDAY} ${LASTDAY}
bash mplot48.o3max_bc.sh para8 all ${FIRSTDAY} ${LASTDAY}
bash mplot48.pmmax.sh para8 all ${FIRSTDAY} ${LASTDAY}
bash mplot48.pmmax_bc.sh para8 all ${FIRSTDAY} ${LASTDAY}
bash mplot48.sp_pm.sh para8 all ${FIRSTDAY} ${LASTDAY}
bash mplot48.diff_o3max_bc.sh para8 para8 all ${FIRSTDAY} ${LASTDAY}
bash mplot48.diff_o3max.sh prod para8 all ${FIRSTDAY} ${LASTDAY}
bash mplot48.diff_sp_pm.sh prod para8 all ${FIRSTDAY} ${LASTDAY}
bash mplot48.diff_pmmax_bc.sh para8 para8 all ${FIRSTDAY} ${LASTDAY}
bash mplot48.diff_pmmax.sh prod para8 all ${FIRSTDAY} ${LASTDAY}
