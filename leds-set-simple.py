#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADALM1000
Ausgabe 8-Bit Zahl über die drei LEDs (R,G und B)
https://analogdevicesinc.github.io/libsmu/classsmu_1_1Signal.html

6.6.2020, S Mack
"""

import time

from pysmu import Session

try:
    session = Session()
    if session.devices:
        dev = session.devices[0]
        while True:
            for val in range(0, 8):
                dev.set_led(val)
                time.sleep(.25)      
    else:
        print('no devices attached')
    
except KeyboardInterrupt:
    print()
    print('Strg + C erkannt...')
    
finally:
    pass    
