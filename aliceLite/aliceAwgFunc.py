#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 2.1.21
"""

import time
import config as cf
import pysmu as smu
import logging
import tkinter as tk

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen und Einstellungen beide Arbitärgeneratoren
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#--- Auslesen der in der UI gewählten Signalform

def update_awg(*dummy): # * damit mit und ohne Übergabe von Argumenten (z.B. Event)
    logging.debug('update_awg()')
    # if running and in continuous streaming mode temp stop, flush buffer and restart to change AWG settings
    if (cf.RUNstatus.get() == 1):
        if cf.session.continuous:
            cf.session.end()
            time.sleep(0.02)
            setup_awg() # set-up new AWG settings
            time.sleep(0.02) # wait awhile here for some reason
            cf.session.start(0) #wieso hier das Argument '0'? Vermutlich kontinuierlicher Modus
    
def setup_awg():
    logging.debug('setup_awg()')
    set_awga_min()
    set_awga_max()
    set_awga_freq()
    set_awga_dutyc()
    set_awga_shape()
    set_awgb_min()
    set_awgb_max()
    set_awgb_freq()
    set_awgb_dutyc()
    set_awgb_shape()
    update_awga()
    update_awgb()
    
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen Arbitärgenerator CHA
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
awga_minval = 0.0
awga_maxval = 0.0
awga_freqval = 0.0
awga_dutycval = 50.0
awga_shape = 'dc' # Initialisierung Singalform

#--- Min-Wert aus UI kontrollieren
def set_awga_min():
    global awga_minval
    try:
        awga_minval = float(eval(cf.AWGAMinEntry.get()))
    except:
        logging.debug('Exeption set_awga_min()')
        cf.AWGAMinEntry.delete(0,tk.END)
        cf.AWGAMinEntry.insert(0, awga_minval)

    if cf.AWGAMode.get() == 0: # Source Voltage measure current mode
        if awga_minval > 5.00:
            awga_minval = 5.00
            cf.AWGAMinEntry.delete(0,tk.END)
            cf.AWGAMinEntry.insert(0, awga_minval)
        if awga_minval < 0.00:
            awga_minval = 0.00
            cf.AWGAMinEntry.delete(0,tk.END)
            cf.AWGAMinEntry.insert(0, awga_minval)

    if cf.AWGAMode.get() == 1: # Source current measure voltage mode
        if awga_minval > 200.00:
            awga_minval = 200.00
            cf.AWGAMinEntry.delete(0,tk.END)
            cf.AWGAMinEntry.insert(0, awga_minval)
        if awga_minval < -200.00:
            awga_minval = -200.00
            cf.AWGAMinEntry.delete(0,tk.END)
            cf.AWGAMinEntry.insert(0, awga_minval)
    logging.debug('set_awga_min() with {}'.format(awga_minval)) 
#--- Max-Wert aus UI kontrollieren
def set_awga_max():
    global awga_maxval

    try:
        awga_maxval = float(eval(cf.AWGAMaxEntry.get()))
    except:
        logging.debug('Exeption set_awga_max()')
        cf.AWGAMaxEntry.delete(0,tk.END)
        cf.AWGAMaxEntry.insert(0, awga_maxval)

    if cf.AWGAMode.get() == 0: # Source Voltage measure current mode
        if awga_maxval > 5.00:
            awga_maxval = 5.00
            cf.AWGAMaxEntry.delete(0,tk.END)
            cf.AWGAMaxEntry.insert(0, awga_maxval)
        if awga_maxval < 0.00:
            awga_maxval = 0.00
            cf.AWGAMaxEntry.delete(0,tk.END)
            cf.AWGAMaxEntry.insert(0, awga_maxval)
        
    if cf.AWGAMode.get() == 1: # Source current measure voltage mode
        if awga_maxval > 200.00:
            awga_maxval = 200.00
            cf.AWGAMaxEntry.delete(0,tk.END)
            cf.AWGAMaxEntry.insert(0, awga_maxval)
        if awga_maxval < -200.00:
            awga_maxval = -200.00
            cf.AWGAMaxEntry.delete(0,tk.END)
            cf.AWGAMaxEntry.insert(0, awga_maxval)
    logging.debug('set_awga_max() with {}'.format(awga_maxval))

#--- Frequenz-Wert aus UI kontrollieren
def set_awga_freq():
    global awga_freqval
    
    try:
        awga_freqval = float(eval(cf.AWGAFreqEntry.get()))
    except:
        cf.AWGAFreqEntry.delete(0,tk.END)
        cf.AWGAFreqEntry.insert(0, awga_freqval)
    if awga_freqval > 25000: # max freq is 25KHz
        awga_freqval = 25000
        cf.AWGAFreqEntry.delete(0,tk.END)
        cf.AWGAFreqEntry.insert(0, awga_freqval)
    if awga_freqval < 0: # Set negative frequency entry to 0
        awga_freqval = 10
        cf.AWGAFreqEntry.delete(0,tk.END)
        cf.AWGAFreqEntry.insert(0, awga_freqval)
    logging.debug('set_awga_freq() with {}'.format(awga_freqval))
#--- Duty Cycle für Rechtecksignal kontrollieren        
def set_awga_dutyc():
    global awga_dutycval
    
    try:
        awga_dutycval = float(eval(cf.AWGADutyCycleEntry.get()))/100
    except:
        cf.AWGADutyCycleEntry.delete(0,tk.END)
        cf.AWGADutyCycleEntry.insert(0, awga_dutycval)

    if awga_dutycval > 1: # max duty cycle is 100%
        awga_dutycval = 1
        cf.AWGADutyCycleEntry.delete(0,tk.END)
        cf.AWGADutyCycleEntry.insert(0, awga_dutycval*100)
    if awga_dutycval < 0: # min duty cycle is 0%
        awga_dutycval = 0
        cf.AWGADutyCycleEntry.delete(0,tk.END)
        cf.AWGADutyCycleEntry.insert(0, awga_dutycval)
    logging.debug('set_awga_dutyc() with {}'.format(awga_dutycval))
#--- Signalform aus UI lesen und als String setzen für späteren M1K-Befehl
def set_awga_shape():
    global awga_shape
    
    if cf.AWGAShape.get() == 0:
        awga_shape = 'dc'
    if cf.AWGAShape.get() == 1:
        awga_shape = 'sine'
    if cf.AWGAShape.get() == 2:
        awga_shape = 'triangle'
    if cf.AWGAShape.get() == 3:
        awga_shape = 'sawtooth'
    if cf.AWGAShape.get() == 4:
        awga_shape = 'square'
    if cf.AWGAShape.get() == 5:
        awga_shape = 'stairstep'
    logging.debug('set_awga_shape() with {}'.format(awga_shape))
#--- Alle Einstellungen aus UI lesen und setzen
def update_awga():
    global awga_minval, awga_maxval, awga_freqval, awga_dutycval
    logging.debug('update_awga()')
    set_awga_min()
    set_awga_max()
    set_awga_freq()
    set_awga_dutyc()
    set_awga_shape()    
    if cf.SampRate == 200000: # 200 kS/s bezieht sich nur auf ADC da durch Mux-Änderung
        AWGSampRate = 100000 # sonst nachfolgend falscher AWGAperiodvalue
    else:
        AWGSampRate = cf.SampRate
    if awga_freqval > 0.0:
        AWGAperiodvalue = AWGSampRate/awga_freqval
    else:
        AWGAperiodvalue = 0.0
    # Nur "Open termination", keine Auswahl 
    cf.devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
    cf.devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
      
    if awga_shape == 'dc':
        if cf.AWGAMode.get() == 0: # Source Voltage measure current mode
            cf.CHA.mode = smu.Mode.SVMI # Put CHA in SVMI mode
            cf.CHA.constant(awga_maxval)
        if cf.AWGAMode.get() == 1: # Source current measure voltage mode
            cf.CHA.mode = smu.Mode.SIMV # Put CHA in SIMV mode
            cf.CHA.constant(awga_maxval/1000)
        if cf.AWGAMode.get() == 2: # High impedance mode
            cf.CHA.mode = smu.Mode.HI_Z # Put CHA in Hi Z mode

    else:
        if cf.AWGAMode.get() == 0: # Source Voltage measure current mode
            cf.CHA.mode = smu.Mode.SVMI # Put CHA in SVMI mode
        if cf.AWGAMode.get() == 1: # Source current measure voltage mode
            cf.CHA.mode = smu.Mode.SIMV # Put CHA in SIMV mode
            awga_maxval = awga_maxval/1000
            awga_minval = awga_minval/1000
        if cf.AWGAMode.get() == 2: # High impedance mode
            cf.CHA.mode = smu.Mode.HI_Z # Put CHA in Hi Z mode
        else:
            MaxV = awga_maxval
            MinV = awga_minval
            # Delayvalue jeweils 0
            try:
                if awga_shape == 'sine':
                    cf.CHA.sine(MaxV, MinV, AWGAperiodvalue, 0)
                elif awga_shape == 'triangle':
                    cf.CHA.triangle(MaxV, MinV, AWGAperiodvalue, 0)
                elif awga_shape == 'sawtooth':
                    cf.CHA.sawtooth(MaxV, MinV, AWGAperiodvalue, 0)
                elif awga_shape == 'square':
                    cf.CHA.square(MaxV, MinV, AWGAperiodvalue, 0, awga_dutycval)
                elif awga_shape == 'stairstep':
                    cf.CHA.stairstep(MaxV, MinV, AWGAperiodvalue, 0)
            except:
                    pass


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen Arbitärgenerator CHB (Das Gleiche nochmals)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
awgb_minval = 0.0
awgb_maxval = 0.0
awgb_freqval = 0.0
awgb_dutycval = 50.0
awgb_shape = 'dc'
  
def set_awgb_min():
    global awgb_minval
    try:
        awgb_minval = float(eval(cf.AWGBMinEntry.get()))
    except:
        cf.AWGBMinEntry.delete(0,tk.END)
        cf.AWGBMinEntry.insert(0, awgb_minval)
    #
    if cf.AWGBMode.get() == 0: # Source Voltage measure current mode
        if awgb_minval > 5.00:
            awgb_minval = 5.00
            cf.AWGBMinEntry.delete(0,tk.END)
            cf.AWGBMinEntry.insert(0, awgb_minval)
        if awgb_minval < 0.00:
            awgb_minval = 0.00
            cf.AWGBMinEntry.delete(0,tk.END)
            cf.AWGBMinEntry.insert(0, awgb_minval)

    elif cf.AWGBMode.get() == 1: # Source current measure voltage mode
        if awgb_minval > 200.00:
            awgb_minval = 200.00
            cf.AWGBMinEntry.delete(0,tk.END)
            cf.AWGBMinEntry.insert(0, awgb_minval)
        if awgb_minval < -200.00:
            awgb_minval = -200.00
            cf.AWGBMinEntry.delete(0,tk.END)
            cf.AWGBMinEntry.insert(0, awgb_minval)
    logging.debug('set_awgb_min() with {}'.format(awgb_minval)) 

def set_awgb_max():
    global awgb_maxval
    try:
        awgb_maxval = float(eval(cf.AWGBMaxEntry.get()))
    except:
        cf.AWGBMaxEntry.delete(0,tk.END)
        cf.AWGBMaxEntry.insert(0, awgb_maxval)

    if cf.AWGBMode.get() == 0: # Source Voltage measure current mode
        if awgb_maxval > 5.00:
            awgb_maxval = 5.00
            cf.AWGBMaxEntry.delete(0,tk.END)
            cf.AWGBMaxEntry.insert(0, awgb_maxval)
        if awgb_maxval < 0.00:
            awgb_maxval = 0.00
            cf.AWGBMaxEntry.delete(0,tk.END)
            cf.AWGBMaxEntry.insert(0, awgb_maxval)
    
    if cf.AWGBMode.get() == 1: # Source current measure voltage mode
        if awgb_maxval > 200.00:
            awgb_maxval = 200.00
            cf.AWGBMaxEntry.delete(0,tk.END)
            cf.AWGBMaxEntry.insert(0, awgb_maxval)
        if awgb_maxval < -200.00:
            awgb_maxval = -200.00
            cf.AWGBMaxEntry.delete(0,tk.END)
            cf.AWGBMaxEntry.insert(0, awgb_maxval)
    logging.debug('set_awgb_max() with {}'.format(awgb_maxval))

def set_awgb_freq():
    global awgb_freqval
    try:
        awgb_freqval = float(eval(cf.AWGBFreqEntry.get()))
    except:
        cf.AWGBFreqEntry.delete(0,tk.END)
        cf.AWGBFreqEntry.insert(0, awgb_freqval)

    if awgb_freqval > 25000: # max freq is 25KHz
        awgb_freqval = 25000
        cf.AWGBFreqEntry.delete(0,tk.END)
        cf.AWGBFreqEntry.insert(0, awgb_freqval)
    if awgb_freqval < 0: # Set negative frequency entry to 0
        awgb_freqval = 10
        cf.AWGBFreqEntry.delete(0,tk.END)
        cf.AWGBFreqEntry.insert(0, awgb_freqval)
    logging.debug('set_awgb_freq() with {}'.format(awgb_freqval))
    
def set_awgb_dutyc():
    global awgb_dutycval
    try:
        awgb_dutycval = float(eval(cf.AWGBDutyCycleEntry.get()))/100
    except:
        cf.AWGBDutyCycleEntry.delete(0,tk.END)
        cf.AWGBDutyCycleEntry.insert(0, awgb_dutycval)

    if awgb_dutycval > 1: # max duty cycle is 100%
        awgb_dutycval = 1
        cf.AWGBDutyCycleEntry.delete(0,tk.END)
        cf.AWGBDutyCycleEntry.insert(0, awgb_dutycval*100)
    if awgb_dutycval < 0: # min duty cycle is 0%
        awgb_dutycval = 0
        cf.AWGBDutyCycleEntry.delete(0,tk.END)
        cf.AWGBDutyCycleEntry.insert(0, awgb_dutycval)
    logging.debug('set_awgb_dutyc() with {}'.format(awgb_dutycval))
    
def set_awgb_shape():
    global awgb_shape
    if cf.AWGBShape.get() == 0:
        awgb_shape = 'dc'
    if cf.AWGBShape.get() == 1:
        awgb_shape = 'sine'
    if cf.AWGBShape.get() == 2:
        awgb_shape = 'triangle'
    if cf.AWGBShape.get() == 3:
        awgb_shape = 'sawtooth'
    if cf.AWGBShape.get() == 4:
        awgb_shape = 'square'
    if cf.AWGBShape.get() == 5:
        awgb_shape = 'stairstep'
    logging.debug('set_awgb_shape() with {}'.format(awgb_shape))
    
def update_awgb():
    logging.debug('update_awgb()')
    global awgb_minval, awgb_maxval, awgb_freqval, awgb_dutycval
    global CHA, CHB, amp2lab, off2lab
    logging.debug('update_awga()')
    set_awgb_min()
    set_awgb_max()
    set_awgb_freq()
    set_awgb_dutyc()
    set_awgb_shape()
    if cf.SampRate == 200000: # 200 kS/s bezieht sich nur auf ADC da durch Mux-Änderung
        AWGSampRate = 100000 # sonst nachfolgend falscher AWGAperiodvalue
    else:
        AWGSampRate = cf.SampRate
    if awgb_freqval > 0.0:
        AWGBperiodvalue = AWGSampRate/awgb_freqval
    else:
        AWGBperiodvalue = 0.0     
    # Open termination
    cf.devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set 2.5 V switch to open
    cf.devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set GND switch to open
       
    if awgb_shape == 'dc':
        if cf.AWGBMode.get() == 0: # Source Voltage measure current mode
            cf.CHB.mode = smu.Mode.SVMI # Put CHB in SVMI mode
            cf.CHB.constant(awgb_maxval)
        if cf.AWGBMode.get() == 1: # Source current measure Voltage mode
            cf.CHB.mode = smu.Mode.SIMV # Put CHB in SIMV mode
            cf.CHB.constant(awgb_maxval/1000)
        if cf.AWGBMode.get() == 2: # Hi impedance mode:
            cf.CHB.mode = smu.Mode.HI_Z # Put CHB in Hi Z mode
    else:
        if cf.AWGBMode.get() == 0: # Source Voltage measure current mode
            cf.CHB.mode = smu.Mode.SVMI # Put CHB in SVMI mode
        if cf.AWGBMode.get() == 1: # Source current measure Voltage mode
            cf.CHB.mode = smu.Mode.SIMV # Put CHB in SIMV mode
            awgb_maxval = awgb_maxval/1000
            awgb_minval = awgb_minval/1000
        if cf.AWGBMode.get() == 2: # Hi impedance mode
            cf.CHB.mode = smu.Mode.HI_Z # Put CHB in Hi Z mode
        else:
            MaxV = awgb_maxval
            MinV = awgb_minval
            try: # keep going even if low level library returns an error
                if awgb_shape == 'sine':
                    cf.CHB.sine(MaxV, MinV, AWGBperiodvalue, 0)
                elif awgb_shape == 'triangle':
                    cf.CHB.triangle(MaxV, MinV, AWGBperiodvalue, 0)
                elif awgb_shape == 'sawtooth':
                    cf.CHB.sawtooth(MaxV, MinV, AWGBperiodvalue, 0)
                elif awgb_shape == 'square':
                    cf.CHB.square(MaxV, MinV, AWGBperiodvalue, 0, awgb_dutycval)
                elif awgb_shape == 'stairstep':
                    cf.CHB.stairstep(MaxV, MinV, AWGBperiodvalue, 0)
            except:
                pass
