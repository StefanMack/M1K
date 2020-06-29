#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADALM1000
ADC CHA im High Impedance Modus gespeist mit einem externen Signal
kontinuierlich auslesen und als Live Plot darstellen.
Objektorientierte Variante ohne Trigger.
https://analogdevicesinc.github.io/libsmu/classsmu_1_1Signal.html

24.6.2020, S Mack
"""
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pysmu import Session, Mode

N_S_PTS = 400 # Number of sampling points
RED_RAT = 10 # Reduction ratio for displayed sample rate


class Scope(object):

    def __init__(self, ax, session, n_s_pts=400, red_rat=1, mode_a='Hi_Z'): 
        self.ax = ax
        self.n_s_pts = n_s_pts # Number of sampling points
        self.red_rat = red_rat # Reduction ratio of effecive sampling rate
        self.n_d_pts = int(n_s_pts/red_rat) # Number of displayed points
        self.x_vals = np.arange(0, self.n_d_pts, 1)*self.red_rat/100 # Sampling times in ms
        self.line_a, = ax.plot(self.x_vals, np.zeros(self.n_d_pts),'.',label='CH A')
        self.ax.set_ylim(-0.1, 5.1)
        self.ax.grid(linestyle=':')
        self.ax.legend(loc='lower right')
        self.ax.set(xlabel='Time (ms)', ylabel='Voltage (V)')
        
        self.session = session
        self.dev = session.devices[0]
        chan_a = self.dev.channels['A']
        
        if (mode_a == 'Hi_Z'): # Set channel to high impedance mode
            chan_a.mode = Mode.HI_Z 
        else:
            print('Mode Channel A not yet supported')
        
        self.session.start(0) # Start a continuous session.

    def get_samples(self):
        samples = []
        # Read NUM_SAM_PTS samples in a blocking fashion (-1), flush surplus samples.
        samples_raw = self.dev.read(self.n_s_pts,timeout=-1, skipsamples=True)
        for x in samples_raw:
            samples.append(x[0][0])
        return samples
    
    def show_samples(self,vals):
        vals = vals[:: self.red_rat] # reduce effective sampling rate
        self.line_a.set_ydata(vals)  # plot new values

    def yield_samples(self): # Must be iterator and separate method
        while True:
            samples = self.get_samples()
            yield samples 
            

try:
    session = Session()
    if session.devices:
        print('ADALM1000 gefunden...')
        fig, ax = plt.subplots()
        my_scope = Scope(ax,session,n_s_pts=N_S_PTS, red_rat=RED_RAT, mode_a='Hi_Z')
        ani = animation.FuncAnimation(fig, func=my_scope.show_samples, frames=my_scope.yield_samples, interval=50, blit=False)
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
    session.end()
    pass    
