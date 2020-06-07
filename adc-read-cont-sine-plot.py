#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADALM1000
ADC CHA im High Impedance Modus gespeist mit einem externen Signal
kontinuierlich auslesen und als Live Plot darstellen
https://analogdevicesinc.github.io/libsmu/classsmu_1_1Signal.html

6.6.2020, S Mack
"""
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pysmu import Session, Mode

NUM_SAM_PTS = 1000 # Number of sampling points
RED_RATIO = 4 # Reduction ratio for displayed sample rate
WAVEFORM_SAMPLES = 1000 # Number of generated sample voltages (repetitive)
num_dsp_pts = int(NUM_SAM_PTS/RED_RATIO)


#def init():  # um beim Start die alten Werte zu löschen
#    #print('init() ausgeführt.')
#    line.set_ydata([np.nan] * num_dsp_pts)
#    return line,

def show_samples(u_vals):
    #print('show_samples() ausgeführt.')
    #print(u_vals[0])
    u_vals = u_vals[:: RED_RATIO]
    line.set_ydata(u_vals)  # neue y-Werte berechnen
    return line,

def get_samples():
    #print('get_samples() ausgeführt.')
    samples = []
    # Read NUM_SAM_PTS samples in a blocking fashion (-1), flush surplus samples.
    samples_raw = dev.read(NUM_SAM_PTS,timeout=-1, skipsamples=True)
    for x in samples_raw:
        samples.append(x[0][0])
    return(samples)

def data_gen(): # Must be iterator, therefor yield and While-loop
    #print('data_gen() ausgeführt.')
    while True:
        samples = get_samples()
        yield samples 


try:
    session = Session()
    if session.devices:
        print('ADALM1000 gefunden...')
        dev = session.devices[0]
        # Set both channels to high impedance mode.
        chan_a = dev.channels['A']
        chan_a.mode = Mode.HI_Z
        chan_b = dev.channels['B']
        chan_b.mode = Mode.SVMI
        chan_b.sine(0, 5, WAVEFORM_SAMPLES, -(WAVEFORM_SAMPLES / 4))
        # Start a continuous session.
        session.start(0)     
        x = np.arange(0, num_dsp_pts, 1)
        fig, ax = plt.subplots()
        line, = ax.plot(x, np.zeros(num_dsp_pts),'.')
        ax.set_ylim(-0.1, 5.1)
        ax.grid(linestyle=':')
        ax.set(xlabel='Sampling Number', ylabel='Voltage', title='ADALM1000 High Impedance Sampling')
        ani = animation.FuncAnimation(fig, func=show_samples, frames=data_gen, interval=50, blit=False)
        plt.show()
        time.sleep(1)
    else:
        print('no devices attached')
    
except KeyboardInterrupt:
    print()
    print('Strg + C erkannt...')
    time.sleep(1)
    
finally:
    print('Ende.')
    session.cancel()
    session.end()
    pass    
