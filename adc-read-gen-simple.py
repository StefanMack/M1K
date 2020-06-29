#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADALM1000
Konstanten Spannung anlegen und am ADC CH A Spannung und Strom auslesen sowie
daraus den Widerstand berechnen.
Beim Strom muss vorher noch ein Offset von ca. 0,23 mA abgezogen werden, da
1 MOhm parallel plus unklarer Rest.
Spannung liegt nicht permanent an, wenn man sie mit Multimeter misst (?)
https://analogdevicesinc.github.io/libsmu/classsmu_1_1Signal.html

6.6.2020, S Mack
"""

import time
import numpy as np
from pysmu import Session, Mode



try:
    session = Session()
    if session.devices:
        dev = session.devices[0]
        # Set both channels to high impedance mode.
        chan_a = dev.channels['A']
        chan_a.mode = Mode.SVMI # Source coltage, measure current
        dev.channels['A'].constant(5) # 5 V source voltage
        print("Spannung (V) Strom (mA)")
        while True:
            u_vals = []
            i_vals = []
            samples = dev.get_samples(100)
            for x in samples:
                u_vals.append(x[0][0])
                i_vals.append(x[0][1])
            u_vals = np.asarray(u_vals)
            i_vals = np.asarray(i_vals)
            u_ave = u_vals.mean()
            i_ave = i_vals.mean() - 0.00023 # Offset correction
            r_ave = int(u_ave / i_ave)
            print("U = {:6f} V, I = {:6f} mA R = {} Ohm".format(u_ave, i_ave*1000, r_ave))
            time.sleep(1)
    else:
        print('no devices attached')
    
except KeyboardInterrupt:
    print()
    print('Strg + C erkannt...')
    
finally:
    pass    
