import numpy as np
from scipy.io import wavfile
import os
from utils import ms2smp, compute_stride, win_taper, build_linear_interp_table
from utils_lpc import ld_eff

"""
Pitch shifting with granular synthesis for shift factors <=1.0
"""

""" User selected parameters """
input_wav = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "_templates", "speech.wav")
grain_len = 20      # in milliseconds
grain_over = 0.3    # grain overlap (0,1)
shift_factor = 0.7  # <= 1.0
LPC_ORDER = 25
use_LPC = True
GAIN = 0.5
N_COEF = LPC_ORDER+1

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
    SAMP_VALS, AMP_VALS = build_linear_interp_table(GRAIN_LEN_SAMP, shift_factor, data_type)

    # TODO: create arrays to pass between buffers (state variables)
    # copy from granular synthesis
    global ...

    # TODO: create arrays for intermediate values
    # copy from granular synthesis
    global ...

    # state variables for LPC
    if use_LPC:
        global lpc_coef, lpc_prev_in, lpc_prev_out
        lpc_coef = np.zeros(N_COEF, dtype=np.float32)
        lpc_prev_in = np.zeros(N_COEF, dtype=data_type)
        lpc_prev_out = np.zeros(N_COEF, dtype=data_type)



# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # TODO: need to specify those global variables changing in this function (state variables and intermediate values)
    # copy from granular synthesis
    global ...

    if USE_LPC:
        global lpc_coef, lpc_prev_in, lpc_prev_out

    # TODO: append samples from previous buffer
    # copy from granular synthesis
    for n in range(GRAIN_LEN_SAMP):
        ...

    # TODO: obtain the LPC coefficients and inverse filter the grain to esimtate excitation
    if use_LPC:
        # compute LPC coefficients
        lpc_coef

        # estimate excitation
        lpc_prev_in
	
    # TODO: resample grain
    # copy from granular synthesis
    for n in range(GRAIN_LEN_SAMP):
        ...

    # TODO: forward filter the resampled grain
    if use_LPC:
	   lpc_prev_out

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
file_name = "output_gran_synth_lpc.wav"
print("Result written to: %s" % file_name)
wavfile.write(file_name, samp_freq, signal_proc)

