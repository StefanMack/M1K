#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 30.8.20
"""

import time
import config as cf
import pysmu as smu
import logging

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen und Einstellungen beide Arbitärgeneratoren
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#--- Auslesen der in der UI gewählten Signalform
def ReMakeAWGwaves(): 
#    global AWGAShapeLabel, AWGBShapeLabel
#
#    if cf.AWGAShape.get()==0:
#        AWGAShapeLabel.config(text = "DC") # change displayed value
#    elif cf.AWGAShape.get()==2:
#        AWGAShapeLabel.config(text = "Triangle") # change displayed value
#    elif cf.AWGAShape.get()==4:
#        AWGAShapeLabel.config(text = "Square") # change displayed value
#    elif cf.AWGAShape.get()==3:
#        AWGAShapeLabel.config(text = "Saw Tooth") # change displayed value
#    elif cf.AWGAShape.get()==5:
#        AWGAShapeLabel.config(text = "Starestep") # change displayed value
#
#    if cf.AWGBShape.get()==0:
#        AWGBShapeLabel.config(text = "DC") # change displayed value
#    elif cf.AWGBShape.get()==2:
#        AWGBShapeLabel.config(text = "Triangle") # change displayed value
#    elif cf.AWGBShape.get()==4:
#        AWGBShapeLabel.config(text = "Square") # change displayed value
#    elif cf.AWGBShape.get()==3:
#        AWGBShapeLabel.config(text = "Saw Tooth") # change displayed value
#    elif cf.AWGBShape.get()==5:
#        AWGBShapeLabel.config(text = "Starestep") # change displayed value
    UpdateAwgCont(0)
    time.sleep(0.05)

def UpdateAwgCont(event):
    logging.info('UpdateAwgCont()')
    # if running and in continuous streaming mode temp stop, flush buffer and restart to change AWG settings
    if (cf.RUNstatus.get() == 1):
        if cf.session.continuous:
            cf.session.end()
            BAWGEnab() # set-up new AWG settings
            time.sleep(0.01) # wait awhile here for some reason
            logging.info('vor cf.session.start(0)')
            cf.session.start(0)

def UpdateAwgContRet():
    ReMakeAWGwaves()
    
def BAWGEnab():
    logging.info('BAWGEnab()')
    BAWGAMin()
    BAWGAMax()
    BAWGAFreq()
    BAWGADutyCycle()
    BAWGAShape()
    BAWGBMin()
    BAWGBMax()
    BAWGBFreq()
    BAWGBDutyCycle()
    BAWGBShape()
    UpdateAWGA()
    UpdateAWGB()
    
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen Arbitärgenerator CHA
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
AWGAMinvalue = 0.0
AWGAMaxvalue = 0.0
AWGAFreqvalue = 0.0
AWGAWave = 'dc' # Initialisierung Singalform

#--- Min-Wert aus UI kontrollieren
def BAWGAMin():
    global AWGAMinvalue
    try:
        AWGAMinvalue = float(eval(cf.AWGAMinEntry.get()))
        logging.info('BAWGAMin() with {}'.format(AWGAMinvalue)) 
    except:
        logging.info('Exeption BAWGAMin()')
        cf.AWGAMinEntry.delete(0,"tk.END")
        cf.AWGAMinEntry.insert(0, AWGAMinvalue)

    if cf.AWGAMode.get() == 0: # Source Voltage measure current mode
        if AWGAMinvalue > 5.00:
            AWGAMinvalue = 5.00
            cf.AWGAMinEntry.delete(0,"tk.END")
            cf.AWGAMinEntry.insert(0, AWGAMinvalue)
        if AWGAMinvalue < 0.00:
            AWGAMinvalue = 0.00
            cf.AWGAMinEntry.delete(0,"tk.END")
            cf.AWGAMinEntry.insert(0, AWGAMinvalue)

    if cf.AWGAMode.get() == 1: # Source current measure voltage mode
        if AWGAMinvalue > 200.00:
            AWGAMinvalue = 200.00
            cf.AWGAMinEntry.delete(0,"tk.END")
            cf.AWGAMinEntry.insert(0, AWGAMinvalue)
        if AWGAMinvalue < -200.00:
            AWGAMinvalue = -200.00
            cf.AWGAMinEntry.delete(0,"tk.END")
            cf.AWGAMinEntry.insert(0, AWGAMinvalue)
#--- Max-Wert aus UI kontrollieren
def BAWGAMax():
    global AWGAMaxvalue

    try:
        AWGAMaxvalue = float(eval(cf.AWGAMaxEntry.get()))
        logging.info('BAWGAMax() with {}'.format(AWGAMaxvalue))
    except:
        logging.info('Exeption BAWGAMax()')
        cf.AWGAMaxEntry.delete(0,"tk.END")
        cf.AWGAMaxEntry.insert(0, AWGAMaxvalue)

    if cf.AWGAMode.get() == 0: # Source Voltage measure current mode
        if AWGAMaxvalue > 5.00:
            AWGAMaxvalue = 5.00
            cf.AWGAMaxEntry.delete(0,"tk.END")
            cf.AWGAMaxEntry.insert(0, AWGAMaxvalue)
        if AWGAMaxvalue < 0.00:
            AWGAMaxvalue = 0.00
            cf.AWGAMaxEntry.delete(0,"tk.END")
            cf.AWGAMaxEntry.insert(0, AWGAMaxvalue)
        
    if cf.AWGAMode.get() == 1: # Source current measure voltage mode
        if AWGAMaxvalue > 200.00:
            AWGAMaxvalue = 200.00
            cf.AWGAMaxEntry.delete(0,"tk.END")
            cf.AWGAMaxEntry.insert(0, AWGAMaxvalue)
        if AWGAMaxvalue < -200.00:
            AWGAMaxvalue = -200.00
            cf.AWGAMaxEntry.delete(0,"tk.END")
            cf.AWGAMaxEntry.insert(0, AWGAMaxvalue)
#--- Frequenz-Wert aus UI kontrollieren
def BAWGAFreq():
    global AWGAFreqvalue
    
    try:
        AWGAFreqvalue = float(eval(cf.AWGAFreqEntry.get()))
        logging.info('BAWGAFreq() with {}'.format(AWGAFreqvalue))
    except:
        cf.AWGAFreqEntry.delete(0,"tk.END")
        cf.AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if cf.AWG_2X == 1:
        if AWGAFreqvalue > 50000: # max freq is 50KHz
            AWGAFreqvalue = 50000
            cf.AWGAFreqEntry.delete(0,"tk.END")
            cf.AWGAFreqEntry.insert(0, AWGAFreqvalue)
    else:
        if AWGAFreqvalue > 25000: # max freq is 25KHz
            AWGAFreqvalue = 25000
            cf.AWGAFreqEntry.delete(0,"tk.END")
            cf.AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if AWGAFreqvalue < 0: # Set negative frequency entry to 0
        AWGAFreqvalue = 10
        cf.AWGAFreqEntry.delete(0,"tk.END")
        cf.AWGAFreqEntry.insert(0, AWGAFreqvalue)
#--- Duty Cycle für Rechtecksignal kontrollieren        
def BAWGADutyCycle():
    global AWGADutyCyclevalue
    
    try:
        AWGADutyCyclevalue = float(eval(cf.AWGADutyCycleEntry.get()))/100
        logging.info('BAWGADutyCycle() with {}'.format(AWGADutyCyclevalue))
    except:
        cf.AWGADutyCycleEntry.delete(0,"tk.END")
        cf.AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue)

    if AWGADutyCyclevalue > 1: # max duty cycle is 100%
        AWGADutyCyclevalue = 1
        cf.AWGADutyCycleEntry.delete(0,"tk.END")
        cf.AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue*100)
    if AWGADutyCyclevalue < 0: # min duty cycle is 0%
        AWGADutyCyclevalue = 0
        cf.AWGADutyCycleEntry.delete(0,"tk.END")
        cf.AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue)
#--- Signalform aus UI lesen und als String setzen für späteren M1K-Befehl
def BAWGAShape():
    global AWGAWave
    
    if cf.AWGAShape.get() == 0:
        AWGAWave = 'dc'
    if cf.AWGAShape.get() == 1:
        AWGAWave = 'sine'
    if cf.AWGAShape.get() == 2:
        AWGAWave = 'triangle'
    if cf.AWGAShape.get() == 3:
        AWGAWave = 'sawtooth'
    if cf.AWGAShape.get() == 4:
        AWGAWave = 'square'
    if cf.AWGAShape.get() == 5:
        AWGAWave = 'stairstep'
    logging.info('BAWGAShape() with {}'.format(AWGAWave))
#--- Alle Einstellungen aus UI lesen und setzen
def UpdateAWGA():
    global AWGAMinvalue, AWGAMaxvalue, AWGAFreqvalue, AWGADutyCyclevalue
    logging.info('UpdateAWGA()')
    BAWGAMin()
    BAWGAMax()
    BAWGAFreq()
    BAWGADutyCycle()
    BAWGAShape()    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = cf.AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    # Nur "Open termination", keine Auswahl 
    cf.devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
    cf.devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
      
    if AWGAWave == 'dc':
        if cf.AWGAMode.get() == 0: # Source Voltage measure current mode
            cf.CHA.mode = smu.Mode.SVMI # Put CHA in SVMI mode
            cf.CHA.constant(AWGAMaxvalue)
        if cf.AWGAMode.get() == 1: # Source current measure voltage mode
            cf.CHA.mode = smu.Mode.SIMV # Put CHA in SIMV mode
            cf.CHA.constant(AWGAMaxvalue/1000)
        if cf.AWGAMode.get() == 2: # High impedance mode
            cf.CHA.mode = smu.Mode.HI_Z # Put CHA in Hi Z mode

    else:
        if cf.AWGAMode.get() == 0: # Source Voltage measure current mode
            cf.CHA.mode = smu.Mode.SVMI # Put CHA in SVMI mode
        if cf.AWGAMode.get() == 1: # Source current measure voltage mode
            cf.CHA.mode = smu.Mode.SIMV # Put CHA in SIMV mode
            AWGAMaxvalue = AWGAMaxvalue/1000
            AWGAMinvalue = AWGAMinvalue/1000
        if cf.AWGAMode.get() == 2: # High impedance mode
            cf.CHA.mode = smu.Mode.HI_Z # Put CHA in Hi Z mode
        else:
            MaxV = AWGAMaxvalue
            MinV = AWGAMinvalue
            # Delayvalue jeweils 0
            try:
                if AWGAWave == 'sine':
                    cf.CHA.sine(MaxV, MinV, AWGAperiodvalue, 0)
                elif AWGAWave == 'triangle':
                    cf.CHA.triangle(MaxV, MinV, AWGAperiodvalue, 0)
                elif AWGAWave == 'sawtooth':
                    cf.CHA.sawtooth(MaxV, MinV, AWGAperiodvalue, 0)
                elif AWGAWave == 'square':
                    cf.CHA.square(MaxV, MinV, AWGAperiodvalue, 0, AWGADutyCyclevalue)
                elif AWGAWave == 'stairstep':
                    cf.CHA.stairstep(MaxV, MinV, AWGAperiodvalue, 0)
            except:
                    pass


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen Arbitärgenerator CHB (Das Gleiche nochmals)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
AWGBMinvalue = 0.0
AWGBMaxvalue = 0.0
AWGBFreqvalue = 0.0
AWGBWave = 'dc'
  
def BAWGBMin():
    global AWGBMinvalue
    try:
        AWGBMinvalue = float(eval(cf.AWGBMinEntry.get()))
        logging.info('BAWGAMin() with {}'.format(AWGBMinvalue)) 
    except:
        cf.AWGBMinEntry.delete(0,"tk.END")
        cf.AWGBMinEntry.insert(0, AWGBMinvalue)
    #
    if cf.AWGBMode.get() == 0: # Source Voltage measure current mode
        if AWGBMinvalue > 5.00:
            AWGBMinvalue = 5.00
            cf.AWGBMinEntry.delete(0,"tk.END")
            cf.AWGBMinEntry.insert(0, AWGBMinvalue)
        if AWGBMinvalue < 0.00:
            AWGBMinvalue = 0.00
            cf.AWGBMinEntry.delete(0,"tk.END")
            cf.AWGBMinEntry.insert(0, AWGBMinvalue)

    elif cf.AWGBMode.get() == 1: # Source current measure voltage mode
        if AWGBMinvalue > 200.00:
            AWGBMinvalue = 200.00
            cf.AWGBMinEntry.delete(0,"tk.END")
            cf.AWGBMinEntry.insert(0, AWGBMinvalue)
        if AWGBMinvalue < -200.00:
            AWGBMinvalue = -200.00
            cf.AWGBMinEntry.delete(0,"tk.END")
            cf.AWGBMinEntry.insert(0, AWGBMinvalue)

def BAWGBMax():
    global AWGBMaxvalue
    try:
        AWGBMaxvalue = float(eval(cf.AWGBMaxEntry.get()))
    except:
        cf.AWGBMaxEntry.delete(0,"tk.END")
        cf.AWGBMaxEntry.insert(0, AWGBMaxvalue)

    if cf.AWGBMode.get() == 0: # Source Voltage measure current mode
        if AWGBMaxvalue > 5.00:
            AWGBMaxvalue = 5.00
            cf.AWGBMaxEntry.delete(0,"tk.END")
            cf.AWGBMaxEntry.insert(0, AWGBMaxvalue)
        if AWGBMaxvalue < 0.00:
            AWGBMaxvalue = 0.00
            cf.AWGBMaxEntry.delete(0,"tk.END")
            cf.AWGBMaxEntry.insert(0, AWGBMaxvalue)
    
    if cf.AWGBMode.get() == 1: # Source current measure voltage mode
        if AWGBMaxvalue > 200.00:
            AWGBMaxvalue = 200.00
            cf.AWGBMaxEntry.delete(0,"tk.END")
            cf.AWGBMaxEntry.insert(0, AWGBMaxvalue)
        if AWGBMaxvalue < -200.00:
            AWGBMaxvalue = -200.00
            cf.AWGBMaxEntry.delete(0,"tk.END")
            cf.AWGBMaxEntry.insert(0, AWGBMaxvalue)

def BAWGBFreq():
    global AWGBFreqvalue
    try:
        AWGBFreqvalue = float(eval(cf.AWGBFreqEntry.get()))
    except:
        cf.AWGBFreqEntry.delete(0,"tk.END")
        cf.AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if cf.AWG_2X == 2:
        if AWGBFreqvalue > 50000: # max freq is 50KHz
            AWGBFreqvalue = 50000
            cf.AWGBFreqEntry.delete(0,"tk.END")
            cf.AWGBFreqEntry.insert(0, AWGBFreqvalue)
    else:
        if AWGBFreqvalue > 25000: # max freq is 25KHz
            AWGBFreqvalue = 25000
            cf.AWGBFreqEntry.delete(0,"tk.END")
            cf.AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if AWGBFreqvalue < 0: # Set negative frequency entry to 0
        AWGBFreqvalue = 10
        cf.AWGBFreqEntry.delete(0,"tk.END")
        cf.AWGBFreqEntry.insert(0, AWGBFreqvalue)
    
def BAWGBDutyCycle():
    global AWGBDutyCyclevalue
    try:
        AWGBDutyCyclevalue = float(eval(cf.AWGBDutyCycleEntry.get()))/100
    except:
        cf.AWGBDutyCycleEntry.delete(0,"tk.END")
        cf.AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)

    if AWGBDutyCyclevalue > 1: # max duty cycle is 100%
        AWGBDutyCyclevalue = 1
        cf.AWGBDutyCycleEntry.delete(0,"tk.END")
        cf.AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue*100)
    if AWGBDutyCyclevalue < 0: # min duty cycle is 0%
        AWGBDutyCyclevalue = 0
        cf.AWGBDutyCycleEntry.delete(0,"tk.END")
        cf.AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)
    
def BAWGBShape():
    global AWGBWave
    if cf.AWGBShape.get() == 0:
        AWGBWave = 'dc'
    if cf.AWGBShape.get() == 1:
        AWGBWave = 'sine'
    if cf.AWGBShape.get() == 2:
        AWGBWave = 'triangle'
    if cf.AWGBShape.get() == 3:
        AWGBWave = 'sawtooth'
    if cf.AWGBShape.get() == 4:
        AWGBWave = 'square'
    if cf.AWGBShape.get() == 5:
        AWGBWave = 'stairstep' 
    
def UpdateAWGB():
    global AWGBMinvalue, AWGBMaxvalue, AWGBFreqvalue, AWGBDutyCyclevalue
    global CHA, CHB, amp2lab, off2lab
    logging.info('UpdateAWGA()')
    BAWGBMin()
    BAWGBMax()
    BAWGBFreq()
    BAWGBDutyCycle()
    BAWGBShape()
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = cf.AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0     
    # Open termination
    cf.devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set 2.5 V switch to open
    cf.devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set GND switch to open
       
    if AWGBWave == 'dc':
        if cf.AWGBMode.get() == 0: # Source Voltage measure current mode
            cf.CHB.mode = smu.Mode.SVMI # Put CHB in SVMI mode
            cf.CHB.constantAWGBMaxvalue
        if cf.AWGBMode.get() == 1: # Source current measure Voltage mode
            cf.CHB.mode = smu.Mode.SIMV # Put CHB in SIMV mode
            cf.CHB.constant(AWGBMaxvalue/1000)
        if cf.AWGBMode.get() == 2: # Hi impedance mode:
            cf.CHB.mode = smu.Mode.HI_Z # Put CHB in Hi Z mode
    else:
        if cf.AWGBMode.get() == 0: # Source Voltage measure current mode
            cf.CHB.mode = smu.Mode.SVMI # Put CHB in SVMI mode
        if cf.AWGBMode.get() == 1: # Source current measure Voltage mode
            cf.CHB.mode = smu.Mode.SIMV # Put CHB in SIMV mode
            AWGBMaxvalue = AWGBMaxvalue/1000
            AWGBMinvalue = AWGBMinvalue/1000
        if cf.AWGBMode.get() == 2: # Hi impedance mode
            cf.CHB.mode = smu.Mode.HI_Z # Put CHB in Hi Z mode
        else:
            MaxV = AWGBMaxvalue
            MinV = AWGBMinvalue
            try: # keep going even if low level library returns an error
                if AWGBWave == 'sine':
                    cf.CHB.sine(MaxV, MinV, AWGBperiodvalue, 0)
                elif AWGBWave == 'triangle':
                    cf.CHB.triangle(MaxV, MinV, AWGBperiodvalue, 0)
                elif AWGBWave == 'sawtooth':
                    cf.CHB.sawtooth(MaxV, MinV, AWGBperiodvalue, 0)
                elif AWGBWave == 'square':
                    cf.CHB.square(MaxV, MinV, AWGBperiodvalue, 0, AWGBDutyCyclevalue)
                elif AWGBWave == 'stairstep':
                    cf.CHB.stairstep(MaxV, MinV, AWGBperiodvalue, 0)
            except:
                pass
