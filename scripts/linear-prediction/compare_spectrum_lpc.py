import numpy as np
import os
from scipy.io import wavfile
import matplotlib.pyplot as plt
from utils_lpc import lpc

MAX_VAL = 32767.0   #int16
MAX_FREQ = 8000
LPC_ORDER = 20


def plot_spec(x, Fs, max_freq=None, do_fft=True, label=None):
    if max_freq is None:
        max_freq = Fs/2
    C = int(len(x) * max_freq / Fs)
    X = np.abs(np.fft.fft(x)[0:C]) if do_fft else x[0:C]
    N = Fs * np.arange(0, C) / len(x);
    plt.plot(N, X, label=label)
    plt.xlim([0, max_freq])
    plt.xlabel("Frequency [Hz]")
    ax = plt.gca()
    ax.axes.yaxis.set_ticklabels([])
    return N, X


"""
Compare energy envelope of original and granular-synthesis spectrum.
"""
current_dir = os.path.dirname(os.path.realpath(__file__))
input_wav = os.path.join(current_dir, "voiced.wav")
mod_input_wav = os.path.join(current_dir, "voiced_gran_synth.wav")
mod_input_wav_2 = os.path.join(current_dir, "voiced_gran_synth_lpc.wav")

# import WAV files
samp_freq, signal_orig = wavfile.read(input_wav)
signal_orig = signal_orig/MAX_VAL
samp_freq, signal_mod = wavfile.read(mod_input_wav)
signal_mod = signal_mod/MAX_VAL
samp_freq, signal_mod_lpc = wavfile.read(mod_input_wav_2)
signal_mod_lpc = signal_mod_lpc/MAX_VAL

# compute energy envelope
A = np.fft.fft(lpc(signal_orig, LPC_ORDER), len(signal_orig))
A_mod = np.fft.fft(lpc(signal_mod, LPC_ORDER), len(signal_orig))
A_mod_lpc = np.fft.fft(lpc(signal_mod_lpc, LPC_ORDER), len(signal_orig))

# plot
plot_spec(signal_orig, samp_freq, label="original spectrum")
plot_spec(np.abs(np.divide(1.0, A)), samp_freq, do_fft=False, label="energy (original)")
plot_spec(np.abs(np.divide(1.0, A_mod)), samp_freq, do_fft=False, label="energy (granular synthesis)")
plot_spec(np.abs(np.divide(1.0, A_mod_lpc)), samp_freq, do_fft=False, label="energy (granular synthesis + lpc)")
plt.legend()
plt.grid()


plt.show()
