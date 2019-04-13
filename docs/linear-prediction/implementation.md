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

The function `bac` is sufficient from a real-time microcontroller "point of view" as it performs operations sample-by-sample in order to compute the entries of the (biased) autocorrelation matrix $$R$$. For our microcontroller implementation in `C`, we may, however, wish to pre-allocate a ***global*** array for `r`, as its values will change for each grain. 

The function `ld` (for performing the Levinson-Durbin recursion) is ***not suitable*** for a microcontroller C implementation, as we have array operations (`np.dot`) and memory is allocated on the fly (`np.r_` concatenates values into a new row vector).

We will therefore re-implement the `ld` function so that porting it to C will be much more straightforward. Below we provide you an ***incomplete*** function `ld_eff` that is meant to implement Levinson-Durbin recursion in a "C-friendly" manner.

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

_Hint: we refer you to [**this document**](https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-341-discrete-time-signal-processing-fall-2005/lecture-notes/lec13.pdf) (p. 5) in order to determine the correct expression for `k` and `a[j]`._
{% endhint %}

You can test your implementation by running the script [`test_lpc_utils.py`](https://github.com/LCAV/dsp-labs/blob/master/scripts/linear_prediction/test_lpc_utils.py). The script should print `CORRECT!` if you have successfully implemented the function; otherwise it will print `Something's wrong...` or error out if you have a bug in your implementation.

As for `bac`, for our microcontroller implementation of `ld_eff` in `C`, we may wish to pre-allocate global arrays for `a` and `a_prev`.


## Modifying the `process` function

In fact, it is possible to use the same function for "vanilla" and LPC granular synthesis pitch shifting. We can do this by introducing a boolean variable `use_LPC`.

Below, we provide the ***incomplete*** `process` function, which you can find in [this script](https://github.com/LCAV/dsp-labs/blob/master/scripts/linear_prediction/granular_synthesis_LPC_incomplete.py).


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

TASK 2: As a sanity check, you can first copy your code from your granular synthesis implementation into the above `process` function and the `init` function in the script [granular_synthesis_LPC_incomplete.py](https://github.com/LCAV/dsp-labs/blob/master/scripts/linear_prediction/granular_synthesis_LPC_incomplete.py). (Copy the appropriate lines under the comments `# copy from granular synthesis`.)

Run the file and make sure the output is the same as before!
{% endhint %}

We can now begin adding the code for LPC! Let's remind ourselves of the steps we mentioned in the previous section:

##### 1. Compute the LPC coefficients for the input speech

{% hint style="info" %}

TASK 3: Complete the code after the comment `# compute LPC coefficients`, namely compute the LPC coefficients for the input raw samples.

_Hint: use the function `lpc_eff` and cast the input raw samples to `np.float32`._
{% endhint %}


##### 2. Inverse-filter the raw samples in order to estimate the excitation

{% hint style="info" %}

TASK 4: Complete the code after the comment `# estimate excitation`, namely filter the raw input samples with the "recently" obtained LPC coefficients.
{% endhint %}

Hints: 
- We are applying an ***FIR filter*** in this case; recall your implementation from the **Digital Filter Design** chapter, notably the code from [this script](https://github.com/LCAV/dsp-labs/blob/master/scripts/filter_design/biquad_direct_form_1_incomplete.py#L62). In this case `input_buffer` should be the concatenated raw samples vector, `x` should be `lpc_prev_in`, and there is no equivalent to `y` since this is an FIR filter.
- You can rewrite into the concatenated raw samples vector, **NOT** `input_buffer`!
- Don't forget to apply `GAIN`!


##### 3. Apply pitch-shifting on the excitation signal

This is already done with your code from the granular synthesis effect!

##### 4. Forward-filter the modified grain

{% hint style="info" %}

TASK 5: Complete the code after the comment `# forward filter the resampled grain`, namely filter the resampled grain with the LPC coefficients.
{% endhint %}

Hints: 
- We are applying an ***IIR filter*** in this case.
- You can rewrite into the resampled grain vector.
- Use `lpc_prev_out` for the previous output samples.

And that's all the extra code needed for this LPC feature! Try out your completed [granular_synthesis_LPC_incomplete.py](https://github.com/LCAV/dsp-labs/blob/master/scripts/linear_prediction/granular_synthesis_LPC_incomplete.py) script with the fixed WAV file (make sure `use_LPC=True`) and listen to the output to see if it sounds correct. 

_If you notice some strange output, make sure you are casting (when appropriate) to `int`; this is a common point for mistakes._


## Real-time implementation

{% hint style="info" %}
TASK 6: When your implementaton works with the fixed WAV file, you can complete the [`sounddevice` template](https://github.com/LCAV/dsp-labs/blob/master/scripts/linear_prediction/granular_synthesis_LPC_sounddevice_incomplete.py) in order to run the effect in real-time with your laptop's soundcard.
{% endhint %}

**Congrats on incorporating this LPC component to your granular synthesis pitch shifter! Given the Python implementation, the porting to C should be more straightforward. As noted earlier, it may be useful to pre-allocate memory for the LPC coefficients and their computation.**

**In the [next chapter](../dft/README.md), we implement a DFT-based pitch shifter. With this effect, we will shift our speech up in order to create a chipmunk-like voice; no need to inhale helium!**
