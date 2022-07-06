@/u/${USER}/IDL/my.idllib/is_h5f_invalid.pro
@/u/${USER}/IDL/my.idllib/isleapyear.pro
@/u/${USER}/IDL/my.idllib/calendar_date.pro
@/u/${USER}/IDL/my.idllib/dayofyear.pro
@/u/${USER}/IDL/my.idllib/mg_h5_getdata.pro

;  call command in idl: read_adp_goes,fname,smoke_con, dust_con
;  where fname is file name
;        smoke_con and dust_con are output smoke and dust confidences
;
 
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
pro read_adp_goes,filename,smoke_con,dust_con

   idum1=-999L

   dust = read_abi_var(filename,'Dust',0)
   Smoke = read_abi_var(filename,'Smoke',0)
   DQF=read_abi_var(filename,'DQF',0)
   
   smoke_con=smoke
   dust_con=dust
;confidence level for both smoke/dust (smoke_con or dust_con):
;0:-bad detection quality, 1-low confidence, 2-medium  3-high
;; DQF is 7bit  (76543210)
;; bitwire operator below to check the value of bit 2-3 i.e., 00003200  --> 2^2 (=4) and 2^3 (=8)
    tmp_mask=DQF
    idx = WHERE((((tmp_mask AND 4) EQ 4) and (tmp_mask AND 8) EQ 8) and smoke eq 1, COMPLEMENT=cidx, nc) 
       print, 'smoke_high=',nc
    IF nc GT 0 THEN smoke_con[idx] = 0 

    tmp_mask=DQF
    idx = WHERE((((tmp_mask AND 4) NE 4) and (tmp_mask AND 8) EQ 8) and smoke eq 1, COMPLEMENT=cidx, nc) 
       print, 'smoke_med=',nc
    IF nc GT 0 THEN smoke_con[idx] = 1 

    tmp_mask=DQF
    idx = WHERE((((tmp_mask AND 4) NE 4) and (tmp_mask AND 8) NE 8) and smoke eq 1, COMPLEMENT=cidx, nc) 
       print, 'smoke_low=',nc
    IF nc GT 0 THEN smoke_con[idx] = 2 

;; bitwire operator below to check the value of bit 4-5, i.e., 00540000  --> 2^4 (=16) and 2^5 (=32)
   tmp_mask=DQF
    idx = WHERE((((tmp_mask AND 16) EQ 16) and (tmp_mask AND 32) EQ 32) and dust eq 1, COMPLEMENT=cidx, nc) 
      ;print, nc
    IF nc GT 0 THEN dust_con[idx] = 0 

    tmp_mask=DQF
   idx = WHERE((((tmp_mask AND 16) NE 16) and (tmp_mask AND 32) EQ 32) and dust eq 1, COMPLEMENT=cidx, nc) 
      ;print, nc
   IF nc GT 0 THEN dust_con[idx] = 1
   tmp_mask=DQF
    idx = WHERE((((tmp_mask AND 16) NE 16) and (tmp_mask AND 32) NE 32) and dust eq 1, COMPLEMENT=cidx, nc)
       ;print, nc
    IF nc GT 0 THEN dust_con[idx] = 2

   tmp_mask=DQF
   idx = WHERE(((tmp_mask AND 1) EQ 1), COMPLEMENT=cidx, nc)

    IF nc GT 0 THEN smoke_con[idx] = 3

    tmp_mask=DQF
    idx = WHERE(((tmp_mask AND 2) EQ 2), COMPLEMENT=cidx, nc)
    IF nc GT 0 THEN dust_con[idx] = 3
; bit 6 (sunglint)
    tmp_mask=DQF
    idx = WHERE(((tmp_mask AND 64) EQ 64), COMPLEMENT=cidx, nc)
    IF nc GT 0 THEN smoke_con[idx] = 3
    IF nc GT 0 THEN dust_con[idx] = 3

;Byte1, bit7 (solar and satellite angles)
    tmp_mask=DQF
    idx = WHERE(((tmp_mask AND 128) EQ 128), COMPLEMENT=cidx, nc)
    IF nc GT 0 THEN dust_con[idx] = 3

    idx=where(smoke_con gt 3,ct)
    smoke_con(idx)=0b

    idx=where(dust_con gt 3,ct)
    dust_con(idx)=0b
end

