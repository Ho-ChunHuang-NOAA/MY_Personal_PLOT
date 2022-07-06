pro read_latlon,ch,lat2km,lon2km

   if ch eq 0 then begin
     nx=2500L
     ny=1500L
     llfname='/lfs/h2/emc/physics/noscrub/${USER}/GOES16_AOD/g16_conus_latlon_2km_20180620.dat'
   endif else begin
     nx=10848L/2L
     ny=10848L/2L
     llfname='g16_fdisk_latlon_2km.dat.gz'
   endelse

   lat2km=fltarr(nx,ny)
   lon2km=fltarr(nx,ny)

   openr,ilun,llfname,/get_lun,/compress
   readu,ilun,lat2km
   readu,ilun,lon2km
   free_lun,ilun

   print,lat2km(2000L,500L),lon2km(2000L,500L)

end
