import os
import numpy as np
import pandas as pd
import datetime as dts
from datetime import date, time, timedelta
from netCDF4 import Dataset
import met_functions as met
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap
import cartopy
from MesoPy import Meso
from matplotlib import dates
import re
#m = Meso(token = '759bf706d60744f8b0ad99d6acc4f29b')
m = Meso(token = '12bf4ba1ccbb4c79a57a02f36b8ec11f')
starting = '201908010000' # 201906100000
ending = '201908012359'# 201906102359
base_dir = '/scratch2/NCEPDEV/naqfc/Jianping.Huang/Python_Scripts/'

variables = 'air_temp,relative_humidity'
var_list = variables.split(',')
network = 1 # NWS/FAA network
#bbox = [-131.77422,21.081833,-58.66989,53.096016] #
bbox = [-100.77422,21.081833,-90.66989,23.096016] #
mesonet_api = m.timeseries(start=starting,end=ending,obtimezone='utc',vars=var_list,varoperator='and',network=network,bbox=bbox)

# Save dictionary as binary NumPy file 
np.save(base_dir+'Data/Mesonet/meso_%s.npy'%starting[:8],mesonet_api)
#'''

# Iterate over files in directory 
d_str3 = base_dir+'Data/Mesonet/'
mesonet_obs = [f for f in os.listdir(d_str3) if f.endswith('.npy')]
