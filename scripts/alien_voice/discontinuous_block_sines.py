from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np

"""
Compute lookup table
"""
# user parameters
samp_freq = 32000
f_sine = 400
n_frames = 128 # buffer length
n_periods = 1   # of sine table for better resolution (more samples)

# periods
samp_per = 1./samp_freq
sine_per = 1./f_sine

# compute time instances
t_vals = np.arange(0, sine_per*n_periods, samp_per)
LOOKUP_SIZE = len(t_vals)
n_vals = np.arange(LOOKUP_SIZE)

# compute the sine table
data_type = 16    # 16 or 32 signed integer
MAX_SINE = 2**(data_type-1)-1   # [-(2*data_type-1), 2**(data_type-1)]
w_mod = 2*np.pi*(f_sine/samp_freq)
sine_table = np.sin(w_mod*n_vals) * MAX_SINE
if data_type == 16:
    sine_table = sine_table.astype(np.int16)
elif data_type == 32:
    sine_table = sine_table.astype(np.int32)
else:
    raise ValueError("Invalid data type!")


"""
Visualize consecutive buffer processing but not stitching properly
"""

n_buffers = 2

# no state variable
sine_vals_disc = []
for k in range(n_buffers):
    for n in range(n_frames):
        sine_vals_disc.append(sine_table[n%LOOKUP_SIZE])

# # using state variable for number of processed blocks
# sine_vals = []
# B = 0
# for k in range(n_buffers):
#     for n in range(n_frames):
#         sine_vals.append(sine_table[(n_frames*B+n)%LOOKUP_SIZE])
#     B += 1

# using state variable for sine pointer
sine_vals = []
sine_pointer = 0
for k in range(n_buffers):
    for n in range(n_frames):
        sine_vals.append(sine_table[sine_pointer])
        sine_pointer += 1
        sine_pointer %= LOOKUP_SIZE

plt.figure()
plt.title("Buffer length of %d; modulating with %d Hz" % (n_frames, f_sine))
plt.scatter(range(len(sine_vals_disc)), sine_vals_disc, marker='^', label="sampled sine (discontinuous)")
plt.scatter(range(len(sine_vals)), sine_vals, marker='v', c='g', label="sampled sine (state var)")
plt.grid()
plt.axvline(x=n_frames, c='r', ls='--', label="buffer boundary")
plt.autoscale(enable=True, axis='x', tight=True)
plt.xlabel("Time index")
plt.xlim([60, 170])
plt.legend(loc=3)

plt.savefig('discontinuous_sine.png', format='png', dpi=300)

plt.show()
