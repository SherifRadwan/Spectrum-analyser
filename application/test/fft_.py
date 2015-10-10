import numpy as np
import math


# from stackoverflow
# FIXME: use numpy or scipy functions instead!!
# linespace ?? float support
def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

# from PlotItem.py
# returns the power sepctrym of y(x)
# original one
# def _fourierTransform(self, x, y):
#     ## Perform fourier transform. If x values are not sampled uniformly,
#     ## then use np.interp to resample before taking fft.
#     dx = np.diff(x)
#     uniform = not np.any(np.abs(dx-dx[0]) > (abs(dx[0]) / 1000.))
#     if not uniform:
#         x2 = np.linspace(x[0], x[-1], len(x))
#         y = np.interp(x2, x, y)
#         x = x2
#     f = np.fft.fft(y) / len(y)
#     y = abs(f[1:len(f)/2])
#     dt = x[-1] - x[0]
#     x = np.linspace(0, 0.5*len(x)/dt, len(y))
#     return x, y

def _fourierTransform(x, y):
    ## Perform fourier transform. If x values are not sampled uniformly,
    ## then use np.interp to resample before taking fft.
    dx = np.diff(x)
    uniform = not np.any(np.abs(dx-dx[0]) > (abs(dx[0]) / 1000.))
    if not uniform:
        x2 = np.linspace(x[0], x[-1], len(x))
        y = np.interp(x2, x, y)
        x = x2
    f = np.fft.fft(y) / len(y)
    h_f = f[1:len(f)/2]
    y = abs(h_f)
    dt = x[-1] - x[0]
    x = np.linspace(0, 0.5*len(x)/dt, len(y))
    return x, h_f 

def powerSpectrum(ft):
    x, y = ft
    return x, abs(y)

def amplitudeSpectrum(ft):
    x, y = ft
    return x, 20*np.log10(np.absolute(y))

def phaseSpectrum(ft):
    x, y = ft
    return x, np.angle(y)


if __name__ == '__main__':
    t = [1,2,3,4,5,6,7,8,9,10,11,11,12]
    u = [1,2,3,4,5,6,7,8,9,10,11,11,12]

    ft =  _fourierTransform(t, u)
    x, y = ft
    print x
    print y
    x, y = powerSpectrum(ft)
    print x
    print y
    x, y = amplitudeSpectrum(ft)
    print x
    print y
    x, y = phaseSpectrum(ft)
    print x
    print y