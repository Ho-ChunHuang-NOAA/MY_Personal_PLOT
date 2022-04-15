function draw_pm25_plot(args)

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

* A25sig 22 207,107,0 ** (profile) Unspecified Anthropogenic Particulates ▒~I▒ 2.5 μm Diameter [μg/m^3]m^
* AECsig 22 206,107,0 ** (profile) Elemental Carbon Particulates ▒~I▒ 2.5 μm Diameter [μg/m^3]m^
* AH2Osig 22 208,107,0 ** (profile) Water Particulates ▒~I▒ 2.5 μm Diameter [μg/m^3]m^
* ALD2sig 22 167,107,0 ** (profile) Acetaldehyde & Higher Aldehydes [ppbV]
* ANH4sig 22 201,107,0 ** (profile) Ammonia (NH4) Particulates ▒~I▒ 2.5 μm Diameter [μg/m^3]m^
* ANO3sig 22 202,107,0 ** (profile) Nitrate (NO3) Particulates ▒~I▒ 2.5 μm Diameter [μg/m^3]m^
* AORGAsig 22 203,107,0 ** (profile) Organic Particulates ▒~I▒ 2.5 μm Diameter [μg/m^3]m^
* AORGBsig 22 205,107,0 ** (profile) Biogenically Originated Particulates ▒~I▒ 2.5 μm Diameter [μg/m^3]m^
* AORGPAsig 22 204,107,0 ** (profile) Primarily Organic Particulates ▒~I▒ 2.5 μm Diameter [μg/m^3]m^
* ASO4sig 22 200,107,0 ** (profile) Sulfate (SO4) Particulates ▒~I▒ 2.5 μm Diameter [μg/m^3]m^
* COsig 22 148,107,0 ** (profile) Carbon Monoxide [ppbV]
* FORMsig 22 166,107,0 ** (profile) Formaldehyde [ppbV]
* HNO3sig 22 144,107,0 ** (profile) Nitric Acid [ppbV]
* HONOsig 22 147,107,0 ** (profile) Nitrous Acid [ppbV]
* N2O5sig 22 143,107,0 ** (profile) Nitrogen Pentoxide [ppbV]
* NO2sig 22 142,107,0 ** (profile) Nitrogen Dioxide [ppbV]
* NO3sig 22 145,107,0 ** (profile) Nitrogen Trioxide [ppbV]
* NOsig 22 141,107,0 ** (profile) Nitrogen Oxide [ppbV]
* NTRsig 22 173,107,0 ** (profile) Lumped Gaseous Organic Nitrate [ppbV]
* NUMACCsig 22 223,107,0 ** (profile) Number Concentration Particulates between 2.5 and 2.5 μm Diameter [number/m^3]m
* NUMATKNsig 22 222,107,0 ** (profile) Number Concentration Particulates between 2.5 and 0.1 μm Diameter [number/m^3]m
* OZCONsig 22 180,107,0 ** (profile) Ozone concentration [ppb]
* PANsig 22 172,107,0 ** (profile) Peroxyacyl Nitrate [ppbV]
* PNAsig 22 146,107,0 ** (profile) Peroxynitric Acid [ppbV]
* SO2sig 22 232,107,0 ** (profile) Sulfur Dioxide [ppbV]
* SRFACCsig 22 229,107,0 ** (profile) Surface Area Contributed by Particulates between 0.1 and 2.5 μm Diameter [m2/m^3]m
* SRFATKNsig 22 228,107,0 ** (profile) Surface Area Contributed by Particulates ▒~I▒ 0.1 μm Diameter [m2/m^3]m

if (area='st')
  xsize=650
  ysize=400
else
  xsize=800
  ysize=600
endif

'set z 1'
'set font 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd A25sig+var196sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' A25  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.A25.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd AECsig+var195sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' AEC  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.AEC.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd AH2Osig+var211sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' AH2O  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.AH2O.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd ALD2sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' ALD2  sfc_conc (ppbV)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.ALD2.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd ANH4sig+var190sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' ANH4  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.ANH4.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd ANO3sig+var191sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' ANO3  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.ANO3.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd AORGAsig+var192sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' AORGA  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.AORGA.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd AORGBsig+var194sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' AORGB  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.AORGB.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd AORGPAsig+var193sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' AORGPA  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.AORGPA.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd ASO4sig+var189sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' ASO4  sfc_conc (ug/m3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.ASO4.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
*'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100. 200. 300. 500. 750.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd COsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' CO  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.CO.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd FORMsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' FORM  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.FORM.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd HNO3sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' HNO3  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.HNO3.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd HONOsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' HONO  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.HONO.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd N2O5sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' N2O5  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.N2O5.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd NO2sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' NO2  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.NO2.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd NO3sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' NO3  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.NO3.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd NOsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' NO  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.NO.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd NTRsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' NTR  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.NTR.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd NUMACCsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' NUMACC  sfc_nump (number/m^3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.NUMACC.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd NUMATKNsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' NUMATKN  sfc_nump (number/m^3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.NUMATKN.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd OZCONsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' OZCON  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.OZCON.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd PANsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PAN  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.PAN.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd PNAsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' PNA  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.PNA.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs  10. 44.  52. 60. 68. 76. 84.  92. 100.'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd SO2sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' SO2  sfc_conc (ppbv)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.SO2.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd SRFACCsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' SRFACC  sfc_area (m2/m^3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.SRFACC.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd SRFATKNsig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' SRFATKN  sfc_area (m2/m^3)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.SRFATKN.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd var181sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' XO2N sfc_conc (undefined)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.var181.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd var189sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' ASO4I   sfc_conc (undefined)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.var189.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd var190sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' ANH4I   sfc_conc (undefined)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.var190.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd var191sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' ANO3I   sfc_conc (undefined)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.var191.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd var192sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' AORGAI  sfc_conc (undefined)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.var192.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd var193sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' AORGPAI sfc_conc (undefined)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.var193.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd var194sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' AORGBI  sfc_conc (undefined)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.var194.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd var195sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' AECI    sfc_conc (undefined)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.var195.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd var196sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' A25I    sfc_conc (undefined)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.var196.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs 3  6  9  12 25 35 45 55 65 75 85 95 105'
'set ccols 79 20 19 18 17  5  3 10  7 12  8  2   6 98'
'd var211sig'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' AH2OI   sfc_conc (undefined)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.var211.k1.gif gif x'xsize' y'ysize' white'
'c'
