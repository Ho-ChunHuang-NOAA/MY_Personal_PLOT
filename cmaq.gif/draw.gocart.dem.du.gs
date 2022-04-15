function draw_emiss_plot(args)

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
'set clevs 10. 25. 50. 75. 100. 150. 200. 250. 300. 400. 500.'
*'set clevs 0. 1. 2. 3. 4. 5. 6. 7. 8. 9. 10.'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd em1/1000.'
*'d log10(em1)'
'cbar'
'draw title 'days' 'resol' 0.1-1.0 um Daily AVG Dust Emission x1.E3 kg/hr'
*'draw title 'days' 'resol' 0.1-1.0 um Daily AVG Dust Emission log10 kg/hr'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.em1.k1.du.gif gif x'xsize' y'ysize' white'
'c'
*'set clevs 0. 1. 2. 3. 4. 5. 6. 7. 8. 9. 10.'
'set clevs 10. 25. 50. 75. 100. 150. 200. 250. 300. 400. 500.'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd em2/1000.'
*'d log10(em2)'
'cbar'
'draw title 'days' 'resol' 1.0-1.8 um Daily AVG Dust Emission x1.E3 kg/hr'
*'draw title 'days' 'resol' 1.0-1.8 um Daily AVG Dust Emission log10 kg/hr'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.em2.k1.du.gif gif x'xsize' y'ysize' white'
'c'
*'set clevs 0. 1. 2. 3. 4. 5. 6. 7. 8. 9. 10.'
'set clevs 10. 25. 50. 75. 100. 150. 200. 250. 300. 400. 500.'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd em3/1000.'
*'d log10(em3)'
'cbar'
'draw title 'days' 'resol' 1.8-3.0 um Daily AVG Dust Emission x1.E3 kg/hr'
*'draw title 'days' 'resol' 1.8-3.0 um Daily AVG Dust Emission log10 kg/hr'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.em3.k1.du.gif gif x'xsize' y'ysize' white'
'c'
*'set clevs 0. 1. 2. 3. 4. 5. 6. 7. 8. 9. 10.'
'set clevs 10. 25. 50. 75. 100. 150. 200. 250. 300. 400. 500.'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd em4/1000.'
*'d log10(em4)'
'cbar'
'draw title 'days' 'resol' 3.0-6.0 um Daily AVG Dust Emission x1.E3 kg/hr'
*'draw title 'days' 'resol' 3.0-6.0 um Daily AVG Dust Emission log10 kg/hr'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.em4.k1.du.gif gif x'xsize' y'ysize' white'
'c'
*'set clevs 0. 1. 2. 3. 4. 5. 6. 7. 8. 9. 10.'
'set clevs 10. 25. 50. 75. 100. 150. 200. 250. 300. 400. 500.'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd em5/1000.'
*'d log10(em5)'
'cbar'
'draw title 'days' 'resol' 6.0-10. um Daily AVG Dust Emission x1.E3 kg/hr'
*'draw title 'days' 'resol' 6.0-10. um Daily AVG Dust Emission log10 kg/hr'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.em5.k1.du.gif gif x'xsize' y'ysize' white'
'c'
