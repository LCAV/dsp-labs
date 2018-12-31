import numpy as np
from scipy.io import wavfile
import os
import matplotlib.pyplot as plt


MAX_FREQ = 4000

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


current_dir = os.path.dirname(os.path.realpath(__file__))
input_wav = os.path.join(current_dir, "clarinet_D4.wav")
samp_freq, audio = wavfile.read(input_wav)
plot_spec(audio, samp_freq, max_freq=MAX_FREQ)

plt.show()