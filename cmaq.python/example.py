cycle=[ "t12z" ]   ## as an example
date=sdate
while date <= edate:
    for cyc in cycle:
        msg=datetime.datetime.now()
        aqmfilein=comout+"/cs."+date.strftime(YMD_date_format)+"/aqm."+cyc+".aconc_sfc.ncf"
        if os.path.exists(aqmfilein):
            print(aqmfilein+" exists")
            cs_aqm = netcdf.Dataset(aqmfilein)

            cs_var = cs_aqm.variables['TFLAG'][:,0,:]
            nstep=len(cs_var)   ## shoule be the same as tmax below

            no2_cs = cs_aqm.variables['NO2'][:,0,:,:]
            cs_aqm.close()

            tmax=no2_cs.shape[0]
            jmax=no2_cs.shape[1]
            imax=no2_cs.shape[2]
            print('"Dimension 0 is %d"' % (tmax))
            print('"Dimension 1 is %d"' % (jmax))
            print('"Dimension 2 is %d"' % (imax))
            max_no2=np.amax(no2_cs)
            min_no2=np.amin(no2_cs)
            print('"MAX of NO2 is  %f"' % (max_no2))
            print('"MIN of NO2 is  %f"' % (min_no2))
            result = np.where(no2_cs == np.amax(no2_cs))
            nidx=result[0]   # is an array
            jidx=result[1]   # is an array
            iidx=result[2]   # is an array
            print(nidx[0])   # only one will be found, can be more than if not unique
            print(jidx[0])   # only one will be found, can be more than if not unique
            print(iidx[0])   # only one will be found, can be more than if not unique
            mld_max_no2=no2_cs[61][169][369]   # to double check the number from result[*] number
            print('"CONC of NO2 is            %f"' % (no2_cs[nidx[0]][jidx[0]][iidx[0]]))
            print('"Asssigned CONC of NO2 is  %f"' % (no2_cs[61][169][369]))
            for n in range(0,tmax):
                print("===================")
                no2_2d=no2_cs[n,:,:]
                print("n = "+str(n)+"  no2 = "+str(no2_2d[mdl_j][mdl_i]))
                max_no2_2d=np.amax(no2_2d)
                min_no2_2d=np.amin(no2_2d)
                print('"MAX of NO2 is  %f"' % (max_no2_2d))
                print('"MIN of NO2 is  %f"' % (min_no2_2d))
                result = np.where(no2_2d == np.amax(no2_2d))
                jidx=result[0]   # is an array
                iidx=result[1]   # is an array
                print(jidx[0])   # only one will be found, can be more than if not unique
                print(iidx[0])   # only one will be found, can be more than if not unique
                if n == 61:
                    mld_max_no2_2d=no2_2d[169][369]
                    print('"CONC of NO2 is           %f"' % (no2_2d[jidx[0]][iidx[0]]))
                    print('"Assigned CONC of NO2 is  %f"' % mld_max_no2_2d)
                print('"MAX CONC of NO2 at time step %d is  %f"' % (n,no2_2d[jidx[0]][iidx[0]]))

        else:
            print("Can not find "+aqmfilein)
            sys.exit()
    date = date + date_inc
