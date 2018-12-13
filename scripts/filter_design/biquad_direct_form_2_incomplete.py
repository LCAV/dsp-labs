"""
Complete biquad implementation.
"""

from scipy.io import wavfile
import numpy as np
import os
from utils import add_offset

# parameters
buffer_len = 128
pole_coef = 0.95
OFFSET = 5000

# test signal
input_wav = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "_templates", "speech.wav")
samp_freq, signal = wavfile.read(input_wav)
data_type = signal.dtype
MAX_VAL = abs(np.iinfo(data_type).min)
signal = signal[:, ]  # get first channel
n_buffers = len(signal)//buffer_len

print("Sampling frequency : %d Hz" % samp_freq)
print("Data type          : %s" % data_type)

# remove offset and add artificial one
signal = add_offset(signal, OFFSET)
wavfile.write("speech_off.wav", samp_freq, signal)

# allocate input and output buffers
input_buffer = np.zeros(buffer_len, dtype=data_type)
output_buffer = np.zeros(buffer_len, dtype=data_type)

# state variables
def init():

    # define filter parameters
    global b_coef, a_coef, HALF_MAX_VAL, GAIN, N_COEF
    GAIN = 0.8
    HALF_MAX_VAL = MAX_VAL // 2
    b_coef = [HALF_MAX_VAL, -2 * HALF_MAX_VAL, HALF_MAX_VAL]
    a_coef = [HALF_MAX_VAL,
              int(-2 * pole_coef * HALF_MAX_VAL),
              int(pole_coef * pole_coef * HALF_MAX_VAL)]
    N_COEF = len(a_coef)

    # declare variables used in `process`
    global w
    w = list(np.zeros(N_COEF, dtype=data_type))  # doesn't work with numpy array for some reason...

    return


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # specify global variables modified here
    global w

    # process one sample at a time
    for n in range(buffer_len):

        # apply input gain
        w[0] = int(GAIN * input_buffer[n])

        # compute contribution from state variables
        for i in range(1, N_COEF):
            # TODO: accumulate signal at top-left adder using prev `w` (middle column)
            w[0] -= 0

        # compute output
        output_buffer[n] = 0
        for i in range(N_COEF):
            # TODO: accumulate signal at top-right adder using `w`
            output_buffer[n] += 0

        # update state variables
        for i in reversed(range(1, N_COEF)):
            # TODO: shift prev values
            w[i] = 0


"""
Nothing to touch after this!
"""
init()
# simulate block based processing
signal_proc = np.zeros(n_buffers*buffer_len, dtype=data_type)
for k in range(n_buffers):

    # index the appropriate samples
    input_buffer = signal[k*buffer_len:(k+1)*buffer_len]
    process(input_buffer, output_buffer, buffer_len)
    signal_proc[k*buffer_len:(k+1)*buffer_len] = output_buffer

# write to WAV
wavfile.write("speech_mod.wav", samp_freq, signal_proc)


"""
Visualize / test
"""
import matplotlib.pyplot as plt

ALPHA = 0.75     # transparency for plot

plt.figure()
plt.plot(np.arange(len(signal)) / samp_freq, signal, 'tab:blue', label="original", alpha=ALPHA)
plt.plot(np.arange(len(signal_proc)) / samp_freq, signal_proc, 'tab:orange', label="biquad", alpha=ALPHA)
plt.xlabel("Time [seconds]")
plt.grid()
f = plt.gca()
f.axes.get_yaxis().set_ticks([0])
plt.legend()

plt.show()
