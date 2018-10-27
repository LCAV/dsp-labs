from scipy.io import wavfile
import numpy as np
import sounddevice as sd

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
"""
Nothing to touch after this!
"""
try:
    sd.default.samplerate = 16000
    sd.default.blocksize = buffer_len
    sd.default.dtype = data_type

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        process(indata[:,0], outdata[:,0], frames)

    init()
    with sd.Stream(channels=1, callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
