# 6. LINEAR PREDICTION

In this exercise, we enhance our Granular Synthesis pitch shifter by using 
[Linear Predictive Coding](https://en.wikipedia.org/wiki/Linear_predictive_coding).
Although our real-time implementation already does a good job in lowering the pitch,
the result may sound *un-natural*. The point of using LPC is to preserve the energy envelope of the initial speech
throughout the transformation in order to make the output sound better.


In [Section 6.1](theory.md), we will briefly explain the theory behind LPC.
In particular, we will see that there exists a simple model to describe the 
production of the human speech. The latter will be very helpful to derive *quite* simple
equations that we will need to solve in order to keep this *energy envelope* untouched.


In [Section 6.2](implementation.md), you will get the pieces of code necessary to derive
and solve the equation system presented in section 6.1. Also, we will help you to find how
to use (*ie* include) this code in your Granular Synthesis pitch shifting algorithm.

As in the previous chapter, text contained in highlighted boxes, as shown below, will require 
_you_ to determine the appropriate solution and implementation.

{% hint style="info" %}
TASK: This is a task for you!
{% endhint %}

