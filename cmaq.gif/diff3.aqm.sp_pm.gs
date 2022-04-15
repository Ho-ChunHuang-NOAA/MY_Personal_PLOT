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

'set z 1'
'set font 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_tot.2-pm25_tot.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 Total sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_tot.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_cl.2-pm25_cl.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 CL sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_cl.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_ec.2-pm25_ec.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 EC sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_ec.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_na.2-pm25_na.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 NA sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_na.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_mg.2-pm25_mg.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 MG sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_mg.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_k.2-pm25_k.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 K  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_k.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_ca.2-pm25_ca.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 CA sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_ca.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_nh4.2-pm25_nh4.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 NH4 sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_nh4.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_no3.2-pm25_no3.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 NO3 sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_no3.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_oc.2-pm25_oc.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 OC  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_oc.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_soil.2-pm25_soil.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 SOIL  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_soil.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pm25_so4.2-pm25_so4.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM25 SO4 sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25_so4.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd pmc_tot.2-pmc_tot.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PMC TOT sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pmc_tot.k1.gif gif x'xsize' y'ysize' white'
'c'
