import os
from scipy.io import wavfile
import numpy as np
from utils_lpc import lpc, lpc_eff


MAX_VAL = 32767.0   #int16
LPC_ORDER = 20
TOL = 1e-10

# import WAV file
current_dir = os.path.dirname(os.path.realpath(__file__))
input_wav = os.path.join(current_dir, "voiced.wav")
samp_freq, signal_orig = wavfile.read(input_wav)
signal_orig = signal_orig/MAX_VAL


a1 = lpc(signal_orig, LPC_ORDER)
print()
print("Correct LPC coefficients: ", end="")
print(a1)
print()

a2 = lpc_eff(signal_orig, LPC_ORDER)
print()
print("Resulting LPC coefficients: ", end="")
print(a2)
print()

if np.linalg.norm(a1-a2) < TOL:
    print("CORRECT!")
else:
    print("Something's wrong...")

