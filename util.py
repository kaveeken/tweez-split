import numpy as np
import matplotlib.pyplot as plt
import csv


def find_pulls(signal, bins=100, stepsize=1000, verbose=False):
    bars = plt.hist(signal[::stepsize], bins=bins)
    highest = np.argmax(bars[0])
    second = np.argmax([heigth for index, heigth in enumerate(bars[0])
                        if index != highest])

    low_signal = bars[1][min(highest, second) + 1]
    high_signal = bars[1][max(highest, second)]

    print(bars[1])
    pulling = True
    relaxing = True
    pulls = []
    for index, position in enumerate(signal[::stepsize]):
        if not index % 100 and verbose:
            print(index * stepsize)
        if pulling and relaxing:  # ignore first partial pull
            if position < low_signal:
                pulling = False
                relaxing = False
        elif not pulling and not relaxing and position >= low_signal:
            pulling = True
            start = max(index * stepsize - stepsize, 0)
        elif pulling and position > high_signal:
            pulling = False
            relaxing = True
        elif relaxing and position < low_signal:
            pulling = False
            relaxing = False
            pulls.append((start, index * stepsize))

    return pulls


def write_csv(fname, curves):
    with open(fname, 'w') as f:
        wr = csv.writer(f)
        for curve_id, curve in curves.items():
            wr.writerow([curve_id, *[dist for dist in curve['dist']]])
            wr.writerow([curve_id, *[force for force in curve['force']]])


def read_csv(fname):
    curves = {}
    with open('mycurves.csv', 'r') as f:
        rows = [line.split('\n')[0].split(',') for line in f]
    for dist, force in zip(*[iter(rows)]*2):
        identifier = dist[0]
        curves[identifier] = {'dist': [float(x) for x in dist[1:]],
                              'force': [float(x) for x in force[1:]]}
    return curves

# def write_hdp5(fname, curves):
#     for curve in curves.items():
