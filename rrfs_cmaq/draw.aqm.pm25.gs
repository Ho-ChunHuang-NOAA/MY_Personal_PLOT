function draw_pm25_plot(args)

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
'set clevs 3 6 9 12 15 35 55 75 100 125 150 250 300 400 500 600 750'
'set ccols 99 98 97 96 95 94 93 92 91 90 89 88 87 86 85 84 83 82'
'set font 1'
'd 'plotvar
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' `2Hourly PM2.5`1 sfc_conc`0 (`3m`2g/m3`0)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pm25.k1.png png x'xsize' y'ysize' white'
'c'
