@/u/${USER}/IDL/my.idllib/is_h5f_invalid.pro
@/u/${USER}/IDL/my.idllib/isleapyear.pro
@/u/${USER}/IDL/my.idllib/calendar_date.pro
@/u/${USER}/IDL/my.idllib/dayofyear.pro
@/u/${USER}/IDL/my.idllib/sym.pro
@/u/${USER}/IDL/my.idllib/mg_h5_getdata.pro
@/u/${USER}/IDL/my.idllib/satellite_colorproductmap.pro
@/u/${USER}/IDL/my.idllib/satellite_colorscale.pro
@/u/${USER}/IDL/my.idllib/satellite_colorscale2.pro
@/u/${USER}/IDL/my.idllib/satellite_setup_display.pro
@/u/${USER}/IDL/my.idllib/colorbar.pro

function read_abi_var,filename,var_name, scaled
   print, filename
   id = ncdf_open(filename)
   v_id = ncdf_varid(id, var_name)
   
   if (v_id eq -1) then begin
   print, var_name + " does not exist"
   return, -1
   endif
   
   long_name = ' '
   
   ;ncdf_attget,id, v_id, 'long_name', long_name
   print, "Getting " + string(var_name)
   
   ncdf_varget,id, v_id, unscaled ; stored data
   test = NCDF_VARINQ(id, v_id)
   
   ; now we need to see if 'scale_factor' is any of the attributes
   
   num_attr = test.Natts
   data_type = test.datatype
   
   if (scaled eq 1) then begin
       ncdf_attget,id, v_id, 'scale_factor', scale_factor
       ncdf_attget,id, v_id, 'add_offset', add_offset
       ncdf_attget,id, v_id, '_FillValue', Fill_value
   
       temp =unscaled
           unscaled = (temp * scale_factor) + add_offset
           index = where(temp eq Fill_value, count)
           if (count gt 0) then unscaled(index) = -999.0
   endif
   
   ncdf_close, id
   return, unscaled
end
pro read_aod_goes
   ;; overwrite default values in viirs_aer.h
   ; Image Position
   ImagePosition    = [0.06, 0.15, 0.95, 0.90]       ;; x0, y0, x1, y1
   ;; set_viewport, ImagePosition[0L], ImagePosition[2L], ImagePosition[1L], ImagePosition[3L]

   ; Colarbar Position
   colorbarPosition = [0.06, 0.07, 0.95, 0.09]      ;; x0, y0, x1, y1

   center = [0., 0.]
   latlonglimits = [-90., -180. ,90., 180.]         ;; lat0, lon0, lat1, lon1
   latlonglimits = [0., -180. ,90., -45.]         ;; lat0, lon0, lat1, lon1
   image_xsize = 1500 ; pixels
   image_ysize = 900 ; pixels
   image_xsize = 650 ; pixels
   image_ysize = 390 ; pixels
   image_xsize = 950 ; pixels
   image_ysize = 570 ; pixels
   image_xsize = 650 ; pixels
   image_ysize = 650 ; pixels
   Large_Frame=0B
   Medium_Frame=0B
   Small_Frame=0B
   title_size = 2.5
   label_size = 2.0
   axis_size  = 1.4
   IF image_xsize EQ 1500. AND image_ysize EQ 900. THEN BEGIN
      title_size = 5.0
      label_size = 4.0
      axis_size  = 0.4
      Large_Frame=1B
   ENDIF
   IF image_xsize EQ 950. AND image_ysize EQ 570. THEN BEGIN
      title_size = 3.5
      label_size = 2.5
      axis_size  = 0.3
      Medium_Frame=1B
   ENDIF
   IF image_xsize EQ 650. AND image_ysize EQ 390. THEN BEGIN
      title_size = 2.5
      label_size = 1.8
      axis_size  = 0.3
      Small_Frame=1B
   ENDIF
   ; missing values
   MISVAL_F32 = -999.999
   MISVAL_INT = 253
   MISVAL_INT16 = 65532
   range = [0.,1.]


   set_viewport, ImagePosition[0L], ImagePosition[2L], ImagePosition[1L], ImagePosition[3L]

   idum1 = -999L

               Set_Plot, 'Z'
               ;; Device,Set_Resolution=[image_xsize,image_ysize], set_font='Times', /tt_font
               Device,Set_Resolution=[image_xsize,image_ysize], set_character_size=[6,9],set_font='Helvetica',/tt_font
               ;; the following call set balck=255, white=254, gold=253, non-white=0
               satellite_colorscale, r, g, b
   nx=2500L
   ny=1500L
   lat2km=fltarr(nx,ny)
   lon2km=fltarr(nx,ny)
   llfname='/gpfs/dell2/emc/modeling/noscrub/${USER}/GOES16_GEO/g16_conus_latlon_2km_20180620.dat'

   openr,ilun,llfname,/get_lun,/compress
   readu,ilun,lat2km
   readu,ilun,lon2km
   free_lun,ilun

   fname='/gpfs/${phase12_id}d3/emc/meso/noscrub/${USER}/GOES16_AOD/AOD/DR_ABI-L2-AODC-M3_G16_s20180211802203_e20180211804576_c20180211807552.nc'
   aod=read_abi_var(fname,'AOD',1)
   ;; dqf=read_abi_var(fname,'DQF',0)
   index=where(aod ne -999.0, nidx)
   IF nidx NE 0L THEN BEGIN
      g16aod=aod(index)
      g16lat=lat2km(index)
      g16lon=lon2km(index)
   ENDIF
                  ipen=255
                  ;;map_set, 0., 0., limit=latlonglimits, /Cylindrical, color=ipen
                  map_set, 0., 0., limit=latlonglimits, /Cylindrical, /noborder, color=ipen
                  ;; map_continents, /hires, color=ipen
                  ;; map_continents, /hires, /countries, /coasts, color=ipen
                  MAP_CONTINENTS, /CONTINENTS, /USA, /countries, /HIRES, color=iline
               background = TVRD()
               background_pixels = Where(background > 0B, nb)

               ;- create resampled byte image
               p = convert_coord( g16lon, g16lat, /data, /to_normal )
               ;; newimage = replicate( 254B, image_xsize, image_ysize)
               newimage = replicate( 0B, image_xsize, image_ysize)
               newimage( p( 0, * ) * ( image_xsize - 1 ), p( 1, * ) * ( image_ysize - 1 ) ) = $
                         bytscl( g16aod, min = float(range[0]), max = float(range[1]), top = !d.table_size - 5 ) + 1B
               image = float(g16aod)
               fill_pixels = where(ABS(image-MISVAL_F32) LT 1.,nFill)
               image[*,*] = float(range[1L])
               if nFill gt 0 then image(fill_pixels) = float(range[0L])

               bottom_vals = replicate( 0B, image_xsize, image_ysize)
               bottom_vals( p( 0, * ) * ( image_xsize - 1 ), p( 1, * ) * ( image_ysize - 1 ) ) = $
                           bytscl( image, min = float(range[0]), max = float(range[1]), top = !d.table_size - 4 )

               beyond_scl=where((bottom_vals eq 0B),byndcnt)
               if byndcnt gt 0 then newImage[beyond_scl]=0B
               image = 0
               IF nb GT 0L THEN newImage[background_pixels] = background[background_pixels]

              aot_plot='test.g16.aod.png'
                  WRITE_PNG, aot_plot, newimage,r,g,b
                  ;; Close device AND return to system device
                  DEVICE, /CLOSE
end

