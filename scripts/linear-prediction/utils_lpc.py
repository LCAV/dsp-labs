import numpy as np


def bac(x, p):
    # compute the biased autocorrelation for x up to lag p
    L = len(x)
    r = np.zeros(p+1)
    for m in range(0, p+1):
        for n in range(0, L-m):
            r[m] += x[n] * x[n+m]
        r[m] /= float(L)
    return r


def ld(r, p):
    # solve the toeplitz system using the Levinson-Durbin algorithm
    g = r[1] / r[0]
    a = np.array([g])
    v = (1. - g * g) * r[0]
    for i in range(1, p):
        g = (r[i+1] - np.dot(a, r[1:i+1])) / v
        a = np.r_[ g,  a - g * a[i-1::-1] ]
        v *= 1. - g*g
    # return the coefficients of the A(z) filter
    return np.r_[1, -a[::-1]]

def lpc(x, p):
    # compute p LPC coefficients for a speech segment
    return ld(bac(x, p), p)


"""
C-"friendly" implementation
"""
def ld_eff(r, order):
    # solve the toeplitz system using the Levinson-Durbin algorithm
    a = np.ones(order+1)
    a_prev = np.ones(order)
    a[1] = r[1]/r[0]
    for p in range(2, order+1):

        for j in range(1, p):
            a_prev[j] = a[j]

        # TODO: compute `k` from `r` and `a`
        k = 1

        # TODO: compute new `a` with `a_prev` and `k`
        # separate vector is needed so we don't overwrite!
        for j in range(1, p):
            a[j] = a_prev[j]
        a[p] = k

    # by convention, have negative of coefficients
    for p in range(1, order+1):
        a[p] *= -1

    return a


def lpc_eff(x, p):
    # compute p LPC coefficients for a speech segment
    return ld_eff(bac(x, p), p)