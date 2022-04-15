function diff_pm25_plot(args)

if (args='')
  prompt 'input arguments gs_dir outdir exp capexp yyyymmdd cycl_hr plot_type plotvar fcsthr vldhr area'
  return
endif

gdir=subwrd(args,1)
odir=subwrd(args,2)
run=subwrd(args,3)
exp=subwrd(args,4)
days=subwrd(args,5)
cyclhr=subwrd(args,6)
plottype=subwrd(args,7)
plotvar=subwrd(args,8)
fcsthr=subwrd(args,9)
vldhr=subwrd(args,10)
area=subwrd(args,11)

if (area='st')
  xsize=650
  ysize=400
else
  xsize=800
  ysize=600
endif

'set z 1'
'set font 1'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
'd 'plotvar'.2-'plotvar'.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' `3D`2PM2.5`1sfc_conc`0 (`3m`2g/m3`0)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25.k1.png png x'xsize' y'ysize' white'
'c'
