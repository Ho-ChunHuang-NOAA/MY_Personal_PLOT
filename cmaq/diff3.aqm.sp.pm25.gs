function diff_pm25_plot(args)

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

'set z 1'
'set font 1'
*'set clevs 3. 6. 9. 12. 15. 18. 35. 55. 100.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
*'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
*'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'set clevs 0.05 1  3  5  10 25 50 75 100 200 300 400 500'
'set ccols 62 66 65 64 63  5  3 10   7 12  8  2   6 61'
*'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
*'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
*'set clevs 3. 6. 9. 12. 15. 18. 35. 55. 100.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
'd PMTFsig1000.2-PMTFsig1000.1'
gdir'/cbar.gs'
'draw title Smoke PM25 'days' 'cyclhr'\'vldhr' Surface Layer Conc. (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25.k1.png png x'xsize' y'ysize' white'
'c'
