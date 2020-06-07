#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADALM1000
ADC CHA kontinuierlich auslesen
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
        chan_a.mode = Mode.HI_Z
        # Start a continuous session.
        session.start(0)
        while True:
            # Read 10000 samples in a blocking fashion (-1).
            samples = dev.read(1000, -1)
            for x in samples:
                print("{: 6f}".format(x[0][0]))
            time.sleep(1)
    else:
        print('no devices attached')
    
except KeyboardInterrupt:
    print()
    print('Strg + C erkannt...')
    
finally:
    print('Ende.')
    pass    
