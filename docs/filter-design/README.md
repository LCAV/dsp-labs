# 4. DIGITAL FILTER DESIGN

In the previous exercise, we used a very simple filter in order to remove the
DC offset. Although the applied filter does the necessary job, it also removes
frequencies of interest! Try running the Python script with and without this 
simple high pass filter (HPF), and you'll notice a lot of the lower frequencies
of the voice are removed when applying this filter.

This motivates the design and use of a filter with a sharper [slope/roll-off](https://en.wikipedia.org/wiki/Roll-off).
In this chapter, we approach this task in order to replace the simplistic 
filter used earlier. After all, no DSP module is complete without a section on
filter design!

As before, text contained in highlighted boxes are tasks for ***you***!
{% hint style="info" %}
TASK: This is a task for you!
{% endhint %}