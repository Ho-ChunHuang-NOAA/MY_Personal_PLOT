function diff_sppm_plot(args)

if (args='')
  prompt 'input arguments gs_dir outdir exp capexp yyyymmdd cycl_hr fcsthr vldhr area'
  return
endif

gdir=subwrd(args,1)
odir=subwrd(args,2)
run=subwrd(args,3)
exp=subwrd(args,4)
days=subwrd(args,5)
cyclhr=subwrd(args,6)
fcsthr=subwrd(args,7)
vldhr=subwrd(args,8)
area=subwrd(args,9)

* O3=>o3   0 t,z,y,x  (ppmV)
* CO=>co   0 t,z,y,x  (ppmV)
* NO=>no   0 t,z,y,x  (ppmV)
* NO2=>no2   0 t,z,y,x  (ppmV)
* NOY=>noy   0 t,z,y,x  (ppmV)
* VOC=>voc   0 t,z,y,x  (ppmC)
* PM25_TOT=>pm25_tot   0 t,z,y,x  (micrograms/m**3)
* PM25_CL=>pm25_cl   0 t,z,y,x  (micrograms/m**3)
* PM25_EC=>pm25_ec   0 t,z,y,x  (micrograms/m**3)
* PM25_NA=>pm25_na   0 t,z,y,x  (micrograms/m**3)
* PM25_MG=>pm25_mg   0 t,z,y,x  (micrograms/m**3)
* PM25_K=>pm25_k   0 t,z,y,x  (micrograms/m**3)
* PM25_CA=>pm25_ca   0 t,z,y,x  (micrograms/m**3)
* PM25_NH4=>pm25_nh4   0 t,z,y,x  (micrograms/m**3)
* PM25_NO3=>pm25_no3   0 t,z,y,x  (micrograms/m**3)
* PM25_OC=>pm25_oc   0 t,z,y,x  (micrograms/m**3)
* PM25_SOIL=>pm25_soil   0 t,z,y,x  (micrograms/m**3)
* PM25_SO4=>pm25_so4   0 t,z,y,x  (micrograms/m**3)
* PMC_TOT=>pmc_tot   0 t,z,y,x  (micrograms/m**3)


if (area='st')
  xsize=650
  ysize=400
else
  xsize=800
  ysize=600
endif

*'set rgb 76 150   0   0'
*'set rgb 75 200   0   0'
*'set rgb 74 255  30  30'
*'set rgb 73 255  90  90'
*'set rgb 72 255 120 120'
*'set rgb 71 255 150 150'
*'set rgb 70 255 200 200'
*'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'set z 1'
'set font 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
*'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
*'set ccols 99 88 16 18 19 20 25 0 70 71 72 73 74 75 76'
'set clevs  1 3 5 10 25 50 100 150 200 250 300 350 400'
'set ccols 60 82 84  3 10  7 12  8 73 74 75 76 77 78'
* 66 -> 80 65->81 64 -> 82 63->84
*'set ccols 62 66 65 64 63  5  3 10   7 12  8  2   6 91'
'd pm25_col.2*pow(10,-3)-pm25_col.1*pow(10,-3)'
gdir'/cbar.gs'
'draw title Smoke PM25 'days' 'cyclhr'\'vldhr' Column Total (mg/m2)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_col.k1.gif gif x'xsize' y'ysize' white'
'c'
