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
STRIDE = grain_len_samp - int(grain_len_samp*overlap/2)-1
overlap_samp = grain_len_samp - STRIDE

# create window
WINDOW = win_taper(grain_len_samp, overlap, data_type)
WINDOW = WINDOW/MAX_VAL

# viz
plt.figure()
plt.plot(np.arange(grain_len_samp), WINDOW, 'b')
plt.axvline(x=overlap_samp, c='k', ls='--', lw=2, label="buffer start")
plt.plot(np.arange(grain_len_samp)+STRIDE, WINDOW, 'b')
plt.axvline(x=STRIDE, c='r', ls='--', lw=2, label="overlap start")
plt.axvline(x=overlap_samp+STRIDE, c='k', ls='-.', lw=2, label="buffer end")
plt.plot(np.arange(grain_len_samp)+2*STRIDE, WINDOW, 'b')
plt.ylim([0, 1.1])
plt.xlim([0, 2*STRIDE])
plt.grid()
plt.xlabel("Sample number", fontsize=18)
# plt.legend(fontsize=18, loc=4)
plt.legend(bbox_to_anchor=(0.65, 1), loc=2, borderaxespad=0., fontsize=18)

plt.show()