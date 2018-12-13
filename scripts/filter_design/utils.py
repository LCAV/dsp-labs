import numpy as np


def add_offset(signal, offset):
    """
    Add an artificial offset to the provided signal.

    :param signal: Original mono signal (which may already have offset).
    :param offset: Artificial DC offset to add
    :return:
    """

    # get data type
    data_type = signal.dtype
    try:
        # integer type
        MAX_VAL = abs(np.iinfo(data_type).min)
    except:
        # float type
        MAX_VAL = abs(np.finfo(data_type).min)

    # new max val to normalize within
    _max_val = MAX_VAL + offset

    # remove offset if already there
    signal = signal - np.mean(signal)
    signal = ((signal / _max_val) * MAX_VAL + offset).astype(data_type)

    return signal

