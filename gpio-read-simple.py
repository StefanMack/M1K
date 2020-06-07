#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADALM1000
Auslesen Zustand GPIO
https://analogdevicesinc.github.io/libsmu/classsmu_1_1Signal.html

7.6.2020, S Mack
"""

import time

from pysmu import Session

# assign digital pins
PIO_0 = 28
PIO_1 = 29
PIO_2 = 47
PIO_3 = 3 

try:
    session = Session(ignore_dataflow=True, queue_size=10000)
    if session.devices:
        dev = session.devices[0]
        while True:
            # get state of PIO0
            state = dev.ctrl_transfer(0xc0, 0x91, PIO_3, 0, 0, 1, 100)
            # funktioniert nicht...
            #for ch in state:
            #    print(ch)
            print(list(state))
            time.sleep(1)
    else:
        print('no devices attached')
    
except KeyboardInterrupt:
    print()
    print('Strg + C erkannt...')
    
finally:
    pass
