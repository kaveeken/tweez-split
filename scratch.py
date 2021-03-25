import lumicks.pylake as lk
import numpy as np
import matplotlib.pyplot as plt
import h5py

# d = lk.File('/home/kris/proj/.data/tweez/full.h5')
# print(d.h5.keys())
# print(d.h5['Force LF'].keys())
# plt.clf()
# plt.ion()
# plt.plot(d.h5['Trap position']['1X'])
# plt.plot(d.h5['Distance']['Piezo Distance'])
# plt.plot(d.h5['Force HF']['Force 1x'][:] / 100)
d = h5py.File('/home/kris/proj/.data/tweez/yhsp2.h5', 'r')
signal = d['Trap position']['1X']
first = np.argwhere(np.asarray(signal) < 2)[0][0]
signal = signal[first:]
distance = d['Distance']['Piezo Distance'][first:]
distance = distance - np.amin(distance)
force = d['Force HF']['Force 1x'][first:]

toseconds = 1e-9
duration = (d['Force LF']['Force 1x'][:][-1][0] \
            - d['Force LF']['Force 1x'][:][0][0]) * toseconds
frequency = len(force) / duration
print(duration, frequency)




from util import find_pulls
pulls = find_pulls(signal)
print(len(pulls))
print(max(signal))

dict_pulls = []
for index, pull in enumerate(pulls):
    region = signal[pull[0]:pull[1]][::10000]
    bars = plt.hist(region, bins=50)
    first_top = last_top = 0
    time = 0
    if index:
        time = int((pull[0] - pulls[index - 1][1]) / frequency * 1000)
    for index, sig in enumerate(region):
        if not first_top and sig > bars[1][-2]:
            first_top = pull[0] + index * 10000
        if first_top and not last_top and sig < bars[1][-2]:
            last_top = pull[0] + index * 10000
    dict_pulls.append({'start': pull[0],
                      'stop': pull[1],
                       'len': pull[1] - pull[0],
                      'pull_stop': first_top,
                      'relax_start': last_top,
                      'rest': time})

from scipy.stats import hmean
target = 5000
pullens = [pull[1] - pull[0] for pull in pulls]
pull_points = int(hmean(pullens))
# pull_points = pulls[0][1] - pulls[0][0]
kernel_size = pull_points // 5000
kernel = np.ones(kernel_size) / kernel_size
smooth_force = np.convolve(force, kernel, mode='same')


curves = {}
for index, pull in enumerate(dict_pulls):
    padding = len(str(len(dict_pulls)))
    identifier = 'curve_' + str(index + 1).zfill(padding)
    if pull['len'] > 2 * target * kernel_size \
       or pull['len'] < target * kernel_size / 2 \
       or smooth_force[pull['start']] > 30:
        continue
    curves[identifier] = \
    {'pull_force': smooth_force[pull['start']:pull['pull_stop']][::kernel_size],
     'pull_dist': distance[pull['start']:pull['pull_stop']][::kernel_size],
     'rlx_force': smooth_force[pull['relax_start']:pull['stop']][::kernel_size],
     'rlx_dist': distance[pull['relax_start']:pull['stop']][::kernel_size],
     'full_force': smooth_force[pull['start']:pull['stop']][::kernel_size],
     'full_dist': distance[pull['start']:pull['stop']][::kernel_size],
     'sign': signal[pull['start']:pull['stop']][::kernel_size],
     'rest': pull['rest']}

print(curves.keys())

with h5py.File('test.h5', 'w') as f:
    for curve_id, curve in curves.items():
        grp = f.create_group(curve_id)
        grp.attrs.create('rest', data=curve['rest'])
        for name in ['pull_force', 'pull_dist', 'rlx_force', 'rlx_dist',
                     'full_force', 'full_dist']:
            grp.create_dataset(name, data=curve[name])
