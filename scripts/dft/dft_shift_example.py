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


def DFT_rescale(x, f):
    X = np.fft.fft(x)
    # separate even and odd lengths
    parity = (len(X) % 2 == 0)
    N = len(X) // 2 + 1 if parity else (len(X) + 1) // 2
    Y = np.zeros(N, dtype=np.complex)
    # work only in the first half of the DFT vector since input is real
    for n in range(N):
        # accumulate original frequency bins into rescaled bins
        ix = int(n * f)
        if ix < N:
            Y[ix] += X[n]
    # now rebuild a Hermitian-symmetric DFT
    Y = np.r_[Y, np.conj(Y[-2:0:-1])] if parity else np.r_[Y, np.conj(Y[-1:0:-1])]
    return np.real(np.fft.ifft(Y))


current_dir = os.path.dirname(os.path.realpath(__file__))
input_wav = os.path.join(current_dir, "clarinet_D4.wav")
samp_freq, audio = wavfile.read(input_wav)

# dft shift
audio_shift = DFT_rescale(audio, 2)
wavfile.write("clarinet_D5.wav", samp_freq, audio_shift)

# plot
plot_spec(audio, samp_freq, max_freq=MAX_FREQ, label="D4")
plot_spec(audio_shift, samp_freq, max_freq=MAX_FREQ, label="D5")

plt.legend()

plt.show()