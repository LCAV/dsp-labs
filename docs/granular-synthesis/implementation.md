# 4.2 Implementation

In the [IPython notebook](http://nbviewer.jupyter.org/github/prandoni/COM303/blob/master/voice_transformer/voicetrans.ipynb), we already have the code that implements pitch shifting via granular synthesis.

```python
def GS_pshift(x, f, G, overlap=0.2):
    N = len(x)
    y = np.zeros(N)
    # size of input given grain size and resampling factor
    igs = int(G * f + 0.5)
    win, stride = win_taper(G, overlap)
    for n in xrange(0, len(x) - max(igs, G), stride):
        w = resample(x[n:n+igs], f)
        y[n:n+G] += w * win

    return y
```

However, this implementation _**does not**_ work for a real-time scenario as the input buffer `x[n:n+igs]` and the output buffer `y[n:n+G]` do not have the same length! Also, we would like to perform operations on individual samples rather than vectors because the former is more representative of how we manipulate data/audio in C.

Nonetheless, having an implementation like the one above is still very useful before beginning a buffer-based implementation. It serves as a reference/sanity check before we attempt the \(typically\) more difficult buffer-based implementation.

In this chapter, we will guide you through the buffer-based implementation of this pitch shifting algorithm. What we present is certainly not the only approach but one we hope will help you for this exercise and for future real-time implementations.

Start off by copying the `utils.py` file from the [repository](https://github.com/LCAV/dsp-labs/tree/master/scripts/granular_synthesis) into a new directory for the granular synthesis effect. There are a few incomplete functions which we will complete down below.

## Save the MIPS! <a id="mips"></a>

A common term in DSP / Embedded Systems is _million instructions per seconds_ \(MIPS\) which reflects the computational cost of a particular implementation. One way to easily save on computational costs is by storing any values that are constant across consecutive frames. We already did this in the alien voice exercise when we stored sinusoid values in a _lookup table_ to perform amplitude modulation. The tradeoff that needs to be considered when storing lookup tables is memory.

So let's look at what should remain constant across consecutive frames so that we can store these values.

### User parameters

The parameters that need to be set by the user are:

1. Grain length in milliseconds.
2. Percentage of grain that overlaps with adjacent grains.
3. The pitch shift factor. In this exercise, we will limit ourselves to values below 1.0 for downward pitch shifts.

From the first two parameters and the sampling frequency, we need to determine:

1. The grain length in samples.
2. The stride length in samples.

{% hint style="info" %}
TASK 1: Inside `utils.py`, complete the function `ms2smp` \(below\) to convert a duration in milliseconds to a duration in samples, given a particular sampling frequency.
{% endhint %}

```python
def ms2smp(ms, fs):
    """
    Parameters
    ----------
    ms: float
        Time in milliseconds
    fs: float
        Sampling rate in Hz.
    """

    # return corresponding length in samples
```

### Lookup tables

From our user \(and derived\) parameters, we can compute _three_ lookup tables to avoid repeated computations:

1. **Tapered window**: given our grain length in samples and the percentage overlap, this window will remain the same and can be stored in an array.
2. **Interpolation times**: for a given grain length in samples and pitch shift factor, we will sample our grains at the same \(possibly\) fractional samples:

   $$
   \mathbf{t} = f\cdot[0, 1, ..., G-1]
   $$

   where $$f$$ is a downwards pitch shift factor and $$G$$ is the length of the grain in samples. Moreover, we will perform linear interpolation \(as specified [in the previous section](effect_description.md#interp_times)\), which requires us to determine the largest integer $$N$$ smaller than the desired time instant $$t$$. Rather than determining this repeatedly for every sample, we can store the integer values in an array that has the same length as the grain length in samples $$[N_0, N_1, ..., N_{G-1}]$$.

3. **Interpolation amplitudes**: we can similarly store the associated amplitude value for each fractional sample \(as specified [in the previous section](effect_description.md#interp_amps)\) in an array $$[a_0, a_1, ..., a_{G-1}]$$.

In `utils.py`, we have already given you the function to compute the tapered window, as shown below.

```python
def win_taper(grain_len_samp, grain_over, data_type=np.int16):

    edge_over = int(grain_len_samp * grain_over / 2)
    r = np.arange(0, edge_over) / float(edge_over)
    win = np.concatenate((r, 
        np.ones(grain_len_samp-2*edge_over), 
        r[::-1]))
    max_val = np.iinfo(data_type).max

    return (win*max_val).astype(data_type)
```

Notice how we set the data type for the lookup table. This is something we would like to do in our Python code to emulate as much as possible how we will be implementing this algorithm in C.

{% hint style="info" %}
TASK 2: In `utils.py`, complete the function \(below\) to compute the lookup tables for the interpolation times and amplitudes.

_Hint: you need to complete the function at the beginning of the_ `for` _loop._
{% endhint %}

```python
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
```

## State variables <a id="state_var"></a>

Now we should consider what values, such as samples or pointers to lookup tables \(as we saw in the alien voice effect\), need to be shared between consecutive frames, i.e. to notify the next buffer of the current state. A visual of the overlapping tapered grains will help us identify what needs to be "passed" between buffers.

![](../.gitbook/assets/viz_buffer.png)

_Figure: Visualizing buffers within overlapping grains._

Our stride length will determine our buffer length. In the figure above, our stride length is equivalent to the length between the lines labeled "buffer start" and "buffer end". Our new samples will be within this interval, as the samples between 0 and the "buffer start" line should have already been available in the previous buffer.

Moreover, the red line labeled "overlap start" indicates when the above buffer's grain will overlap with the next buffer's grain. Therefore, even though we have already received the samples between "overlap start" and "buffer end", _**we will not be able to output them yet since we still need to add them with weighted grain of the next buffer!**_ And computing the grain for the next buffer requires those samples after the "buffer end" line \(due to the resampling operation\).

The samples we will be able to output are between 0 and the "overlap start" line, also equivalent to the stride length. We therefore have a latency of:

$$
\text{latency} = \text{grain length} - \text{stride length},
$$

which is the length between 0 and "buffer start" and between "overlap start" and "buffer end".

{% hint style="info" %}
TASK 3: How many arrays do we need to pass/store between consecutive buffers? And how many samples should each of them have?

_Hint: due to the resampling operation, the next buffer's grain can only be computed when it contains all of the necessary samples._
{% endhint %}

## Allocating memory for intermediate values <a id="allocate_tmp"></a>

As we have several operations between our input and output samples, we will need some intermediate vectors to store a couple results. To see this, let's consider the "chain of events" for a single buffer:

1. Concatenate previous raw input samples with currently received samples: 

   $$
   x_{concat} = [x_{prev}, \text{ } x_{current}].
   $$

2. This should create an array of our desired grain length which we then need to resample using our two linear interpolation lookup tables:

   $$
   \text{grain} = \text{resample}(x_{concat})
   $$

3. We could apply our tapered window at the same time as resampling or right after:

   $$
   \text{grain} = \text{win} \times \text{grain}.
   $$

4. Finally, we need to combine the previous grain with the current one at the relevant overlapping samples and write to the output buffer. We also need to update the array\(s\) we share between buffers.

For a clean implementation, it is hopefully clear from the description above that we need at least two intermediate arrays for our computations at each buffer. Moreover, this need to be allocated beforehand.

## Coding it up! <a id="code"></a>

Now you should have enough information to implement the real-time version of downwards pitch shifting with granular synthesis.

{% hint style="info" %}
TASK 4: Complete the Python script below.

_Note: make sure that the below script is saved in the same directory as_ `utils.py` _and_ `speech.wav`_._
{% endhint %}

```python
import numpy as np
from scipy.io import wavfile
from utils import ms2smp, compute_stride, win_taper, build_linear_interp_table

"""
Pitch shifting with granular synthesis for shift factors <=1.0
"""

""" User selected parameters """
input_wav = "speech.wav"
grain_len = 20      # in milliseconds
grain_over = 0.3    # grain overlap (0,1)
shift_factor = 0.7  # <= 1.0

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
    SAMP_VALS, AMP_VALS = build_linear_interp_table(GRAIN_LEN_SAMP, shift_factor, data_type)

    # create arrays to pass between buffers (state variables)
    global ...

    # create arrays for intermediate values
    global ...


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # need to specify those global variables changing in this function (state variables and intermediate values)
    global ...

    # append samples from previous buffer
    for n in range(GRAIN_LEN_SAMP):
        ...

    # resample
    for n in range(GRAIN_LEN_SAMP):
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
file_name = "output_gran_synth.wav"
print("Result written to: %s" % file_name)
wavfile.write(file_name, samp_freq, signal_proc)
```

{% hint style="info" %}
BONUS: Implement the granular synthesis pitch shifting in real-time using your laptop's soundcard and the [`sounddevice`](https://python-sounddevice.readthedocs.io/en/0.3.11/) module.

_Hint: copy-and-paste your_ `init` _and_ `process` _functions \(once they are working\) into the script below._
{% endhint %}

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
    sd.default.samplerate = 16000
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

**Congrats on implementing granular synthesis pitch shifting! This is not a straightforward task, even in Python. But now that you have this code, the C implemention on the STM board should be much easier.**

