import numpy as np
from scipy.io import wavfile
import os
from utils_dft_sol import dft_rescale, build_dft_rescale_lookup, ms2smp, compute_stride, win_taper

"""
DFT pitch shifting.
"""

""" User selected parameters """
input_wav = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "_templates", "speech.wav")
grain_len = 40      # in milliseconds
grain_over = 0.4   # grain overlap (0,1)
shift_factor = 1.5

# open WAV file
samp_freq, signal = wavfile.read(input_wav)
if len(signal.shape)>1 :
    signal = signal[:,0]  # get first channel
data_type = signal.dtype
MAX_VAL = np.iinfo(data_type).max

# derived parameters
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

    # lookup table for tapering window
    global WIN
    WIN = win_taper(GRAIN_LEN_SAMP, grain_over, data_type)

    # lookup table for DFT rescaling
    global SHIFT_IDX, MAX_BIN, input_concat_float
    SHIFT_IDX, MAX_BIN = build_dft_rescale_lookup(N_BINS, shift_factor)
    input_concat_float = np.zeros(GRAIN_LEN_SAMP, dtype=np.float32)

    # TODO: create arrays to pass between buffers (state variables)
    # copy from granular synthesis
    global ...

    # TODO: create arrays for intermediate values
    # copy from granular synthesis
    global ...


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    global input_concat_float
    # TODO: need to specify those global variables changing in this function (state variables and intermediate values)
    # copy from granular synthesis
    global ...

    """
    Apply effect
    """
    # TODO: append samples from previous buffer
    # copy from granular synthesis
    for n in range(GRAIN_LEN_SAMP):
        ...

    # TODO: rescale
    for n in range(GRAIN_LEN_SAMP):
        grain[n] = input_concat[n]

    # TODO: apply window
    # copy from granular synthesis
    for n in range(GRAIN_LEN_SAMP):
        ...

    # TODO: write to output and update state variables
    # copy from granular synthesis
    for n in range(GRAIN_LEN_SAMP):
        # overlapping part
        if n < OVERLAP_LEN:
            ...
        # non-overlapping part
        elif n < STRIDE:
            ...
        # update state variables
        else:
            ...


"""
Nothing to touch after this!
"""
init()
# simulate block based processing
n_buffers = len(signal)//STRIDE
signal_proc = np.zeros(n_buffers*STRIDE, dtype=data_type)
for k in range(n_buffers):

    # sample indices
    start_idx = k*STRIDE
    end_idx = (k+1)*STRIDE

    # index the appropriate samples
    input_buffer = signal[start_idx:end_idx]
    process(input_buffer, output_buffer, STRIDE)
    signal_proc[start_idx:end_idx] = output_buffer

# write to WAV
file_name = "output_dft_pitch_shift.wav"
print("Result written to: %s" % file_name)
wavfile.write(file_name, samp_freq, signal_proc)

