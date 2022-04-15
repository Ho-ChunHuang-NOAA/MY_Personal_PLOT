function draw_o3_plot(args)

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
plottype=subwrd(args,7)
fcsthr=subwrd(args,8)
vldhr=subwrd(args,9)
area=subwrd(args,10)

if (area='st')
  xsize=650
  ysize=400
else
  xsize=800
  ysize=600
endif

'set z 1'
'set font 1'
'set clevs 3 6 9 12 25 35 45 55 65 70 75 85 95 105'
'set ccols 99 98 97 96 95 94 93 92 91 90 89 88 87 86 85'
'd OZCONsig1000'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' 'plottype' sfc_conc (ppbV)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.'plottype'.k1.png png x'xsize' y'ysize' white'
'c'
