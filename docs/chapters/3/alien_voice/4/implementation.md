# 3.4 C Implementation with STM32

Assuming you have successfully implemented a passthrough in the previous guide, we can simply copy and paste this project from within the SW4STM32 software. After pasting it, a pop-up will ask to give a name to the copied project. We recommend choosing a name with the current date and `"alien_voice"` in it. Remember to delete the binary (ELF) file of the original project inside the copied project!

## <a id="timer"></a>Setting up timer for benchmarking

Open the CubeMX software to update the initialization code by opening the IOC file of the copied project.

For this exercise, we will only need to add the configuration of a _timer_ (to benchmark our implementation) as the rest of the system is already up and running. In order to activate a timer, you need to set a "Clock Source". This is done from the "Pinout" tab on the left-hand column as shown below:

<div style="text-align:center"><img src ="figs/Activate_the_clock_for_TIM2.png" width="400"/></div>
<center><i>Set the "Clock Source" to "Internal Clock" in order to enable "TIM2".</i></center>
<br>

Next, we need to configure the timer from the "Configuration" tab by pressing "TIM2" under "Control" (see below).

<div style="text-align:center"><img src ="figs/config_tab.png"/></div>
<br>

A pop-up similar to below should appear.

<div style="text-align:center"><img src ="figs/Setup_TIM2_as_us_timebase_edited.png" width="600"/></div>
<br>

{% hint style='working' %}
TASK 5: We ask you to set the "Prescaler" value (in the figure above) in order to achieve a $$1\,[\mu s]$$ period for "TIM2", i.e. we want our timer to have a $$1\,[\mu s]$$ resolution.

_Hint: Go to the "Clock Configuration"  tab (from the main window pane) to see what is the frequency of the input clock to "TIM2". From this calculate the prescaler value to increase the timer's period to $$1\,[\mu s]$$._
{% endhint %}

You can leave the rest of the parameters as is for "TIM2". Finally, you can update the initialization code by pressing the _gear_ button in the toolbar. As before, do not open the project when prompted to do; select "Close".

You can now open the SW4STM32 software. In order to use the timer we configured, we will need to define a variable to keep track of the time and a macro to reset the timer. Between the `USER CODE BEGIN PV` and `USER CODE END PV` comments, add the following lines in the `main.c` file.

```C
/* USER CODE BEGIN PV */
volatile int32_t current_time_us;
#define RESET_TIMER ({\
        current_time_us = __HAL_TIM_GET_COUNTER(&htim2);\
        HAL_TIM_Base_Stop(&htim2);\
        HAL_TIM_Base_Init(&htim2);\
        HAL_TIM_Base_Start(&htim2);\
    })
```

To use this macro, just call it in your code, then the variable `current_time_us` will be updated and the timer will be reset.

We want to assess if the processing time is longer or shorter than what our chosen buffer length and sampling frequency allows us. To do this, we will define some additional variables and constants (also between the `USER CODE BEGIN PV` and `USER CODE END PV` comments).

{% hint style='working' %}
TASK 6: In the passthrough example, we set the buffer length (the macro called `FRAME_PER_BUFFER`) to just 32. Increase it to 512 and use this value and `FS` to calculate the maximum processing time allowed in microseconds. Replace the variable `USING_FRAME_PER_BUFFER_AND_FS` in the code snippet below with this expression for the maximum processing time.

_Note: keep in mind the points made about using `float` or `int` variables (see [here](../2/dsp_tips.md#float))._
{% endhint %}


```C
/* USER CODE BEGIN PV */
volatile int16_t processing_load;
#define FS     hi2s1.Init.AudioFreq
#define MAX_PROCESS_TIME_ALLOWED_us   USING_FRAME_PER_BUFFER_AND_FS
```

In between the `USER CODE BEGIN 2` and `USER CODE END 2` comments, we propose adding the following lines to read the timer and print the result of the benchmarking tool to the console.

```C
/* USER CODE BEGIN 2 */

// Mute codec
MUTE
HAL_Delay(500);

// begin DMA to fill the buffer with values
HAL_I2S_Transmit_DMA(&hi2s1, (uint16_t *) dataOut, DOUBLE_BUFFER_I2S);
HAL_I2S_Receive_DMA(&hi2s2, (uint16_t *) dataIn, DOUBLE_BUFFER_I2S);

// Wait that the buffers are full
HAL_Delay(1000);

// Stop DMAs to get a precise process timing
HAL_I2S_DMAPause(&hi2s1);
HAL_I2S_DMAPause(&hi2s2);

// Measure Processing time
RESET_TIMER;
process(dataIn, dataOut, BUFFER_SIZE);
RESET_TIMER;

// Display the results
printf("-- Processing time assert -- fs = %ld[Hz]\n", FS);

// load in percent
processing_load = USING_CURRENT_TIME_US_AND_MAX_PROCESS_TIME_ALLOWED_US;

if (current_time_us < MAX_PROCESS_TIME_ALLOWED_us) {
    printf("Processing time shorter than allowed time: t_proc = %ld [us], t_buf = %ld [us] (%i%%) \n", current_time_us, MAX_PROCESS_TIME_ALLOWED_us, processing_load);
} else {
    printf("Processing time longer than allowed time: t_proc = %ld [us], t_buf = %ld [us] (%i%%) \n", current_time_us, MAX_PROCESS_TIME_ALLOWED_us, processing_load);
}

// Reactivate the DMAs
HAL_I2S_DMAResume(&hi2s1);
HAL_I2S_DMAResume(&hi2s2);

UNMUTE
SET_MIC_LEFT
```

{% hint style='working' %}
TASK 7: Using the `current_time_us` and `MAX_PROCESS_TIME_ALLOWED_us`, compute the value of `processing_load` as a percentage in the code snippet above, i.e. replace `USING_CURRENT_TIME_US_AND_MAX_PROCESS_TIME_ALLOWED_US` with the appropriate expression.

_Note: keep in mind the points made about using `float` or `int` variables (see [here](../2/dsp_tips.md#float))._
{% endhint %}

You will notice that we used a `printf` function in order to output text on the debug console. To enable this function you need to make the following changes to your project:
* In the Project Properties ("right-click" project > Properties), navigate to "C/C++ Build -> Settings" on the left-hand side (see the figure below). Under "MCU GCC Linker -> Miscellaneous", update the "Linker flags" field with:
```
-specs=nosys.specs -specs=nano.specs -specs=rdimon.specs -lc -lrdimon
```
<div style="text-align:center"><img src ="figs/proj_prop.png"/></div>
<br>
* Add the following function prototype above the `main` function (e.g. between the `USER CODE BEGIN PFP` and `USER CODE END PFP` comments):
```C
extern void initialise_monitor_handles(void);
```
* Add the following function call in the body of the `main` function (before any `printf`):
```C
initialise_monitor_handles();
```
* In Debug Configurations (dropdown from the _bug_ icon) add the following option under the "Startup" tab:
```
monitor arm semihosting enable
```

After this setup, the `printf` output will be shown in the debug console of Eclipse (precisely in the `open ocd` console). **_Be careful, the modification made in the Debug Configuration will not stay if you copy and paste your project to make a new version!_**


## <a id="effect"></a>Alien voice effect

We will now add our robot voice effect! As mentioned [previously](../2/dsp_tips.md#removing-dc-noise), we will also implement a simple high pass filter and add a gain to make the output more audible. Below is the final `process` function we propose you to use. Insert it between the `USER CODE BEGIN 4` and `USER CODE END 4` comments.

```C
/* USER CODE BEGIN 4 */

void inline process(int16_t *bufferInStereo, int16_t *bufferOutStereo,
        uint16_t size) {
        
    int16_t static x_1 = 0;
    int16_t x[FRAME_PER_BUFFER];
    int16_t y[FRAME_PER_BUFFER];
    
    #define GAIN 8      // We lose 1us processing time if we use a value that is not a power of 2

    static uint16_t pointer_sine = 0;

    // Take signal from left side
    for (uint16_t i = 0; i < size; i += 2) {
        x[i / 2] = bufferInStereo[i];
    }
    
    for (uint16_t i = 0; i < FRAME_PER_BUFFER; i++) {
    
        // High pass filter
        y[i] = x[i] - x_1;
        
        // Apply alien voice effect and gain
        y[i] =
        
        // Update state variables
        pointer_sine = 
        x_1 =
    
    }

    // Interleaved left and right
    for (uint16_t i = 0; i < size; i += 2) {
        bufferOutStereo[i] = (int16_t) y[i / 2];
        bufferOutStereo[i + 1] = 0;
    }
```

{% hint style='working' %}
TASK 8: Modify the code within the second `for` loop in order to compute the alien voice output and update the state variables.

_Note: normalize the sinusoid using the constant `SINE_MAX`!_
{% endhint %}

Copy the sinusoid lookup table below and place it between the `USER CODE BEGIN PV` and `USER CODE END PV` comments.

```C
#define SINE_TABLE_SIZE 80
#define SIN_MAX 0x7fff
const int16_t sine_table[SINE_TABLE_SIZE] = {
0x0000,0x0a0a,0x1405,0x1de1,0x278d,0x30fb,0x3a1b,0x42e0,
0x4b3b,0x5320,0x5a81,0x6154,0x678d,0x6d22,0x720b,0x7640,
0x79bb,0x7c75,0x7e6b,0x7f99,0x7fff,0x7f99,0x7e6b,0x7c75,
0x79bb,0x7640,0x720b,0x6d22,0x678d,0x6154,0x5a81,0x5320,
0x4b3b,0x42e0,0x3a1b,0x30fb,0x278d,0x1de1,0x1405,0x0a0a,
0x0000,0xf5f6,0xebfb,0xe21f,0xd873,0xcf05,0xc5e5,0xbd20,
0xb4c5,0xace0,0xa57f,0x9eac,0x9873,0x92de,0x8df5,0x89c0,
0x8645,0x838b,0x8195,0x8067,0x8001,0x8067,0x8195,0x838b,
0x8645,0x89c0,0x8df5,0x92de,0x9873,0x9eac,0xa57f,0xace0,
0xb4c5,0xbd20,0xc5e5,0xcf05,0xd873,0xe21f,0xebfb,0xf5f6
};
```

## <a id="extra"></a>Extra features

If you have some extra time, we propose to make a few improvements to the system!

{% hint style='working' %}
TASK 9: Put the robot voice signal on both output channels.

_Hint: edit the processing function, certainly near the end._
{% endhint %}

We will now program one of the on-board buttons - the blue button called "B1" - to toggle the alien voice effect. Copy the following code between the `USER CODE BEGIN PV` and `USER CODE END PV` comments.

```C
/* USER CODE BEGIN PV */
// Enumeration for a clean FX ON/OFF toggle
enum {
    FX_OFF, FX_ON
} FX_STATE;

// State variable for the FX
uint8_t FX = FX_OFF;

/* USER CODE BEGIN 0 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {

    if (GPIO_Pin == B1_Pin) {
        FX = !FX;
        LED_TOGGLE
    }
}
```

In the above code snippet, you will find the state variable we propose for the FX (effects) state and the callback that is needed to react to the button. To activate the callback, you need to go into CubeMX and enable "EXTI line 4 to 15" from the Configuration tab under "System > NVIC". Then modify your `process` function using a condition as proposed in the code snippet below.

```C
for (uint16_t i = 1; i < FRAME_PER_BUFFER; i++) {

    // High pass filter
    y[i] = x[i] - x_1;
    
    // Apply robot voice modulation and gain
    if (FX == FX_ON) {

    } else {

    }
    
    // Update state variables
    pointer_sine = 
    x_1 =
}
```

Finally, you can try changing the modulation frequency and creating your lookup tables by running [this Python code](../2/dsp_tips.md#lookup_python) for modified values of `f_sine`.

** Congrats implementing your (potentially) first voice effect! In the [next chapter](../../../4/granular_synthesis/_intro.md), we will build a more sophisticated voice effect that can alter the pitch so that you sound like a chipmunk or Darth Vader.**

