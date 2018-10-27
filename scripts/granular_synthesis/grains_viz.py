import numpy as np
import matplotlib.pyplot as plt

from utils import ms2smp, double_len, double_len_taper

f = 100
grain_len = 32   # ms
overlap = 0.3
duration = 100   # ms
disp = 60
fs = 16000

# original
time = np.arange(int(duration*1e-3*fs))/fs
x = np.sin(2*np.pi*f*time)

# double length
grain_len_samp = ms2smp(grain_len, fs)
x_double = double_len(x, grain_len_samp)
time_double = np.arange(len(x_double))/fs

# double length with overlap/window
x_double_win, stride_samp, grains = double_len_taper(x, grain_len_samp, overlap)
stride_len = stride_samp/fs*1000
time_double_win = np.arange(len(x_double_win))/fs


# visualize discontinuous
f, (ax1, ax2) = plt.subplots(2,1)

ax1.plot(time, x)
ax1.grid()
ax1.set_ylabel("Original", fontsize=18)
ax1.set_xlim([0,disp*1e-3])
ax1.get_yaxis().set_ticklabels([])

ax2.plot(time_double, x_double)
for k in range(1, 2*duration//grain_len+1):
    if k%2:  # across doubling (discontinuity)
        ax2.axvline(x=k*grain_len*1e-3, c='r', ls='--', lw=1)
    else:  
        ax2.axvline(x=k*grain_len*1e-3, c='g', ls='--', lw=1)
ax2.grid()
ax2.set_ylabel("Double", fontsize=18)
ax2.set_xlim([0,2*disp*1e-3])
ax2.set_xlabel("Time [seconds]", fontsize=18)
ax2.get_yaxis().set_ticklabels([])

plt.savefig("doubling_discontinuity.png", format='png', dpi=300)

# visualize continuous
f, (ax1, ax2, ax3) = plt.subplots(3,1)

ax1.plot(time, x)
ax1.grid()
ax1.set_ylabel("Original", fontsize=18)
ax1.set_xlim([0,disp*1e-3])
ax1.get_yaxis().set_ticklabels([])

for k, grain in enumerate(grains):
    grain_padded = np.zeros(len(time_double_win))
    start_samp = k*stride_samp
    end_samp = start_samp + grain_len_samp
    grain_padded[start_samp:end_samp] = grain
    ax2.plot(time_double_win, grain_padded)
ax2.grid()
ax2.set_ylabel("Grains", fontsize=18)
ax2.set_xlim([0,2*disp*1e-3])
ax2.get_yaxis().set_ticklabels([])

ax3.plot(time_double_win, x_double_win)
for k in range(1, 2*int(duration//stride_len)+1):
    if k%2:  # across doubling (discontinuity)
        ax3.axvline(x=k*stride_len*1e-3, c='r', ls='--', lw=1)
    else:  
        ax3.axvline(x=k*stride_len*1e-3, c='g', ls='--', lw=1)
ax3.grid()
ax3.set_ylabel("Windowed", fontsize=18)
ax3.set_xlim([0,2*disp*1e-3])
ax3.set_xlabel("Time [seconds]", fontsize=18)
ax3.get_yaxis().set_ticklabels([])

plt.savefig("doubling_continuous.png", format='png', dpi=300)

plt.show()