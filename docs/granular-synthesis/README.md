# 4. GRANULAR SYNTHESIS \(Python\)

In this exercise, we will implement a more sophisticated voice transformation with 
[granular synthesis](https://en.wikipedia.org/wiki/Granular_synthesis). Although the alien 
voice does a good job in altering the voice, it can severely harm intelligibility due to 
aliasing and can only be used for shifting the pitch up. With granular synthesis, 
intelligibility will not be so significantly affected _and_ we can shift the pitch down to 
create a Darth Vader voice.

In [Section 4.1](effect_description.md), we will briefly explain how we will be performing 
pitch shifting with granular synthesis. As for the alien voice effect, we will _prototype_ 
the implementation in Python by simulating a real-time environment that receives samples in 
a buffer-based fashion. This should minimize the amount of errors when implementing the voice 
transformation in C on an embedded device. We will guide you through the Python implementation 
in [Section 4.2](implementation.md).

As in the previous chapter, text contained in highlighted boxes, as shown below, will require 
_you_ to determine the appropriate solution and implementation.

{% hint style="info" %}
TASK: This is a task for you!
{% endhint %}

May the Force be with you!

```text
                                   _.-'~~~~~~~~~~~~`-._
                                  /         ||         \
                                 /          ||          \
                                |           ||          |
                                | __________||__________|
                                |/ -------- \/ ------- \|
                               /     (     )  (     )    \
                              / \     ----- () -----    / \
                             /   \         /||\        /   \
                            /     \       /||||\      /     \
                           /       \     /||||||\    /       \
                          /_        \o=============o/        _\
                            `--...__|`-._       _.-'|__...--'
                                    |    `-----'    |
```

_Figure: Modified from_ [here](http://www.ascii-art.de/ascii/s/starwars.txt).

