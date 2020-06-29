#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADALM1000
Ausgabe kontinuierliches Signaĺ
https://analogdevicesinc.github.io/libsmu/classsmu_1_1Signal.html

6.6.2020, S Mack
"""

from pysmu import Session, Mode

waveform_samples = 500

try:
    session = Session()

    if session.devices:
        dev = session.devices[0]
        dev.channels['A'].mode = Mode.SVMI
        dev.channels['A'].constant(2.8)
#        dev.channels['A'].sine(0, 5, waveform_samples, -(waveform_samples / 4))
#        dev.channels['A'].sawtooth(0, 5, waveform_samples, -(waveform_samples / 4))
#        dev.channels['A'].triangle(0, 5, waveform_samples, -(waveform_samples / 4))
#        dev.channels['A'].stairstep(0, 5, waveform_samples, -(waveform_samples / 4))
#        dev.channels['A'].square(0, 5, waveform_samples, -(waveform_samples / 4), 0.5)
        session.start(0)
        while True:
            pass
    else:
        print('no devices attached')
    
except KeyboardInterrupt:
    print()
    print('Strg + C erkannt...')
    
finally:
    pass
    #session.remove(0)