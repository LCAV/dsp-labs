# 2.3 Wiring the breakout boards

Now that we have initialized the different peripherals that we will use
to interface with the microphone and DAC, we are ready to wire
everything up! Make sure that the STM32 board is not powered, i.e.
unplugged, while connecting the microphone and DAC breakout boards.

For this task, we will have to refer to the card provided with the STM32
board (see below) and the image of the chip
on the "Pinout" tab of our CubeMX project (further below).

<div style="text-align:center"><img src ="stm32f072_extensions.png" width="600"/></div>
<br>

<div style="text-align:center"><img src ="pinout_tab.png" width="600"/></div>
<br>

## <a id="microphone"></a>Adafruit I2S MEMS Microphone Breakout

*As previously mentioned, make sure that the STM32 board is powered
off!* We can then begin by connecting the microphone's ground pin. In electronics, it is common practice to first ground a component/circuit.

{% hint style='working' %}
TASK 3: Connect the microphone's **GND** pin to one of the STM32 board's **GND**
pins, e.g. slot 22 on the **CN7** (left) header.

*Tip: try to keep all the connector cables attached to each other to avoid messy wiring!*
{% endhint %}

We can now connect the supply voltage pin.

{% hint style='working' %}
TASK 4: Connect the microphone's **3V** pin to the STM32 board's **3V3** pin.

*Note: the microphone component accepts voltage levels between 1.6V and
3.6V so **do not** use the STM32 board's **5V** pin!*
{% endhint %}

Previously, we configured I2S2 for the microphone
so we will have to connect the following pins (see
image of chip from "Pinout" tab for the names on the left side of the
arrow) to the corresponding pins on the microphone breakout board (right
side of the arrow):
*  **I2S2_SD** $$\leftarrow$$ **DOUT**
*  **I2S2_CK** $$\rightarrow$$ **BCLK**
*  **I2S2_WS** $$\rightarrow$$ **LRCL**

{% hint style='working' %}
TASK 5: From the "Pinout" configuration on CubeMX, determine which pins of the STM32 board are used by I2S2. Using the card provided with the board (see PDF figure above), use the connector cables to wire the pins from the STM32 board to the appropriate pins on the microphone breakout board.

_Hint: for example, from the "Pinout" tab we can see that **I2S2_SD** is outputted on pin **PC3**. From the card provided with the board, we see **PC3** is located in the bottom left corner of the board's pin header extensions. Therefore, we will use a wire to connect this pin to the **DOUT** pin of the microphone breakout board._
{% endhint %}

Finally, we configured an additional GPIO pin in order to select whether we would like the microphone to be assigned to the left or right channel.

{% hint style='working' %}
TASK 6: Connect the microphone's **SEL** pin to the pin on the STM32 board corresponding to **LR_SEL**.

BONUS: do we have to connect the microphone's **SEL** pin for the passthrough to work? What would happen if we didn't?
{% endhint %}

## <a id="dac"></a>Adafruit I2S Stereo Decoder

*As previously mentioned, make sure that the STM32 board is powered off!* We can then begin by connecting the DAC's power supply, starting with the ground pin.

{% hint style='working' %}
TASK 7: Connect the DAC's **GND** and **VIN** pins to the STM32 board.

*Note: you can provide 5V to the **VIN** pin and the built-in regulator will produce a 3.3V supply, which is also available on the **3VO** pin.*
{% endhint %}



Previously, we configured I2S1 for the DAC so we will have to connect the following
pins to the appropriate pins on the DAC breakout board:
* **I2S1_SD**
* **I2S1_CK**
* **I2S1_WS**

Moreover, we configured an additional GPIO pin in order to mute the output.
* **MUTE**

{% hint style='working' %}
TASK 8: Connect the above four pins from the STM32 board to the appropriate pins on the DAC breakout board.
 
*Hint: see the [DAC chip explanation](../1/hardware_interfaces/dac.md) and [Adafruit's site](https://learn.adafruit.com/adafruit-i2s-stereo-decoder-uda1334a/pinouts) for more information on wiring the DAC component.*
{% endhint %}

With everything correctly wired up, we can proceed to [coding](../4/coding.md) the passthrough on the SW4STM32 software!