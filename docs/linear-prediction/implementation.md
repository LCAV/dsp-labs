# 6.2 Implementation

Below are the LPC utility functions provided in the [IPython notebook](https://nbviewer.jupyter.org/github/prandoni/COM303-Py3/blob/master/VoiceTransformer/VoiceTransformer.ipynb).

```python
def bac(x, p):
    # compute the biased autocorrelation for x up to lag p
    L = len(x)
    r = np.zeros(p+1)
    for m in range(0, p+1):
        for n in range(0, L-m):
            r[m] += x[n] * x[n+m]
        r[m] /= float(L)
    return r


def ld(r, p):
    # solve the toeplitz system using the Levinson-Durbin algorithm
    g = r[1] / r[0]
    a = np.array([g])
    v = (1. - g * g) * r[0];
    for i in range(1, p):
        g = (r[i+1] - np.dot(a, r[1:i+1])) / v
        a = np.r_[ g,  a - g * a[i-1::-1] ]
        v *= 1. - g*g
    # return the coefficients of the A(z) filter
    return np.r_[1, -a[::-1]]


def lpc(x, p):
    # compute p LPC coefficients for a speech segment
    return ld(bac(x, p), p)
```

The function `bac` is sufficient from a real-time microcontroller "point of view" as it performs operations sample-by-sample in order to compute the entries of the \(biased\) autocorrelation matrix $$R$$. For our microcontroller implementation in `C`, we may, however, wish to pre-allocate a _**global**_ array for `r`, as its values will change for each grain.

The function `ld` \(for performing the Levinson-Durbin recursion\) is _**not suitable**_ for a microcontroller C implementation, as we have array operations \(`np.dot`\) and memory is allocated on the fly \(`np.r_` concatenates values into a new row vector\).

We will therefore re-implement the `ld` function so that porting it to C will be much more straightforward. Below we provide you an _**incomplete**_ function `ld_eff` that is meant to implement Levinson-Durbin recursion in a "C-friendly" manner.

```python
def ld_eff(r, order):
    # solve the toeplitz system using the Levinson-Durbin algorithm
    a = np.ones(order+1)
    a_prev = np.ones(order)
    a[1] = r[1]/r[0]
    for p in range(2, order+1):

        for j in range(1, p):
            a_prev[j] = a[j]

        # TODO: compute `k` from `r` and `a`
        k = 1

        # TODO: compute new `a` with `a_prev` and `k`
        # separate vector is needed so we don't overwrite!
        for j in range(1, p):
            a[j] = a_prev[j]
        a[p] = k

    # by convention, have negative of coefficients
    for p in range(1, order+1):
        a[p] *= -1

    return a
```

{% hint style="info" %}
TASK 1: Complete the above function `ld_eff` in the [`utils_lpc.py`](https://github.com/LCAV/dsp-labs/blob/master/scripts/linear_prediction/utils_lpc.py) file so that it correctly implements Levinson-Durbin recursion.

_Hint: we refer you to_ [_**this document**_](https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-341-discrete-time-signal-processing-fall-2005/lecture-notes/lec13.pdf) _\(p. 5\) in order to determine the correct expression for `k` and `a[j]`._
{% endhint %}

You can test your implementation by running the script [`test_lpc_utils.py`](https://github.com/LCAV/dsp-labs/blob/master/scripts/linear_prediction/test_lpc_utils.py). The script should print `CORRECT!` if you have successfully implemented the function; otherwise it will print `Something's wrong...` or error out if you have a bug in your implementation.

As for `bac`, for our microcontroller implementation of `ld_eff` in `C`, we may wish to pre-allocate global arrays for `a` and `a_prev`.

## Modifying the `process` function

In fact, it is possible to use the same function for "vanilla" and LPC granular synthesis pitch shifting. We can do this by introducing a boolean variable `use_LPC`.

Below, we provide the _**incomplete**_ `process` function, which you can find in [this script](https://github.com/LCAV/dsp-labs/blob/master/scripts/linear_prediction/granular_synthesis_LPC_incomplete.py).

```python
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
        # compute LPC coefficients, cast input to `np.float32`
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
```

{% hint style="info" %}
TASK 2: As a sanity check, you can first copy your code from your granular synthesis implementation into the above `process` function and the `init` function in the script [granular\_synthesis\_LPC\_incomplete.py](https://github.com/LCAV/dsp-labs/blob/master/scripts/linear_prediction/granular_synthesis_LPC_incomplete.py). \(Copy the appropriate lines under the comments `# copy from granular synthesis`.\)

Run the file and make sure the output is the same as before!
{% endhint %}

We can now begin adding the code for LPC! Let's remind ourselves of the steps we mentioned in the previous section:

### 1. Compute the LPC coefficients for the input speech

{% hint style="info" %}
TASK 3: Complete the code after the comment `# compute LPC coefficients`, namely compute the LPC coefficients for the input raw samples.

_Hint: use the function `lpc_eff` and cast the input raw samples to `np.float32`._
{% endhint %}

### 2. Inverse-filter the raw samples in order to estimate the excitation

{% hint style="info" %}
TASK 4: Complete the code after the comment `# estimate excitation`, namely filter the raw input samples with the "recently" obtained LPC coefficients.

_Hints:_

* _We are applying an **FIR filter** in this case; recall your implementation from the **Digital Filter Design** chapter, notably the code from_ [_this script_](https://github.com/LCAV/dsp-labs/blob/master/scripts/filter_design/biquad_direct_form_1_incomplete.py#L62)_. In this case `input_buffer` should be the concatenated raw samples vector, `x` should be `lpc_prev_in`, and there is no equivalent to `y` since this is an FIR filter._
* _You can rewrite into the concatenated raw samples vector, **NOT** `input_buffer`!_
* _Don't forget to apply `GAIN`!_
{% endhint %}

### 3. Apply pitch-shifting on the excitation signal

This is already done with your code from the granular synthesis effect!

### 4. Forward-filter the modified grain

{% hint style="info" %}
TASK 5: Complete the code after the comment `# forward filter the resampled grain`, namely filter the resampled grain with the LPC coefficients.
{% endhint %}

Hints:

* We are applying an _**IIR filter**_ in this case.
* You can rewrite into the resampled grain vector.
* Use `lpc_prev_out` for the previous output samples.

And that's all the extra code needed for this LPC feature! Try out your completed [granular\_synthesis\_LPC\_incomplete.py](https://github.com/LCAV/dsp-labs/blob/master/scripts/linear_prediction/granular_synthesis_LPC_incomplete.py) script with the fixed WAV file \(make sure `use_LPC=True`\) and listen to the output to see if it sounds correct.

_If you notice some strange output, make sure you are casting \(when appropriate\) to `int`; this is a common point for mistakes._

## Real-time implementation

{% hint style="info" %}
TASK 6: When your implementaton works with the fixed WAV file, you can complete the [`sounddevice` template](https://github.com/LCAV/dsp-labs/blob/master/scripts/linear_prediction/granular_synthesis_LPC_sounddevice_incomplete.py) in order to run the effect in real-time with your laptop's soundcard.
{% endhint %}

**Congrats on incorporating this LPC component to your granular synthesis pitch shifter! Given the Python implementation, the porting to C should be more straightforward. As noted earlier, it may be useful to pre-allocate memory for the LPC coefficients and their computation.**

**In the** [**next chapter**](../dft/)**, we implement a DFT-based pitch shifter. With this effect, we will shift our speech up in order to create a chipmunk-like voice; no need to inhale helium!**

## Tasks solutions

{% tabs %}
{% tab title="Anti-spoiler tab" %}
Are you sure you are ready to see the solution? ;\)
{% endtab %}

{% tab title="Task 1" %}




```python
def ld(r, p):
    # solve the toeplitz system using the Levinson-Durbin algorithm
    g = r[1] / r[0]
    a = np.array([g])
    v = (1. - g * g) * r[0];
    for i in range(1, p):
        g = (r[i+1] - np.dot(a, r[1:i+1])) / v
        a = np.r_[ g,  a - g * a[i-1::-1] ]
        v *= 1. - g*g
    # return the coefficients of the A(z) filter
    return np.r_[1, -a[::-1]]
```
{% endtab %}

{% tab title="Task 2" %}
As a reminder there is the granula synthesis process function:

```python
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


```
{% endtab %}

{% tab title="Task 3" %}


```python
# compute LPC coefficients
if USE_LPC:
    a = lpc(np.float32(input_concat), P) # Compute coefs 
    input_concat = sp.lfilter(a, [1.], input_concat) # Modify the grain so that it contains the excitation signal
```
{% endtab %}

{% tab title="Task 4" %}
?
{% endtab %}

{% tab title="Task 5" %}
There is the code used to apply the filter:

```python
# apply filter so that energy envelope is preserved
if USE_LPC:
    grain = sp.lfilter([1], a, grain)
```

There is the complete solution for this chapter:

```python
There is the complete solution of this chapter:
import numpy as np
from scipy.io import wavfile
import scipy.signal as sp
from utils_sol import ms2smp, compute_stride, win_taper, build_linear_interp_table, lpc

"""
Pitch shifting with granular synthesis for shift factors <=1.0
"""

""" User selected parameters """
input_wav = "voiced.wav"
grain_len = 20      # in milliseconds
grain_over = 0.3    # grain overlap (0,1)
shift_factor = 0.9  # <= 1.0
P = 20
USE_LPC = True

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

    # compute LPC coefficients
    if USE_LPC:
        a = lpc(np.float32(input_concat), P) # Compute coefs 
        input_concat = sp.lfilter(a, [1.], input_concat) # Modify the grain so that it contains the excitation signal

    # resample
    for n in range(GRAIN_LEN_SAMP):
        grain[n] = (AMP_VALS[n]/MAX_VAL*input_concat[SAMP_VALS[n]] + \
            (1-AMP_VALS[n]/MAX_VAL)*input_concat[SAMP_VALS[n]+1]) 

    # apply filter so that energy envelope is preserved
    if USE_LPC:
        grain = sp.lfilter([1], a, grain)

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
if USE_LPC:
    file_name = "output_gran_synth.wav"
else:
    file_name = "output_gran_synth_lpc.wav"
file_name = "voiced_gran_synth_lpc.wav"
print("Result written to: %s" % file_name)
wavfile.write(file_name, samp_freq, signal_proc)
```
{% endtab %}

{% tab title="Task 6" %}
Copy the same sounddevice template as in the prevous parts and insert the _utils.py_ and _process\(\)_ function from Task 5.
{% endtab %}
{% endtabs %}

