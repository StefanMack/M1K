#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bestimmung der Phase einer Sinusfunktion mit curve-fit Funktion.
Damit soll die Phasendifferenz zweier Sinussignale anstatt mit der Kreuzkorrelation
berechnet werden.

Quelle: stackoverflow.com/questions/16716302/how-do-i-fit-a-sine-curve-to-my-data-with-pylab-and-numpy

16.1.21 S. Mack
"""




import numpy as np
from scipy.optimize import curve_fit
import pylab as plt

N = 1000 # number of data points
t = np.linspace(0, 4*np.pi, N)
phase = 2*np.pi/360*180.0
data = 3.0*np.sin(t+phase) + 0.5 + np.random.randn(N)*0.1 # create artificial data with noise

guess_freq = 1
guess_amplitude = 3*np.std(data)/(2**0.5)
guess_phase = 0
guess_offset = np.mean(data)

p0=[guess_freq, guess_amplitude,
    guess_phase, guess_offset]

# create the function we want to fit
def my_sin(x, freq, amplitude, phase, offset):
    return np.sin(x * freq + phase) * amplitude + offset


# bounds um negative Amplituden zu vermeiden
#fit = curve_fit(my_sin, t, data, p0=p0, bounds=([0,0,0,-10],[100,100,2*np.pi,10]))
fit = curve_fit(my_sin, t, data, p0=p0)

# we'll use this to plot our first estimate. This might already be good enough for you
data_first_guess = my_sin(t, *p0)

# recreate the fitted curve using the optimized parameters
data_fit = my_sin(t, *fit[0])
if(fit[0][1]>=0):
    phase_fit = fit[0][2]
else: # Noetig fuer den Fall ohne bounds wenn Amplitude > 0
    phase_fit = fit[0][2] + np.pi

print('Phase simuliert (rad): {} Fitergebnis Phase (rad): {}'.format(phase, phase_fit))

plt.plot(t,data, '.')
plt.plot(t,data_fit, label='after fitting')
plt.plot(t,data_first_guess, label='first guess')
plt.legend()
plt.show()
