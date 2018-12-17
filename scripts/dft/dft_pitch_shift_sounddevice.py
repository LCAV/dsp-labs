import numpy as np
import os
import sounddevice as sd
from utils_dft_sol import dft_rescale, build_dft_rescale_lookup, ms2smp, compute_stride, win_taper

"""
DFT pitch shifting
"""

""" User selected parameters """
input_wav = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "_templates", "speech.wav")
grain_len = 40      # in milliseconds
grain_over = 0.4   # grain overlap (0,1)
shift_factor = 1.5
data_type = np.int16
samp_freq = 16000

# derived parameters
MAX_VAL = np.iinfo(data_type).max
GRAIN_LEN_SAMP = ms2smp(grain_len, samp_freq)
STRIDE = compute_stride(GRAIN_LEN_SAMP, grain_over)
OVERLAP_LEN = GRAIN_LEN_SAMP-STRIDE

is_even = (GRAIN_LEN_SAMP % 2 == 0)  
if is_even:
    N_BINS = GRAIN_LEN_SAMP // 2 + 1
else:
    N_BINS = (GRAIN_LEN_SAMP + 1) // 2

# allocate input and output buffers
input_buffer = np.zeros(STRIDE, dtype=data_type)
output_buffer = np.zeros(STRIDE, dtype=data_type)

# state variables and constants
def init():
    ...
    


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    ...


"""
# Nothing to touch after this!
# """
try:
    sd.default.samplerate = samp_freq
    sd.default.blocksize = STRIDE
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
    print('\nInterrupted by user')

