# 3.3 Real-time implementation with Python

In the process of implementing an algorithm on an embedded system, it is sometimes worth testing it in a workspace with less constraints than on the final environment. Here we propose a Python framework that will help in this prototype/debugging state for the alien voice effect (and for future applications). In the [next section](../4/implementation.md) we will implement it on the STM32 board and set up a timer to benchmark our implementation.

The whole idea of this framework is to code in the same way as it will be done in C. It probably means that the implementation will be very cumbersome in Python but very easy to port to C in the final stage. One big obstacle is to think in a block-based manner, as if buffers were filled and processed one after the other in real-time. The other obstacle of porting the code from Python to C is the definition of variables and to manage their sizes.

**_Python requirements: Python 3, numpy, scipy.io_**

## Empty template

We propose the following template for simulating real-time processing in C with Python. Note that the below code will not run as `...` is not valid syntax! Please note the use of block processing and the definition of the variables (the `dtype` arguments).

```Python
from scipy.io import wavfile
import numpy as np

# define necessary utility functions
...

# parameters
buffer_len = 256
...

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

    # declare variables used in process
    global ...

    # define variables
    ...


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    # specify global variables modified here
    global ...

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
```Python
from scipy.io import wavfile
import numpy as np
```
* **Parameters definition**: Equivalent to `#define` definitions we did in C.
```Python
buffer_len = 256
```
* **Test signal**: Here we load a WAV test signal with the [`scipy.io.wavfile.read`](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.io.wavfile.read.html) function. We will parse the test signal one block at a time (according to `buffer_len`) in order to simulate a real-time operation. You can download a sample speech file [here](https://github.com/LCAV/dsp-labs/blob/fix_image_rendering/scripts/_templates/speech.wav).
```Python
input_wav = "speech.wav"
samp_freq, signal = wavfile.read(input_wav)
signal = signal[:,]  # get first channel
n_buffers = len(signal)//buffer_len
data_type = signal.dtype
```
* **Allocation**: We do this to fix the length of our buffer, as needs to be done in C. Note that we use the data type of the speech file; we try to use files that are 16-bit or 32-bit PCM.
```Python
input_buffer = np.zeros(buffer_len, dtype=data_type)
output_buffer = np.zeros(buffer_len, dtype=data_type)
```
* **State variables**: The `init` function initializes all variables and should build all necessary lookup tables. We need the `global` definition for those variables used in other functions.
* **`process` function**: This is the heart of the block-based processing. Please note that every time a global variable is touched in a function, you will need to define it as `global` otherwise it will use a local clone. Note that we process **_one sample at a time_** to replicate how we would have to code our STM32 board in C!
* **Simulate block processing**: This last part (after `Nothing to touch after this!`) slices the test signal into buffers, then calls the `process` function one buffer at a time. Finally, the modified output is written to a new WAV file.


## Alien voice effect

{% hint style='working' %}
TASK 2: Copy the above script into an empty file called `"alien_voice_effect.py"` and add the following function under the comment about utility functions.
{% endhint %}

```Python
def build_sine_table(f_sine, samp_freq, data_type=16):
    """
    :param f_sine: Modulate frequency for voice effect in Hz.
    :param samp_freq: Sampling frequency in Hz
    :param data_type: Data type of sinusoid table. Must be either uint16 (default) or uint32.
    :return:
    """

    if data_type!=16 and data_type!=32:
        data_type = 16

    # periods
    samp_per = 1./samp_freq
    sine_per = 1./f_sine

    # compute time instances
    t_vals = np.arange(0, sine_per, samp_per)
    LOOKUP_SIZE = len(t_vals)
    n_vals = np.arange(LOOKUP_SIZE)

    # compute the sine table
    MAX_SINE = 2**(data_type-1)-1
    w_mod = 2*np.pi*f_sine/samp_freq
    SINE_TABLE = np.sin(w_mod*n_vals) * MAX_SINE

    return SINE_TABLE, MAX_SINE, LOOKUP_SIZE
```

As you know, we try to use integer variables in order to save processing time. When using integer values though it is not possible, for example, to code a window that goes from 0 to 1 with 0.1 increments. In order to maximize our precision and to minimize the computation cost, we try to use the full range of our integer variables. For example, in the case of the window, instead of having it coded from 0 to 1 we will code it from 0 to the max value possible in the corresponding data type. For example 65'535 in the case of `unsigned int 16`. This scaling factor will need to be incorporated whenever using the window. With an intelligent use of operation priority (for example multiply before dividing in order to perform integer arithmetic without losing precision) it will not impact our precision and processing time. By convention we will use the maximum value relative to each type, thus we do not need to explicitly link the scaling factor with each variables.

In the above code, we can observe this use of the full range when creating the sinus table:
```Python
SINE_TABLE = np.sin(w_mod*n_vals) * MAX_SINE
```

{% hint style='working' %}
TASK 3: Add the following code within the `init` function.
{% endhint %}

```Python
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
    vals = build_sine_table(f_sine, samp_freq, data_type=16)
    SINE_TABLE = vals[0]
    MAX_SINE = vals[1]
    LOOKUP_SIZE = vals[2]
```

Now we come to the main processing for the alien voice effect! Below we provide the `process` function for you to complete.

```Python
# the process function!
def process(input_buffer, output_buffer, buffer_len):

    global x_prev
    global sine_pointer

    for n in range(buffer_len):

        # high pass filter
        output_buffer[n] = input_buffer[n] - x_prev

        # modulation
        output_buffer[n] = ...

        # update state variables
        sine_pointer = ...
        x_prev = ...
```

{% hint style='working' %}
TASK 4: Replace the lines with `...` with the appropriate content in order to implement the alien voice effect. 

_Note: normalize the sinusoid using the constant `MAX_SINE`!_
{% endhint %}

You can test your implementation by running your script with the following line on the command line:
```Bash
python alien_voice_effect.py
```
Make sure that you have a WAV file called `"speech.wav"` in the same directory! Your alien voice effect will be applied to this file and saved into a file called `"speech_mod.wav"` if it runs without error.

When the output file sounds as expected (see/listen [here](http://nbviewer.jupyter.org/github/prandoni/COM303/blob/master/voice_transformer/voicetrans.ipynb#1---The-%22Robot-Voice%22) to verify with the robot voice effect), you can move on to implementing the effect on the STM32 board!

{% hint style='working' %}
BONUS: Implement the alien voice effect in real-time using your laptop's soundcard and the [`sounddevice`](https://python-sounddevice.readthedocs.io) library.

_Hint: copy your `alien_voice_effect.py` file and create a new one called `alien_voice_effect_sd.py`. Replace the content after the `Nothing to touch after this!` comment block with the code below._
{% endhint %}

```Python
"""
Nothing to touch after this!
"""
try:
    sd.default.samplerate = 16000
    sd.default.blocksize = buffer_len
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

Run the following command (with headphones!) to run your alien voice effect in real-time:
```Bash
python alien_voice_effect_sd.py
```


