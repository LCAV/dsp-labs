def bac(x, p):
    # compute the biased autocorrelation for x up to lag p
    L = len(x)
    r = np.zeros(p+1)
    for m in xrange(0, p+1):
        for n in xrange(0, L-m):
            r[m] += x[n] * x[n+m]
        r[m] /= float(L)
    return r


def ld(r, p):
    # solve the toeplitz system using the Levinson-Durbin algorithm
    g = r[1] / r[0]
    a = np.array([g])
    v = (1. - g * g) * r[0];
    for i in xrange(1, p):
        g = (r[i+1] - np.dot(a, r[1:i+1])) / v
        a = np.r_[ g,  a - g * a[i-1::-1] ]
        v *= 1. - g*g
    # return the coefficients of the A(z) filter
    return np.r_[1, -a[::-1]]


def lpc(x, p):
    # compute p LPC coefficients for a speech segment
    return ld(bac(x, p), p)