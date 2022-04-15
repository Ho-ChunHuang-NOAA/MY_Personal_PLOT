function draw_pm25_plot(args)

if (args='')
  prompt 'input arguments gs_dir outdir exp capexp yyyymmdd cycl_hr area'
  return
endif

gdir=subwrd(args,1)
odir=subwrd(args,2)
smlsat=subwrd(args,3)
capsat=subwrd(args,4)
days=subwrd(args,5)
cyclhr=subwrd(args,6)
qc=subwrd(args,7)
area=subwrd(args,8)

* AOD_Smoke=>aod   0 t,z,y,x aerosol optical depth (unitless)

if (area='st')
  xsize=650
  ysize=400
else
  xsize=800
  ysize=600
endif

if (area='nyc')
  xsize=700
  ysize=650
endif
if (area='md')
  xsize=700
  ysize=650
endif
if (area='mdatl')
  xsize=700
  ysize=600
endif

'set z 1'
* 'set font 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 0. 0.2 0.4 0.6 0.8 1.0 1.5 2.0 2.5 3.0'
'set ccols 79 20 19 5 3 10 7 12 8 2 98'
'd aod'
gdir'/cbar.gs'
'draw title  HYSPLIT Mapped 'capsat' Smoke AOD 'days' 'cyclhr'Z 'qc' Quality'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/hysplit.'area'.'smlsat'.'days'.'cyclhr'.smkaod.'qc'.png png x'xsize' y'ysize' white'
'c'
