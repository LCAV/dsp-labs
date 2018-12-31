# 6. LINEAR PREDICTION

In this exercise, we enhance our granular synthesis pitch shifter by using 
[Linear Predictive Coding](https://en.wikipedia.org/wiki/Linear_predictive_coding) (LPC).
Although our real-time implementation already does a good job in lowering the pitch,
the result may sound *unnatural*. The motivation behind using LPC is to preserve the energy envelope of the initial speech
**throughout the transformation** in order to improve the output quality.


In [Section 6.1](theory.md), we briefly explain the theory behind LPC.
In particular, we will see that there exists an intuitive model to describe the production of human speech.
This model results in a system of linear equations that needs to be solved (for each buffer) in order to keep this energy envelope untouched.


In [Section 6.2](implementation.md), we implement the code that solves the set of equations presented in Section 6.1.
We then guide you on the use of this code in order to improve the quality of the granular synthesis effect from the previous chapter.

As before, text contained in highlighted boxes, as shown below, will require 
***you*** to determine the appropriate solution/implementation.

{% hint style="info" %}
TASK: This is a task for you!
{% endhint %}

