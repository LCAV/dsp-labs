# 1.2 Software

The ST Nucleo board is a microcontroller that is both: 

* highly _configurable_, in the sense that some of its electrical pins can be rerouted in software and assigned to specific function
* _programmable at a high level,_ since we can use C code and use a compiler to produce the microcode that will be uploaded onboard

To handle this great flexibility, ST provides us with an integrated development environment \(IDE\) that we can use to manage both aspects of Nucleo programming. This is the [**STM32CubeIDE**](https://www.st.com/en/development-tools/stm32cubeide.html)**,** an Eclipse-based IDE for programming STM32 microcontrollers. From the description webpage:

> STM32CubeIDE is an all-in-one multi-OS development tool, which is part of the STM32Cube software ecosystem. STM32CubeIDE is an advanced C/C++ development platform with peripheral configuration, code generation, code compilation, and debug features for STM32 microcontrollers and microprocessors. It is based on the ECLIPSE™/CDT framework and GCC toolchain for the development, and GDB for the debugging.

The IDE includes a chip configuration graphical interface called CubeMX:

![](../../.gitbook/assets/screenshot-2019-09-25-at-17.51.49-1%20%281%29.png)

and an Eclipse-based programming enviromnent:

![Figure: Screenshot of STM32CubeIDE.](../../.gitbook/assets/screenshot-2019-09-25-at-12.18.18%20%281%29.png)

In the next section we will review the installation of the [**STM32CubeIDE**](https://www.st.com/en/development-tools/stm32cubeide.html) ****software and we will later review some useful tips when using the IDE; don't forget to look back to the tips section when starting to play with the IDE!

