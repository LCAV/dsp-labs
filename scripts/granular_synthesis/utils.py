import numpy as np


def ms2smp(ms, fs):
    """
    Parameters
    ----------
    ms: float
        Time in milliseconds
    fs: float
        Sampling rate in Hz.
    
    return int(fs*ms/1000.)

def compute_stride(grain_len_samp, grain_over):
    return grain_len_samp - int(grain_len_samp * grain_over / 2) - 1


def win_taper(grain_len_samp, grain_over, data_type=np.int16):

    edge_over = int(grain_len_samp * grain_over / 2)
    r = np.arange(0, edge_over) / float(edge_over)
    win = np.concatenate((r,
        np.ones(grain_len_samp-2*edge_over),
        r[::-1]))
    max_val = np.iinfo(data_type).max

    return (win*max_val).astype(data_type)


def build_linear_interp_table(n_samples, down_fact, data_type=np.int16):

    samp_vals = []
    amp_vals = []
    for n in range(n_samples):
        # compute t, N, and a

        samp_vals.append(N)
        amp_vals.append(a)

    MAX_VAL = np.iinfo(data_type).max
    amp_vals =  np.array(amp_vals)
    amp_vals = (amp_vals*MAX_VAL).astype(data_type)

    return samp_vals, amp_vals

