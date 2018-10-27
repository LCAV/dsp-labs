import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import freqz
from scipy.stats import linregress
import sys
from mpl_toolkits.axes_grid.inset_locator import inset_axes

from plot_zplane import zplane 

save = True

"""
H(z) = (b0 + b1*z^-1 + ... + bN*z^-N) / (a0 + a1*z^-1 + ... + aN*z^-N) 
"""
b = np.array([1, -1])
a = np.array([1])
fs = 32000

# zeros/poles plot
zplane(b, a)
plt.title("Zeros/poles plot")

if save:
    plt.savefig('zplot_high_pass.png', format='png', dpi=1000)

# frequency response
w, h = freqz(b)

h = h[1:]
w = w[1:]

h_db = 20 * np.log10(abs(h))
angles = np.unwrap(np.angle(h))
freq = w / (2*np.pi) *fs

fig = plt.figure()
plt.title('Frequency response')
ax1 = fig.add_subplot(111)
plt.plot(freq, h_db, 'b')
plt.ylabel('Magnitude [dB]', color='b')
plt.xlabel('Frequency [Hz]')
ax2 = ax1.twinx()
plt.plot(freq, angles, 'g')
plt.ylabel('Phase (radians)', color='g')
plt.grid()
plt.axis('tight')

if save:
    plt.savefig('freq_resp_high_pass.png', format='png', dpi=1000)

fig = plt.figure()
plt.title('Frequency response (log scale)')
ax1 = fig.add_subplot(111)
plt.semilogx(freq, h_db, 'b')
plt.ylabel('Magnitude [dB]', color='b')
plt.xlabel('Frequency [Hz]')
ax2 = ax1.twinx()
plt.semilogx(freq, angles, 'g')
plt.ylabel('Phase (radians)', color='g')
plt.grid()
plt.axis('tight')

if save:
    plt.savefig('freq_resp_high_pass_log.png', format='png', dpi=1000)

# calculate filter roll-off
slope = linregress(np.log10(freq), h_db)[0]
print("Filter roll-off : %0.2f dB/decade" % slope)
slope = linregress(np.log2(freq), h_db)[0]
print("Filter roll-off : %0.2f dB/octave" % slope)

plt.show()
