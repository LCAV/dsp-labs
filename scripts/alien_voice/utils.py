import numpy as np


def build_sine_table(f_sine, samp_freq, data_type):
    """
    :param f_sine: Modulate frequency for voice effect in Hz.
    :param samp_freq: Sampling frequency in Hz
    :param data_type: Data type of sinusoid table. Must be signed integer type.
    :return:
    """

    if data_type is np.int16 or np.int32:
        MAX_SINE = np.iinfo(data_type).max
    else:
        raise ValueError("Data type must be signed integer.")

    # periods
    samp_per = 1./samp_freq
    sine_per = 1./f_sine

    # compute time instances
    t_vals = np.arange(0, sine_per, samp_per)
    LOOKUP_SIZE = len(t_vals)
    n_vals = np.arange(LOOKUP_SIZE)

    # compute the sine table
    w_mod = 2*np.pi*f_sine/samp_freq
    SINE_TABLE = np.sin(w_mod*n_vals) * MAX_SINE

    return SINE_TABLE, MAX_SINE, LOOKUP_SIZE
