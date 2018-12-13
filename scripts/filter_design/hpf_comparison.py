import numpy as np
from scipy.io import wavfile
import os
import matplotlib.pyplot as plt
from scipy.signal import firwin, lfilter, freqz
from utils import add_offset

# parameters
fir_win_order = 180; cutoff = 100.
ma_order = 40
pole_coef = 0.95
OFFSET = 5000

# load signal
fp = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "_templates", "speech.wav")
fs, audio = wavfile.read(fp)
data_type = audio.dtype
time_vec = np.arange(len(audio)) / fs
nyq = 0.5 * fs
fc_norm = cutoff / nyq

# add articifial offset
audio_off = add_offset(audio, OFFSET)

# prepare figure
ALPHA = 0.75    # transparency for plot
plt.figure()
plt.plot(time_vec, audio_off, label="original", alpha=ALPHA)

# window approach
b_win = firwin(numtaps=fir_win_order + 1, cutoff=fc_norm, window="hanning", pass_zero=False)
y_fir_win = lfilter(b_win, a=1, x=audio_off)
plt.plot(time_vec, y_fir_win, label="FIR window, %d taps" % (fir_win_order+1), alpha=ALPHA)

# moving average approach
b_ma = -1*np.ones(ma_order)/ma_order
b_ma[0] = 1 + b_ma[0]
y_ma = lfilter(b_ma, a=1, x=audio_off)
plt.plot(time_vec, y_fir_win, label="MA, %d taps" % ma_order, alpha=ALPHA)

# first order
b_iir = np.array([1., -1.])
a_iir = np.array([1, -1 * pole_coef])
y_iir = lfilter(b_iir, a=a_iir, x=audio_off)
plt.plot(time_vec, y_iir, label="Single pole, 3 taps", alpha=ALPHA)

plt.xlabel("Time [seconds]")
plt.grid()
f = plt.gca()
f.axes.get_yaxis().set_ticks([0])
plt.legend()


"""
Frequency response
"""
def rad2freq(rad, fs):
    return rad * (fs/2) / np.pi

plt.figure()

w, h = freqz(b_win)
plt.semilogx([rad2freq(rad, fs) for rad in w],
                 20 * np.log10(abs(h)),
                 label="FIR window, %d taps" % (fir_win_order+1),
                 alpha=ALPHA)

w, h = freqz(b_ma)
plt.semilogx([rad2freq(rad, fs) for rad in w],
                 20 * np.log10(abs(h)),
                 label="MA, %d taps" % ma_order,
                 alpha=ALPHA)

w, h = freqz(b_iir, a_iir)
plt.semilogx([rad2freq(rad, fs) for rad in w],
                 20 * np.log10(abs(h)),
                 label="Single pole, 3 taps",
                 alpha=ALPHA)

plt.margins(0, 0.1)
plt.title("Frequency response (log scale)")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude [dB]")
plt.ylim([-20, 5])
plt.grid()
plt.legend(loc="lower right")
plt.tight_layout()

plt.show()
