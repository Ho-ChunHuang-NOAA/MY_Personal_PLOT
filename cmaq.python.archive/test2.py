import pandas as pd
import numpy as np

dataset = [1,5,7,2,6,7,8,2,5,2,6,8,2,6,13,25,-9]

def movingaverage(values,window):
    weights = np.repeat(1.0, window)/window
    smas = np.convolve(values,weights,'valid')
    return smas

#print(movingaverage(dataset,8))

dat = movingaverage(dataset,8)

print(dat)

max8 = dat.max()

print(max8)
