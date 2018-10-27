# 2.4 Coding the passthrough

In this section, we will guide you through programming the
microcontroller in order to implement the *passthrough*! In the previous
section, you should have copied the blinking LED project before updating the
IOC file with CubeMX. From the SW4STM32
software, open the file `"Src/main.c"` in the new project; we will be
making all of our modifications here.

## <a id="mute_macro"></a>Muting the DAC

We will start off by creating *macros* to change the logical level of
the **MUTE** pin. See [here](https://www.cprogramming.com/tutorial/cpreprocessor.html) for more on macros and preprocessor commands
(we will also be defining constants). 

Macros are usually defined at the top of a `main` program; we will place
our macros between the `USER CODE BEGIN Includes` and
`USER CODE END Includes` comments.

As in the blinking LED example, we will be
using the same HAL library in order to modify the state of the **MUTE**
GPIO pin.

{% hint style='working' %}
TASK 9: Define two macros - `MUTE` and `UNMUTE` - in order to mute/unmute the output. See below for the necessary syntax.
 
Use syntax like below, replacing `GPIO_PIN_SET_OR_RESET` with the appropriate value.
 
*Hint: you should check the [datasheet of the DAC](https://www.nxp.com/docs/en/data-sheet/UDA1334ATS.pdf) to determine whether you need a HIGH (`GPIO_PIN_SET`) or LOW (`GPIO_PIN_RESET`) value to turn on the mute function of the DAC.*
{% endhint %}

```C
#define MUTE HAL_GPIO_WritePin(MUTE_GPIO_Port, MUTE_Pin, GPIO_PIN_SET_OR_RESET);
#define UNMUTE HAL_GPIO_WritePin(MUTE_GPIO_Port, MUTE_Pin, GPIO_PIN_SET_OR_RESET);    
```

Note how the **MUTE** pin we configured before automatically generated two *constants*
called `MUTE_GPIO_Port` and `MUTE_Pin`, which is why we suggested giving
meaningful names to pins configured with the CubeMX tool.

If you press "Ctrl" ("Command" on MacOS) + click on `MUTE_GPIO_Port` or
`MUTE_Pin` to see its definition, you should see how the values are
defined according to the pin we selected for **MUTE**. In our case, we chose pin **PC0**
which means that the *Pin 0* on the *GPIO C* port will be used. The
convenience of the CubeMX software is that we do not need to manually
write these definitions for the constants! The same can be observed for
the **LR_SEL**.

## <a id="channel_macro"></a> Setting microphone as _left_ or _right_ channel

We will now define two more macros in order to set the microphone to the
left or right channel of the I2S bus, using the **LR_SEL** pin we
defined. As before, you should place
these macros between the `USER CODE BEGIN Includes` and
`USER CODE END Includes` comments.

{% hint style='working' %}
TASK 10: Define two macros - `SET_MIC_RIGHT` and `SET_MIC_LEFT` - in order to set the microphone to the left or right channel. You will need to use similar commands as for the **MUTE** macros!

*Hint: you should check the [I2S protocol](https://www.sparkfun.com/datasheets/BreakoutBoards/I2SBUS.pdf) (and perhaps the [datasheet of the microphone](https://cdn-shop.adafruit.com/product-files/3421/i2S+Datasheet.PDF)) to determine whether you need a HIGH or LOW value to set the microphone to the left/right channel.*
{% endhint %}

## <a id="constants"></a>Private variables

The following code should be placed between the
`USER CODE BEGIN PV` and `USER CODE END PV` comments.

#### Common DSP parameters

We will now define a few constants which will be useful in coding our
application. Before defining them in our code, let's clarify some of the
terminology we will be using:

1.  *Sample*: A single sample represents the value of a **single**
    channel at a certain point in time.
2.  *Frame*: A frame consists of exactly one sample per channel.
3.  *Buffer length*: This is a key parameter that often needs to be
    tuned to one's application. DSP applications are typically performed
    on multiple frames; this collection of frames is called a *buffer*.
    A large buffer length (the number of frames) allows one to apply
    more complex processing (e.g. better frequency resolution by
    applying a larger FFT). However, a large buffer length comes with
    the cost of more *latency* as we need to wait for more samples for
    each channel before we can begin processing.

Add the following lines to define the frame length (in terms of samples)
and the buffer length (in terms of frames):

```C
#define SAMPLE_PER_FRAME 2
#define FRAME_PER_BUFFER 32
```

`SAMPLE_PER_FRAME` is set to 2 as we have two input channels (left and
right) as per the I2S protocol.

As our application is a simple passthrough, which involves no
processing, we can set the buffer length - `FRAME_PER_BUFFER` - to a low
value, e.g. 32.

#### Storing samples

Finally, we need to store the incoming samples into an array, and while
we receive these new samples we do not want to tamper any samples we
might still be processing. The I2S peripheral of our microcontroller has
the nice feature of sending *interruptions* at two critical state of its
operation. The first is simply when the buffer is full. However they
added a second interruption for when the buffer is half full. More on
this is explained [below](#dma). 

In this way we will use an
array that is *twice* the size of our application's buffer, i.e. the
size of our buffer in terms of samples. With this solution, we can place
new samples on one half of the buffer while we simultaneously process
samples on the other half of the buffer.

{% hint style='working' %}
TASK 11: Using the constants defined before - `SAMPLE_PER_FRAME` and `FRAME_PER_BUFFER` - define two more constants for the buffer size and for the size of the double buffer.

_Hint: replace `USING_FRAME_PER_BUFFER_AND_SAMPLE_PER_FRAME` below with the appropriate expression._
{% endhint %}

```C
#define BUFFER_SIZE (USING_FRAME_PER_BUFFER_AND_SAMPLE_PER_FRAME)
#define DOUBLE_BUFFER_I2S (2*BUFFER_SIZE)
```

Finally, we can create the input and output buffers as such:
```C
int16_t dataIn[DOUBLE_BUFFER_I2S];
int16_t dataOut[DOUBLE_BUFFER_I2S];
```

## <a id="callback"></a>Private function prototypes

The following code will be placed between the
`USER CODE BEGIN PFP` and `USER CODE END PFP` comments.

#### Main processing function

It is now time to actually process the samples! As a simple solution, we
will simply copy the input buffer into the output buffer. This
processing will be done in the I2S-triggered interrupt callbacks, which
happens every time either the first or the second half of the buffer is
full.

We will declare our `process` function as such:

```C
void process(int16_t *bufferInStereo, int16_t *bufferOutStereo, uint16_t size);
```

Our `process` function will take as input:
1.  Two pointers: one to the input buffer to process and one to the
    output buffer to place the processed samples.
2.  The number of samples to read/write.

#### <a id="dma"></a>DMA callback functions

As previously mentioned, the STM32 board uses DMA (direct memory access)
to offload the main chip from the tasks of transferring data in and out
of memory. This is incredibly important for audio as we will have very
frequent transfer from the I2S data line of the microphone to memory and
from memory to the I2S data line of the DAC. With DMA, our main chip can
focus on processing the audio!

The HAL family of instructions allows us the define [callback functions](https://www.reddit.com/r/DSP/comments/53t2k3/whats_an_audio_callback_function/). In these functions we will take care of processing the audio! Add the following function definitions for the callbacks we will be using:

```C
void HAL_I2S_RxHalfCpltCallback(I2S_HandleTypeDef *hi2s) {
}

void HAL_I2S_RxCpltCallback(I2S_HandleTypeDef *hi2s) {
}

void HAL_I2S_TxHalfCpltCallback(I2S_HandleTypeDef *hi2s) {
    process(dataIn, dataOut, BUFFER_SIZE);
}

void HAL_I2S_TxCpltCallback(I2S_HandleTypeDef *hi2s) {
    process(&dataIn[BUFFER_SIZE], &dataOut[BUFFER_SIZE], BUFFER_SIZE);
}
```

For the receive callbacks, we will not be performing any processing;
instead we will use our `process` function before transmitting, i.e.
sending the data to the DAC. It is a way of synchronizing the input and
the output peripheral. We can see here that if the `process` function is
too long, the buffer will not be ready in time for the next callback and
there will be audio losses. In the next guide, we will introduce a
mechanism to monitor this.

You can read more about the HAL functions for DMA Input/Output for the
I2S protocol in the comments of the file
`"Drivers/STM32F0XX_HAL_Driver/Src/stm32f0xx_hal_i2s.c"` from the
SW4STM32 software:

```C
/* 
...
*** DMA mode IO operation ***
==============================
[..] 
(+) Send an amount of data in non blocking mode (DMA) using HAL_I2S_Transmit_DMA() 
(+) At transmission end of half transfer HAL_I2S_TxHalfCpltCallback is executed and user can 
add his own code by customization of function pointer HAL_I2S_TxHalfCpltCallback 
(+) At transmission end of transfer HAL_I2S_TxCpltCallback is executed and user can 
add his own code by customization of function pointer HAL_I2S_TxCpltCallback
(+) Receive an amount of data in non blocking mode (DMA) using HAL_I2S_Receive_DMA() 
(+) At reception end of half transfer HAL_I2S_RxHalfCpltCallback is executed and user can 
add his own code by customization of function pointer HAL_I2S_RxHalfCpltCallback 
(+) At reception end of transfer HAL_I2S_RxCpltCallback is executed and user can 
add his own code by customization of function pointer HAL_I2S_RxCpltCallback
(+) In case of transfer Error, HAL_I2S_ErrorCallback() function is executed and user can 
add his own code by customization of function pointer HAL_I2S_ErrorCallback
(+) Pause the DMA Transfer using HAL_I2S_DMAPause()
(+) Resume the DMA Transfer using HAL_I2S_DMAResume()
(+) Stop the DMA Transfer using HAL_I2S_DMAStop()
...
*/
```

## <a id="main"></a>Passthrough code

Between the `USER CODE BEGIN 4` and `USER CODE END 4`
comments, we will define our function `process` which will implement a
simple passthrough!

```C
void inline process(int16_t *bufferInStereo, int16_t *bufferOutStereo, uint16_t size) {
    // Strictly copying input to output
    for (uint16_t i = 0; i < size; i++) {
        // Here copy input buffer to output buffer
    }
}
```

{% hint style='working' %}
TASK 12: Use the two buffers - `bufferInStereo` and `bufferOutStereo` - in the loop above in order to realize a passthrough.
 
*Hint: you just need to add one line! In C, you have to manipulate one element at a time, using `[` and `]` to index the array.*
{% endhint %}

#### Setup code

Between the `USER CODE BEGIN 2` and `USER CODE END 2`
comments, we need to initialize our STM32 board, namely:

1.  Un-muting the DAC using the macro defined [here](#mute_macro).
2.  Setting the microphone to either left or right channel using the
    macro defined [here](#channel_macro).
3.  Instigating the receive and transmit DMAs with `HAL_I2S_Receive_DMA`
    and `HAL_I2S_Transmit_DMA` respectively.

Add the following lines:

```C
// Control of the codec
UNMUTE
SET_MIC_LEFT

// begin DMAs
HAL_I2S_Transmit_DMA(&hi2s1, (uint16_t *) dataOut, DOUBLE_BUFFER_I2S);
HAL_I2S_Receive_DMA(&hi2s2, (uint16_t *) dataIn, DOUBLE_BUFFER_I2S);
```

We can now try building and debugging the project (remember to press
*Resume* after entering the Debug perspective). If all goes well, you
should have successfully built a passthrough!

## Going a bit further

If you still have time and you are curious to go a bit further, we
propose to make a modification to the `process` function. Depending on
your current implementation, you may have noticed that only one output
channel consists of audio. Wouldn't it be nice if both had audio?

*Note: remember to copy your project before making any significant
modifications; that way you will always be able to go back to a stable
solution!*

{% hint style='working' %}
BONUS: Modify the `process` function so that both output channels contain audio.
{% endhint %}


```C
void inline process(int16_t *bufferInStereo, int16_t *bufferOutStereo, uint16_t size) {
    // Strictly copying input to output
    for (uint16_t i = 0; i < size; i++) {
        // Here copy either left or right channel to both output channels
    }
}
```

** Congrats on completeting the passthrough! This project will serve as an extremely useful starting point for the following (more interesting) applications. The first one we will build is an [_alien voice effect_](../../../3/alien_voice/_intro.md).**