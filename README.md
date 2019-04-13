# Practical Digital Signal Processing Through Voice Effects

**By [Eric Bezzam](https://ebezzam.github.io/), [Adrien Hoffet](https://lcav.epfl.ch/people/people-current_staff/page-145331-en-html/), and [Paolo Prandoni](https://lcav.epfl.ch/people/people-current_staff/people-paolo-prandoni/)**

This repository contains the content and scripts for the [practical exercises](https://lcav.gitbook.io/dsp-labs/) for the EPFL course [COM-303, Signal processing for communications](http://isa.epfl.ch/imoniteur_ISAP/!itffichecours.htm?ww_i_matiere=24007074&ww_x_anneeacad=1866893861&ww_i_section=944590&ww_i_niveau=6683147&ww_c_langue=en).

The material in this book is based off of the voice effects presented in [this Jupyter notebook](https://nbviewer.jupyter.org/github/prandoni/COM303-Py3/blob/master/VoiceTransformer/VoiceTransformer.ipynb).
However, the focus is on implementing these effects in a real-time manner: first in Python with a laptop's soundcard
then in C with a microcontroller from ST Microelectronics.

***The goal of these exercises is to expose participants to the practical sides of digital signal processing (DSP) through
fun and intuitive audio applications***, while also using industry-level tools that are low-cost and accessible so that others
around the world can try them out. 

Even if the [hardware](https://lcav.gitbook.io/dsp-labs/bom) cannot be obtained, the main lessons in DSP can still be acquired in Python with your laptop! In this case, you can skip ahead to Chapter 3, but we do recommend reading [Section 2.1](https://lcav.gitbook.io/dsp-labs/passthrough/audio-io) on Audio I/O theory.

Table of contents:

1. [Overview and installation of ST Microelectronics material](https://lcav.gitbook.io/dsp-labs/installation)
2. [Audio passthrough](https://lcav.gitbook.io/dsp-labs/passthrough)
3. [Alien voice effect](https://lcav.gitbook.io/dsp-labs/alien-voice)
4. [Digital filter design](https://lcav.gitbook.io/dsp-labs/filter-design)
5. [Granular synthesis pitch shifting](https://lcav.gitbook.io/dsp-labs/granular-synthesis)
6. [Linear predictive coding](https://lcav.gitbook.io/dsp-labs/linear-prediction)
7. [DFT-based pitch shifting](https://lcav.gitbook.io/dsp-labs/dft)

To set up the book for local development or to suggest changes (more than welcome!), check out the [setup guide](https://github.com/LCAV/dsp-labs/blob/master/SETUP.md).

If you use this material in your own work, please cite [our paper](https://infoscience.epfl.ch/record/258046/files/dsp_labs_icassp_2019.pdf).

> E. Bezzam, A. Hoffet, P. Prandoni, *Teaching Practical DSP with Off-the-Shelf Hardware and Free Software*, Proc. IEEE ICASSP, Brighton, UK, 2019.
