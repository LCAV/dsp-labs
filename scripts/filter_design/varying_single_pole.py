"""
Vary coefficient for pole.
"""

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


def freq2rad(freq, fs):
    return freq * np.pi / (fs/2)


def rad2freq(rad, fs):
    return rad * (fs/2) / np.pi


pole_coef = [0, 0.5, 0.75, 0.9, 0.95]

fs = 16000

# prepare figure
ALPHA = 0.8
f_max = 4000
plt.figure()

for R in pole_coef:
    b = np.array([1., -1.])
    a = np.array([1, -R])
    w, h = signal.freqz(b, a)
    plt.semilogx([rad2freq(rad, fs) for rad in w],
                 20 * np.log10(abs(h)),
                 label=R,
                 alpha=ALPHA)

plt.margins(0, 0.1)
plt.title("Single pole frequency response (log scale)")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude [dB]")
plt.grid()
plt.legend(loc="lower right")
plt.tight_layout()

plt.show()
