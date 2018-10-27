# 4.2 Python framework

In the process of implementing an algorithm on an embedded system, it is sometimes worth testing it in a workspace with less constraints than on the final environment. Here we propose a Python framework that will help in this prototype/debugging state. In the [next chapter](../3/implementation.md) we will help you to develop the granular synthesis pitch shifting in this same framework. The last step will be to translate the algorithm to C code for the STM32 board.

The whole idea of this framework is to code in the same way as it will be done in C. It probably means that the implementation will be very cumbersome in Python but very easy to port to C in the final stage. One big obstacle is to think in a block-based manner, as if buffers were filled and processed one after the other in real-time. The other obstacle of porting the code from Python to C is the definition of variables and to manage their sizes.

## Empty template

We propose the following template for simulating real-time processing in C with Python. Note that the below code will not run as `...` is not valid syntax! Please note the use of block processing and the definition of the variables (the `dtype` arguments).

```Python
from scipy.io import wavfile
import numpy as np

# define necessary utility functions

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
* **Test signal**: Here we load a WAV test signal with the [`scipy.io.wavfile.read`](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.io.wavfile.read.html) function. We will parse the test signal one block at a time (according to `buffer_len`) in order to simulate a real-time operation.
```Python
input_wav = "speech.wav"
samp_freq, signal = wavfile.read(input_wav)
signal = signal[:,]  # get first channel
n_buffers = len(signal)//buffer_len
data_type = signal.dtype
```
* **Allocation**: We do this to fix the length of our buffer, as needs to be done in C.
```Python
input_buffer = np.zeros(buffer_len, dtype=data_type)
output_buffer = np.zeros(buffer_len, dtype=data_type)
```
* **State variables**: The `init` function initializes all variables and should build all necessary lookup tables. We need the `global` definition for those variables used in other functions.
* **`process` function**: This is the heart of the block-based processing. Please note that every time a global variable is touched in a function, you will need to define it as `global` otherwise it will use a local clone. Note that we process **_one sample at a time_** to replicate how we would have to code our STM32 board in C!
* **Simulate block processing**: This last part slices the test signal into buffers, then calls the `process` function one buffer at a time. Finally, the modified output is written to a new WAV file.

In the following chapter, we will guide you through the implementation of granular synthesis pitch shifting.


<!-- 


## Alien Voice in Python

Below is the full example to test the Alien Voice in Python. Please note the use of block processing and the definition of the variables (the `dtype` arguments).

```Python
from scipy.io import wavfile
import numpy as np

def build_sine_table(f_sine, samp_freq, data_type):

    # periods
    samp_per = 1./samp_freq
    sine_per = 1./f_sine

    # compute time instances
    t_vals = np.arange(0, sine_per, samp_per)
    LOOKUP_SIZE = len(t_vals)
    n_vals = np.arange(LOOKUP_SIZE)

    # compute the sine table
    data_type = 16    # 16 or 32 signed integer
    MAX_SINE = 2**(data_type-1)-1   # [-(2*data_type-1), 2**(data_type-1)]
    w_mod = 2*np.pi*f_sine/samp_freq
    SINE_TABLE = np.sin(w_mod*n_vals) * MAX_SINE

    return SINE_TABLE, MAX_SINE, LOOKUP_SIZE

# parameters
buffer_len = 256
f_sine = 100 # Hz, for modulation
high_pass_on = False

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


# the process function!
def process(input_buffer, output_buffer, buffer_len):

    global x_prev
    global sine_pointer

    for n in range(buffer_len):

        # high pass filter
        if high_pass_on:
            output_buffer[n] = input_buffer[n] - x_prev
        else:
            output_buffer[n] = input_buffer[n]

        # modulation
        output_buffer[n] = output_buffer[n]*SINE_TABLE[sine_pointer] / MAX_SINE * GAIN

        # update state variables
        sine_pointer = (sine_pointer+1)%LOOKUP_SIZE
        x_prev = input_buffer[n]

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
wavfile.write("speech_alien_effect.wav", samp_freq, signal_proc)
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
* **Test signal**: Here we load a WAV test signal with the [`scipy.io.wavfile.read`](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.io.wavfile.read.html) function. We will parse the test signal one block at a time (according to `buffer_len`) in order to simulate a real-time operation.
```Python
input_wav = "speech.wav"
samp_freq, signal = wavfile.read(input_wav)
signal = signal[:,]  # get first channel
n_buffers = len(signal)//buffer_len
data_type = signal.dtype
```
* **Allocation**: We do this to fix the length of our buffer, as needs to be done in C.
```Python
input_buffer = np.zeros(buffer_len, dtype=data_type)
output_buffer = np.zeros(buffer_len, dtype=data_type)
```
* **State variables**: The `init` function initializes all variables and will build the sine table. In our C project, we had a fixed sinus table; however, we could also rebuild it to change the modulation rate. We need the `global` definition for those variables used in other functions.
* **`process` function**: This is the heart of the block-based processing. Please note that every time a global variable is touched in a function, you will need to define it as `global` otherwise it will use a local clone. Note that we process **_one sample at a time_** to replicate how we would have to code our STM32 board in C!
* **Simulate block processing**: This last part slices the test signal into buffers, then calls the `process` function one buffer at a time. Finally, the modified output is written to a new WAV file.

## Using the full range

As you know, we try to use integer variables in order to save processing time. When using integer values though it is not possible, for example, to code a window that goes from 0 to 1 with 0.1 increments. In order to maximize our precision and to minimize the computation cost, we try to use the full range of our integer variables. For example, in the case of the window, instead of having it coded from 0 to 1 we will code it from 0 to the max value possible in the corresponding data type. For example 65'535 in the case of `unsigned int 16`. This scaling factor will need to be incorporated whenever using the window. With an intelligent use of operation priority (for example multiply before dividing in order to perform integer arithmetic without losing precision) it will not impact our precision and processing time. By convention we will use the maximum value relative to each type, thus we do not need to explicitly link the scaling factor with each variables.

In the above code, we can observe this use of the full range when creating the sinus table:
```Python
SINE_TABLE = np.sin(w_mod*n_vals) * MAX_SINE
```
and the modulation step maintains the precision while keeping the range of our sinus table from 0 to 1.
```Python
output_buffer[n] = output_buffer[n]*SINE_TABLE[sine_pointer] / MAX_SINE * GAIN
```

## Empty template

We propose the following template for simulating real-time processing in C with Python. Note that the below code will not run as `...` is not valid syntax! In the following chapter, we will guide you through the implementation of granular synthesis pitch shifting.

```Python
from scipy.io import wavfile
import numpy as np

# define necessary utility functions

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

 -->