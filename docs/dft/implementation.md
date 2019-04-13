# 7.2 Python implementation

In the [IPython notebook](https://nbviewer.jupyter.org/github/prandoni/COM303-Py3/blob/master/VoiceTransformer/VoiceTransformer.ipynb) (Section 4), we already have code that implements pitch shifting:

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

Unlike the granular synthesis chapter, the above function `DFT_pshift` is more suitable for a real-time implementation as the input `x[n:n+G]` and output `y[n:n+G]` buffers have the same length. Recall that this was not the case for the granular synthesis implementation in the IPython notebook (cell 70 under Section 3).

However, in order to make the task of porting to C much easier, we would like to implement the above effect without using array operations and using some of the [tips and tricks](../alien-voice/dsp_tips.md) we saw in the alien voice chapter, namely:

- Lookup tables.
- State variables.
- Integer data types.

There exist C libraries for performing the FFT (e.g. [FFTW](http://www.fftw.org/)) so we will still use `numpy`'s FFT library in our Python implementation.

{% hint style="info" %}
TASK 1: Your first task is to build a lookup table from a frequency bin to a rescaled bin, i.e. `ix = int(n * f)` for the scaling factor `f` in `DFT_rescale` above. This mapping is the same for each buffer so we can avoid redundant computations with a lookup table.

In [`utils_dft.py`](https://github.com/LCAV/dsp-labs/tree/master/scripts/dft/utils_dft.py), you can find an ***incomplete*** function `build_dft_rescale_lookup` for building this lookup table (see below). Read the `TODO` comment for hints on how to compute it!
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

In [`utils_dft.py`](https://github.com/LCAV/dsp-labs/tree/master/scripts/dft/utils_dft.py), you can find an ***incomplete*** function `dft_rescale` for performing this operation (see below). Edit the code under the `TODO` comment in order to perform the spectrum rescaling.
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

With our DFT rescaling functions now complete, we can procede to applying the effect on a fixed WAV file.

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

This code defines a new global variable `N_BINS` for the number of frequency bins in the positive half of the spectrum after performing a DFT of length `GRAIN_LEN_SAMP` (grain length in samples).

***Now for the fun part!*** That is, implementing the pitch shifting and trying it out.

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

1. Apply tapering window to the (integer) input grain.
2. Cast input grain to floating point.
3. Apply the DFT rescaling function.
4. Cast rescaled grain to integer type.

You may notice that in the provided script there is a new global array called `input_concat_float`, which you are suggested to use.

{% hint style="info" %}
TASK 4:  Modify the code after the comment `# TODO: rescale` so that it performs the DFT rescaling as detailed by the ***four*** steps above. Remember to perform operations sample-by-sample, as to replicate a C implementation.

_Hint: you should use `MAX_VAL` when casting between integer and floating point and vice versa._
{% endhint %}

With this additional code, your DFT-based pitch shifter should be complete!


## Real-time implementation

{% hint style="info" %}
TASK 5: When your implementaton works with the fixed WAV file, you can copy your `init` and `process` functions to the [`sounddevice` template](https://github.com/LCAV/dsp-labs/blob/master/scripts/dft/dft_pitch_shift_sounddevice.py) in order to run the effect in real-time with your laptop's soundcard.

We can now shift the speech up to create a chipmunk-like effect; no need to inhale helium!
{% endhint %}


**Congrats on implementing the DFT-based pitch shifter! You may notice some unwanted artifacts when applying this effect. More advanced versions (such as commercial "auto-tune" applications) take great care to minimize such artifacts by doing a more sophisticated analysis of each speech segment. We saw a similar type of analysis when computing the LPC coefficients in the previous chapter.**

**The code here is essentially ready for porting to C. However, we still need to introduce you to a library for computing the DFT. This will be covered in a (yet to come) section.**

**For now, enjoy your various voice effects!**
