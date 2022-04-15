function draw_aod_plot(args)

if (args='')
  prompt 'input arguments outdir yyyymmdd resol area'
  return
endif

odir=subwrd(args,1)
days=subwrd(args,2)
resol=subwrd(args,3)
area=subwrd(args,4)

if (area='st')
  xsize=650
  ysize=400
else
  xsize=600
  ysize=500
endif

'set clevs 25 50 75 100 200 400 600 800 1000 1500 2000'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd colconc1/1000.'
'cbar'
'draw title 'days' 'resol' DAVG Column total 0.1-1.0 um (10-3 g/m2)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.colconc1.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 50 75 100 200 400 600 800 1000 1500 2000'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd colconc2/1000.'
'cbar'
'draw title 'days' 'resol' DAVG Column total 1.0-1.8 um (10-3 g/m2)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.colconc2.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 50 75 100 200 400 600 800 1000 1500 2000'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd colconc3/1000.'
'cbar'
'draw title 'days' 'resol' DAVG Column total 1.8-3.0 um (10-3 g/m2)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.colconc3.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 50 75 100 200 400 600 800 1000 1500 2000'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd colconc4/1000.'
'cbar'
'draw title 'days' 'resol' DAVG Column total 3.0-6.0 um (10-3 g/m2)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.colconc4.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 50 75 100 200 400 600 800 1000 1500 2000'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd colconc5/1000.'
'cbar'
'draw title 'days' 'resol' DAVG Column total 6.0-10 um (10-3 g/m2)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.colconc5.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 50 75 100 200 400 600 800 1000 1500 2000'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (colconc1+colconc2+colconc3+colconc4+colconc5)/1000.'
'cbar'
'draw title 'days' 'resol' DAVG Column total 0.1-10 um (10-3 g/m2)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.colconct.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 0.05 0.1 0.2 0.4 0.6 0.8 1.0 1.2 1.6 2.0 3.0'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd aod500'
'cbar'
'draw title 'days' 'resol' FCST - Daily AVG Dust Column AOD at 500nm'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.aod500.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 0.05 0.1 0.2 0.4 0.6 0.8 1.0 1.2 1.6 2.0 3.0'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd aod550'
'cbar'
'draw title 'days' 'resol' FCST - Daily AVG Dust Column AOD at 550nm'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.aod550.k1.du.gif gif x'xsize' y'ysize' white'
'c'

