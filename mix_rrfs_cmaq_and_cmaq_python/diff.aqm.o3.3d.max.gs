function diffpm25maxplot(args)

if (args='')
  prompt 'input arguments gs_dir outdir exp capexp yyyymmdd cycl_hr plottype num_day*hr-range area'
  return
endif

gdir=subwrd(args,1)
odir=subwrd(args,2)
run=subwrd(args,3)
exp=subwrd(args,4)
days=subwrd(args,5)
cyclhr=subwrd(args,6)
plottype=subwrd(args,7)
range1=subwrd(args,8)
range2=subwrd(args,9)
range3=subwrd(args,10)
area=subwrd(args,11)

if (area='st')
  xsize=650
  ysize=400
else
  xsize=800
  ysize=600
endif

'set t 1'
'set z 1'
'set clevs -60. -40. -20. -10. -5. -1. -0.05 0.05 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 25 0 55 54 53 52 2 49 48'
if(plottype='max_1hr_o3')
'd v1.2-v1.1'
else
'd v2.2-v2.1'
endif
gdir'/cbar.gs'
'set font 1'
'draw title 'exp' 'days' 'cyclhr'\ 'range1' `3D`2'plottype'`1 sfc_conc`0 (`2ppbV`0)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'plottype'.day1.k1.png png x'xsize' y'ysize' white'
'c'
