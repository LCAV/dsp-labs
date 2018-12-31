# 3. ALIEN VOICE EFFECT

In this exercise, we will create a simple voice effect, namely taking the microphone's input 
signal and producing an "alien" version of it. During the implementation, we will come across 
a few limitations that arise when trying to realize digital signal processing \(DSP\) in 
real-time.

In [Section 3.1](effect_description.md), we will explain the effect that we will be 
implementing. In [Section 3.2](dsp_tips.md), we will discuss some important points that need 
to be considered when implementing real-time DSP. In [Section 3.3](python.md), we propose a 
Python framework for simulating a real-time environment with your laptop's sound card the 
[`sounddevice`](http://python-sounddevice.readthedocs.io/) library. Finally, we will guide 
you through the implementation on the STM32 board in [Section 3.4](implementation.md).

As in the previous chapter, text contained in highlighted boxes, as shown below, will require ***you*** to determine the appropriate solution and implementation.

{% hint style="info" %}
TASK: This is a task for you!
{% endhint %}

```text
        .     .       .  .   . .   .   . .    +  .
          .     .  :     .    .. :. .___---------___.
               .  .   .    .  :.:. _".^ .^ ^.  '.. :"-_. .
            .  :       .  .  .:../:            . .^  :.:\.
                .   . :: +. :.:/: .   .    .        . . .:\
         .  :    .     . _ :::/:               .  ^ .  . .:\
          .. . .   . - : :.:./.                        .  .:\
          .      .     . :..|:                    .  .  ^. .:|
            .       . : : ..||        .                . . !:|
          .     . . . ::. ::\(                           . :)/
         .   .     : . : .:.|. ######              .#######::|
          :.. .  :-  : .:  ::|.#######           ..########:|
         .  .  .  ..  .  .. :\ ########          :######## :/
          .        .+ :: : -.:\ ########       . ########.:/
            .  .+   . . . . :.:\. #######       #######..:/
              :: . . . . ::.:..:.\           .   .   ..:/
           .   .   .  .. :  -::::.\.       | |     . .:/
              .  :  .  .  .-:.":.::.\             ..:/
         .      -.   . . . .: .:::.:.\.           .:/
        .   .   .  :      : ....::_:..:\   ___.  :/
           .   .  .   .:. .. .  .: :.:.:\       :/
             +   .   .   : . ::. :.:. .:.|\  .:/|
             .         +   .  .  ...:: ..|  --.:|
        .      . . .   .  .  . ... :..:.."(  ..)"
         .   .       .      :  .   .: ::/  .  .::\
```

[Source](http://www.asciiworld.com/-Aliens,128-.html).

