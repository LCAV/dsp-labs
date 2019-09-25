# 3.3 Real-time with Python

In the process of implementing an algorithm on an embedded system, it is sometimes worth testing it in a workspace with less constraints than on the final environment. Here we propose a Python framework that will help in this prototype/debugging state for the alien voice effect \(and for future applications\). In the [next section](implementation.md) we will implement it on the STM32 board and set up a timer to benchmark our implementation.

The main idea of this framework is to code in the same way as it will be done in C. This probably means that the Python implementation will be very cumbersome. However, this will make the porting to C much easier. One big obstacle is to think in a block-based manner, as if buffers were filled and processed one after the other in real-time. The other obstacle of porting the code from Python to C is the definition of variables and to manage their sizes.

_**Python requirements: Python 3, numpy, scipy.io**_

## Empty template

We propose the following template for simulating real-time processing in C with Python. Please note the use of block processing and the definition of the variables with the `dtype` argument. You can find this code in the [repository](https://github.com/LCAV/dsp-labs) in the [`rt_simulated.py`](https://github.com/LCAV/dsp-labs/blob/master/scripts/_templates/rt_simulated.py) script.

We recommend cloning/downloading the repository so that you have all the necessary files in place, _i.e._ the `speech.wav` file for the code below and utility functions for the various voice effects we will be implementing.

```python
from scipy.io import wavfile
import numpy as np

# define necessary utility functions

# parameters
buffer_len = 256

# test signal
input_wav = "speech.wav"
samp_freq, signal = wavfile.read(input_wav)
signal = signal[:,]  # get first channel
n_buffers = len(signal)//buffer_len
data_type = signal.dtype

print("Sampling frequency : %d Hz" % samp_freq)
print("Data type          : %s" % signal.dtype)

# allocate input and output buffers
input_buffer = np.zeros(buffer_len, dtype=data_type)
output_buffer = np.zeros(buffer_len, dtype=data_type)

# state variables
def init():

    # declare variables used in `process`
    # global

    # define variables, lookup tables

    return


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # specify global variables modified here
    # global

    # process one sample at a time
    for n in range(buffer_len):

        # passthrough
        output_buffer[n] = input_buffer[n]

"""
Nothing to touch after this!
"""
init()
# simulate block based processing
signal_proc = np.zeros(n_buffers*buffer_len, dtype=data_type)
for k in range(n_buffers):

    # index the appropriate samples
    input_buffer = signal[k*buffer_len:(k+1)*buffer_len]
    process(input_buffer, output_buffer, buffer_len)
    signal_proc[k*buffer_len:(k+1)*buffer_len] = output_buffer

# write to WAV
wavfile.write("speech_mod.wav", samp_freq, signal_proc)
```

In the above code, we can observe several key sections:

* **Imports**: The normal Python imports, use only the necessary ones as they will also need to be ported to C.

  ```python
  from scipy.io import wavfile
  import numpy as np
  ```

* **Parameters definition**: Equivalent to `#define` definitions we did in C.

  ```python
  buffer_len = 256
  ```

* **Test signal**: Here we load a WAV test signal with the [`scipy.io.wavfile.read`](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.io.wavfile.read.html) function. We will parse the test signal one block at a time \(according to `buffer_len`\) in order to simulate a real-time operation.

  ```python
  input_wav = "speech.wav"
  samp_freq, signal = wavfile.read(input_wav)
  signal = signal[:,]  # get first channel
  n_buffers = len(signal)//buffer_len
  data_type = signal.dtype
  ```

* **Allocation**: We do this to fix the length of our buffer, as needs to be done in C. Note that we use the data type of the speech file; we try to use files that are 16-bit or 32-bit PCM.

  ```python
  input_buffer = np.zeros(buffer_len, dtype=data_type)
  output_buffer = np.zeros(buffer_len, dtype=data_type)
  ```

* **State variables**: The `init` function initializes all variables and should build all necessary lookup tables. We need the `global` definition for those variables used in other functions.
* `process` **function**: This is the heart of the block-based processing. Please note that every time a global variable is touched in a function, you will need to define it as `global` otherwise it will use a local clone. Note that we process _**one sample at a time**_ to replicate how we would have to code our STM32 board in C!
* **Simulate block processing**: This last part \(after `Nothing to touch after this!`\) slices the test signal into buffers, then calls the `process` function one buffer at a time. Finally, the modified output is written to a new WAV file.

## Alien voice effect

Below we provide you with the function that computes the sinusoid lookup table. This function is implemented in a [`utils.py`](https://github.com/LCAV/dsp-labs/blob/master/scripts/alien_voice/utils.py) file.

```python
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
```

As previously mentioned, we try to use integer variables in order to save processing time. So for the sinusoid lookup table, we will code it from the minimum to the maximum value possible in the corresponding \(typically integer\) data type. This scaling factor will need to be incorporated whenever using the lookup table.

In the above code, we can observe this use of the full range when creating the sinusoid table:

```python
SINE_TABLE = np.sin(w_mod*n_vals) * MAX_SINE
```

In the repository, there is an _**incomplete**_ script [`alien_voice_effect_incomplete.py`](https://github.com/LCAV/dsp-labs/blob/master/scripts/alien_voice/alien_voice_effect_incomplete.py) for you to complete. Notice that in the `init()` function we use the above `build_sine_table` function to create the sinusoid lookup table, and that the variables needed in the `process` function are declared as `global`.

```python
# state variables
def init():
    global sine_pointer
    global x_prev
    global GAIN
    global SINE_TABLE
    global MAX_SINE
    global LOOKUP_SIZE

    GAIN = 1
    x_prev = 0
    sine_pointer = 0

    # compute SINE TABLE
    vals = build_sine_table(f_sine, samp_freq, data_type)
    SINE_TABLE = vals[0]
    MAX_SINE = vals[1]
    LOOKUP_SIZE = vals[2]
```

Now we come to the main processing for the alien voice effect. Notice that `x_prev` and `sine_pointer` are declared as `global` as their values will be modified within the `process` function.

```python
def process(input_buffer, output_buffer, buffer_len):

    global x_prev
    global sine_pointer

    for n in range(buffer_len):

        # high pass filter
        if high_pass_on:
            output_buffer[n] = input_buffer[n] - x_prev
        else:
            output_buffer[n] = input_buffer[n]

        # TODO: perform modulation for effect
        output_buffer[n]

        # TODO: update state variables
        sine_pointer
        x_prev
```

{% hint style="info" %}
TASK 2: Under the comments with `TODO`, fill in the appropriate code in order to implement the alien voice effect.

_Reminder: normalize the sinusoid using the constant_ `MAX_SINE`_!_
{% endhint %}

You can test your implementation by running your script with the following line from the command line \(replacing `[script_name].py` with your script's name\):

```bash
python [script_name].py
```

If your script runs without error, your alien voice effect will be applied to the [`speech.wav`](https://github.com/LCAV/dsp-labs/blob/master/scripts/_templates/speech.wav) file, and the processed speech will be saved into a file called `"alien_voice_effect.wav"`.

When the output file sounds as expected - see/listen to [`alien_voice_effect_200Hz.wav`](https://github.com/LCAV/dsp-labs/blob/master/scripts/alien_voice/alien_voice_effect_200Hz.wav) in the repository - you can move on to implementing the effect in real-time!

### Real-time with laptop's sound card

Similar to the `rt_simulated.py` script we saw earlier, we also provide a template script for performing block-based processing with your laptop's sound card. The script, entitled [`rt_sounddevice.py`](https://github.com/LCAV/dsp-labs/blob/master/scripts/_templates/rt_sounddevice.py), can also be found in the repository.

The main difference is the setup code at the bottom of the script, which uses the [`sounddevice`](https://python-sounddevice.readthedocs.io) library:

```python
"""
Nothing to touch after this!
"""
try:
    sd.default.samplerate = samp_freq
    sd.default.blocksize = buffer_len
    sd.default.dtype = data_type

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        process(indata[:, 0], outdata[:, 0], frames)

    init()
    with sd.Stream(channels=1, callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
except KeyboardInterrupt:
    print('\nInterrupted by user')
```

Notice how we define a `callback` function that calls our `process` function and that before streaming audio we call the `init` function.

{% hint style="info" %}
TASK 3: Implement the alien voice effect in real-time using your laptop's sound card.

_Hint: complete the `process` function in the script_ [_`alien_voice_sounddevice_incomplete.py`_](https://github.com/LCAV/dsp-labs/blob/master/scripts/alien_voice/alien_voice_sounddevice_incomplete.py)_, which can also be found in the repository._
{% endhint %}

As before, run your script from the command line to try out your alien voice effect in real-time. Use headphones so that you avoid feedback!

**In the** [**next section**](implementation.md)**, we guide you through implementing the alien voice effect on the microcontroller, as we also setup a timer to benchmark the implementation.**

