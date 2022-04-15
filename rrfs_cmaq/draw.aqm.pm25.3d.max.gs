function drawpm25maxplot(args)

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
'set clevs 3 6 9 12 15 35 55 75 100 125 150 250 300 400 500 600 750'
'set ccols 99 98 97 96 95 94 93 92 91 90 89 88 87 86 85 84 83 82'
if(plottype='max_1hr_pm25')
'd v3'
else
'd v4'
endif
gdir'/cbar.gs'
'set font 1'
'draw title 'exp' 'days' 'cyclhr'\ 'range1' `2'plottype'`1 sfc_conc`0 (`3m`2g/m3`0)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'plottype'.day1.k1.png png x'xsize' y'ysize' white'
'c'
