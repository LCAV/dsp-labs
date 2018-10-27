# 1.1 Hardware

In this section, we introduce the different hardware components that will be used in our lab exercises:
* [Microcontroller](#microcontroller)
* [Microphone](#microphone)
* [DAC + audio jack](#dac_jack)

Both the microphone and the DAC will rely on the I2S (Inter-IC Sound) bus specification for audio transfer. This is a 3-line serial bus consisting of a data line for two time-multiplexed channels, a word select line, and a clock line. More information about the I2S bus specification can be found [here](https://www.sparkfun.com/datasheets/BreakoutBoards/I2SBUS.pdf).

## <a id="microcontroller"></a>Microcontroller

The board we will be using comes from the STM32 Nucleo-64 family. In particular, we will be using the STM32 Nucleo-64 development board with the [STM32F072RB microcontroller unit](https://www.st.com/en/evaluation-tools/nucleo-f072rb.html). You can find more information about this family of boards by reading the [official documentation](https://www.st.com/content/ccc/resource/technical/document/data_brief/c8/3c/30/f7/d6/08/4a/26/DM00105918.pdf/files/DM00105918.pdf/jcr:content/translations/en.DM00105918.pdf).

<br/>
<div style="text-align:center"><img src ="figs/nucleo_board.jpg" /></div>
<center><i>STM32 Nucleo development board. <a href="https://www.st.com/en/evaluation-tools/nucleo-f072rb.html" target="_blank">Picture source</a>.</i></center>

## <a id="microphone"></a>Microphone

The microphone part we will be using is the [I2S MEMS Microphone Breakout](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/overview) by Adafruit. In the [following chapter](../../../2/passthrough/1/hardware_interfaces/microphone.md), we describe the component in more detail as we build a _passthrough_, the "hello world" equivalent for audio - passing though microphone input directly to the output.

<br/>
<div style="text-align:center"><img src ="figs/sensors_3421_quarter_ORIG.jpg" /></div>
<center><i>Adafruit I2S MEMS Microphone Breakout. <a href="http://learn.adafruit.com/assets/39631" target="_blank">Picture source</a>.</i></center>


## <a id="dac_jack"></a>DAC + Audio Jack

The microphone we are using measures an _analog_ (continuous in time and amplitude) signal and returns a _digital_ (discrete in time and amplitude) signal, which can be further processed by our microcontroller. In order to playback or listen to this digital signal, it is necessary to convert it back to an analog signal; this can be done with a DAC (Digital-to-Analog Converter). We will be using Adafruit's [I2S Stereo Decoder Breakout](https://learn.adafruit.com/adafruit-i2s-stereo-decoder-uda1334a/overview), which contains the DAC, an audio jack for connecting headphones, and the necessary additional components. As with the microphone component, we will describe the component in more detail as we build a passthrough in the [following chapter](../../../2/passthrough/1/hardware_interfaces/dac.md).

<br/>
<div style="text-align:center"><img src ="figs/adafruit_products_3678_top_ORIG.jpg" /></div>
<center><i>Adafruit I2S Stereo Decoder - UDA1334A Breakout. <a href="http://learn.adafruit.com/assets/48396" target="_blank">Picture source</a>.</i></center>
