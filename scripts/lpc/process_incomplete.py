def process(input_buffer, output_buffer, buffer_len):

    # need to specify those global variables changing in this function (state variables and intermediate values)
    global ...

    # append samples from previous buffer
    for n in range(GRAIN_LEN_SAMP):
        ...

    # save the last raw samples of the grain before modifying them
	...

    # obtain the LPC coefficients and reverse filter the grain
    if use_LPC :
	...

    # resample
    for n in range(GRAIN_LEN_SAMP):
        ...

    # forward filter the resampled version of the modified grain
    if use_LPC :
	...

    # apply window
    for n in range(GRAIN_LEN_SAMP):
        ...

    # write to output
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