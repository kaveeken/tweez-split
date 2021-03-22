import numpy as np
import matplotlib.pyplot as plt


def find_pulls(signal, bins=100, stepsize=1000, verbose=False):
    bars = plt.hist(signal[::stepsize], bins=bins)
    highest = np.argmax(bars[0])
    second = np.argmax([heigth for index, heigth in enumerate(bars[0])
                        if index != highest])

    low_signal = bars[1][min(highest, second) + 1]
    high_signal = bars[1][max(highest, second)]

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
