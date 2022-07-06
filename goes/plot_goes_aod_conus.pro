@/u/${USER}/IDL/my.idllib/is_h5f_invalid.pro
@/u/${USER}/IDL/my.idllib/isleapyear.pro
@/u/${USER}/IDL/my.idllib/calendar_date.pro
@/u/${USER}/IDL/my.idllib/dayofyear.pro
@/u/${USER}/IDL/my.idllib/sym.pro
@/u/${USER}/IDL/my.idllib/mg_h5_getdata.pro
@/u/${USER}/IDL/my.idllib/satellite_colorproductmap.pro
@/u/${USER}/IDL/my.idllib/satellite_colorscale.pro
;;@/u/${USER}/IDL/my.idllib/satellite_colorscale2.pro
@/u/${USER}/IDL/my.idllib/satellite_colorscalei_rainbow_no_purple.pro
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
   
   flag_check=1B
   if flag_check then begin
      ncdf_attget,id, v_id, '_FillValue', pre_Fill_value
      index = WHERE(unscaled EQ pre_Fill_value, count) 
      ;fixed the issue for unsigned integer by idl reading as signed integer
      pretemp=uint(unscaled)
      aodmax=max(pretemp,ilocmax)
      aodmin=min(pretemp,ilocmin)
      print, var_name+' Valid values are maximum = '+string(aodmax,'(f12.4)')+'   minimum = '+string(aodmin,'(f12.4)')
         
      indexT=where(pretemp gt 0., nidx)
      if nidx gt 0L then begin
         print, var_name+' number > 0 is '+string(nidx,'(i10)')
         aod_test=pretemp(indexT)
         aodmax=max(pretemp(indexT),ilocmax)
         aodmin=min(pretemp(indexT),ilocmin)
         print, var_name+' maximum = '+string(aodmax,'(f12.4)')+'   minimum = '+string(aodmin,'(f12.4)')
      endif
         
      indexT=where(pretemp eq 0., nidx)
      if nidx gt 0L then begin
         print, var_name+' number = 0 is '+string(nidx,'(i10)')
      endif
         
      indexT=where(pretemp lt 0., nidx)
      if nidx gt 0L then begin
         print, var_name+' number < 0 is '+string(nidx,'(i10)')
         aod_test=pretemp(indexT)
         aodmax=max(pretemp(indexT),ilocmax)
         aodmin=min(pretemp(indexT),ilocmin)
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
       print,var_name,' valid_range,',valid_range
       temp = (temp * scale_factor[0]) + add_offset[0]
       unscaled = float(temp)
       if (count gt 0) then unscaled(index) = -999.0
   endif
   
   ncdf_close, id
   return, unscaled
end
pro plot_goes_aod_conus
   @run.plot_goes_aod_conus.h
   print, 'Program plot_goes_aod_conus.pro START AT '+SYSTIME()
   idum1 = -999L
   ;;
   ;; check directory path with / at the end
   ;;
   idum1 = strlen(idir)
   IF strmid(idir,idum1-1L,1L) NE '/' THEN idir = idir+'/'
   idum1 = strlen(odir)
   IF strmid(odir,idum1-1L,1L) NE '/' THEN odir = odir+'/'
   ;;
   ;; overwrite default values in viirs_aer.h
   ; Image Position
   ImagePosition    = [0.06, 0.15, 0.95, 0.90]       ;; x0, y0, x1, y1
   ;; set_viewport, ImagePosition[0L], ImagePosition[2L], ImagePosition[1L], ImagePosition[3L]

   ; Colarbar Position
   colorbarPosition = [0.06, 0.07, 0.95, 0.09]      ;; x0, y0, x1, y1

   center = [0., 0.]
   ;; latlonglimits = [-90., -180. ,90., 180.]         ;; lat0, lon0, lat1, lon1
   latlonglimits = [0., -180. ,90., 0.]         ;; lat0, lon0, lat1, lon1
   latlonglimits = [15., -150. ,60., -50.]         ;; lat0, lon0, lat1, lon1
   image_xsize = 1500 ; pixels
   image_ysize = 900 ; pixels
   image_xsize = 650 ; pixels
   image_ysize = 390 ; pixels
   image_xsize = 950 ; pixels
   image_ysize = 570 ; pixels
   image_xsize = 900 ; pixels
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
   range = [0.,1.]


   set_viewport, ImagePosition[0L], ImagePosition[2L], ImagePosition[1L], ImagePosition[3L]


               Set_Plot, 'Z'
               ;; Device,Set_Resolution=[image_xsize,image_ysize], set_font='Times', /tt_font
               Device,Set_Resolution=[image_xsize,image_ysize], set_character_size=[6,9],set_font='Helvetica',/tt_font
               ;; the following call set balck=255, white=254, gold=253, non-white=0
               satellite_colorscale, r, g, b
   nx=2500L
   ny=1500L
   lat2km=fltarr(nx,ny)
   lon2km=fltarr(nx,ny)
   llfname='/lfs/h2/emc/physics/noscrub/${USER}/GOES16_GEO/g16_conus_latlon_2km_20180620.dat'

   openr,ilun,llfname,/get_lun,/compress
   readu,ilun,lat2km
   readu,ilun,lon2km
   free_lun,ilun

   nfile=n_elements(aod_files)
   FOR ifile = 0L, nfile-1L DO BEGIN
      fname=idir+aod_files[ifile]
      ;; ' /gpfs/${phase12_id}d3/emc/meso/noscrub/${USER}/GOES16_AOD/AOD/DR_ABI-L2-AODC-M3_G16_s20180211802203_e20180211804576_c20180211807552.nc'
      IF ~ File_Test(fname) THEN BEGIN
         print, 'Can not find '+fname
         continue
      ENDIF
      print, fname
      tmp = strsplit(aod_files[ifile],'_',/extract,count=cnt)
      header=strtrim(tmp[0L])
      data_name=strtrim(tmp[1L])
      satellite_name=strtrim(tmp[2L])
      start_time=strtrim(tmp[3L])
      end_time=strtrim(tmp[4L])
      center_time=strtrim(tmp[5L])
      msg=string(ifile,'(i2.2)')+' '+header+'_'+data_name+'_'+satellite_name+'_'+start_time+'_'+end_time+'_'+center_time+'.nc'
      ;; print, msg
      syear=long(strmid(start_time,1,4))
      jday=long(strmid(start_time,5,3))
      jdate=long(strmid(start_time,1,7))
      start_hr=long(strmid(start_time,8,2))
      CALENDAR_DATE, syear, jday, xmon, xday
      ;; print, string(jdate,'(i7)')+' '+string(start_hr,'(i2.2)')+'  calendar = '+string(syear,'(i4.4)')+' '+string(xmon,'(i2.2)')+' '+string(xday,'(i2.2)')
   strYYYYMMDD=string(syear,'(i4.4)')+string(xmon,'(i2.2)')+string(xday,'(i2.2)')
   strGMT=strmid(start_time,8,4)
   aod=read_abi_var(fname,'AOD',1)
   dqf=read_abi_var(fname,'DQF',0)
   index=where(aod ne -999.0, nidx)
   IF nidx NE 0L THEN BEGIN
      g16aod=aod(index)
      g16lat=lat2km(index)
      g16lon=lon2km(index)
      dqf=dqf(index)
   ENDIF
   print,'aodqf ',aodqf
   strDQF=' '
   strfile=' '
   if aodqf eq 0L then begin
      index=where(dqf eq 0L, nidx)
      strDQF='DQF=0'
      strfile='high'
   endif else begin
      if aodqf eq 1L then begin
         index=where(dqf le 1L, nidx)
         strDQF='DQF=0 or DQF=1'
         strfile='medium'
      endif else begin
         index=where(dqf le 2L, nidx)
         strDQF='DQF=0 or DQF=1 or DQF=2'
         strfile='low'
      endelse
   endelse
   IF nidx NE 0L THEN BEGIN
      g16aod=g16aod(index)
      g16lat=g16lat(index)
      g16lon=g16lon(index)
   ENDIF
   flag_check=1B
   if flag_check then begin
      aodmax=max(g16aod,ilocmax)
      aodmin=min(g16aod,ilocmin)
      print, 'Valid values are maximum = '+string(aodmax,'(f10.4)')+'   minimum = '+string(aodmin,'(f10.4)')
         
      indexT=where(g16aod gt 0., nidx)
      if nidx gt 0L then begin
         print, 'number of AOD > 0 is '+string(nidx,'(i10)')
         aod_test=g16aod(indexT)
         aodmax=max(g16aod(indexT),ilocmax)
         aodmin=min(g16aod(indexT),ilocmin)
         print, 'maximum = '+string(aodmax,'(f10.4)')+'   minimum = '+string(aodmin,'(f10.4)')
      endif
         
      indexT=where(g16aod eq 0., nidx)
      if nidx gt 0L then begin
         print, 'number of AOD = 0 is '+string(nidx,'(i10)')
      endif
         
      indexT=where(g16aod lt 0., nidx)
      if nidx gt 0L then begin
         print, 'number of AOD < 0 is '+string(nidx,'(i10)')
         aod_test=g16aod(indexT)
         aodmax=max(g16aod(indexT),ilocmax)
         aodmin=min(g16aod(indexT),ilocmin)
         print, 'maximum = '+string(aodmax,'(f10.4)')+'   minimum = '+string(aodmin,'(f10.4)')
      endif
   endif
   ;; only keep aod values with in domain of latlonglimits
   ;; latlonglimits = [15., -150. ,60., -50.]         ;; lat0, lon0, lat1, lon1
   index=where( (g16lat ge latlonglimits[0L] ) and ( g16lat le latlonglimits[2L] ), nidx)
   if nidx gt 0L then begin
      g16aod=g16aod(index)
      g16lat=g16lat(index)
      g16lon=g16lon(index)
      index=where( (g16lon ge latlonglimits[1L] ) and ( g16lon le latlonglimits[3L] ), nidx)
      if nidx gt 0L then begin
         g16aod=g16aod(index)
         g16lat=g16lat(index)
         g16lon=g16lon(index)
      endif else begin
         print, 'no valid point with in ['+strtrim(latlonglimits[1L])+','+strtrim(latlonglimits[1L])+']'
      endelse
   endif else begin
      print, 'no valid point with in ['+strtrim(latlonglimits[0L])+','+strtrim(latlonglimits[2L])+']'
   endelse
   ipen=255
   ;; map_set, 0., 0., limit=latlonglimits, /Cylindrical, /noborder, color=ipen
   map_set, 0., 0., limit=latlonglimits, /Cylindrical, color=ipen
   MAP_CONTINENTS, /CONTINENTS, /USA, /countries, /HIRES, color=iline
   figTitle = strYYYYMMDD+' '+strGMT+'Z'+' AOD!D550nm!N'+'   '+strDQF
   xyouts, 0.5,ImagePosition[3L]+0.025, figTitle, /normal, alignment=0.5, charsize=title_size, font=1, color=ipen

               label_interval=10.
               x0 = long(latlonglimits[1L])
               int_interval=long(label_interval)
               ; plot the axis label by every label_interval degree
               nflon = long((latlonglimits[3L]-latlonglimits[1L])/label_interval)+1L
               xtickv = INDGEN(nflon)*int_interval + long(latlonglimits[1L])
               xtickname = '!17'+STRTRIM(ABS(xtickv),2)
               westInd = WHERE(xtickv LT 0, count)
               IF count GT 0 THEN xtickname[westInd] = xtickname[westInd]+'!Uo!NW'
               eastInd = WHERE(xtickv GT 0, count)
               IF count GT 0 THEN xtickname[eastInd] = xtickname[eastInd]+'!Uo!NE'

               label_interval=15.
               int_interval=long(label_interval)
               y0 = long(latlonglimits[0L])
               y0 = 15L
               nflat = long((latlonglimits[2L]-latlonglimits[0L])/label_interval)+1L
               ytickv = INDGEN(nflat)*int_interval + y0
               ytickname = '!17'+STRTRIM(ABS(ytickv),2)
               northInd = WHERE(ytickv GT 0, count)
               IF count GT 0 THEN ytickname[northInd] = ytickname[northInd]+'!Uo!NN'
               southInd = WHERE(ytickv LT 0, count)
               IF count GT 0 THEN ytickname[southInd] = ytickname[southInd]+'!Uo!NS'

               FOR i = 0L, nflon - 1L  DO BEGIN
                 xx=xtickv[i]
                 yy=long(latlonglimits[0L])
                 p = convert_coord( xx, yy, /data, /to_normal )
                 xyouts, p[0L], p[1L] - 0.03 , xtickname[i], /normal, alignment=0.5, charsize=axis_size, font=1, color=ipen
               ENDFOR
               FOR i = 0L, nflat - 1L  DO BEGIN
                 xx=long(latlonglimits[1L])
                 yy=ytickv[i]
                 p = convert_coord( xx, yy, /data, /to_normal )
                 xyouts, p[0L]-0.03, p[1L], ytickname[i], /normal, alignment=0.5, charsize=axis_size, font=1, color=ipen
               ENDFOR
               nv = 5L
               ctbfmt = '(F4.1)'
               COLORBAR,position = colorbarPosition, $
                        divisions = nv, range = range, CHARSIZE = label_size, Font = 1, $
                        format = ctbfmt, NCOLORS = !d.table_size-4, BOTTOM = 1, COLOR = ipen
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

              aot_plot='g16.aod.'+string(syear,'(i4.4)')+string(xmon,'(i2.2)')+string(xday,'(i2.2)')+'_'+string(start_hr,'(i2.2)')+'.'+strfile+'.png'
                  WRITE_PNG, aot_plot, newimage,r,g,b
                  ;; Close device AND return to system device
                  DEVICE, /CLOSE
   ENDFOR
   print, 'Successfully finish.  Exit plot_goes_aod_conus.pro AT '+SYSTIME()
end

