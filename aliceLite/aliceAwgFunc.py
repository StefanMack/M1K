#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 30.8.20
"""

import time
import numpy as np
#import tkinter as tk
import config as cf
#import pysmu as smu

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Arbiträrgenerator Messeinstellungs- und Initialisierungswerte
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
AWGAMinvalue = 0.0
AWGAMaxvalue = 0.0
AWGAFreqvalue = 0.0
AWGAPhasevalue = 0
AWGAdelayvalue = 0
AWGADutyCyclevalue = 50
AWGAWave = 'dc'
AWGBMinvalue = 0.0
AWGBMaxvalue = 0.0
AWGBFreqvalue = 0.0
AWGBPhasevalue = 0
AWGBdelayvalue = 0
AWGBDutyCyclevalue = 50
AWGBWave = 'dc'
ModFreq = 10 # Aus usrsprünglichen Code, keine Ahnung wozu gut

AWGAwaveform = []
AWGA2X = [] # array for odd numbers samples when in 2x sample rate
AWGBwaveform = []
AWGB2X = [] # array for odd numbers samples when in 2x sample rate


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter Instanzierungen
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Arbiträrgenerator

# ADC-Mux-Modus
Last_ADC_Mux_Mode = 0
v1_adc_conf = 0x20F1 # ADC Mux defaults
i1_adc_conf = 0x20F7
v2_adc_conf = 0x20F7
i2_adc_conf = 0x20F1

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen und Einstellungen Arbitärgenerator allgemein
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Re Make the current selected AWG waveform buffers 
def ReMakeAWGwaves(): # re make awg waveforms ib case something changed
    global AWGAShape, AWGBShape, AWGAShapeLabel, AWGBShapeLabel

    if AWGAShape.get()==9:
        AWGAMakeImpulse()
        AWGAShapeLabel.config(text = "Impulse") # change displayed value
    elif AWGAShape.get()==11:
        AWGAMakeTrapazoid()
        AWGAShapeLabel.config(text = "Trapazoid") # change displayed value
    elif AWGAShape.get()==16:
        AWGAMakeRamp()
        AWGAShapeLabel.config(text = "Ramp") # change displayed value
    elif AWGAShape.get()==12:
        AWGAMakeUpDownRamp()
        AWGAShapeLabel.config(text = "Up Down Ramp") # change displayed value
    elif AWGAShape.get()==20:
        AWGAMakePulse()
        AWGAShapeLabel.config(text = "Pulse") # change displayed value
    elif AWGAShape.get()==7:
        AWGAMakeUUNoise()
        AWGAShapeLabel.config(text = "UU Noise") # change displayed value
    elif AWGAShape.get()==8:
        AWGAMakeUGNoise()
        AWGAShapeLabel.config(text = "UG Noise") # change displayed value
    elif AWGAShape.get()==0:
        AWGAShapeLabel.config(text = "DC") # change displayed value
    elif AWGAShape.get()==2:
        AWGAShapeLabel.config(text = "Triangle") # change displayed value
    elif AWGAShape.get()==4:
        AWGAShapeLabel.config(text = "Square") # change displayed value
    elif AWGAShape.get()==3:
        AWGAShapeLabel.config(text = "Saw Tooth") # change displayed value
    elif AWGAShape.get()==5:
        AWGAShapeLabel.config(text = "Starestep") # change displayed value
    else:
        AWGAShapeLabel.config(text = "Other Shape") # change displayed value
    if AWGBShape.get()==9:
        AWGBMakeImpulse()
        AWGBShapeLabel.config(text = "Impulse") # change displayed value
    elif AWGBShape.get()==11:
        AWGBMakeTrapazoid()
        AWGBShapeLabel.config(text = "Trapazoid") # change displayed value
    elif AWGBShape.get()==16:
        AWGBMakeRamp()
        AWGBShapeLabel.config(text = "Ramp") # change displayed value
    elif AWGBShape.get()==12:
        AWGBMakeUpDownRamp()
        AWGBShapeLabel.config(text = "Up Doen Ramp") # change displayed value
    elif AWGBShape.get()==20:
        AWGBMakePulse()
        AWGBShapeLabel.config(text = "Pulse") # change displayed value
    elif AWGBShape.get()==7:
        AWGBMakeUUNoise()
        AWGBShapeLabel.config(text = "UU Noise") # change displayed value
    elif AWGBShape.get()==8:
        AWGBMakeUGNoise()
        AWGBShapeLabel.config(text = "UG Noise") # change displayed value
    elif AWGBShape.get()==0:
        AWGBShapeLabel.config(text = "DC") # change displayed value
    elif AWGBShape.get()==2:
        AWGBShapeLabel.config(text = "Triangle") # change displayed value
    elif AWGBShape.get()==4:
        AWGBShapeLabel.config(text = "Square") # change displayed value
    elif AWGBShape.get()==3:
        AWGBShapeLabel.config(text = "Saw Tooth") # change displayed value
    elif AWGBShape.get()==5:
        AWGBShapeLabel.config(text = "Starestep") # change displayed value
    else:
        AWGBShapeLabel.config(text = "Other Shape") # change displayed value
    UpdateAwgCont()
    time.sleep(0.05)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen und Einstellungen Arbitärgenerator CHA
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def BAWGAMin():
    global AWGAMinvalue
    # 0 = Min/Max mode, 1 = Amp/Offset
    
    try:
        AWGAMinvalue = float(eval(cf.AWGAMinEntry.get()))
    except:
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

def BAWGAMax():
    global AWGAMaxvalue
    
    try:
        AWGAMaxvalue = float(eval(cf.AWGAMaxEntry.get()))
    except:
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

def BAWGAFreq():
    global AWGAFreqvalue
    try:
        AWGAFreqvalue = float(eval(cf.AWGAFreqEntry.get()))
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

def BAWGADutyCycle():
    global AWGADutyCycleEntry, AWGADutyCyclevalue

    try:
        AWGADutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))/100
    except:
        AWGADutyCycleEntry.delete(0,"tk.END")
        AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue)

    if AWGADutyCyclevalue > 1: # max duty cycle is 100%
        AWGADutyCyclevalue = 1
        AWGADutyCycleEntry.delete(0,"tk.END")
        AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue*100)
    if AWGADutyCyclevalue < 0: # min duty cycle is 0%
        AWGADutyCyclevalue = 0
        AWGADutyCycleEntry.delete(0,"tk.END")
        AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue)

def BAWGAShape():
    global AWGAShape, AWGAWave, phasealab, duty1lab

    if AWGAShape.get() == 0:
        AWGAWave = 'dc'
        duty1lab.config(text="%")
    if AWGAShape.get() == 1:
        AWGAWave = 'sine'
        duty1lab.config(text="%")
    if AWGAShape.get() == 2:
        AWGAWave = 'triangle'
        duty1lab.config(text="%")
    if AWGAShape.get() == 3:
        AWGAWave = 'sawtooth'
        duty1lab.config(text="%")
    if AWGAShape.get() == 4:
        AWGAWave = 'square'
        duty1lab.config(text="%")
    if AWGAShape.get() == 5:
        AWGAWave = 'stairstep'
        duty1lab.config(text="%")
    if AWGAShape.get() > 5:
        AWGAWave = 'arbitrary'
    
# Split 2X sampled AWGAwaveform array into odd and even sample arrays
def SplitAWGAwaveform():
    global AWGA2X, AWGAwaveform
    
    if cf.AWG_2X == 1:
        Tempwaveform = []
        AWGA2X = []
        AWGA2X = AWGAwaveform[1::2] # odd numbered samples
        Tempwaveform = AWGAwaveform[::2] # even numbered samples Tempwaveform
        AWGAwaveform = Tempwaveform


def AWGAMakeTrapazoid():
    global AWGAwaveform, AWGAMinvalue, AWGAMaxvalue, AWGALength, phasealab, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGADutyCyclevalue, AWGAPhasevalue # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X   
    BAWGAMin(0)
    BAWGAMax(0)
    BAWGAFreq(0)
    BAWGADutyCycle(0)
    
    if AWGAFreqvalue > 0.0:
        if cf.AWG_2X == 1:
            AWGAperiodvalue = int((cf.BaseSampleRate*2)/AWGAFreqvalue)
            SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = cf.BaseSampleRate/AWGAFreqvalue
            SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0

    MaxV = AWGAMaxvalue
    MinV = AWGAMinvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue * SamplesPermS) # convert mS to samples
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGAperiodvalue - PulseWidth) - SlopeValue
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepValue = (MaxV - MinV) / SlopeValue
    SampleValue = MinV
    for i in range(SlopeValue):
        AWGAwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue + StepValue
    for i in range(PulseWidth):
        AWGAwaveform.apptk.END(MaxV)
    for i in range(SlopeValue):
        AWGAwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue - StepValue
    for i in range(Remainder):
        AWGAwaveform.apptk.END(MinV)
    SplitAWGAwaveform()
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    duty1lab.config(text="%")
    phasealab.config(text = "Rise Time")
    UpdateAwgCont()

def AWGAMakePulse():
    global AWGAwaveform, AWGAMinvalue, AWGAMaxvalue, AWGALength, phasealab, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGADutyCyclevalue, AWGAPhasevalue # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X
    

    BAWGAMin(0)
    BAWGAMax(0)
    BAWGAFreq(0)

    try:
        AWGADutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))
    except:
        AWGADutyCycleEntry.delete(0,"tk.END")
        AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue)
        
    if AWGAFreqvalue > 0.0:
        if cf.AWG_2X == 1:
            AWGAperiodvalue = int((cf.BaseSampleRate*2)/AWGAFreqvalue)
            SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = cf.BaseSampleRate/AWGAFreqvalue
            SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0

    MaxV = AWGAMaxvalue
    MinV = AWGAMinvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue * SamplesPermS) # convert mS to samples
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGADutyCyclevalue * SamplesPermS) # convert mS to samples
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGAperiodvalue - PulseWidth) - SlopeValue
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepValue = (MaxV - MinV) / SlopeValue
    SampleValue = MinV
    for i in range(SlopeValue):
        AWGAwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue + StepValue
    for i in range(PulseWidth):
        AWGAwaveform.apptk.END(MaxV)
    for i in range(SlopeValue):
        AWGAwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue - StepValue
    for i in range(Remainder):
        AWGAwaveform.apptk.END(MinV)
    SplitAWGAwaveform()
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    duty1lab.config(text="Width mS")
    phasealab.config(text = "Rise Time")
    UpdateAwgCont()

def AWGAMakeRamp():
    global AWGAwaveform, AWGAMinvalue, AWGAMaxvalue, AWGALength, phasealab, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGADutyCyclevalue, AWGAPhasevalue # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X
    

    BAWGAMin(0)
    BAWGAMax(0)
    BAWGAFreq(0)
    BAWGADutyCycle(0)
    
    if AWGAFreqvalue > 0.0:
        if cf.AWG_2X == 1:
            AWGAperiodvalue = int((cf.BaseSampleRate*2)/AWGAFreqvalue)
            SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = cf.BaseSampleRate/AWGAFreqvalue
            SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0

    MaxV = AWGAMaxvalue
    MinV = AWGAMinvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue * SamplesPermS) # convert mS to samples
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGAperiodvalue - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepValue = (MaxV - MinV) / SlopeValue
    SampleValue = MinV
    for i in range(SlopeValue):
        AWGAwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue + StepValue
    for i in range(PulseWidth):
        AWGAwaveform.apptk.END(MaxV)
    for i in range(Remainder):
        AWGAwaveform.apptk.END(MinV)
    SplitAWGAwaveform()
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    duty1lab.config(text="%")
    phasealab.config(text = "Slope Time")
    UpdateAwgCont()

def AWGAMakeUpDownRamp():
    global AWGAwaveform, AWGAMinvalue, AWGAMaxvalue, AWGALength, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGADutyCyclevalue, AWGAPhasevalue # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X
    

    BAWGAMin(0)
    BAWGAMax(0)
    BAWGAFreq(0)
    BAWGADutyCycle(0)
    
    if AWGAFreqvalue > 0.0:
        if cf.AWG_2X == 1:
            AWGAperiodvalue = int((cf.BaseSampleRate*2)/AWGAFreqvalue)
            #SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = cf.AWGSAMPLErate/AWGAFreqvalue
            #SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0

    MaxV = AWGAMaxvalue
    MinV = AWGAMinvalue

    AWGAwaveform = []
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGAperiodvalue - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    UpStepValue = (MaxV - MinV) / PulseWidth
    DownStepValue = (MaxV - MinV) / Remainder
    SampleValue = MinV
    for i in range(PulseWidth):
        AWGAwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue + UpStepValue
    for i in range(Remainder):
        AWGAwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue - DownStepValue
    AWGAwaveform = np.roll(AWGAwaveform, int(AWGAdelayvalue))
    SplitAWGAwaveform()
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    duty1lab.config(text = "Symmetry")
    UpdateAwgCont()

def AWGAMakeImpulse():
    global AWGAwaveform, AWGAMinvalue, AWGAMaxvalue, AWGALength
    global AWGAFreqvalue, AWGAperiodvalue, AWGADutyCyclevalue
    global AWGA2X
    BAWGAMin(0)
    BAWGAMax(0)
    BAWGAFreq(0)
    BAWGADutyCycle(0)
    
    if AWGAFreqvalue > 0.0:
        if cf.AWG_2X == 1:
            AWGAperiodvalue = int((cf.BaseSampleRate*2)/AWGAFreqvalue)
            #SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = cf.BaseSampleRate/AWGAFreqvalue
            #SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0
    MaxV = AWGAMaxvalue
    MinV = AWGAMinvalue
    AWGAwaveform = []
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue / 2.0)

    for i in range(PulseWidth):
        AWGAwaveform.append((MinV+MaxV)/2.0)
    for i in range(PulseWidth):
        AWGAwaveform.append(MaxV)
    for i in range(PulseWidth):
        AWGAwaveform.append(MinV)
    DelayValue = int(AWGAperiodvalue)
    for i in range(DelayValue-PulseWidth):
        AWGAwaveform.apped((MinV+MaxV)/2.0)
    SplitAWGAwaveform()
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
    
def AWGAMakeUUNoise():
    global AWGAwaveform, AWGAMinvalue, AWGAMaxvalue, AWGAFreqvalue
    global AWGALength, AWGAperiodvalue # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X
    

    BAWGAMin(0)
    BAWGAMax(0)
    BAWGAFreq(0)
    
    if AWGAFreqvalue > 0.0:
        if cf.AWG_2X == 1:
            AWGAperiodvalue = int((cf.BaseSampleRate*2)/AWGAFreqvalue)
            #SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = cf.BaseSampleRate/AWGAFreqvalue
            #SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0

    if AWGAMinvalue > AWGAMaxvalue:
        MinV = AWGAMaxvalue
        MaxV = AWGAMinvalue
    else:
        MaxV = AWGAMaxvalue
        MinV = AWGAMinvalue
    AWGAwaveform = []
    AWGAwaveform = np.random.uniform(MinV, MaxV, int(AWGAperiodvalue))
    #Mid = (MaxV+MinV)/2.0
    SplitAWGAwaveform()
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
    
def AWGAMakeUGNoise():
    global AWGAwaveform, AWGAMinvalue, AWGAMaxvalue, AWGAFreqvalue
    global AWGALength, AWGAperiodvalue # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X
    

    BAWGAMin(0)
    BAWGAMax(0)
    BAWGAFreq(0)
    
    if AWGAFreqvalue > 0.0:
        if cf.AWG_2X == 1:
            AWGAperiodvalue = int((cf.BaseSampleRate*2)/AWGAFreqvalue)
            #SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = cf.BaseSampleRate/AWGAFreqvalue
            #SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0

    if AWGAMinvalue > AWGAMaxvalue:
        MinV = AWGAMaxvalue
        MaxV = AWGAMinvalue
    else:
        MaxV = AWGAMaxvalue
        MinV = AWGAMinvalue
    AWGAwaveform = []
    AWGAwaveform = np.random.normal((MinV+MaxV)/2, (MaxV-MinV)/3, int(AWGAperiodvalue))
    #Mid = (MaxV+MinV)/2.0
    SplitAWGAwaveform()
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
    
def BAWGAModeLabel():
    global AWGAModeLabel, CHA
    # Hier werden Modi der Channels gesetzt: Ref D und F Boards reagieren hier unterschiedlich
    if cf.AWGAMode.get() == 0: # Source Voltage measure current mode
        label_txt = "SVMI"
    elif cf.AWGAMode.get() == 1: # Source current measure voltage mode
        label_txt = "SIMV"
    elif cf.AWGAMode.get() == 2: # High impedance mode
        label_txt = "Hi-Z" 
    label_txt = label_txt + " Mode"
    AWGAModeLabel.config(text = label_txt ) # change displayed value
    ReMakeAWGwaves()
    #UpdateAwgCont()

def UpdateAWGA():
    global AWGAMinvalue, AWGAMaxvalue
    global AWGAFreqvalue, AWGAPhasevalue, AWGAPhaseDelay
    global AWGADutyCyclevalue, AWGARepeatFlag
    global AWGAWave, AWGATerm, AWGAwaveform
    global CHA, CHB
    global amp1lab, off1lab, AWGA2X, AWGA2X, AWGBWave, AWGBRepeatFlag    
    BAWGAMin(0)
    BAWGAMax(0)
    BAWGAFreq(0)
    BAWGADutyCycle(0)
    BAWGAShape()

    amp1lab.config(text = "Min Ch A" ) # change displayed value
    off1lab.config(text = "Max Ch A" ) # change displayed value
      
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = cf.AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0

    if AWGAPhaseDelay.get() == 0:
        if AWGAWave == 'square':
            AWGAPhasevalue = AWGAPhasevalue + 270.0
            if AWGAPhasevalue > 359:
                AWGAPhasevalue = AWGAPhasevalue - 360
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * 100

    if AWGATerm.get() == 0: # Open termination
        cf.devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
        cf.devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
    elif AWGATerm.get() == 1: # 50 Ohm termination to GND
        cf.devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
        cf.devx.ctrl_transfer( 0x40, 0x50, 33, 0, 0, 0, 100) # set GND switch to closed
    elif AWGATerm.get() == 2: # 50 Ohm termination to +2.5 Volts
        cf.devx.ctrl_transfer( 0x40, 0x50, 32, 0, 0, 0, 100) # set 2.5 V switch to closed
        cf.devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
        
    if AWGAWave == 'dc':
        if cf.AWG_2X == 2:
            AWGAWave == 'arbitrary'
            CHA.arbitrary(AWGB2X, AWGBRepeatFlag.get())
        else:
            if cf.AWGAMode.get() == 0: # Source Voltage measure current mode
                CHA.mode = smu.Mode.SVMI # Put CHA in SVMI mode
                CHA.constantAWGAMaxvalue
            if cf.AWGAMode.get() == 1: # Source current measure voltage mode
                CHA.mode = smu.Mode.SIMV # Put CHA in SIMV mode
                CHA.constant(AWGAMaxvalue/1000)
            if cf.AWGAMode.get() == 2: # High impedance mode
                CHA.mode = smu.Mode.HI_Z # Put CHA in Hi Z mode

    else:
        if cf.AWGAMode.get() == 0: # Source Voltage measure current mode
            CHA.mode = smu.Mode.SVMI # Put CHA in SVMI mode
        if cf.AWGAMode.get() == 1: # Source current measure voltage mode
            CHA.mode = smu.Mode.SIMV # Put CHA in SIMV mode
            AWGAMaxvalue = AWGAMaxvalue/1000
            AWGAMinvalue = AWGAMinvalue/1000
        if cf.AWGAMode.get() == 2: # High impedance mode
            CHA.mode = smu.Mode.HI_Z # Put CHA in Hi Z mode
        else:

            MaxV = AWGAMaxvalue
            MinV = AWGAMinvalue
            try:
                if AWGAWave == 'sine':
                    CHA.sine(MaxV, MinV, AWGAperiodvalue, AWGAdelayvalue)
                elif AWGAWave == 'triangle':
                    CHA.triangle(MaxV, MinV, AWGAperiodvalue, AWGAdelayvalue)
                elif AWGAWave == 'sawtooth':
                    CHA.sawtooth(MaxV, MinV, AWGAperiodvalue, AWGAdelayvalue)
                elif AWGAWave == 'square':
                    CHA.square(MaxV, MinV, AWGAperiodvalue, AWGAdelayvalue, AWGADutyCyclevalue)
                elif AWGAWave == 'stairstep':
                    CHA.stairstep(MaxV, MinV, AWGAperiodvalue, AWGAdelayvalue)
                elif AWGAWave == 'arbitrary':
                    AWGARepeatFlag.set(1)
                    if cf.AWG_2X == 2:
                        AWGAWave == 'arbitrary'
                        CHA.arbitrary(AWGB2X, AWGBRepeatFlag.get())
                    else:
                        CHA.arbitrary(AWGAwaveform, AWGARepeatFlag.get()) # set repeat flag
            except:
                    pass


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen und Einstellungen Arbitärgenerator CHB (Das Gleiche nochmals)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def SetBCompA():
    global AWGADutyCycleEntry, AWGBDutyCycleEntry, AWGAShape, AWGBShape
    # sawp Min and Max values
    AWGBMinvalue = float(eval(cf.AWGAMinEntry.get()))
    AWGBMaxvalue = float(eval(cf.AWGAMaxEntry.get()))
    cf.AWGBMinEntry.delete(0,"tk.END")
    cf.AWGBMinEntry.insert(0, AWGBMaxvalue)
    cf.AWGBMaxEntry.delete(0,"tk.END")
    cf.AWGBMaxEntry.insert(0, AWGBMinvalue)
    # copy everything else
    AWGBFreqvalue = float(eval(cf.AWGAFreqEntry.get()))
    cf.AWGBFreqEntry.delete(0,"tk.END")
    cf.AWGBFreqEntry.insert(0, AWGBFreqvalue)
    AWGBDutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))
    AWGBDutyCycleEntry.delete(0,"tk.END")
    AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)
    AWGBShape.set(AWGAShape.get())
   
def BAWGBMin(temp):
    global AWGBMinvalue
    try:
        AWGBMinvalue = float(eval(cf.AWGBMinEntry.get()))
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

def BAWGBMax(temp):
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

def BAWGBFreq(temp):
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
    
def BAWGBDutyCycle(temp):
    global AWGBDutyCycleEntry, AWGBDutyCyclevalue
    try:
        AWGBDutyCyclevalue = float(eval(AWGBDutyCycleEntry.get()))/100
    except:
        AWGBDutyCycleEntry.delete(0,"tk.END")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)

    if AWGBDutyCyclevalue > 1: # max duty cycle is 100%
        AWGBDutyCyclevalue = 1
        AWGBDutyCycleEntry.delete(0,"tk.END")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue*100)
    if AWGBDutyCyclevalue < 0: # min duty cycle is 0%
        AWGBDutyCyclevalue = 0
        AWGBDutyCycleEntry.delete(0,"tk.END")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)
    
def BAWGBShape():
    global AWGBShape, AWGBWave, duty2lab, CHA, CHB
    if AWGBShape.get() == 0:
        AWGBWave = 'dc'
        duty2lab.config(text="%")
    if AWGBShape.get() == 1:
        AWGBWave = 'sine'
        duty2lab.config(text="%")
    if AWGBShape.get() == 2:
        AWGBWave = 'triangle'
        duty2lab.config(text="%")
    if AWGBShape.get() == 3:
        AWGBWave = 'sawtooth'
        duty2lab.config(text="%")
    if AWGBShape.get() == 4:
        AWGBWave = 'square'
        duty2lab.config(text="%")
    if AWGBShape.get() == 5:
        AWGBWave = 'stairstep'
        duty2lab.config(text="%")
    if AWGBShape.get() > 5:
        AWGBWave = 'arbitrary'
    if cf.AWG_2X == 1:
        CHB.mode = CHA.mode
        AWGBWave = 'arbitrary'
    
# Split 2X sampled AWGBwaveform array into odd and even sample arrays 
def SplitAWGBwaveform():
    global AWGB2X, AWGBwaveform   
    if cf.AWG_2X == 2:
        Tempwaveform = []
        AWGB2X = []
        AWGB2X = AWGBwaveform[::2] # even numbered samples
        Tempwaveform = AWGBwaveform[1::2] # odd numbered samples Tempwaveform
        AWGBwaveform = Tempwaveform
    
def AWGBMakePWMSine():
    global AWGBwaveform, AWGBMinvalue, AWGBMaxvalue, AWGBLength
    global AWGBDutyCyclevalue, AWGBFreqvalue # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGB2X
    BAWGBMin(0)
    BAWGBMax(0)
    BAWGBFreq(0)
    BAWGBDutyCycle(0)

    if AWGBFreqvalue > 0.0:
        if cf.AWG_2X == 2:
            AWGBperiodvalue = (cf.BaseSampleRate*2)/AWGBFreqvalue
        else:
            AWGBperiodvalue = cf.BaseSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0

    MaxV = AWGBMaxvalue
    MinV = AWGBMinvalue
    
    PulseWidth = int(AWGBDutyCyclevalue*100)
    PulseSamples = int(AWGBperiodvalue/PulseWidth)
    AWGBwaveform = []
    for i in range(PulseSamples): #(i = 0; i < cPulse; i++)
        v = round(PulseWidth/2*(1+np.sin(i*2*np.pi/PulseSamples)))
    # print(v)
        for j in range(PulseWidth): #(j = 0; j < cLength; j++)
            if j >= v:
                AWGBwaveform.apptk.END(MaxV) # j>=v?1:0
            else:
                AWGBwaveform.apptk.END(MinV) # j>=v?1:0
    SplitAWGBwaveform()
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    duty2lab.config(text="PWidth")
    UpdateAwgCont()
    
def AWGBMakeTrapazoid():
    global AWGBwaveform, AWGBMinvalue, AWGBMaxvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGB2X
    BAWGBMin(0)
    BAWGBMax(0)
    BAWGBFreq(0)
    BAWGBDutyCycle(0)
    
    if AWGBFreqvalue > 0.0:
        if cf.AWG_2X == 2:
            AWGBperiodvalue = (cf.BaseSampleRate*2)/AWGBFreqvalue
            SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = cf.BaseSampleRate/AWGBFreqvalue
            SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0

    MaxV = AWGBMaxvalue
    MinV = AWGBMinvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue * SamplesPermS) # convert mS to samples
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGBperiodvalue - PulseWidth) - SlopeValue
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepValue = (MaxV - MinV) / SlopeValue
    SampleValue = MinV
    for i in range(SlopeValue):
        AWGBwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue + StepValue
    for i in range(PulseWidth):
        AWGBwaveform.apptk.END(MaxV)
    for i in range(SlopeValue):
        AWGBwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue - StepValue
    for i in range(Remainder):
        AWGBwaveform.apptk.END(MinV)
    SplitAWGBwaveform()
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    duty2lab.config(text="%")
    UpdateAwgCont()

def AWGBMakePulse():
    global AWGBwaveform, AWGBMinvalue, AWGBMaxvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGB2X
    BAWGBMin(0)
    BAWGBMax(0)
    BAWGBFreq(0)
    
    try:
        AWGBDutyCyclevalue = float(eval(AWGBDutyCycleEntry.get()))
    except:
        AWGBDutyCycleEntry.delete(0,"tk.END")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)
        
    if AWGBFreqvalue > 0.0:
        if cf.AWG_2X == 2:
            AWGBperiodvalue = (cf.BaseSampleRate*2)/AWGBFreqvalue
            SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = cf.BaseSampleRate/AWGBFreqvalue
            SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0
    MaxV = AWGBMaxvalue
    MinV = AWGBMinvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue * SamplesPermS) # convert mS to samples
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGBDutyCyclevalue * SamplesPermS) # convert mS to samples
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGBperiodvalue - PulseWidth) - SlopeValue
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepValue = (MaxV - MinV) / SlopeValue
    SampleValue = MinV
    for i in range(SlopeValue):
        AWGBwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue + StepValue
    for i in range(PulseWidth):
        AWGBwaveform.apptk.END(MaxV)
    for i in range(SlopeValue):
        AWGBwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue - StepValue
    for i in range(Remainder):
        AWGBwaveform.apptk.END(MinV)
    SplitAWGBwaveform()
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    duty2lab.config(text="Width mS")
    UpdateAwgCont()

def AWGBMakeRamp():
    global AWGBwaveform, AWGBMinvalue, AWGBMaxvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGB2X
    BAWGBMin(0)
    BAWGBMax(0)
    BAWGBFreq(0)
    BAWGBDutyCycle(0)
    
    if AWGBFreqvalue > 0.0:
        if cf.AWG_2X == 2:
            AWGBperiodvalue = (cf.BaseSampleRate*2)/AWGBFreqvalue
            SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = cf.BaseSampleRate/AWGBFreqvalue
            SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0

    MaxV = AWGBMaxvalue
    MinV = AWGBMinvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue * SamplesPermS)
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGBperiodvalue - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepValue = (MaxV - MinV) / SlopeValue
    SampleValue = MinV
    for i in range(SlopeValue):
        AWGBwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue + StepValue
    for i in range(PulseWidth):
        AWGBwaveform.apptk.END(MaxV)
    for i in range(Remainder):
        AWGBwaveform.apptk.END(MinV)
    SplitAWGBwaveform()
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    duty2lab.config(text="%")
    UpdateAwgCont()

def AWGBMakeUpDownRamp():
    global AWGBwaveform, AWGBMinvalue, AWGBMaxvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGB2X
    BAWGBMin(0)
    BAWGBMax(0)
    BAWGBFreq(0)
    BAWGBDutyCycle(0)
    
    if AWGBFreqvalue > 0.0:
        if cf.AWG_2X == 2:
            AWGBperiodvalue = (cf.BaseSampleRate*2)/AWGBFreqvalue
            #SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = cf.BaseSampleRate/AWGBFreqvalue
            #SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0

    MaxV = AWGBMaxvalue
    MinV = AWGBMinvalue
    #
    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * cf.AWGSAMPLErate / 1000
    #
    AWGBwaveform = []
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGBperiodvalue - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    UpStepValue = (MaxV - MinV) / PulseWidth
    DownStepValue = (MaxV - MinV) / Remainder
    SampleValue = MinV
    for i in range(PulseWidth):
        AWGBwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue + UpStepValue
    for i in range(Remainder):
        AWGBwaveform.apptk.END(SampleValue)
        SampleValue = SampleValue - DownStepValue
    AWGBwaveform = np.roll(AWGBwaveform, int(AWGBdelayvalue))
    SplitAWGBwaveform()
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    duty2lab.config(text = "Symmetry")
    UpdateAwgCont()

def AWGBMakeImpulse():
    global AWGBwaveform, AWGBMinvalue, AWGBMaxvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGB2X
    BAWGBMin(0)
    BAWGBMax(0)
    BAWGBFreq(0)
    BAWGBDutyCycle(0)
    
    if AWGBFreqvalue > 0.0:
        if cf.AWG_2X == 2:
            AWGBperiodvalue = (cf.BaseSampleRate*2)/AWGBFreqvalue
            SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = cf.BaseSampleRate/AWGBFreqvalue
            SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0

    MaxV = AWGBMaxvalue
    MinV = AWGBMinvalue
    AWGBwaveform = []
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue / 2)
    if AWGBPhaseDelay.get() == 0:
        DelayValue = int(AWGBperiodvalue*(AWGBPhasevalue/360))
    elif AWGBPhaseDelay.get() == 1:
        DelayValue = int(AWGBPhasevalue * SamplesPermS)
    for i in range(DelayValue-PulseWidth):
        AWGBwaveform.apptk.END((MinV+MaxV)/2)
    for i in range(PulseWidth):
        AWGBwaveform.apptk.END(MaxV)
    for i in range(PulseWidth):
        AWGBwaveform.apptk.END(MinV)
    DelayValue = int(AWGBperiodvalue-DelayValue)
    for i in range(DelayValue-PulseWidth):
        AWGBwaveform.apptk.END((MinV+MaxV)/2)
    SplitAWGBwaveform()
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    UpdateAwgCont()

def AWGBMakeUUNoise():
    global AWGBwaveform, AWGBMinvalue, AWGBMaxvalue, AWGBFreqvalue
    global AWGBLength, AWGBperiodvalue
    global AWGB2X
    BAWGBMin(0)
    BAWGBMax(0)
    BAWGBFreq(0)
    
    if AWGBFreqvalue > 0.0:
        if cf.AWG_2X == 2:
            AWGBperiodvalue = (cf.BaseSampleRate*2)/AWGBFreqvalue
            #SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = cf.BaseSampleRate/AWGBFreqvalue
            #SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0

    if AWGBMinvalue > AWGBMaxvalue:
        MinV = AWGBMaxvalue
        MaxV = AWGBMinvalue
    else:
        MaxV = AWGBMaxvalue
        MinV = AWGBMinvalue
    AWGBwaveform = []
    AWGBwaveform = np.random.uniform(MinV, MaxV, int(AWGBperiodvalue))
    #Mid = (MaxV+MinV)/2
    SplitAWGBwaveform()
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    UpdateAwgCont()
    
def AWGBMakeUGNoise():
    global AWGBwaveform, AWGBMinvalue, AWGBMaxvalue, AWGBFreqvalue
    global AWGBLength, AWGBperiodvalue
    global AWGB2X
    BAWGBMin(0)
    BAWGBMax(0)
    BAWGBFreq(0)
    
    if AWGBFreqvalue > 0.0:
        if cf.AWG_2X == 2:
            AWGBperiodvalue = (cf.BaseSampleRate*2)/AWGBFreqvalue
            #SamplesPermS = int((cf.BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = cf.BaseSampleRate/AWGBFreqvalue
            #SamplesPermS = int(cf.BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0
    if AWGBMinvalue > AWGBMaxvalue:
        MinV = AWGBMaxvalue
        MaxV = AWGBMinvalue
    else:
        MaxV = AWGBMaxvalue
        MinV = AWGBMinvalue
    AWGBwaveform = []
    AWGBwaveform = np.random.normal((MinV+MaxV)/2, (MaxV-MinV)/3, int(AWGBperiodvalue))
    #Mid = (MaxV+MinV)/2
    SplitAWGBwaveform()
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    UpdateAwgCont()

def BAWGBModeLabel():
    global AWGBModeLabel, CHB
    if cf.AWGBMode.get() == 0: # Source Voltage measure current mode
        label_txt = "SVMI"
    elif cf.AWGBMode.get() == 1: # Source current measure voltage mode
        label_txt = "SIMV"
    elif cf.AWGBMode.get() == 2: # High impedance mode
        label_txt = "Hi-Z" 
    label_txt = label_txt + " Mode"
    AWGBModeLabel.config(text = label_txt ) # change displayed value
    ReMakeAWGwaves()
    #UpdateAwgCont()
    
def UpdateAWGB():
    global AWGBMinvalue, AWGBMaxvalue, AWGA2X
    global AWGBFreqvalue, AWGBPhasevalue, AWGBPhaseDelay
    global AWGBDutyCyclevalue, AWGBRepeatFlag
    global AWGBWave, AWGBTerm, AWGBwaveform
    global CHA, CHB
    global amp2lab, off2lab
    global AWGA2X, AWGB2X, AWGAWave, AWGARepeatFlag
    
    

    amp2lab.config(text = "Min Ch B" ) # change displayed value
    off2lab.config(text = "Max Ch B" ) # change displayed value

    if cf.AWG_2X == 1:
        AWGBWave = 'arbitrary'
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = cf.AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0

    if AWGBPhaseDelay.get() == 0:
        if AWGBWave == 'square':
            AWGBPhasevalue = AWGBPhasevalue + 270.0
            if AWGBPhasevalue > 359:
                AWGBPhasevalue = AWGBPhasevalue - 360
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * 100
       
    if AWGBTerm.get() == 0: # Open termination
        cf.devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set 2.5 V switch to open
        cf.devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set GND switch to open
    elif AWGBTerm.get() == 1: # 50 Ohm termination to GND
        cf.devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set 2.5 V switch to open
        cf.devx.ctrl_transfer( 0x40, 0x50, 38, 0, 0, 0, 100) # set GND switch to closed
    elif AWGBTerm.get() == 2: # 50 Ohm termination to +2.5 Volts
        cf.devx.ctrl_transfer( 0x40, 0x50, 37, 0, 0, 0, 100) # set 2.5 V switch to closed
        cf.devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set GND switch to open
        
    if AWGBWave == 'dc':
        if cf.AWG_2X == 1:
            AWGBWave == 'arbitrary'
            CHB.arbitrary(AWGA2X, AWGARepeatFlag.get())
        else:
            if cf.AWGBMode.get() == 0: # Source Voltage measure current mode
                CHB.mode = smu.Mode.SVMI # Put CHB in SVMI mode
                CHB.constantAWGBMaxvalue
            if cf.AWGBMode.get() == 1: # Source current measure Voltage mode
                CHB.mode = smu.Mode.SIMV # Put CHB in SIMV mode
                CHB.constant(AWGBMaxvalue/1000)
            if cf.AWGBMode.get() == 2: # Hi impedance mode:
                CHB.mode = smu.Mode.HI_Z # Put CHB in Hi Z mode
    else:
        if cf.AWGBMode.get() == 0: # Source Voltage measure current mode
            CHB.mode = smu.Mode.SVMI # Put CHB in SVMI mode
        if cf.AWGBMode.get() == 1: # Source current measure Voltage mode
            CHB.mode = smu.Mode.SIMV # Put CHB in SIMV mode
            AWGBMaxvalue = AWGBMaxvalue/1000
            AWGBMinvalue = AWGBMinvalue/1000
        if cf.AWGBMode.get() == 2: # Hi impedance mode
            CHB.mode = smu.Mode.HI_Z # Put CHB in Hi Z mode
        else:
            MaxV = AWGBMaxvalue
            MinV = AWGBMinvalue
            try: # keep going even if low level library returns an error
                if AWGBWave == 'sine':
                    CHB.sine(MaxV, MinV, AWGBperiodvalue, AWGBdelayvalue)
                elif AWGBWave == 'triangle':
                    CHB.triangle(MaxV, MinV, AWGBperiodvalue, AWGBdelayvalue)
                elif AWGBWave == 'sawtooth':
                    CHB.sawtooth(MaxV, MinV, AWGBperiodvalue, AWGBdelayvalue)
                elif AWGBWave == 'square':
                    CHB.square(MaxV, MinV, AWGBperiodvalue, AWGBdelayvalue, AWGBDutyCyclevalue)
                elif AWGBWave == 'stairstep':
                    CHB.stairstep(MaxV, MinV, AWGBperiodvalue, AWGBdelayvalue)
                elif AWGBWave == 'arbitrary':
                    AWGBRepeatFlag.set(1)
                    if cf.AWG_2X == 1:
                        AWGBWave == 'arbitrary'
                        CHB.arbitrary(AWGA2X, AWGARepeatFlag.get())
                    else:
                        CHB.arbitrary(AWGBwaveform, AWGBRepeatFlag.get()) # set repeat flag
            except:
                pass

def UpdateAwgCont():
    global CHA, CHB
    # if running and in continuous streaming mode temp stop, flush buffer and restart to change AWG settings
    if (cf.RUNstatus.get() == 1):
        if cf.session.continuous:
            BAWGEnab() # set-up new AWG settings
            time.sleep(0.01) # wait awhile here for some reason
            cf.session.start(0)

def UpdateAwgContRet(temp):
    ReMakeAWGwaves()
    
def BAWGEnab():
    global CHA, CHB

    # Stream = False
    # print "Updateing AWGs"
    BAWGAMin(0)
    BAWGAMax(0)
    BAWGAFreq(0)
    BAWGADutyCycle(0)
    BAWGAShape()
    BAWGBMin(0)
    BAWGBMax(0)
    BAWGBFreq(0)
    BAWGBDutyCycle(0)
    BAWGBShape()
    UpdateAWGA()
    UpdateAWGB()
