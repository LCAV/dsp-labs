import numpy as np
from scipy.io import wavfile
import os
import matplotlib.pyplot as plt
from scipy.signal import firwin, lfilter
from utils import add_offset


def apply_fir(audio, b):
    y_fir = lfilter(b, a=1, x=audio)
    wavfile.write(filename="audio_hpf_{}.wav".format(len(b)),
                  rate=fs, data=y_fir.astype(data_type))

    plt.figure()
    plt.plot(time_vec, audio, 'tab:blue', label="original", alpha=ALPHA)
    plt.plot(time_vec, y_fir, 'tab:orange', label="{}-tap".format(len(b)), alpha=ALPHA)
    plt.xlabel("Time [seconds]")
    plt.grid()
    f = plt.gca()
    f.axes.get_yaxis().set_ticks([0])
    plt.legend()


fp = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "_templates", "speech.wav")
OFFSET = 5000
ALPHA = 0.75     # transparency for plot

# load signal
fs, audio = wavfile.read(fp)
data_type = audio.dtype
time_vec = np.arange(len(audio)) / fs

# add articifial offset
audio_off = add_offset(audio, OFFSET)

# apply different filters
fir_order = [40, 320]
cutoff = 100.
nyq = 0.5 * fs
fc_norm = cutoff / nyq

for order in fir_order:
    b = firwin(numtaps=order+1, cutoff=fc_norm, window="hanning", pass_zero=False)
    apply_fir(audio_off, b)

plt.show()
