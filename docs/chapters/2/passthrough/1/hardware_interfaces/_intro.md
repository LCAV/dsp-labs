# 2.1 Hardware interfaces

The microphone and DAC components we will be using rely on the I2S (Inter-IC Sound) bus specification for audio transfer. This is a 3-line serial bus consisting of:

1. A **data** line for two time-multiplexed channels (usually denoted as _left_ and _right_).
2. A **word select** line for indicating which of the two channels is being transmitted/received.
3. A **clock** line for which each period will correspond to a unique bit of data.

More information about the I2S bus specification can be read [here](https://www.sparkfun.com/datasheets/BreakoutBoards/I2SBUS.pdf).

We first discuss the I2S protocol with respect to the [microphone](microphone.md) and then for the [DAC](dac.md). We recommend reading in this order as the microphone section is easier to grasp and will introduce common terminology used later on.

For the STM board that we are using, we will configure two I2S buses: one for input and the other for output. This configuration process will be covered in [Chapter 2.2](../../2/updating_stm32_peripherals.md).