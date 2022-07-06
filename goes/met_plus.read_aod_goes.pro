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
   nx=2500L
   ny=1500L
   lat2km=fltarr(nx,ny)
   lon2km=fltarr(nx,ny)
   llfname='/gpfs/dell2/emc/modeling/noscrub/${USER}/GOES16_GEO/g16_conus_latlon_2km_20180620.dat'

   openr,ilun,llfname,/get_lun,/compress
   readu,ilun,lat2km
   readu,ilun,lon2km
   free_lun,ilun

   fname=' /gpfs/${phase12_id}d3/emc/meso/noscrub/${USER}/GOES16_AOD/AOD/20180514/OR_ABI-L2-AODC-M3_G16_s20181341702215_e20181341704588_c20181341711418.nc'
   IF ~ File_Test(fname) THEN BEGIN
      print, 'Can not find '+fname
      continue
   ENDIF
   print, fname

   ;; Retrieve AOD
   aod=read_abi_var(fname,'AOD',1)

   ;; Retrieve AOD Quality Flag  0: high, 1: medium, 2: low, 3: not retrieved
   dqf=read_abi_var(fname,'DQF',0)

   ;; filter AOD based on Missing Value, this one can be skiiped if using QF < 3 alone for filtering
   index=where(aod ne -999.0, nidx)
   IF nidx NE 0L THEN BEGIN
      g16aod=aod(index)
      g16lat=lat2km(index)
      g16lon=lon2km(index)
      dqf=dqf(index)
   ENDIF
   strDQF=' '
   strfile=' '
   ;; filter again based on Quality Flag
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
end

