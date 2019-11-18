# 2.1 Audio I/O

Any real-time audio application running on the microcontroller will need to acquire data from a source \(for instance, a microphone\) and deliver data to an outuput sink \(for instance, an analog-to-digital converter connected to a loudspeaker\) that we can listen to. The source and the sink are peripheral components external to the microcontroller board and therefore we need to understand two fundamental things:

* the protocol used by external peripherals to electrically transfer data to and from the microcontroller board; for audio, this is usually the I2S protocol
* the mechanism by which the data transfer is handled; in our case this will be a so-called DMA transfer.

### I2S data transfer protocol

Our digital microphone and DAC components rely on the **I2S** \(Inter-IC Sound\) bus specification for transferring digital audio samples to and from the microcontroller. Ultimately, the data that transits on the bus is simply a sequence of binary digits \(zeros and ones\) that are mapped to two distinct voltage levels, HIGH and LOW; each audio sample is encoded by a fixed number of bits \(usually 24 or 32\), that is, by a binary _word_. The bus will require some form of synchronization in order to determine when words begin and end. Finally, note that the audio data is usually _stereo_, that is, it consists of a time-multiplexed stream in which left and right channel data words are interleaved. 

The I2S bus is a 3-line serial bus consisting of:

1. A **clock \(CLK\)** line that indicates the timing for each binary digit
2. A **data** line for the actual sequence of binary digits.
3. A **word select \(WS\)** line to indicate the beginning of a binary word.

A typical word transfer over the I2S bus looks like so:

![](../../.gitbook/assets/word.png)

We will look at the details in the next section but, for now, notice the following:

1. the data signal is synchronized to the rising edge of the the clock signal and is kept constant for the duration of a clock cycle.
2. the beginning of a word is signaled by a state _transition_ in the word select signal   
3. words are sent starting from the most significant bit \(MSB\)
4. in this example words are 32-bit long; however only 18 bits are actually used for the data. Bits 19 to 24 are set to zero and from the 25th to the 32nd clock cycle the data signal is set to _tri-state_, which is a high impedance mode that essentially removes an output port from the circuit in order to avoid a _short circuit_. See [here](https://en.wikipedia.org/wiki/Three-state_logic) for more information on tri-state.
5. words are started either on the _rising_ or on the _falling_ edge of the **WS** signal, depending on the configuration of the DAC. In the above figure, words are started on the falling edge: the output is kept on tri-state after the rising edge at the end of the diagram and until the next falling edge of **WS**. This is to allow for two DACs to operate in parallel when building a stereo system, with the **WS** signal selecting one out of the two possible channels for data transmission.

More information about the I2S bus specification can be read [here](https://www.sparkfun.com/datasheets/BreakoutBoards/I2SBUS.pdf).

We first discuss the I2S protocol with respect to the [microphone](microphone.md) and then for the [DAC](dac.md). We recommend reading in this order as the microphone section is easier to grasp and will introduce some common terminology used later on.

For the STM board that we are using, we will configure two I2S buses: one for the input and the other for the output. This configuration process will be covered in [Chapter 2.2](../updating_stm32_peripherals.md).

### DMA transfers

The microcontroller has a certain amount of onboard memory that it can access, and the input samples need be stored in this memory before they can be processed. It would however be too onerous for the microcontroller to explicitly fetch each new input sample from the input peripheral and, similarly, deliver each sample to the output peripheral explicitly. To free the microcontroller from these tasks and use the CPU power primarily for processing, peripherals can access the onboard memory directly both to write and to read data; such data transfers are called Direct Memory Access \(DMA\) and the peripherals only contact the microcontroller \(via a so-called _interrupt_\) to signal that a transfer has just been completed.

DMA transfers occur automatically, but they need to be configured; for an input DMA, for instance, we need to decide:

* _where_ in memory the peripheral should store the data; this means that we need to set up a buffer reserved for input DMA
* _how much_ data should a DMA transfer handle before notifying the microcontroller; this will determine the size of the DMA buffer.

Obviously, yhe same design decisions need to be performed for an output DMA.

The buffer's length is a key parameter that needs to be fine-tuned to the demands of a specific audio application. In general, the longer the buffer, the fewer DMA transfers per second, which is desirable since it minimizes the number of interrupts and allows for more code optimization. Additionally, certain types of signal processing operations provide results that are dependent on the buffer length; the DFT of a signal, for instance, will provide a frequency resolution that is proportional to the buffer's length. On the other hand, a large buffer will also introduce a ssignificant _latency,_ as we need to wait for more samples to arrive before we can begin processing. For real-time audio applications, having a low latency is extremely important for the user experience and so we are in a situation of conflicting requirements for which a suitable compromise needs to be determined on a case-by-case basis. 

For a refresher on buffering in real-time applications, please refer to Lecture 2.2.5b in the [second DSP module](https://www.coursera.org/learn/dsp2/) on Coursera.

Finally, remember that, in real-time DSP applications, we usually need to use alternating buffers for DMA transfers. Consider for instance an input DMA transfer: while the incoming samples are placed into an array by the DMA controller, the incoming array should _not_ be accessed by our application until the DMA transfer is complete. When the DMA interrupt is signaled, it is then safe to copy the data from the incoming buffer into a safe area for processing. We will see later that, in our case, half-buffer interrupts will allow us to process the data in place.

