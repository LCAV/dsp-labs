# 2.4 Coding the passthrough

In this section, we will guide you through programming the microcontroller in order to implement the passthrough. Many of the concepts in this section lay the foundations for how to structure and code a real-time audio application on the microcontroller. In later sections we will build more complex processing functions, but the architecture of the code will remain the same. 

In the previous section, you should have copied the blinking LED project before updating the `IOC` file with CubeMX. From the SW4STM32 software, open the file `"Src/main.c"` in the new project; we will be making all of our modifications here.

## 2.4.1 Macros <a id="mute_macro"></a>

In programming a microcontroller, it is customary to define preprocessor _macros_ to set the values of reusable constants and to concisely package simple tasks that do not require much logic and flow control and for which, therefore, a function call would be overkill. See [here](https://www.cprogramming.com/tutorial/cpreprocessor.html) for more on macros and preprocessor directives when programming in C.

Macros are usually defined before the `main` function; we will place our macros between the `USER CODE BEGIN Includes` and `USER CODE END Includes` comment tags.

### **The MUTE macro**

As an example, we will begin by creating _macros_ to change the logical level of the **MUTE** pin. 

As in the blinking LED example, we will be using HAL library calls in order to modify the state of the **MUTE** GPIO pin.

{% hint style="info" %}
TASK 9: Define two macros - `MUTE` and `UNMUTE` - in order to mute/unmute the output. See below for the necessary syntax.

Use syntax like below, replacing `GPIO_PIN_SET_OR_RESET` with the appropriate value.

_Hint: you should check the_ [_datasheet of the DAC_](https://www.nxp.com/docs/en/data-sheet/UDA1334ATS.pdf) _to determine whether you need a HIGH \(_`GPIO_PIN_SET`_\) or LOW \(_`GPIO_PIN_RESET`_\) value to turn on the mute function of the DAC._
{% endhint %}

```c
#define MUTE HAL_GPIO_WritePin(MUTE_GPIO_Port, MUTE_Pin, GPIO_PIN_SET_OR_RESET);
#define UNMUTE HAL_GPIO_WritePin(MUTE_GPIO_Port, MUTE_Pin, GPIO_PIN_SET_OR_RESET);
```

Note how the **MUTE** pin we configured before automatically generated two _constants_ called `MUTE_GPIO_Port` and `MUTE_Pin`, which is why we suggested giving meaningful names to pins configured with the CubeMX tool.

If you press "Ctrl" \("Command" on MacOS\) + click on `MUTE_GPIO_Port` or `MUTE_Pin` to see its definition, you should see how the values are defined according to the pin we selected for **MUTE**. In our case, we chose pin **PC0** which means that _Pin 0_ on the _GPIO C_ port will be used. The convenience of the CubeMX software is that we do not need to manually write these definitions for the constants! The same can be said for **LR\_SEL**.

## Setting microphone as _left_ or _right_ channel <a id="channel_macro"></a>

### **The Channel Select macro**

We will now define two more macros in order to assign the MEMS microphone to the left or right channel of the I2S bus, using the **LR\_SEL** pin we defined previously. As before, you should place these macros between the `USER CODE BEGIN Includes` and `USER CODE END Includes` comments.

{% hint style="info" %}
TASK 10: Define two macros - `SET_MIC_RIGHT` and `SET_MIC_LEFT` - in order to set the microphone to the left or right channel. You will need to use similar commands as for the **MUTE** macros!

_Hint: you should check the_ [_I2S protocol_](https://www.sparkfun.com/datasheets/BreakoutBoards/I2SBUS.pdf) _\(and perhaps the_ [_datasheet of the microphone_](https://cdn-shop.adafruit.com/product-files/3421/i2S+Datasheet.PDF)_\) to determine whether you need a HIGH or LOW value to set the microphone to the left/right channel._
{% endhint %}

## 2.4.2 Private variables \(aka Constants\) <a id="constants"></a>

In most applications we will need to set some numerical constants that define key parameters used in the application. These definitions are also preprocessing macros and they are usually grouped together at the beginning of the code between the `USER CODE BEGIN PV` and `USER CODE END PV` comment tags. 

We will now define a few constants which will be useful in coding our application. Before defining them in our code, let's clarify some of the terminology:

Before we show some examples, here are some useful definitions:

1. _Sample_: a sample is a single discrete-time value; for a stereo signal, a sample can belong either to the left or right channel.
2. _Frame_: a frame collects all synchronous samples from all channel so, for a stereo signal, a frame will contain two samples, left and right.
3. _Buffer length_: a buffer is a collection of _frames_, stored in memory and ready for processing \(or ready for a DMA transfer\). The buffer's length is a key parameter that needs to be fine-tuned to the demands of our application, [as we explained before](audio-io/#dma-transfers).

### Audio Parameters

Add the following lines to define the frame length \(in terms of samples\) and the buffer length \(in terms of frames\):

```c
#define SAMPLE_PER_FRAME 2
#define FRAME_PER_BUFFER 32
```

`SAMPLE_PER_FRAME` is set to 2 as we have two input channels \(left and right\) as per the I2S protocol.

 Since our application is a simple passthrough, which involves no processing, we can set the buffer length - `FRAME_PER_BUFFER` - to a low value, e.g. 32.

### Data buffers

Again, as explained in Lecture 2.2.5b in the [second DSP module](https://www.coursera.org/learn/dsp2/), for real-time processing we normally need to use alternating buffers for input and output DMA transfers. The I2S peripheral of our microcontroller, however, conveniently sends _two_ interrupt signals, one when the buffer is half-full and one when the buffer is full. Because of this feature, we can simply use an array that is _twice_ the size of our target application's buffer and let the DMA transfer fill one half of the buffer while we simultaneously process the samples in the other half in place.

{% hint style="info" %}
TASK 11: Using the constants defined before - `SAMPLE_PER_FRAME` and `FRAME_PER_BUFFER` - define two more constants for the buffer size and for the size of the double buffer.

_Hint: replace_ `USING_FRAME_PER_BUFFER_AND_SAMPLE_PER_FRAME` _below with the appropriate expression._
{% endhint %}

```c
#define BUFFER_SIZE (USING_FRAME_PER_BUFFER_AND_SAMPLE_PER_FRAME)
#define DOUBLE_BUFFER_I2S (2*BUFFER_SIZE)
```

Finally, we can create the input and output buffers as such:

```c
int16_t dataIn[DOUBLE_BUFFER_I2S];
int16_t dataOut[DOUBLE_BUFFER_I2S];
```

## 2.4.3 Private function prototypes <a id="callback"></a>

In this section we will declare the function prototypes that implement the final application. The code should be placed between the `USER CODE BEGIN PFP` and `USER CODE END PFP` comment tags.

### Main processing function

Ultimately, the application will work by obtaining a fresh data buffer filled by the input DMA transfer, processing the buffer and placing the result in a data buffer for the output DMA to ship out. We will therefore implement a main processing function with the following arguments:

1. a pointer to the input buffer to process
2. a pointer to the output buffer to fill with the processed samples
3. the number of samples to read/write.

```c
void process(int16_t *bufferInStereo, int16_t *bufferOutStereo, uint16_t size);
```

The main processing function will be invoked by the interrupts raised by the DMA transfer, which are raised every time either the first or the second half of the buffer has been filled. 

### DMA callback functions <a id="dma"></a>

As previously mentioned, the STM32 board uses DMA to transfer data in and out of memory from the peripherals and issues interrupts when the DMA buffer is half full and when it's full. 

The HAL family of instructions allows us the define [callback functions](https://www.reddit.com/r/DSP/comments/53t2k3/whats_an_audio_callback_function/) triggered by these interrupts. Add the following function definitions for the callbacks, covering the four cases of two input and output DMAs times two interrupt signals:

```c
void HAL_I2S_RxHalfCpltCallback(I2S_HandleTypeDef *hi2s) {
}

void HAL_I2S_RxCpltCallback(I2S_HandleTypeDef *hi2s) {
}

void HAL_I2S_TxHalfCpltCallback(I2S_HandleTypeDef *hi2s) {
    process(dataIn, dataOut, BUFFER_SIZE);
}

void HAL_I2S_TxCpltCallback(I2S_HandleTypeDef *hi2s) {
    process(dataIn + BUFFER_SIZE, dataOut + BUFFER_SIZE, BUFFER_SIZE);
}
```

Note that the Rx callbacks \(that is, the callbacks triggered by the input DMAs\), have an empty body and only the Tx callbacks \(that is, the ones driven by the output process\) perform the processing via our  `process` function.

This is a simple but effective way of synchronizing the input and the output peripherals when we know that the data throughput should be the same for both devices. Of course we can see that if the `process` function takes too long, the buffer will not be ready in time for the next callback and there will be audio losses. In the next chapter, we will introduce a mechanism to monitor this.

You can read more about the HAL functions for DMA Input/Output for the I2S protocol in the comments of the file `"Drivers/STM32F0XX_HAL_Driver/Src/stm32f0xx_hal_i2s.c"` from the SW4STM32 software:

```c
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

## 2.4.4. The processing code <a id="main"></a>

Between the `USER CODE BEGIN 4` and `USER CODE END 4` comment tags, we will define the body of the `process` function which, in this case, implements a simple passthrough.

```c
void inline process(int16_t *bufferInStereo, int16_t *bufferOutStereo, uint16_t size) {
    // Strictly copying input to output
    for (uint16_t i = 0; i < size; i++) {
        // Here copy input buffer to output buffer
    }
}
```

{% hint style="info" %}
TASK 12: Use the two buffers - `bufferInStereo` and `bufferOutStereo` - in the loop above in order to realize a passthrough.

_Hint: you just need to add one line! In C, you have to manipulate one element at a time, using_ `[` _and_ `]` _to index the array._
{% endhint %}

## 2.4.5 Setup 

Between the `USER CODE BEGIN 2` and `USER CODE END 2` comment tags, we need to initialize our STM32 board, namely we need to:

1. un-mute the DAC using the macro defined [before](coding.md#mute_macro).
2. set the microphone to either left or right channel using the macro defined [here](coding.md#channel_macro).
3. start the receive and transmit DMAs with `HAL_I2S_Receive_DMA` and `HAL_I2S_Transmit_DMA` respectively.

This is accomplished by the following lines:

```c
// Control of the codec
UNMUTE
SET_MIC_LEFT

// begin DMAs
HAL_I2S_Transmit_DMA(&hi2s1, (uint16_t *) dataOut, DOUBLE_BUFFER_I2S);
HAL_I2S_Receive_DMA(&hi2s2, (uint16_t *) dataIn, DOUBLE_BUFFER_I2S);
```

We can now try building and debugging the project \(remember to press _Resume_ after entering the Debug perspective\). If all goes well, you should have a functioning passthrough and you should be able to hear in the headphones the sound captured by the microphone.

## 2.5.6. Going a bit further

If you still have time and you are curious to go a bit further, we propose to make a modification to the `process` function. Depending on your current implementation, you may have noticed that only one output channel carries the audio while the other is silent. Wouldn't it be nice if both had audio, thereby converting the mono input to a stereo output?

_Note: remember to copy your project before making any significant modifications; that way you will always be able to go back to a stable solution!_

{% hint style="info" %}
BONUS: Modify the `process` function so that both output channels contain audio.
{% endhint %}

```c
void inline process(int16_t *bufferInStereo, int16_t *bufferOutStereo, uint16_t size) {
    // Strictly copying input to output
    for (uint16_t i = 0; i < size; i++) {
        // Here copy either left or right channel to both output channels
    }
}
```

**Congrats on completeting the passthrough! This project will serve as an extremely useful starting point for the following \(more interesting\) applications. The first one we will build is an** [_**alien voice effect**_](../alien-voice/)**.**

## Tasks solutions

{% tabs %}
{% tab title="Anti-spoiler tab" %}
Are you sure you are ready to see the solution? ;\)
{% endtab %}

{% tab title="Task 9" %}
Here you are asked to modify the macros and change the string

```c
GPIO_PIN_SET_OR_RESET
```

to be either

```c
GPIO_PIN_SET
```

or

```c
GPIO_PIN_RESET
```

The table 6 section 8.6.3 of the DAC [datasheet](https://www.nxp.com/docs/en/data-sheet/UDA1334ATS.pdf) sais: LOW = mute off, HIGH = mute on.  
We will thus define the following macros:

```c
/* USER CODE BEGIN Includes */

#define MUTE HAL_GPIO_WritePin(MUTE_GPIO_Port, MUTE_Pin, GPIO_PIN_SET);
#define UNMUTE HAL_GPIO_WritePin(MUTE_GPIO_Port, MUTE_Pin, GPIO_PIN_RESET);

/* USER CODE END Includes */
```
{% endtab %}

{% tab title="Task 10" %}
In the same way as we did for the DAC, we will look in the microphone datasheet. the information we are looking for in on page 6 of the datasheet: _The Tri-state Control \(gray\) uses the state of the WS and SELECT inputs to determine if the DATA pin is driven or tri-stated. This allows 2 microphones to operate on a single I2S port. When SELECT =HIGH the DATA pin drives the SDIN bus when WS=HIGH otherwise DATA= tri-state. When SELECT =LOW the DATA pin drives the SDIN bus when WS=LOW otherwise DATA= tri-state._ As the WS pin is LOW when the left signal is transmitted \(cf. fig. 5 of the DAC datasheet\), we will define the macro as following:

```c
/* USER CODE BEGIN Includes */

#define MUTE HAL_GPIO_WritePin(MUTE_GPIO_Port, MUTE_Pin, GPIO_PIN_SET);
#define UNMUTE HAL_GPIO_WritePin(MUTE_GPIO_Port, MUTE_Pin, GPIO_PIN_RESET);

#define SET_MIC_RIGHT HAL_GPIO_WritePin(LR_SEL_GPIO_Port, LR_SEL_Pin, GPIO_PIN_SET);
#define SET_MIC_LEFT HAL_GPIO_WritePin(LR_SEL_GPIO_Port, LR_SEL_Pin, GPIO_PIN_RESET);

/* USER CODE END Includes */
```
{% endtab %}

{% tab title="Task 11" %}
The arithmetic is quite trivial here, and here is  a quick recap:  
  - a sample is "a value at a certain time for one channel"  
  - a frame is "the package of a left and a right sample"  
Thus the buffer has in our case the length SAMPLE\_PER\_FRAME x FRAME\_PER\_BUFFER, as every sample has 16 bits \(1 half-word\) a buffer will be 32x2 half-words long.

The double buffer size is then 128 values.

```c
/* USER CODE BEGIN PV */
#define SAMPLE_PER_FRAME 2      // L+R
#define FRAME_PER_BUFFER 32     // user-choice, depends on application
#define BUFFER_SIZE (FRAME_PER_BUFFER*SAMPLE_PER_FRAME)
#define DOUBLE_BUFFER_I2S (2*BUFFER_SIZE)
```
{% endtab %}

{% tab title="Task 12" %}
The pass-through is made by copying the input buffer on the output buffer. This is done like so:

```c
void inline process(int16_t *bufferInStereo, int16_t *bufferOutStereo, uint16_t size) {
    for (uint16_t i = 0; i < size; i++) {
        bufferOutStereo[i] = bufferInStereo[i];
    }
}
```
{% endtab %}

{% tab title="Bonus" %}
There is alway several way to the same goal in C, however we propose you the following solution:

```c
void inline process(int16_t *bufferInStereo, int16_t *bufferOutStereo, uint16_t size) {
    for (uint16_t i = 0; i < size; i+=2) {
        bufferOutStereo[i] = bufferInStereo[i];
        bufferOutStereo[i+1] = bufferInStereo[i];
    }
}
```

In this way the value of the microphone, that is only on one side \(every second channel\) will be copied to both side of the output buffer.

Be careful that the code above will only work of you have set your microphone to the left channel. You can modify the code to take the SET\_MIC\_LEFT/SET\_MIC\_RIGHT macro into account as well.
{% endtab %}
{% endtabs %}

