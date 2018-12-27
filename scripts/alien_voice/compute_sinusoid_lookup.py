from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np

"""
Compute lookup table
"""
data_type = 16    # 16 or 32 signed integer
samp_freq = 32000
f_sine = 400

# periods
samp_per = 1./samp_freq
sine_per = 1./f_sine

# compute time instances
t_vals = np.arange(0, sine_per*1, samp_per)
LOOKUP_SIZE = len(t_vals)
n_vals = np.arange(LOOKUP_SIZE)

# compute the sine table
MAX_SINE = 2**(data_type-1)-1   # [-(2*data_type-1), 2**(data_type-1)]
w_mod = 2*np.pi*(f_sine/samp_freq)
sine_table = np.sin(w_mod*n_vals) * MAX_SINE
if data_type == 16:
    sine_table = sine_table.astype(np.int16)
    print_type = np.uint16
    print_format = '0x%04x'
elif data_type == 32:
    sine_table = sine_table.astype(np.int32)
    print_type = np.uint32
    print_format = '0x%08x'
else:
    raise ValueError("Invalid data type!")

"""
Print C code.
"""
print('#define SINE_TABLE_SIZE', str(LOOKUP_SIZE))
print('#define SIN_MAX', (print_format % MAX_SINE))
if data_type == 16:
    print('const int16_t sine_table[SINE_TABLE_SIZE] = {')
elif data_type == 32:
    print('const int32_t sine_table[SINE_TABLE_SIZE] = {')
print(','.join([print_format % i.astype(print_type) for i in sine_table]))
print('};')

"""
Visualize
"""
plt.figure()
plt.stem(n_vals, sine_table)
plt.grid()
plt.autoscale(enable=True, axis='x', tight=True)
plt.xlabel("Index")
plt.title("Sine table for %d Hz at %d Hz sampling rate" % (f_sine, samp_freq))
plt.show()
