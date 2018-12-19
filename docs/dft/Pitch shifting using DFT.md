# Pitch shifting using DFT

In this tutorial, we will implement a pitch shifting using DFT in real-time.

The relation between pitch and frequency is not straightforward: while the frequency is an objective value that can be measured, the pitch is a subjective perception of sound. However, a *definite* pitch, i.e. a pitch that can be easily discerned, has a harmonic frequency spectra: all present frequencies are multiples of the first one, which is called *fundamental* frequency. What we hear is the fundamental frequency; its multiples are called *partials*, and serve to color the tone. Here is an example of an A3 played on a synthesized piano:

![alt text](pianofreq.png "Piano frequencies - A3")
_Figure: Fourier Transform of A3 on a synthesized piano._

The fundamental frequency is 220 Hz which corresponds indeed to A3 (recall that A4 corresponds to 440 Hz, and one octave higher means doubling the frequency). Note that the actual first "frequency" is 0 and represents the energy of the signal; thus it can't be fundamental.

$$ 
X(\omega = 0) = \sum_{n = -∞}^∞ x[n]e^{-i\omega n} \biggr\rvert_{\omega = 0} = \sum_{n = -∞}^∞ x[n]
$$

Luckily, we’re only interested in shifting the definite pitches of an input signal, as they are the only ones we can perceive. In a speech signal, definite pitches are vowels and voiced consonants, so ideally we would like to shift their pitches and nothing else. However, it would be too complicated to extract them from the input signal; it is easier to shift the pitch of every phonetic one by one, as shifting the pitch of an unvoiced consonant wouldn’t change much. Instead of parsing the input speech to phonetics, we simply separate the signal into intervals small enough: this way, every processed part of signal contains no more than one consonant or vowel.

To keep the definite pitch characteristics, the shifted pitch should still have a fundamental frequency and its partials. It means that we can’t simply shift all frequencies of the pitch, but we should stretch or compress them, so that the partials are still multiples of the fundamental frequency. This is done in the frequency domain: we first chose the pitch we want to shift to, and then place the signal samples to all multiples of its fundamental frequency. We then go back to the time domain.

![alt text](pianofreq1.png "Piano A3 shifted to A4") | ![alt text](pianofreq2.png "Piano A3 shifted to A2")
_Figure: Shifting A3 in the frequency domain: to A4 (on the left) and to A2 (on the right). Partial frequencies remain multiples of the fundamental one._

The challenge here is to process the signal in real time. The technique is similar to the granular synthesis: we process the signal with a delay corresponding to the analysis window size. 

Solarized dark             |  Solarized Ocean
:-------------------------:|:-------------------------:
![alt text](pianofreq1.png "Piano A3 shifted to A4")  |  ![alt text](pianofreq2.png "Piano A3 shifted to A2")
