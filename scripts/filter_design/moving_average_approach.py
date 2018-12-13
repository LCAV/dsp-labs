"""
Compare moving average approach with different lengths
"""

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


def rad2freq(rad, fs):
    return rad * (fs/2) / np.pi


fs = 16000
filter_order = [5, 10, 20, 40, 80]
cutoff = 100.   # in Hz

# for plotting
ALPHA = 0.8
f_max = 1000

# normalized cutoff
nyq = 0.5 * fs
fc_norm = cutoff / nyq

# prepare figure
plt.figure()

for N in filter_order:

    b = -1*np.ones(N)/N
    b[0] = 1 + b[0]
    w, h = signal.freqz(b)
    plt.semilogx([rad2freq(rad, fs) for rad in w],
                 20 * np.log10(abs(h)),
                 label=N,
                 alpha=ALPHA)

plt.margins(0, 0.1)
plt.title("Frequency response (log scale)")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude [dB]")
plt.ylim([-40, 10])
plt.grid()
plt.legend(loc="lower right")
plt.tight_layout()

plt.show()

