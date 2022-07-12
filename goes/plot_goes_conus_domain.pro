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
   id = ncdf_open(filename, /nowrite)
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
   
   flag_check=0B
   if flag_check then begin
      aodmax=max(unscaled,ilocmax)
      aodmin=min(unscaled,ilocmin)
      print, 'Valid values are maximum = '+string(aodmax,'(f12.4)')+'   minimum = '+string(aodmin,'(f12.4)')
         
      indexT=where(unscaled gt 0., nidx)
      if nidx gt 0L then begin
         print, 'number of AOD > 0 is '+string(nidx,'(i10)')
         aod_test=unscaled[indexT]
         aodmax=max(unscaled[indexT],ilocmax)
         aodmin=min(unscaled[indexT],ilocmin)
         print, 'maximum = '+string(aodmax,'(f12.4)')+'   minimum = '+string(aodmin,'(f12.4)')
      endif
         
      indexT=where(unscaled eq 0., nidx)
      if nidx gt 0L then begin
         print, 'number of AOD = 0 is '+string(nidx,'(i10)')
      endif
         
      indexT=where(unscaled lt 0., nidx)
      if nidx gt 0L then begin
         print, 'number of AOD < 0 is '+string(nidx,'(i10)')
         aod_test=unscaled[indexT]
         aodmax=max(unscaled[indexT],ilocmax)
         aodmin=min(unscaled[indexT],ilocmin)
         print, 'maximum = '+string(aodmax,'(f12.4)')+'   minimum = '+string(aodmin,'(f12.4)')
      endif
   endif
   ; now we need to see if 'scale_factor' is any of the attributes
   
   num_attr = test.Natts
   data_type = test.datatype
   
   if (scaled eq 1) then begin
       ncdf_attget,id, v_id, 'valid_range', valid_range
       ncdf_attget,id, v_id, 'scale_factor', scale_factor
       ncdf_attget,id, v_id, 'add_offset', add_offset
       ncdf_attget,id, v_id, '_FillValue', Fill_value
   
       index = WHERE(unscaled EQ Fill_value, count) 
       ;fixed the issue for unsigned integer by idl reading as signed integer
       unscaled=uint(unscaled)
       temp=unscaled
       valid_range=uint(valid_range)
       print,'valid_range,',valid_range
       temp = (temp * scale_factor[0]) + add_offset[0]
       unscaled = float(temp)
       if (count gt 0) then unscaled(index) = -999.0
   endif
   
   ncdf_close, id
   return, unscaled
end
pro  plot_goes_conus_domain
   ;; overwrite default values in viirs_aer.h
   ; Image Position
   ImagePosition    = [0.06, 0.15, 0.95, 0.90]       ;; x0, y0, x1, y1
   ;; set_viewport, ImagePosition[0L], ImagePosition[2L], ImagePosition[1L], ImagePosition[3L]

   ; Colarbar Position
   colorbarPosition = [0.06, 0.07, 0.95, 0.09]      ;; x0, y0, x1, y1

   center = [0., 0.]
   latlonglimits = [-90., -180. ,90., 180.]         ;; lat0, lon0, lat1, lon1
   latlonglimits = [0., -180. ,90., -45.]         ;; lat0, lon0, lat1, lon1
   latlonglimits = [15., -150. ,65., -50.]         ;; lat0, lon0, lat1, lon1
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
   title_size = 2.5
   label_size = 2.0
   axis_size  = 1.5
   ; missing values
   MISVAL_F32 = -999.999
   MISVAL_INT = 253
   MISVAL_INT16 = 65532
   range = [0.,3.]


   set_viewport, ImagePosition[0L], ImagePosition[2L], ImagePosition[1L], ImagePosition[3L]

   idum1 = -999L

               Set_Plot, 'Z'
               ;; Device,Set_Resolution=[image_xsize,image_ysize], set_font='Times', /tt_font
               Device,Set_Resolution=[image_xsize,image_ysize], set_character_size=[6,9],set_font='Helvetica',/tt_font
               ;; the following call set balck=255, white=254, gold=253, non-white=0
               satellite_colorscale, r, g, b
   nx=2500L
   ny=1500L
   IF 1L EQ 1L THEN BEGIN
      lat2km=fltarr(nx,ny)
      lon2km=fltarr(nx,ny)
      aod2km=fltarr(nx,ny)
      llfname='/lfs/h2/emc/physics/noscrub/${USER}/GOES16_GEO/g16_conus_latlon_2km_20180620.dat'

      openr,ilun,llfname,/get_lun,/compress
      readu,ilun,lat2km
      readu,ilun,lon2km
      free_lun,ilun

      aod2km=1.
   ENDIF ELSE BEGIN
      fname='/lfs/h2/emc/physics/noscrub/${USER}/GOES16_GEO/ABI_GOESR_GOES-East_Full_Disk_2km_latlon_grid.nc'
      fname='/lfs/h2/emc/physics/noscrub/${USER}/GOES16_GEO/latlon_L2_conus.nc'
      lat2km=read_abi_var(fname,'latitude',0)
      lon2km=read_abi_var(fname,'longitude',0)
      aod2km=lon2km
      aod2km=1.
   ENDELSE
idx=where(lat2km EQ -999., nidx)
if nidx gt 0L then print, 'number of lat2km = -999. is '+strtrim(nidx)
idx=where(lat2km NE -999., nidx)
if nidx GT 0L then begin
   latval=lat2km[idx]
   idx=where((latval GT 90.) or (latval lt -90.), nidx)
   if nidx gt 0L then begin
      print, 'Exclude value = -999., # lat2km not in [-90., 90.] is '+strtrim(nidx)
      print, latval[idx]
   endif
   idx=where((latval le 90.) and (latval ge -90.), nidx)
   if nidx gt 0L then begin
      pmaxlat=max(latval[idx],ilat0)
      pminlat=min(latval[idx],ilat1)
      print, 'For LAT in [-90.,90] minlat maxlat '+string(pminlat,'(f10.4)')+' '+string(pmaxlat,'(f10.4)')
   endif
endif
idx=where(lon2km EQ -999., nidx)
if nidx gt 0L then print, 'number of lon2km = -999. is '+strtrim(nidx)
idx=where(lon2km NE -999., nidx)
if nidx GT 0L then begin
   lonval=lon2km[idx]
   idx=where((lonval GT 180.) or (lonval lt -180.), nidx)
   if nidx gt 0L then begin
      print, 'Exclude value = -999., # lon2km not in [-180., 180.] is '+strtrim(nidx)
      print, lonval[idx]
   endif
   idx=where((lonval le 180.) and (lonval ge -180.), nidx)
   if nidx gt 0L then begin
      pmaxlon=max(lonval[idx],ilon0)
      pminlon=min(lonval[idx],ilon1)
      print, 'For LON in [-180.,180] minlon, maxlon '+string(pminlon,'(f10.4)')+' '+string(pmaxlon,'(f10.4)')
   endif
endif


                  ipen=255
                  map_set, 0., 0., limit=latlonglimits, /Cylindrical, color=ipen
                  ;; map_set, 0., 0., limit=latlonglimits, /Cylindrical, /noborder, color=ipen
                  ;; map_continents, /hires, color=ipen
                  ;; map_continents, /hires, /countries, /coasts, color=ipen
                  MAP_CONTINENTS, /CONTINENTS, /USA, /countries, /HIRES, color=iline
               label_interval=15.
               int_interval=long(label_interval)
               ; plot the axis label by every 15 degree
               nflon = long((latlonglimits[3L]-latlonglimits[1L])/label_interval)+1L
               xtickv = INDGEN(nflon)*int_interval + long(latlonglimits[1L])
               xtickname = '!17'+STRTRIM(ABS(xtickv),2)
               westInd = WHERE(xtickv LT 0, count)
               IF count GT 0 THEN xtickname[westInd] = xtickname[westInd]+'!Uo!NW'
               eastInd = WHERE(xtickv GT 0, count)
               IF count GT 0 THEN xtickname[eastInd] = xtickname[eastInd]+'!Uo!NE'
               nflat = long((latlonglimits[2L]-latlonglimits[0L])/label_interval)+1L
               ytickv = INDGEN(nflat)*int_interval + long(latlonglimits[0L])
               ytickname = '!17'+STRTRIM(ABS(ytickv),2)
               northInd = WHERE(ytickv GT 0, count)
               IF count GT 0 THEN ytickname[northInd] = ytickname[northInd]+'!Uo!NN'
               southInd = WHERE(ytickv LT 0, count)
               IF count GT 0 THEN ytickname[southInd] = ytickname[southInd]+'!Uo!NS'

               FOR i = 0L, nflon - 1L  DO BEGIN
                 xx=xtickv[i]
                 yy=long(latlonglimits[0L])
                 p = convert_coord( xx, yy, /data, /to_normal )
                 xyouts, p[0], p[1] - 0.03 , xtickname[i], /normal, alignment=0.5, charsize=axis_size, font=1, color=ipen
               ENDFOR
               FOR i = 0L, nflat - 1L  DO BEGIN
                 xx=long(latlonglimits[1L])
                 yy=ytickv[i]
                 p = convert_coord( xx, yy, /data, /to_normal )
                 xyouts, p[0]-0.03, p[1], ytickname[i], /normal, alignment=0.5, charsize=axis_size, font=1, color=ipen
               ENDFOR
               nv = 6L
               ctbfmt = '(F4.1)'
               COLORBAR,position = colorbarPosition, $
                        divisions = nv, range = range, CHARSIZE = label_size, Font = 1, $
                        format = ctbfmt, NCOLORS = !d.table_size-4, BOTTOM = 1, COLOR = ipen
               background = TVRD()
               background_pixels = Where(background > 0B, nb)

               ;- create resampled byte image
               p = convert_coord( lon2km, lat2km, /data, /to_normal )
               ;; newimage = replicate( 254B, image_xsize, image_ysize)
               newimage = replicate( 0B, image_xsize, image_ysize)
               newimage( p( 0, * ) * ( image_xsize - 1 ), p( 1, * ) * ( image_ysize - 1 ) ) = $
                         bytscl( aod2km, min = float(range[0]), max = float(range[1]), top = !d.table_size - 5 ) + 1B
               image = float(aod2km)
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

              aot_plot='test.g16.conus.domain.png'
                  WRITE_PNG, aot_plot, newimage,r,g,b
                  ;; Close device AND return to system device
                  DEVICE, /CLOSE
end

