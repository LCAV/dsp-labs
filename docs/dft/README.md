# 7. DFT PITCH SHIFTING

In this chapter, we consider pitch shifting in the **frequency domain** by performing the _Discrete Fourier Transform_ (DFT). As the pitch is strongly related to frequency, it is quite intuitive what operation needs to be done in this domain, namely shift the spectrum up or down. However, as mentioned in the previous chapter, we wish to preserve a certain structure in the spectrum.

[Section 7.1](theory.md) explains the operations that need to be performed for DFT pitch shifting and the motivation behind them, while [Section 7.2](implementation.md) guides you through implementing this approach in Python.

With this effect, we will be creating a chipmunk-like voice effect; so no need to inhale helium!

Text contained in highlighted boxes, as shown below, are tasks for ***you***.
{% hint style="info" %}
TASK: This is a task for you!
{% endhint %}


```
                              _
                          .-'` `}
                  _./)   /       }
                .'o   \ |       }
                '.___.'`.\    {`
                /`\_/  , `.    }
                \=' .-'   _`\  {
                 `'`;/      `,  }
                    _\       ;  }
                   /__`;-...'--'

```

[Source](http://www.heartnsoul.com/ascii_art/squirrels.txt).

