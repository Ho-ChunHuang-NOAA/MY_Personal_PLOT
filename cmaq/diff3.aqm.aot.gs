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

*'set rgb 48 150   0   0'
*'set rgb 49 200   0   0'
*'set rgb 52 255  80  80'
*'set rgb 53 255 120 120'
*'set rgb 54 255 150 150'
*'set rgb 55 255 220 220'
*'set rgb 89 238 220 220'
'set z 1'
'set font 1'
'set clevs -1.0 -0.8 -0.6 -0.4 -0.2 -0.1 -0.05 0.05 0.1 0.2 0.4 0.6 0.8 1.0'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
*'set clevs 3. 6. 9. 12. 15. 18. 35. 55. 100.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
'd aotk.2-aotk.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM2.5 AOD'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.aod.k1.png png x'xsize' y'ysize' white'
'c'
