import numpy as np
from scipy.io import wavfile
import os
import matplotlib.pyplot as plt
from utils import add_offset


fp = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "_templates", "speech.wav")
OFFSET = 5000
ALPHA = 0.75     # transparency for plot

# load signal
fs, audio = wavfile.read(fp)
data_type = audio.dtype
time_vec = np.arange(len(audio)) / fs

# add articifial offset
audio_off = add_offset(audio, OFFSET)

plt.figure()
plt.plot(time_vec, audio, 'tab:blue', label="original", alpha=ALPHA)
plt.plot(time_vec, audio_off, 'tab:orange', label="offset", alpha=ALPHA)
plt.xlabel("Time [seconds]")
plt.grid()
f = plt.gca()
f.axes.get_yaxis().set_ticks([0])
plt.legend()

# apply simple filter
prev_samples = np.roll(audio_off, 1)
prev_samples[0] = 0
audio_hpf_simple = audio_off - prev_samples

# comparisons
plt.figure()
plt.plot(time_vec, audio_off, 'tab:orange', label="offset", alpha=ALPHA)
plt.plot(time_vec, audio_hpf_simple, 'tab:green', label="simple hpf", alpha=ALPHA)
plt.xlabel("Time [seconds]")
plt.grid()
f = plt.gca()
f.axes.get_yaxis().set_ticks([0])
plt.legend()

plt.figure()
plt.plot(time_vec, audio, 'tab:blue', label="original", alpha=ALPHA)
plt.plot(time_vec, audio_hpf_simple, 'tab:green', label="simple hpf", alpha=ALPHA)
plt.xlabel("Time [seconds]")
plt.grid()
f = plt.gca()
f.axes.get_yaxis().set_ticks([0])
plt.legend()

# write to file to listen
wavfile.write("audio_hpf_simple.wav", fs, audio_hpf_simple.astype(data_type))

plt.show()
