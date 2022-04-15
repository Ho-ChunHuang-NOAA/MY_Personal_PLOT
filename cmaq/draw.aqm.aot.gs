function draw_aot_plot(args)

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
'set clevs 0. 0.2 0.4 0.6 0.8 1.0 1.5 2.0 2.5 3.0'
'set ccols 79 20 19 5 3 10 7 12 8 2 98 33 44 55 66'
'set clevs 0. 0.2 0.4 0.6 0.8 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5 5.0'
*'set clevs 0. 0.1 0.2 0.3 0.4 0.5 0.6 0.7 1.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
'd v1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PM2.5 AOD'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.aod.k1.png png x'xsize' y'ysize' white'
'c'
