#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADALM1000
ADC CHA **und** CHB im High Impedance Modus gespeist mit einem externen Signal
kontinuierlich auslesen und als Live Plot darstellen.
Objektorientierte Variante mit Trigger.
Bei einem positiven Triggerwert wird beim Überschreien der Triggerschwelle und
bei einem negativen Triggerwert bei Unterschreiten der Triggerschwelle getriggert.
https://analogdevicesinc.github.io/libsmu/classsmu_1_1Signal.html

24.6.2020, S Mack
"""
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pysmu import Session, Mode

N_S_PTS = 7000 # Number of sampling points
RED_RATE = 1 # Reduction ratio for displayed sample rate
TRIG = 3 # Trigger level in Volts, negative: Signal must be smaller
V_RANGE = [-0.1,5.1] # Vertical Range in Volts
H_MAX = 5 # Horizontal Range from 0 to this value in Milliseconds


class Scope(object):

    def __init__(self, ax, session, h_max, v_range, n_s_pts=400, red_rate=1, mode_a='Hi_Z',mode_b='Hi_Z', trig=0): 
        self.ax = ax
        self.n_s_pts = n_s_pts # Number of sampling points
        self.red_rate = red_rate # Reduction ratio of effecive sampling rate
        self.n_d_pts = int(n_s_pts/red_rate) # Number of displayed points
        self.trig = trig # Trigger level in Volts, 0 = no trigger action
        self.x_vals = np.arange(0, self.n_d_pts, 1)*self.red_rate/100 # Sampling times in ms
        self.line_a, = ax.plot(self.x_vals, np.zeros(self.n_d_pts),'-',label='CH A (TRG)')
        self.line_b, = ax.plot(self.x_vals, np.zeros(self.n_d_pts),'-',label='CH B')
        self.ax.set_ylim(v_range[0], v_range[1])
        if(h_max < self.n_d_pts*self.red_rate/100):
            self.ax.set_xlim(-0.5, h_max + 0.5)
        else:
            self.ax.set_xlim(-0.5, self.n_d_pts*self.red_rate/100 + 0.5)
        self.ax.grid(linestyle=':')
        self.ax.legend(loc='lower right')
        self.ax.set(xlabel='Time (ms)', ylabel='Voltage (V)')
        
        self.session = session
        self.dev = session.devices[0]
        chan_a = self.dev.channels['A']
        chan_b = self.dev.channels['B']
        
        if (mode_a == 'Hi_Z'): # Set channel to high impedance mode
            chan_a.mode = Mode.HI_Z 
        else:
            print('Mode Channel A not yet supported')
        if (mode_b == 'Hi_Z'): # Set channel to high impedance mode
            chan_b.mode = Mode.HI_Z 
        else:
            print('Mode Channel B not yet supported')
        
        self.session.start(0) # Start a continuous session.

    def get_samples(self):
        samples = [[],[]]
        # Read NUM_SAM_PTS samples in a blocking fashion (-1), flush surplus samples.
        samples_raw = self.dev.read(self.n_s_pts,timeout=-1, skipsamples=True)
        for x in samples_raw:
            samples[0].append(x[0][0])
            samples[1].append(x[1][0])
        return samples

    # returns first index of sampled data with value > val for positive vals
    # and < val for negative vals
    def trigger(self, vals):
        trigger_start = 0 # return 0 in case of no trigger event
        # flatnonzero returns index of nonzero (=True) elements
        if(self.trig > 0): 
            thres_indices = np.flatnonzero(np.array(vals) > self.trig)
        else:
            thres_indices = np.flatnonzero(np.array(vals) < -self.trig)
        if (len(thres_indices)>0):
            print('triggered')
            trigger_start = min(thres_indices) # returs index trigger event
        else:
            print('no trigger')
            trigger_start = -1
        return trigger_start
    
    def show_samples(self,vals):
        vals_a = vals[0][:: self.red_rate] # reduce effective sampling rate
        vals_b = vals[1][:: self.red_rate] # reduce effective sampling rate
        if(self.trig != 0): # show only if trigger event
            trigger_start=self.trigger(vals_a) 
            if(trigger_start != -1):
                disp_start = max(0, trigger_start - 20) # display 20 pts ahead trigger
                self.line_a.set_data(self.x_vals[:(self.n_d_pts-disp_start)],vals_a[disp_start:])
                self.line_b.set_data(self.x_vals[:(self.n_d_pts-disp_start)],vals_b[disp_start:])
        else:
            self.line_a.set_ydata(vals_a)  # plot new values
            self.line_b.set_ydata(vals_b)  # plot new values
   
    def yield_samples(self): # Must be iterator and separate method
        while True:
            samples = self.get_samples()
            yield samples 
            

try:
    session = Session()
    if session.devices:
        print('ADALM1000 gefunden...')
        fig, ax = plt.subplots()
        my_scope = Scope(ax,session,H_MAX,V_RANGE,n_s_pts=N_S_PTS, red_rate=RED_RATE, mode_a='Hi_Z', mode_b='Hi_Z', trig=TRIG)
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
