function drawpm25maxplot(args)

if (args='')
  prompt 'input arguments gs_dir outdir exp capexp yyyymmdd cycl_hr prod num_day hr-range area'
  return
endif

gdir=subwrd(args,1)
odir=subwrd(args,2)
run=subwrd(args,3)
exp=subwrd(args,4)
days=subwrd(args,5)
cyclhr=subwrd(args,6)
prod=subwrd(args,7)
range1=subwrd(args,8)
range2=subwrd(args,9)
pvar=subwrd(args,10)
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
*'set clevs 3. 6. 9. 12. 15. 18. 35. 55. 100.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
*'d PDMAX1sig1'
'd 'pvar
gdir'/cbar.gs'
'set font 1'
'draw title 'exp' 'days' 'cyclhr'\ 'range1' 'prod' (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'prod'.day1.k1.gif gif x'xsize' y'ysize' white'
'c'
'set t 2'
'set z 1'
*'set clevs 3. 6. 9. 12. 15. 18. 35. 55. 100.'
*'set ccols 79 19 17 3 10 7 12 8 2 98'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd 'pvar
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\ 'range2' 'prod' (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'prod'.day2.k1.gif gif x'xsize' y'ysize' white'
'c'
