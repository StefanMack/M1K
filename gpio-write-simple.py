#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADALM1000
Schreiben auf Register um z.B. GPIOs zu setzen
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
            # set PIO0 high
            state = dev.ctrl_transfer(0x40, 0x51, PIO_0, 0, 0, 0, 100)
            time.sleep(0.2)
            # set PIO0 low
            state = dev.ctrl_transfer(0x40, 0x50, PIO_0, 0, 0, 0, 100) 
            time.sleep(0.2)
    else:
        print('no devices attached')
    
except KeyboardInterrupt:
    print()
    print('Strg + C erkannt...')
    
finally:
    pass
