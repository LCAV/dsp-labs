"""
Compare various IIR filters
"""

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


def freq2rad(freq, fs):
    return freq * np.pi / (fs/2)


def rad2freq(rad, fs):
    return rad * (fs/2) / np.pi


# MAIN PARAMETER
pole_coef = 0.95
fs = 16000

# prepare figure
ALPHA = 0.8
f_max = 4000
plt.figure()

# simple filter
b = np.array([1, -1])
w, h = signal.freqz(b)
plt.semilogx([rad2freq(rad, fs) for rad in w],
             20 * np.log10(abs(h)),
             label="simple (2-tap)",
             alpha=ALPHA)

# First order single pole
b = np.array([1., -1.])
a = np.array([1, -1*pole_coef])

w, h = signal.freqz(b, a)
plt.semilogx([rad2freq(rad, fs) for rad in w],
             20 * np.log10(abs(h)),
             label="1-stage",
             alpha=ALPHA)

# (2nd order)
b = np.array([1., -2., 1.])
a = np.array([1, -2*pole_coef, pole_coef*pole_coef])

w, h = signal.freqz(b, a)
plt.semilogx([rad2freq(rad, fs) for rad in w],
             20 * np.log10(abs(h)),
             label="2-stage",
             alpha=ALPHA)

# (3rd order)
b = np.array([1., -3., 3., -1.])
a = np.array([1, -3*pole_coef, 3*pole_coef*pole_coef, -1*pole_coef**3])

w, h = signal.freqz(b, a)
plt.semilogx([rad2freq(rad, fs) for rad in w],
             20 * np.log10(abs(h)),
             label="3-stage",
             alpha=ALPHA)


plt.margins(0, 0.1)
plt.title("Frequency response for varying num. of stages (log scale)")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude [dB]")
plt.grid()
plt.legend(loc="lower right")
plt.tight_layout()

plt.show()
