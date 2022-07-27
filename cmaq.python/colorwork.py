#
# Aaume already has obsrvation array of
# lat_o3, lon_03, obs_o3
num_o3=len(obs_o3)
clevs = [ 3., 6., 9., 12., 25., 35., 45., 55., 65., 70., 75., 85., 95., 105. ]
nlev=len(clevs)
ccols = [
         (0.6471,0.6471,1.0000), (0.4314,0.4314,1.0000),
         (0.0000,0.7490,1.0000), (0.0000,1.0000,1.0000),
         (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
         (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000), (0.9412,0.5098,0.1569),
         (1.0000,0.0000,0.0000), (0.7020,0.0000,0.0000)
        ]
ncols=len(ccols)
if ncols+1 != nlev:
    print("Warning: color interval does not match wiht color setting")
color=[]
for i in range(0,num_o3]:
    if obs_o3[i] < clevs[0]:
        color.append((0.8627,0.8627,1.0000))
    elif obs_o3[i] >= clevs[nlev-1]:
        color.append((0.4310,0.2780,0.7250))
    else:
        flag_find_color="no"
        for j in range[0,nlev-2]:
            if obs_o3[i] >= clevs[j] and obs_o3[i] < clevs[j+1]
                color.append(ccols[j])
                flag_find_color="yes"
                break
        if flag_find_color =="no":
            print("Can not assign proper value for color, program stop")
            sys.exit()

Then use c=color in stead of plot_o3


# For PM25:
#
# Aaume already has obsrvation array of
# lat_pm25, lon_03, obs_pm25
num_pm25=len(obs_pm25)
clevs = [ 3., 6., 9., 12., 15., 35., 55., 75., 100., 125., 150., 250., 300., 400., 500., 600., 750. ]
nlev=len(clevs)
ccols = [
        (0.0000,0.7060,0.0000), (0.0000,0.9060,0.0000), (0.3020,1.0000,0.3020),
        (1.0000,1.0000,0.4980), (1.0000,0.8745,0.0000), (1.0000,0.6471,0.0000),
        (1.0000,0.3840,0.3840), (1.0000,0.0000,0.0000), (0.8000,0.0000,0.0000), (0.7020,0.0000,0.0000),
        (0.6120,0.5100,0.8120), (0.5180,0.3880,0.7650), (0.4310,0.2780,0.7250),(0.2980,0.1920,0.5020),
        (0.4706,0.4706,0.4706), (0.7843,0.7843,0.7843)
        ]
ncols=len(ccols)
if ncols+1 != nlev:
    print("Warning: color interval does not match wiht color setting")
color=[]
for i in range(0,num_pm25]:
    if obs_pm25[i] < clevs[0]:
        color.append((0.8627,0.8627,1.0000))
    elif obs_pm25[i] >= clevs[nlev-1]:
        color.append((0.9412,0.9412,0.9412))
    else:
        flag_find_color="no"
        for j in range[0,nlev-2]:
            if obs_pm25[i] >= clevs[j] and obs_pm25[i] < clevs[j+1]
                color.append(ccols[j])
                flag_find_color="yes"
                break
        if flag_find_color =="no":
            print("Can not assign proper value for color, program stop")
            sys.exit()

Then use c=color in stead of plot_pm25
