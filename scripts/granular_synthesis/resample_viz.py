import numpy as np
import matplotlib.pyplot as plt
from utils import resample

n_samples = 20
fact_up = 2
fact_down = 0.6

t_orig = np.arange(n_samples)
samples = np.random.randn(n_samples)*64

samples_hi = resample(samples, fact_up)
t_hi = np.arange(len(samples_hi))

samples_low = resample(samples, fact_down)
t_lo = np.arange(len(samples_low))

f, (ax1, ax2, ax3) = plt.subplots(3,1)
ax1.stem(t_orig, samples)
ax1.plot(t_orig, samples)
ax1.set_ylabel("Original (%d)" % n_samples)
ax1.set_xlim([0,n_samples/fact_down])
ax1.grid()

ax2.stem(t_orig/fact_down, samples, label="Original")
ax2.plot(t_lo, samples_low, 'r')
ax2.stem(t_lo, samples_low, 'r', markerfmt='r^')
ax2.set_ylabel("Darth Vader (%d)" % (len(samples_low)))
ax2.legend()
ax2.set_xlim([0,n_samples/fact_down])
ax2.grid()

ax3.stem(t_orig/fact_up, samples, label="Original")
ax3.plot(t_hi, samples_hi, 'g')
ax3.stem(t_hi, samples_hi, 'g', markerfmt='g^')
ax3.set_ylabel("Chipmunk (%d)" % (len(samples_hi)))
ax3.set_xlim([0,n_samples/fact_down])
ax3.grid()
ax3.legend()

plt.show()