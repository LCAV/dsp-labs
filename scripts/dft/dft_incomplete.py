import numpy as np
from scipy.io import wavfile
from utils import ms2smp, compute_stride, win_taper, dft_rescale

"""
Pitch shifting with DFT for shift factors <=1.0
"""

""" User selected parameters """
input_wav = "speech.wav"
grain_len = 20      # in milliseconds
grain_over = 0.99   # grain overlap (0,1)
shift_factor = 0.7

# open WAV file
samp_freq, signal = wavfile.read(input_wav)
signal = signal[:,]  # get first channel
data_type = signal.dtype
MAX_VAL = np.iinfo(data_type).max

# derived parameters
GRAIN_LEN_SAMP = ms2smp(grain_len, samp_freq)
STRIDE = compute_stride(GRAIN_LEN_SAMP, grain_over)
OVERLAP_LEN = GRAIN_LEN_SAMP-STRIDE

# allocate input and output buffers
input_buffer = np.zeros(STRIDE, dtype=data_type)
output_buffer = np.zeros(STRIDE, dtype=data_type)

# state variables and constants
def init():

    # lookup table for tapering window
    global WIN
    WIN = win_taper(GRAIN_LEN_SAMP, grain_over, data_type)

    # lookup table for linear interpolation
    global SAMP_VALS
    global AMP_VALS

    # create arrays to pass between buffers (state variables)
    global ...

    # create arrays for intermediate values
    global ...

# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # need to specify those global variables changing in this function (state variables and intermediate values)
    global ...

    # append samples from previous buffer, construction of the grain
    for n in range(int(GRAIN_LEN_SAMP)):
        ...

    # rescale
    ...

    # apply window
    for n in range(int(GRAIN_LEN_SAMP)):
        ...

    # write to output
    for n in range(int(GRAIN_LEN_SAMP)):
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
file_name = "output_pitch_synth_low.wav"
print("Result written to: %s" % file_name)
wavfile.write(file_name, samp_freq, signal_proc)
