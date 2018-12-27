import numpy as np
from utils import ms2smp, compute_stride, win_taper, build_linear_interp_table
from utils_lpc import ld_eff
import sounddevice as sd


"""
Real-time pitch shifting with granular synthesis for shift factors <=1.0
"""

""" User selected parameters """
grain_len = 30
grain_over = 0.2
shift_factor = 0.7
LPC_ORDER = 25
use_LPC = True
GAIN = 0.5
N_COEF = LPC_ORDER+1

data_type = np.int16
samp_freq = 16000

# derived parameters
MAX_VAL = np.iinfo(data_type).max
GRAIN_LEN_SAMP = ms2smp(grain_len, samp_freq)
STRIDE = compute_stride(GRAIN_LEN_SAMP, grain_over)
OVERLAP_LEN = GRAIN_LEN_SAMP-STRIDE

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
        process(indata[:, 0], outdata[:, 0], frames)

    init()
    with sd.Stream(channels=1, callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
except KeyboardInterrupt:
    print('\nInterrupted by user')
