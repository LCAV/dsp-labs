# 3.1 How it works

The alien voice effect that we will be creating is done by simply using _sinusoidal modulation_ to shift the voice spectrum up. In communications terminology, this is often called _amplitude modulation_ \(or AM for short\).

Given a modulation frequency $$f_{mod}$$ \(in Hz\) and an input sample $$x[n]$$ we can compute each output sample $$y[n]$$ as such:
$$y[n] = x[n] \cdot \sin(2 \pi \cdot (f_{mod} / f_s) \cdot n),$$
where $$f_s$$ is the sampling frequency \(in Hz\) and $$n$$ is the time index of the samples that are taken at regular intervals of $$1/f_s$$. From now on, we will denote $$2 \pi \cdot (f_{mod} / f_s)$$ with $$\omega_{mod}$$, which represents the corresponding _normalized_ frequency for $$f_{mod}$$ given $$f_s$$.

The modulation frequency must be kept small in order to preserve intelligibility as the resulting signal will be affected by _aliasing_ due to the process of shifting up the spectrum \(and maintaining the same sampling frequency\).

We recommend downloading [this IPython notebook](https://github.com/prandoni/COM303/blob/master/voice_transformer/voicetrans.ipynb) from GitHub. Under the section entitled `"1 - The Robot Voice"`, you can hear this simple voice effect applied to a sample audio file. You can also modify the modulation frequency to hear how it affects the output and the spectrum due to aliasing. You can also preview the notebook and listen to the effect without downloading it by heading over to [nbviewer](http://nbviewer.jupyter.org/github/prandoni/COM303/blob/master/voice_transformer/voicetrans.ipynb).

As mentioned in the IPython notebook above, this voice transformer is great for real-time applications as it is very cheap, consisting of only one multiplication per sample. However, the intelligibility can be quite poor due to aliasing. In the next chapter, we will implement a more sophisticated voice transformer, namely [pitch shifting with granular synthesis](../granular-synthesis/). Nevertheless, this simple exercise will already expose us to some important practical DSP "tricks" in order to implement a real-time version of this effect.

