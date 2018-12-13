"""
Compare the simple filter with other FIR filters that have been designed using the windwo method.
"""

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


def freq2rad(freq, fs):
    return freq * np.pi / (fs/2)


def rad2freq(rad, fs):
    return rad * (fs/2) / np.pi


fs = 16000
filter_order = [40, 110, 180, 250, 320]
cutoff = 100.   # in Hz

# for plotting
ALPHA = 0.8
f_max = 1000

# normalized cutoff
nyq = 0.5 * fs
fc_norm = cutoff / nyq

# prepare figure
plt.figure()

# simple filter
b = np.array([1, -1])
w, h = signal.freqz(b)
plt.semilogx([rad2freq(rad, fs) for rad in w],
             20 * np.log10(abs(h)),
             label="simple (2-tap)",
             alpha=ALPHA)


# compare FIR filters of different lengths
for order in filter_order:
    # design filter
    b = signal.firwin(numtaps=order + 1, cutoff=fc_norm, window="hanning", pass_zero=False)

    # visualize response
    w, h = signal.freqz(b)
    plt.semilogx([rad2freq(rad, fs) for rad in w],
                 20 * np.log10(abs(h)),
                 label="%d-tap FIR" % (order + 1),
                 alpha=ALPHA)

plt.margins(0, 0.1)
plt.title("Frequency response (log scale)")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude [dB]")
plt.ylim([-50, 10])
plt.grid()
plt.legend(loc="lower right")
plt.tight_layout()

plt.show()
