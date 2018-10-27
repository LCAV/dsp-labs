import numpy as np
import matplotlib.pyplot as plt

from utils import win_taper, ms2smp

grain_len = 35   # ms
overlap = 0.3
fs = 16000
data_type = np.int16

# derived parameters
MAX_VAL = np.iinfo(data_type).max
grain_len_samp = ms2smp(grain_len, fs)
grain_stride = grain_len_samp - int(grain_len_samp * overlap / 2) - 1

# create window
WINDOW = win_taper(grain_len_samp, overlap, data_type)
WINDOW = WINDOW/MAX_VAL
time = np.arange(len(WINDOW))/fs

# visualize
plt.figure()
plt.plot(time, WINDOW)
plt.xlabel("Time [seconds]", fontsize=18)
plt.grid()

plt.savefig("taper_window.png", format='png', dpi=300)


# align two windows using the given stride and sum them 
win1 = np.r_[WINDOW, np.zeros(grain_stride)]
win2 = np.r_[np.zeros(grain_stride), WINDOW]
time = np.arange(len(win1))/fs
plt.figure()
plt.plot(time, win1);
plt.plot(time, win2);
plt.grid()

# if the windows are properly aligned, the tapered areas compensate
plt.plot(time, win1 + win2, label="sum");
plt.legend(fontsize=18, loc=4)
plt.xlabel("Time [seconds]", fontsize=18)

plt.show()