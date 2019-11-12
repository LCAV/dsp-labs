# 7.2 Python implementation

In the [IPython notebook](https://nbviewer.jupyter.org/github/prandoni/COM303-Py3/blob/master/VoiceTransformer/VoiceTransformer.ipynb) \(Section 4\), we already have code that implements pitch shifting:

```python
def DFT_rescale(x, f):
    """
    Utility function that pitch shift a short segment `x`.
    """
    X = np.fft.fft(x)
    # separate even and odd lengths
    parity = (len(X) % 2 == 0)
    N = len(X) / 2 + 1 if parity else (len(X) + 1) / 2
    Y = np.zeros(N, dtype=np.complex)
    # work only in the first half of the DFT vector since input is real
    for n in xrange(0, N):
        # accumulate original frequency bins into rescaled bins
        ix = int(n * f)
        if ix < N:
            Y[ix] += X[n]
    # now rebuild a Hermitian-symmetric DFT
    Y = np.r_[Y, np.conj(Y[-2:0:-1])] if parity else np.r_[Y, np.conj(Y[-1:0:-1])]
    return np.real(np.fft.ifft(Y))


def DFT_pshift(x, f, G, overlap=0):
    """
    Function for pitch shifting an input signal by applying the above utility function on overlapping segments.
    """
    N = len(x)
    y = np.zeros(N)
    win, stride = win_taper(G, overlap)
    for n in xrange(0, len(x) - G, stride):
        w = DFT_rescale(x[n:n+G] * win, f)
        y[n:n+G] += w * win
    return y
```

Unlike the granular synthesis chapter, the above function `DFT_pshift` is more suitable for a real-time implementation as the input `x[n:n+G]` and output `y[n:n+G]` buffers have the same length. Recall that this was not the case for the granular synthesis implementation in the IPython notebook \(cell 70 under Section 3\).

However, in order to make the task of porting to C much easier, we would like to implement the above effect without using array operations and using some of the [tips and tricks](../alien-voice/dsp_tips.md) we saw in the alien voice chapter, namely:

* Lookup tables.
* State variables.
* Integer data types.

There exist C libraries for performing the FFT \(e.g. [FFTW](http://www.fftw.org/)\) so we will still use `numpy`'s FFT library in our Python implementation.

{% hint style="info" %}
TASK 1: Your first task is to build a lookup table from a frequency bin to a rescaled bin, i.e. `ix = int(n * f)` for the scaling factor `f` in `DFT_rescale` above. This mapping is the same for each buffer so we can avoid redundant computations with a lookup table.

In [`utils_dft.py`](https://github.com/LCAV/dsp-labs/tree/master/scripts/dft/utils_dft.py), you can find an _**incomplete**_ function `build_dft_rescale_lookup` for building this lookup table \(see below\). Read the `TODO` comment for hints on how to compute it!
{% endhint %}

```python
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
        TODO
        - compute the mapping from a bin `k` to the rescaled bin `ix`
        - if: smaller than `n_bins` store in lookup table
        - else: update value of `max_bin` and break from loop
        """
        shift_idx[k] = k

    return shift_idx, max_bin
```

{% hint style="info" %}
TASK 2: Compute the spectrum of the shifted audio segment, using the lookup table computed with `build_dft_rescale_lookup`.

In [`utils_dft.py`](https://github.com/LCAV/dsp-labs/tree/master/scripts/dft/utils_dft.py), you can find an _**incomplete**_ function `dft_rescale` for performing this operation \(see below\). Edit the code under the `TODO` comment in order to perform the spectrum rescaling.
{% endhint %}

```python
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
```

Notice that we use the functions [`np.fft.rfft`](https://docs.scipy.org/doc/numpy-1.15.1/reference/generated/numpy.fft.rfft.html) and [`np.fft.irfft`](https://docs.scipy.org/doc/numpy-1.15.1/reference/generated/numpy.fft.irfft.html) so that we only work with the positive half of the spectrum, as we have a real-valued input signal.

With our DFT rescaling functions now complete, we can proceed to applying the effect on a fixed WAV file.

{% hint style="info" %}
TASK 3: As a sanity check, copy your code from your granular synthesis implementation below the comments `# copy from granular synthesis` into the [incomplete DFT pitch shifting script](https://github.com/LCAV/dsp-labs/tree/master/scripts/dft/dft_pitch_shift_incomplete.py).

Complete also the `ms2smp` function in [`utils_dft.py`](https://github.com/LCAV/dsp-labs/blob/master/scripts/dft/utils_dft.py)

Run the file and make sure the output is unchanged from the input, i.e. no pitch shifting.
{% endhint %}

At the top of the script, we have a new code snippet:

```python
is_even = (GRAIN_LEN_SAMP % 2 == 0)  
if is_even:
    NFFT = GRAIN_LEN_SAMP // 2 + 1
else:
    NFFT = (GRAIN_LEN_SAMP + 1) // 2
```

This code defines a new global variable `NFFT` for the number of frequency bins in the positive half of the spectrum after performing a DFT of length `GRAIN_LEN_SAMP` \(grain length in samples\).

_**Now for the fun part!**_  That is, implementing the pitch shifting and trying it out.

If we look at the following code snippet from the function `DFT_pshift` of the IPython notebook:

```python
w = DFT_rescale(x[n:n+G] * win, f)
y[n:n+G] += w * win
```

We can observe three steps:

1. Apply the tapering window to the input grain: `x[n:n+G] * win`.
2. Apply the DFT rescaling function.
3. Apply the tapering window to the DFT-rescaled grain: `w * win`.

The last step is already performed as part of our granular synthesis code, so we have to implement the first two steps. However, we will also have additional steps of casting our input grain to floating point, as the FFT works with this variable type, and casting back to integer.

1. Apply tapering window to the \(integer\) input grain.
2. Cast input grain to floating point.
3. Apply the DFT rescaling function.
4. Cast rescaled grain to integer type.

You may notice that in the provided script there is a new global array called `input_concat_float`, which you are suggested to use.

{% hint style="info" %}
TASK 4: Modify the code after the comment `# TODO: rescale` so that it performs the DFT rescaling as detailed by the _**four**_ steps above. Remember to perform operations sample-by-sample, as to replicate a C implementation.

_Hint: you should use `MAX_VAL` when casting between integer and floating point and vice versa._
{% endhint %}

With this additional code, your DFT-based pitch shifter should be complete!

## Real-time implementation

{% hint style="info" %}
TASK 5: When your implementaton works with the fixed WAV file, you can copy your `init` and `process` functions to the [`sounddevice` template](https://github.com/LCAV/dsp-labs/blob/master/scripts/dft/dft_pitch_shift_sounddevice.py) in order to run the effect in real-time with your laptop's soundcard.

We can now shift the speech up to create a chipmunk-like effect; no need to inhale helium!
{% endhint %}

**Congrats on implementing the DFT-based pitch shifter! You may notice some unwanted artifacts when applying this effect. More advanced versions \(such as commercial "auto-tune" applications\) take great care to minimize such artifacts by doing a more sophisticated analysis of each speech segment. We saw a similar type of analysis when computing the LPC coefficients in the previous chapter.**

**The code here is essentially ready for porting to C. However, we still need to introduce you to a library for computing the DFT. This will be covered in a \(yet to come\) section.**

**For now, enjoy your various voice effects!**

## Tasks solutions

{% tabs %}
{% tab title="Anti-spoiler tab" %}
Are you sure you are ready to see the solution? ;\)
{% endtab %}

{% tab title="Task 1" %}
With the following code you will be able to create the new frequency vector:

```python
def build_dft_rescale_lookup(n_bins, shift_factor):
    """
    Build lookup table from FFT bins to rescaled bins.

    :param n_bins: Number of bins in positive half of FFT.
    :param shift_factor: Shift factor for voice effect.
    :return shift_idx: Mapping from bin to rescaled bin.
    :return max_bin: Maximum bin until rescaled is less than `n_bins`.
    """

    shift_idx = np.zeros(n_bins, dtype=np.int16)
    max_bin = n_bins
    for k in range(n_bins):
        ix = int(k * shift_factor)
        if ix < n_bins:
            shift_idx[k] = ix
        else:
            max_bin = k
            break

    return shift_idx, max_bin
```
{% endtab %}

{% tab title="Task 2" %}
Adding the shift array calculated in the previous task:

```python
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

    # accumulate original frequency bins into rescaled bins
    for k in range(max_bin):
        Y[shift_idx[k]] += X[k]

    # take inverse RFFT
    return np.fft.irfft(Y)
```
{% endtab %}

{% tab title="Task 3" %}
There is how your main script should look like at this stage.

```python
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
    global x_overlap, y_overlap
    x_overlap = np.zeros(OVERLAP_LEN, dtype=data_type)
    y_overlap = np.zeros(OVERLAP_LEN, dtype=data_type)
    
    # TODO: create arrays for intermediate values
    global grain, input_concat
    input_concat = np.zeros(GRAIN_LEN_SAMP, dtype=data_type)
    grain = np.zeros(GRAIN_LEN_SAMP, dtype=data_type)


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # TODO: need to specify those global variables changing in this function (state variables and intermediate values)
    global grain, input_concat, x_overlap, y_overlap, input_concat_float

    """
    Apply effect
    """
    # TODO: append samples from previous buffer
    for n in range(GRAIN_LEN_SAMP):
        if n < OVERLAP_LEN:
            input_concat[n] = x_overlap[n]
        else:
            input_concat[n] = input_buffer[n-OVERLAP_LEN]

    # TODO: rescale
    for n in range(GRAIN_LEN_SAMP):
        grain[n] = input_concat[n]

    # TODO: apply window
    for n in range(GRAIN_LEN_SAMP):
        grain[n] = (WIN[n]/MAX_VAL)*grain[n]

    # TODO: write to output and update state variables
    for n in range(GRAIN_LEN_SAMP):
        # overlapping part
        if n < OVERLAP_LEN:
            output_buffer[n] = grain[n] + y_overlap[n]
        # non-overlapping part
        elif n < STRIDE:
            output_buffer[n] = grain[n]
        # update state variables
        else:
            x_overlap[n-STRIDE] = input_buffer[n-OVERLAP_LEN] 
            y_overlap[n-STRIDE] = grain[n]

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
wavfile.write(file_name, samp_freq, signal_proc)?
```
{% endtab %}

{% tab title="Task 4" %}
Here is the final rescale operation:

```python
# rescale
for n in range(GRAIN_LEN_SAMP):
    input_concat_float[n] = input_concat[n] / MAX_VAL * (WIN[n]/MAX_VAL)
input_concat_float = dft_rescale(input_concat_float, N_BINS, SHIFT_IDX, MAX_BIN)
for n in range(GRAIN_LEN_SAMP):
    grain[n] = int(input_concat_float[n]*MAX_VAL)
```

It leads to the following finished DFT Pitch shifting script.

```python
import numpy as np
from scipy.io import wavfile
import os
from utils_dft_sol import dft_rescale, build_dft_rescale_lookup, ms2smp, compute_stride, win_taper

"""
DFT pitch shifting
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

    # create arrays to pass between buffers (state variables)
    global x_overlap, y_overlap
    x_overlap = np.zeros(OVERLAP_LEN, dtype=data_type)
    y_overlap = np.zeros(OVERLAP_LEN, dtype=data_type)

    # create arrays for intermediate values
    global grain, input_concat
    input_concat = np.zeros(GRAIN_LEN_SAMP, dtype=data_type)
    grain = np.zeros(GRAIN_LEN_SAMP, dtype=data_type)
    


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # need to specify those global variables changing in this function (state variables and intermediate values)
    global grain, input_concat, x_overlap, y_overlap, input_concat_float

    """
    Apply effect
    """
    # append samples from previous buffer, construction of the grain
    for n in range(GRAIN_LEN_SAMP):
        if n < OVERLAP_LEN:
            input_concat[n] = x_overlap[n]
        else:
            input_concat[n] = input_buffer[n-OVERLAP_LEN]

    # rescale
    for n in range(GRAIN_LEN_SAMP):
        input_concat_float[n] = input_concat[n] / MAX_VAL * (WIN[n]/MAX_VAL)
    input_concat_float = dft_rescale(input_concat_float, N_BINS, SHIFT_IDX, MAX_BIN)
    for n in range(GRAIN_LEN_SAMP):
        grain[n] = int(input_concat_float[n]*MAX_VAL)

    

    # apply window
    for n in range(GRAIN_LEN_SAMP):
        grain[n] = (WIN[n]/MAX_VAL)*grain[n]

    # write to output
    for n in range(GRAIN_LEN_SAMP):
        # overlapping part
        if n < OVERLAP_LEN:
            output_buffer[n] = grain[n] + y_overlap[n]
        # non-overlapping part
        elif n < STRIDE:
            output_buffer[n] = grain[n]
        # update state variables
        else:
            x_overlap[n-STRIDE] = input_buffer[n-OVERLAP_LEN] 
            y_overlap[n-STRIDE] = grain[n]


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
```
{% endtab %}

{% tab title="Task 5" %}
Once again there is the adaptation of the sounddevice template to our DFT pitch shifting algorithm:

```python
import numpy as np
from utils import ms2smp, compute_stride, win_taper, build_linear_interp_table
import sounddevice as sd

"""
Real-time pitch shifting with granular synthesis for shift factors <=1.0
"""

""" User selected parameters """
grain_len = 30
grain_over = 0.2
shift_factor = 0.7 
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

    # lookup table for tapering window
    global WIN
    WIN = win_taper(GRAIN_LEN_SAMP, grain_over, data_type)

    # lookup table for linear interpolation
    global SAMP_VALS
    global AMP_VALS
    SAMP_VALS, AMP_VALS = build_linear_interp_table(GRAIN_LEN_SAMP, shift_factor, data_type)

    # create arrays to pass between buffers (state variables)
    global x_overlap
    global y_overlap
    x_overlap = np.zeros(OVERLAP_LEN, dtype=data_type)
    y_overlap = np.zeros(OVERLAP_LEN, dtype=data_type)

    # create arrays for intermediate values
    global grain
    global input_concat
    input_concat = np.zeros(GRAIN_LEN_SAMP, dtype=data_type)
    grain = np.zeros(GRAIN_LEN_SAMP, dtype=data_type)


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # need to specify those global variables changing in this function (state variables and intermediate values)
    global x_overlap
    global y_overlap
    global input_concat
    global grain

    # append samples from previous buffer
    for n in range(GRAIN_LEN_SAMP):
        if n < OVERLAP_LEN:
            input_concat[n] = x_overlap[n]
        else:
            input_concat[n] = input_buffer[n-OVERLAP_LEN]

    # resample
    for n in range(GRAIN_LEN_SAMP):
        grain[n] = (AMP_VALS[n]/MAX_VAL*input_concat[SAMP_VALS[n]] + \
            (1-AMP_VALS[n]/MAX_VAL)*input_concat[SAMP_VALS[n]+1]) 

    # apply window
    for n in range(GRAIN_LEN_SAMP):
        grain[n] = (WIN[n]/MAX_VAL)*grain[n]
    
    # write to output
    for n in range(GRAIN_LEN_SAMP):
        # overlapping part
        if n < OVERLAP_LEN:
            output_buffer[n] = grain[n] + y_overlap[n]
        # non-overlapping part
        elif n < STRIDE:
            output_buffer[n] = grain[n]
        # update state variables
        else:
            x_overlap[n-STRIDE] = input_buffer[n-OVERLAP_LEN] 
            y_overlap[n-STRIDE] = grain[n]


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
    parser.exit('\nInterrupted by user')
```
{% endtab %}
{% endtabs %}

