#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADALM1000
NUM_SAM_PTS beider ADCs auslesen und als Plot darstellen

20.6.2020, S Mack
"""

import numpy as np
import matplotlib.pyplot as plt
from pysmu import Session, Mode

NUM_SAM_PTS = 5000 # Number of sampling points


try:
    #if not ('session' in locals()): 
    session = Session()
    if session.devices:
        samp_ch_a = []
        samp_ch_b = []
        dev = session.devices[0]
        # Set both channels to high impedance mode.
        chan_a = dev.channels['A']
        chan_b = dev.channels['B']
        chan_a.mode = Mode.HI_Z
        chan_b.mode = Mode.HI_Z
        samples = dev.get_samples(NUM_SAM_PTS)
        for data in samples:
            samp_ch_a.append(data[0][0])
            samp_ch_b.append(data[1][0])     
        fig, ax = plt.subplots()
        x = np.arange(0, NUM_SAM_PTS, 1)
        ax.plot(x,samp_ch_a,'-',label='CH A')
        ax.plot(x,samp_ch_b,'-',label='CH B')
        ax.set_ylim(-0.1, 5.1)
        ax.set_xlim(-50, NUM_SAM_PTS + 50)
        ax.grid(linestyle=':')
        ax.set(xlabel='Sampling Number', ylabel='Voltage', title='ADALM1000 High Impedance Sampling')
        ax.legend(loc='upper right')
        plt.show()
    
    else:
        print('no devices attached')
    
except KeyboardInterrupt:    
    print()
    print('Strg + C erkannt...')    
    
finally:
    print('Ende.')
    #session.cancel()
    #session.end()
    #del session
    pass       
