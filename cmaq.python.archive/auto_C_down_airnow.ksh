#!/bin/ksh


export dat_dir=/scratch2/NCEPDEV/naqfc/Jianping.Huang/Python_Scripts/Data/AirNow/201907_T05_T04

wget -N -O $dat_dir/20190708T05_20190709T04.csv  http://www.airnowapi.org/aq/data/?startDate=2019-07-08T05&endDate=2019-07-09T04&parameters=PM25&BBOX=-131.77422,21.081833,-58.66989,53.096016&dataType=C&format=text/csv&verbose=0&nowcastonly=0&includerawconcentrations=0&API_KEY=3771C87A-669E-42DC-898E-A26BAFDEDBEA
