# 1.1 Hardware

In this section, we introduce the different hardware components that will be used in this module:

* [Microcontroller](hardware.md#microcontroller)
* [Microphone](hardware.md#microphone)
* [DAC + audio jack](hardware.md#dac_jack)

Both the microphone and the DAC will rely on the I2S bus \(Inter-IC Sound\) for audio transfers. This is a 3-line serial bus consisting of a data line for two time-multiplexed channels, a word select line, and a clock line. More information about the I2S bus specification can be found [here](https://www.sparkfun.com/datasheets/BreakoutBoards/I2SBUS.pdf).

## Microcontroller <a id="microcontroller"></a>

Our board of choice is the STM32 Nucleo-64 development board with the [STM32F072RB microcontroller unit](https://www.st.com/en/evaluation-tools/nucleo-f072rb.html), which belongs to the STM32 Nucleo-64 family. You can find more information about this family of boards by reading the [official documentation](https://www.st.com/content/ccc/resource/technical/document/data_brief/c8/3c/30/f7/d6/08/4a/26/DM00105918.pdf/files/DM00105918.pdf/jcr:content/translations/en.DM00105918.pdf).

![](../.gitbook/assets/nucleo_board.jpg)

_Figure: STM32 Nucleo development board._ [Picture source](https://www.st.com/en/evaluation-tools/nucleo-f072rb.html).

## Microphone <a id="microphone"></a>

The component used to capture sound is the [I2S MEMS Microphone Breakout](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/overview) by Adafruit. The actual microphone on this mini-board produces an _analog signal_ \(continuous in time and amplitude\) but the device also contains an Analog-to-Digital Converter that returns a _digital_ signal \(discrete in time and amplitude\), which is the format we need in order to pass the data to our microcontroller. We will describe the component in more detail in the [next chapter](../passthrough/audio-io/microphone.md), which is devoted to building a _passthrough_ circuit; the configuration, which simply passes the microphone input directly to the output, is the "hello world" equivalent of an embedded audio application.

![](../.gitbook/assets/sensors_3421_quarter_orig.jpg)

_Figure: Adafruit I2S MEMS Microphone Breakout._ [Picture source](http://learn.adafruit.com/assets/39631).

## DAC + Audio Jack <a id="dac_jack"></a>

The microcontroller accepts and produces digital signals; in order to playback its output on a pair of headphones, it is necessary to obtain analog signal and this can be achieved via a Digital-to-Analog Converter \(DAC\). We will use Adafruit's [I2S Stereo Decoder Breakout](https://learn.adafruit.com/adafruit-i2s-stereo-decoder-uda1334a/overview), which contains the DAC, an audio jack for connecting headphones, and the necessary additional components. We will describe the DAC in more detail as we build a passthrough in the [next chapter](../passthrough/audio-io/dac.md).

![](../.gitbook/assets/adafruit_products_3678_top_orig.jpg)

_Figure: Adafruit I2S Stereo Decoder - UDA1334A Breakout._ [Picture source](http://learn.adafruit.com/assets/48396).

