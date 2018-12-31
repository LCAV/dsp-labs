import numpy as np


def build_dft_rescale_lookup(n_bins, shift_factor):
    """
    Build lookup table from DFT bins to rescaled bins.
    
    :param n_bins: Number of bins in positive half of DFT.
    :param shift_factor: Shift factor for voice effect.
    :return shift_idx: Mapping from bin to rescaled bin.
    :return max_bin: Maximum bin until rescaled is less than `n_bins`.
    """

    shift_idx = np.zeros(n_bins, dtype=np.int16)
    max_bin = n_bins
    for k in range(n_bins):
        """
        TODO:
        - compute the mapping from a bin `k` to the rescaled bin `ix`
        - if: smaller than `n_bins` store in lookup table
        - else: update value of `max_bin` and break from loop
        """
        shift_idx[k] = k

    return shift_idx, max_bin


def dft_rescale(x, n_bins, shift_idx, max_bin):
    """
    Rescale spectrum using the lookup table.

    :param x: Input segment in time domain
    :param n_bins: Number of bins in positive half of DFT.
    :param shift_idx: Mapping from bin to rescaled bin.
    :param max_bin: Maximum bin until rescaled is less than `n_bins`.
    :return: Pitch-shifted audio segment in time domain.
    """

    X = np.fft.rfft(x)
    Y = np.zeros(n_bins, dtype=np.complex)

    for k in range(max_bin):
        # TODO: use lookup table to shift original bins.
        Y[k] += X[k]

    # take inverse RFFT
    return np.fft.irfft(Y)


def ms2smp(ms, fs):
    """
    Parameters
    ----------
    ms: float
        Time in milliseconds
    fs: float
        Sampling rate in Hz.
    """
​
    # return corresponding length in samples


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

