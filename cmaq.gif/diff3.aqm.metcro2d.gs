function diff_pm25_plot(args)

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

* PRSFC=>prsfc   0 t,z,y,x surface pressure (Pascal)
* JACOBS=>jacobs   0 t,z,y,x total Jacobian at surface (M)
* USTAR=>ustar   0 t,z,y,x cell averaged friction velocity (M/S)
* WSTAR=>wstar   0 t,z,y,x convective velocity scale (M/S)
* PBL=>pbl   0 t,z,y,x PBL height (M)
* ZRUF=>zruf   0 t,z,y,x surface rouhness length (M)
* MOLI=>moli   0 t,z,y,x inverse of Monin-Obukhov length (1/M)
* HFX=>hfx   0 t,z,y,x sensible heat flux (WATTS/M**2)
* QFX=>qfx   0 t,z,y,x latent heat flux (WATTS/M**2)
* RADYNI=>radyni   0 t,z,y,x inverse of aerodynaic resistance (M/S)
* RBNDYI=>rbndyi   0 t,z,y,x inverse laminar bnd layer resistance (M/S)
* RSTOMI=>rstomi   0 t,z,y,x inverse of bulk stomatal resistance (M/S)
* TEMPG=>tempg   0 t,z,y,x skin temperature at ground (K)
* TEMP2=>temp2   0 t,z,y,x air temperature at 2 m (K)
* WSPD10=>wspd10   0 t,z,y,x wind speed at 10 m (M/S)
* WDIR10=>wdir10   0 t,z,y,x wind direction at 10 m (DEGREES)
* GLW=>glw   0 t,z,y,x longwave radiation at ground (WATTS/M**2)
* GSW=>gsw   0 t,z,y,x solar radiation absorbed at ground (WATTS/M**2)
* RGRND=>rgrnd   0 t,z,y,x solar rad reaching sfc (WATTS/M**2)
* RN=>rn   0 t,z,y,x nonconvec. pcpn per met TSTEP (CM)
* RC=>rc   0 t,z,y,x convective pcpn per met TSTEP (CM)
* CFRAC=>cfrac   0 t,z,y,x total cloud fraction (FRACTION)
* CLDT=>cldt   0 t,z,y,x cloud top layer height (m) (M)
* CLDB=>cldb   0 t,z,y,x cloud bottom layer height (m) (M)
* WBAR=>wbar   0 t,z,y,x avg. liquid water content of cloud (G/M**3)
* TROP=>trop   0 t,z,y,x tropopause height (Pascal)
* ATTEN_X=>atten_x   0 t,z,y,x radiation attenuation fctr, off-line (DIM-LESS)
* ATTEN=>atten   0 t,z,y,x radiation attenuation factor (DIM-LESS)
* CSRAD=>csrad   0 t,z,y,x dnward srfc clear-sky SW, off-line (WATTS/M**2)
* CSWTOA=>cswtoa   0 t,z,y,x dnward TOA SW, off-line (WATTS/M**2)
* CSUSF=>csusf   0 t,z,y,x upward surface clear-sky SW (Eta) (WATTS/M**2)
* CSDSF=>csdsf   0 t,z,y,x downward surface clear-sky SW (Eta) (WATTS/M**2)
* PSCCB=>psccb   0 t,z,y,x shallow convective cloud bottom (Pascal)
* PSCCT=>pscct   0 t,z,y,x shallow convective cloud top (Pascal)
* PDCCB=>pdccb   0 t,z,y,x deep convective cloud bottom (Pascal)
* PDCCT=>pdcct   0 t,z,y,x deep convective cloud top (Pascal)
* PTCCB=>ptccb   0 t,z,y,x convective cloud bottom (Pascal)
* PTCCT=>ptcct   0 t,z,y,x convective cloud top (Pascal)
* PBL2=>pbl2   0 t,z,y,x PBL height, ACM2 based Richardson # (M)
* PBLR=>pblr   0 t,z,y,x PBL height, NCEP based Richardson # (M)
* MIXHT=>mixht   0 t,z,y,x Mixed layer depth [m] (M)
* SOTYP=>sotyp   0 t,z,y,x soil type (DIM_LESS)
* SOILW=>soilw   0 t,z,y,x volumetric soil moisture content (fraction)
* LAI=>lai   0 t,z,y,x Leaf Area Index(non-dim) (DIM_LESS)
* SNOWC=>snowc   0 t,z,y,x Snow Cover (fraction)
* SNOCOV=>snocov   0 t,z,y,x Snow Cover (DECIMAL)
* VEG=>veg   0 t,z,y,x Vegetaion (DECIMAL)
* Q2=>q2   0 t,z,y,x mixing ratio at 2 m (KG/KG)
* WR=>wr   0 t,z,y,x canopy moisture content (M)
* SOIM1=>soim1   0 t,z,y,x volumetric soil moisture in top cm (M**3/M**3)
* SOIM2=>soim2   0 t,z,y,x volumetric soil moisture in top m (M**3/M**3)
* SOIT1=>soit1   0 t,z,y,x soil temperature in top cm (K)
* SOIT2=>soit2   0 t,z,y,x soil temperature in top m (K)
* SLTYP=>sltyp   0 t,z,y,x soil textture type by USDA category (DIM_LESS)
* SEAICE=>seaice   0 t,z,y,x sea ice fraction (fraction)
* VD_SO2=>vd_so2   0 t,z,y,x deposition velocity for species SO2 (M/S)
* VD_SULF=>vd_sulf   0 t,z,y,x deposition velocity for species SULF (M/S)
* VD_NO2=>vd_no2   0 t,z,y,x deposition velocity for species NO2 (M/S)
* VD_NO=>vd_no   0 t,z,y,x deposition velocity for species NO (M/S)
* VD_O3=>vd_o3   0 t,z,y,x deposition velocity for species O3 (M/S)
* VD_HNO3=>vd_hno3   0 t,z,y,x deposition velocity for species HNO3 (M/S)
* VD_H2O2=>vd_h2o2   0 t,z,y,x deposition velocity for species H2O2 (M/S)
* VD_ALD=>vd_ald   0 t,z,y,x deposition velocity for species ALD (M/S)
* VD_HCHO=>vd_hcho   0 t,z,y,x deposition velocity for species HCHO (M/S)
* VD_OP=>vd_op   0 t,z,y,x deposition velocity for species OP (M/S)
* VD_PAA=>vd_paa   0 t,z,y,x deposition velocity for species PAA (M/S)
* VD_ORA=>vd_ora   0 t,z,y,x deposition velocity for species ORA (M/S)
* VD_NH3=>vd_nh3   0 t,z,y,x deposition velocity for species NH3 (M/S)
* VD_PAN=>vd_pan   0 t,z,y,x deposition velocity for species PAN (M/S)
* VD_HONO=>vd_hono   0 t,z,y,x deposition velocity for species HONO (M/S)
* VD_CO=>vd_co   0 t,z,y,x deposition velocity for species CO (M/S)
* VD_METHANOL=>vd_methanol   0 t,z,y,x deposition velocity for species METHANOL (M/S)
* VD_N2O5=>vd_n2o5   0 t,z,y,x deposition velocity for species N2O5 (M/S)
* VD_NO3=>vd_no3   0 t,z,y,x deposition velocity for species NO3 (M/S)
* VD_GEN_ALD=>vd_gen_ald   0 t,z,y,x deposition velocity for species GEN_ALD (M/S)

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
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pbl2.2-pbl2.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' CMAQ PBL height (M)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pbl2.k1.gif gif x'xsize' y'ysize' white'
'c'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pbl.2-pbl.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' NAM PBL height (M)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pbl.k1.gif gif x'xsize' y'ysize' white'
'c'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd pblr.2-pblr.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' NCEP RICH PBL height (M)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.pblr.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
*'set clevs 1. 9. 12. 15. 18. 35. 55. 100. 200.'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd rgrnd.2-rgrnd.1'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' solar rad reaching sfc (WATTS/M**2)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.swrad.k1.gif gif x'xsize' y'ysize' white'
'c'
'set z 1'
'set clevs -60. -40. -20. -10. -5. -1. 1. 5. 10. 20. 40. 60.'
'set ccols 99 88 16 18 19 20 0 54 53 52 2 49 48'
'd (cfrac.2-cfrac.1)*100'
gdir'/cbar.gs'
'draw title 'exp' 'days' 'cyclhr'\'vldhr' total cloud cover  (%)'
if(area='st')
'draw.cmaq.box.st.gs'
endif
'printim 'odir'/aqm.'area'.'run'.'days'.'cyclhr'.'fcsthr'.cldc.k1.gif gif x'xsize' y'ysize' white'
'c'
