"""
This template script will just perform a passthrough, namely the output WAV
file will be unprocessed.

Run with the following command:

    python rt_simulated.py
"""

from scipy.io import wavfile
import numpy as np

# define necessary utility functions

# parameters
buffer_len = 256

# test signal
input_wav = "speech.wav"
samp_freq, signal = wavfile.read(input_wav)
signal = signal[:,]  # get first channel
n_buffers = len(signal)//buffer_len
data_type = signal.dtype

print("Sampling frequency : %d Hz" % samp_freq)
print("Data type          : %s" % signal.dtype)

# allocate input and output buffers
input_buffer = np.zeros(buffer_len, dtype=data_type)
output_buffer = np.zeros(buffer_len, dtype=data_type)

# state variables
def init():

    # declare variables used in `process`
    # global

    # define variables, lookup tables

    return


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # specify global variables modified here
    # global

    # process one sample at a time
    for n in range(buffer_len):

        # passthrough
        output_buffer[n] = input_buffer[n]

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
