function draw_pm25_plot(args)

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

if (area='st')
  xsize=650
  ysize=400
else
  xsize=800
  ysize=600
endif
'set z 35'
'set font 1'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
*'set clevs 3. 6. 9. 12. 15. 18. 35. 55. 100.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
'd v6*pow(10,9)'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' SIG_LVL=1 TOT AERO CONC (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.totaero.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 31'
'set font 1'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
*'set clevs 3. 6. 9. 12. 15. 18. 35. 55. 100.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
'd v6*pow(10,9)'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' SIG_LVL=5 TOT AERO CONC (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.totaero.k5.gif gif x'xsize' y'ysize' white'
'c'
'set z 26'
'set font 1'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
*'set clevs 3. 6. 9. 12. 15. 18. 35. 55. 100.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
'd v6*pow(10,9)'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' SIG_LVL=10 TOT AERO CONC (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.totaero.k10.gif gif x'xsize' y'ysize' white'
'c'
'set z 21'
'set font 1'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
*'set clevs 3. 6. 9. 12. 15. 18. 35. 55. 100.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
'd v6*pow(10,9)'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' SIG_LVL=15 TOT AERO CONC (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.totaero.k15.gif gif x'xsize' y'ysize' white'
'c'
'set z 16'
'set font 1'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
*'set clevs 3. 6. 9. 12. 15. 18. 35. 55. 100.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
'd v6*pow(10,9)'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' SIG_LVL=20 TOT AERO CONC (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.totaero.k20.gif gif x'xsize' y'ysize' white'
'c'

