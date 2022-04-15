function draw_dust_plot(args)

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

'set z 1'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du1'
'cbar'
'draw title 'days' 'resol' SFC CONC 0.1-1.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du1.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du2'
'cbar'
'draw title 'days' 'resol' SFC CONC 1.0-1.8 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du2.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du3'
'cbar'
'draw title 'days' 'resol' SFC CONC 1.8-3.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du3.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du4'
'cbar'
'draw title 'days' 'resol' SFC CONC 3.0-6.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du4.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du5'
'cbar'
'draw title 'days' 'resol' SFC CONC 6.0-10. um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du5.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+du4+du5)'
'cbar'
'draw title 'days' 'resol' SFC CONC Total Dust Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dut.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+0.7685*du4)'
'cbar'
'draw title 'days' 'resol' SFC CONC PM10 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.duc.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+0.4187*du2)'
'cbar'
'draw title 'days' 'resol' SFC CONC PM2.5 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dux.k1.du.gif gif x'xsize' y'ysize' white'
'c'
'set z 15'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du1'
'cbar'
'draw title 'days' 'resol' K=15 (~814mb) 0.1-1.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du1.k15.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du2'
'cbar'
'draw title 'days' 'resol' K=15 (~814mb) 1.0-1.8 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du2.k15.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du3'
'cbar'
'draw title 'days' 'resol' K=15 (~814mb) 1.8-3.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du3.k15.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du4'
'cbar'
'draw title 'days' 'resol' K=15 (~814mb) 3.0-6.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du4.k15.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du5'
'cbar'
'draw title 'days' 'resol' K=15 (~814mb) 6.0-10. um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du5.k15.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+du4+du5)'
'cbar'
'draw title 'days' 'resol' K=15 (~814mb) Total Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dut.k15.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+0.7685*du4)'
'cbar'
'draw title 'days' 'resol' K=15 (~814mb) PM10 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.duc.k15.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+0.4187*du2)'
'cbar'
'draw title 'days' 'resol' K=15 (~814mb) PM2.5 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dux.k15.du.gif gif x'xsize' y'ysize' white'
'c'
'set z 19'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du1'
'cbar'
'draw title 'days' 'resol' K=19 (~700mb) 0.1-1.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du1.k19.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du2'
'cbar'
'draw title 'days' 'resol' K=19 (~700mb) 1.0-1.8 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du2.k19.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du3'
'cbar'
'draw title 'days' 'resol' K=19 (~700mb) 1.8-3.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du3.k19.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du4'
'cbar'
'draw title 'days' 'resol' K=19 (~700mb) 3.0-6.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du4.k19.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du5'
'cbar'
'draw title 'days' 'resol' K=19 (~700mb) 6.0-10. um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du5.k19.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+du4+du5)'
'cbar'
'draw title 'days' 'resol' K=19 (~700mb) Total Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dut.k19.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+0.7685*du4)'
'cbar'
'draw title 'days' 'resol' K=19 (~700mb) PM10 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.duc.k19.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+0.4187*du2)'
'cbar'
'draw title 'days' 'resol' K=19 (~700mb) PM2.5 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dux.k19.du.gif gif x'xsize' y'ysize' white'
'c'
'set z 22'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du1'
'cbar'
'draw title 'days' 'resol' K=22 (~600mb) 0.1-1.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du1.k22.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du2'
'cbar'
'draw title 'days' 'resol' K=22 (~600mb) 1.0-1.8 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du2.k22.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du3'
'cbar'
'draw title 'days' 'resol' K=22 (~600mb) 1.8-3.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du3.k22.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du4'
'cbar'
'draw title 'days' 'resol' K=22 (~600mb) 3.0-6.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du4.k22.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du5'
'cbar'
'draw title 'days' 'resol' K=22 (~600mb) 6.0-10. um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du5.k22.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+du4+du5)'
'cbar'
'draw title 'days' 'resol' K=22 (~600mb) Total Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dut.k22.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+0.7685*du4)'
'cbar'
'draw title 'days' 'resol' K=22 (~600mb) PM10 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.duc.k22.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 15 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+0.4187*du2)'
'cbar'
'draw title 'days' 'resol' K=22 (~600mb) PM2.5 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dux.k22.du.gif gif x'xsize' y'ysize' white'
'c'
'set z 25'
'set clevs 25 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du1'
'cbar'
'draw title 'days' 'resol' K=25 (~6km) 0.1-1.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du1.k25.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du2'
'cbar'
'draw title 'days' 'resol' K=25 (~6km) 1.0-1.8 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du2.k25.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du3'
'cbar'
'draw title 'days' 'resol' K=25 (~6km) 1.8-3.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du3.k25.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du4'
'cbar'
'draw title 'days' 'resol' K=25 (~6km) 3.0-6.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du4.k25.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du5'
'cbar'
'draw title 'days' 'resol' K=25 (~6km) 6.0-10. um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du5.k25.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+du4+du5)'
'cbar'
'draw title 'days' 'resol' K=25 (~6km) Total Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dut.k25.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+0.7685*du4)'
'cbar'
'draw title 'days' 'resol' K=25 (~6km) PM10 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.duc.k25.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 25 35 60 80 160 320 640 1280 2560 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+0.4187*du2)'
'cbar'
'draw title 'days' 'resol' K=25 (~6km) PM2.5 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dux.k25.du.gif gif x'xsize' y'ysize' white'
'c'
'set z 29'
'set clevs 29 35 60 80 160 320 640 1280 2960 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du1'
'cbar'
'draw title 'days' 'resol' K=29 (~8km) 0.1-1.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du1.k29.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 29 35 60 80 160 320 640 1280 2960 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du2'
'cbar'
'draw title 'days' 'resol' K=29 (~8km) 1.0-1.8 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du2.k29.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 29 35 60 80 160 320 640 1280 2960 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du3'
'cbar'
'draw title 'days' 'resol' K=29 (~8km) 1.8-3.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du3.k29.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 29 35 60 80 160 320 640 1280 2960 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du4'
'cbar'
'draw title 'days' 'resol' K=29 (~8km) 3.0-6.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du4.k29.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 29 35 60 80 160 320 640 1280 2960 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du5'
'cbar'
'draw title 'days' 'resol' K=29 (~8km) 6.0-10. um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du5.k29.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 29 35 60 80 160 320 640 1280 2960 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+du4+du5)'
'cbar'
'draw title 'days' 'resol' K=29 (~8km) Total Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dut.k29.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 29 35 60 80 160 320 640 1280 2960 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+0.7685*du4)'
'cbar'
'draw title 'days' 'resol' K=29 (~8km) PM10 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.duc.k29.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 29 35 60 80 160 320 640 1280 2960 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+0.4187*du2)'
'cbar'
'draw title 'days' 'resol' K=29 (~8km) PM2.5 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dux.k29.du.gif gif x'xsize' y'ysize' white'
'c'
'set z 32'
'set clevs 32 35 60 80 160 320 640 1280 3260 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du1'
'cbar'
'draw title 'days' 'resol' K=32 (~10km) 0.1-1.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du1.k32.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 32 35 60 80 160 320 640 1280 3260 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du2'
'cbar'
'draw title 'days' 'resol' K=32 (~10km) 1.0-1.8 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du2.k32.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 32 35 60 80 160 320 640 1280 3260 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du3'
'cbar'
'draw title 'days' 'resol' K=32 (~10km) 1.8-3.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du3.k32.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 32 35 60 80 160 320 640 1280 3260 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du4'
'cbar'
'draw title 'days' 'resol' K=32 (~10km) 3.0-6.0 um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du4.k32.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 32 35 60 80 160 320 640 1280 3260 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd du5'
'cbar'
'draw title 'days' 'resol' K=32 (~10km) 6.0-10. um Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.du5.k32.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 32 35 60 80 160 320 640 1280 3260 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+du4+du5)'
'cbar'
'draw title 'days' 'resol' K=32 (~10km) Total Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dut.k32.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 32 35 60 80 160 320 640 1280 3260 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+du2+du3+0.7685*du4)'
'cbar'
'draw title 'days' 'resol' K=32 (~10km) PM10 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.duc.k32.du.gif gif x'xsize' y'ysize' white'
'c'
'set clevs 32 35 60 80 160 320 640 1280 3260 5120 10240'
'set ccols 79 20 19 18 17 3 10 7 12 8 2 98'
'd (du1+0.4187*du2)'
'cbar'
'draw title 'days' 'resol' K=32 (~10km) PM2.5 Daily AVG (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/'area'g.'days'.'resol'.dux.k32.du.gif gif x'xsize' y'ysize' white'
'c'
