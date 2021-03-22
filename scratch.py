import lumicks.pylake as lk
import numpy as np
import matplotlib.pyplot as plt

d = lk.File('/home/kris/proj/.data/tweez/full.h5')
print(d.h5.keys())
print(d.h5['Force LF'].keys())
plt.clf()
plt.ion()
plt.plot(d.h5['Trap position']['1X'])
plt.plot(d.h5['Distance']['Piezo Distance'])
plt.plot(d.h5['Force HF']['Force 1x'][:] / 100)

