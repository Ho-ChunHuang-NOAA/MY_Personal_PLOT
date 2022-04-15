#!/bin/sh
whereami=`pwd`
echo ${whereami}
hname=`hostname`
hl=`hostname | cut -c1-1`
if [ ${hl} == 't' ]; then
   rsync -ravv ${whereami}/ ${USER}@gyre:${whereami}
else
   rsync -ravv ${whereami}/ ${USER}@tide:${whereami}
fi
exit
