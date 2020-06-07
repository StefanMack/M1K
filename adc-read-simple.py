#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADALM1000
Beide ADCs auslesen
https://analogdevicesinc.github.io/libsmu/classsmu_1_1Signal.html

6.6.2020, S Mack
"""

import time

from pysmu import Session, Mode

try:
    session = Session()
    if session.devices:
        dev = session.devices[0]
        # Set both channels to high impedance mode.
        chan_a = dev.channels['A']
        chan_b = dev.channels['B']
        chan_a.mode = Mode.HI_Z
        chan_b.mode = Mode.HI_Z
        while True:
            samples = dev.get_samples(1000)
            for x in samples:
                print("{: 6f} {: 6f} {: 6f} {: 6f}".format(x[0][0], x[0][1], x[1][0], x[1][1]))
            time.sleep(1)
    else:
        print('no devices attached')
    
except KeyboardInterrupt:
    print()
    print('Strg + C erkannt...')
    
finally:
    pass    
