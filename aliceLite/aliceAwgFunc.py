#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 29.8.20
"""
import math
import time
import numpy as np
import sys
import tkinter as tk
import tkinter.font as tkf
import tkinter.messagebox as tkm
import tkinter.ttk as tkt
from tkinter.filedialog import asksaveasfilename
from tkinter.simpledialog import askstring
import pysmu as smu
# check which operating system
import platform

from aliceIcons import hipulse, lowpulse, TBicon # Bilddateien der Icons
from aliceTimeFunc import MakeTimeTrace, MakeTimeScreen
from aliceMenus import MakeAWGMenu, UpdateAWGMenu, DestroyAWGMenu, MakeSampleRateMenu,
DestroySampleRateMenu, MakeSettingsMenu, UpdateSettingsMenu, DestroySettingsMenu,
MakeMeasureMenu, UpdateMeasureMenu

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
    elif AWGAShape.get()==17:
        AWGAMakePWMSine()
        AWGAShapeLabel.config(text = "PWN Sine") # change displayed value
    elif AWGAShape.get()==12:
        AWGAMakeUpDownRamp()
        AWGAShapeLabel.config(text = "Up Down Ramp") # change displayed value
    elif AWGAShape.get()==20:
        AWGAMakePulse()
        AWGAShapeLabel.config(text = "Pulse") # change displayed value
    elif AWGAShape.get()==21:
        AWGAMakeFMSine()
        AWGAShapeLabel.config(text = "FM Sine") # change displayed value
    elif AWGAShape.get()==22:
        AWGAMakeAMSine()
        AWGAShapeLabel.config(text = "AM Sine") # change displayed value
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
    elif AWGBShape.get()==17:
        AWGBMakePWMSine()
        AWGBShapeLabel.config(text = "PWN Sine") # change displayed value
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

def BAWGAAmpl(temp):
    global AWGAAmplEntry, AWGAAmplvalue, AWGAMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset
    
    try:
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    except:
        AWGAAmplEntry.delete(0,"tk.END")
        AWGAAmplEntry.insert(0, AWGAAmplvalue)
    #
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode
        if AWGAMode.get() == 0: # Source Voltage measure current mode
            if AWGAAmplvalue > 5.00:
                AWGAAmplvalue = 5.00
                AWGAAmplEntry.delete(0,"tk.END")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
            if AWGAAmplvalue < 0.00:
                AWGAAmplvalue = 0.00
                AWGAAmplEntry.delete(0,"tk.END")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
    elif AWG_Amp_Mode.get() == 1: # 1 = Amp/Offset
        if AWGAMode.get() == 0: # Source Voltage measure current mode
            if AWGAAmplvalue > (2.5 / AWGA_Ext_Gain.get()):
                AWGAAmplvalue = 2.5 / AWGA_Ext_Gain.get()
                AWGAAmplEntry.delete(0,"tk.END")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
            if AWGAAmplvalue < (-2.50 / AWGA_Ext_Gain.get()):
                AWGAAmplvalue = -2.50 / AWGA_Ext_Gain.get() 
                AWGAAmplEntry.delete(0,"tk.END")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
    if AWGAMode.get() == 1: # Source current measure voltage mode
        if AWGAAmplvalue > 200.00:
            AWGAAmplvalue = 200.00
            AWGAAmplEntry.delete(0,"tk.END")
            AWGAAmplEntry.insert(0, AWGAAmplvalue)
        if AWGAAmplvalue < -200.00:
            AWGAAmplvalue = -200.00
            AWGAAmplEntry.delete(0,"tk.END")
            AWGAAmplEntry.insert(0, AWGAAmplvalue)

def BAWGAOffset(temp):
    global AWGAOffsetEntry, AWGAOffsetvalue, AWGAMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset
    
    try:
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    except:
        AWGAOffsetEntry.delete(0,"tk.END")
        AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode
        if AWGAMode.get() == 0: # Source Voltage measure current mode
            if AWGAOffsetvalue > 5.00:
                AWGAOffsetvalue = 5.00
                AWGAOffsetEntry.delete(0,"tk.END")
                AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
            if AWGAOffsetvalue < 0.00:
                AWGAOffsetvalue = 0.00
                AWGAOffsetEntry.delete(0,"tk.END")
                AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
        elif AWG_Amp_Mode.get() == 1: # 1 = Amp/Offset
            if AWGAOffsetvalue > (2.50-AWGA_Ext_Offset.get()):
                AWGAOffsetvalue = 2.50-AWGA_Ext_Offset.get()
                AWGAOffsetEntry.delete(0,"tk.END")
                AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
            if AWGAOffsetvalue < (-2.50-AWGA_Ext_Offset.get()):
                AWGAOffsetvalue = -2.50-AWGA_Ext_Offset.get()
                AWGAOffsetEntry.delete(0,"tk.END")
                AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
    if AWGAMode.get() == 1: # Source current measure voltage mode
        if AWGAOffsetvalue > 200.00:
            AWGAOffsetvalue = 200.00
            AWGAOffsetEntry.delete(0,"tk.END")
            AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
        if AWGAOffsetvalue < -200.00:
            AWGAOffsetvalue = -200.00
            AWGAOffsetEntry.delete(0,"tk.END")
            AWGAOffsetEntry.insert(0, AWGAOffsetvalue)

def BAWGAFreq(temp):
    global AWGAFreqEntry, AWGAFreqvalue, AWG_2X
    global BodeScreenStatus, BodeDisp
    try:
        AWGAFreqvalue = float(eval(AWGAFreqEntry.get()))
    except:
        AWGAFreqEntry.delete(0,"tk.END")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if AWG_2X.get() == 1:
        if BodeScreenStatus.get() > 0 and BodeDisp.get() > 0:
            if AWGAFreqvalue > 90000: # max freq is 90KHz foe Bode Plots
                AWGAFreqvalue = 90000
                AWGAFreqEntry.delete(0,"tk.END")
                AWGAFreqEntry.insert(0, AWGAFreqvalue)
        else:
            if AWGAFreqvalue > 50000: # max freq is 50KHz
                AWGAFreqvalue = 50000
                AWGAFreqEntry.delete(0,"tk.END")
                AWGAFreqEntry.insert(0, AWGAFreqvalue)
    else:
        if AWGAFreqvalue > 25000: # max freq is 25KHz
            AWGAFreqvalue = 25000
            AWGAFreqEntry.delete(0,"tk.END")
            AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if AWGAFreqvalue < 0: # Set negative frequency entry to 0
        AWGAFreqvalue = 10
        AWGAFreqEntry.delete(0,"tk.END")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)

def BAWGAPhaseDelay():
    global AWGAPhaseDelay, phasealab, awgaph, awgadel
    if AWGAPhaseDelay.get() == 0:
        phasealab.configure(text="Deg")
        awgaph.configure(style="WPhase.TRadiobutton")
        awgadel.configure(style="GPhase.TRadiobutton")
    elif AWGAPhaseDelay.get() == 1:
        phasealab.configure(text="mSec")
        awgaph.configure(style="GPhase.TRadiobutton")
        awgadel.configure(style="WPhase.TRadiobutton")
    
def BAWGAPhase(temp):
    global AWGAPhaseEntry, AWGAPhasevalue
    try:
        AWGAPhasevalue = float(eval(AWGAPhaseEntry.get()))
    except:
        AWGAPhaseEntry.delete(0,"tk.END")
        AWGAPhaseEntry.insert(0, AWGAPhasevalue)

    if AWGAPhasevalue > 360: # max phase is 360 degrees
        AWGAPhasevalue = 360
        AWGAPhaseEntry.delete(0,"tk.END")
        AWGAPhaseEntry.insert(0, AWGAPhasevalue)
    if AWGAPhasevalue < 0: # min phase is 0 degrees
        AWGAPhasevalue = 0
        AWGAPhaseEntry.delete(0,"tk.END")
        AWGAPhaseEntry.insert(0, AWGAPhasevalue)

def BAWGADutyCycle(temp):
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
        BAWGAPhaseDelay()
    if AWGAShape.get() == 1:
        AWGAWave = 'sine'
        duty1lab.config(text="%")
        BAWGAPhaseDelay()
    if AWGAShape.get() == 2:
        AWGAWave = 'triangle'
        duty1lab.config(text="%")
        BAWGAPhaseDelay()
    if AWGAShape.get() == 3:
        AWGAWave = 'sawtooth'
        duty1lab.config(text="%")
        BAWGAPhaseDelay()
    if AWGAShape.get() == 4:
        AWGAWave = 'square'
        duty1lab.config(text="%")
        BAWGAPhaseDelay()
    if AWGAShape.get() == 5:
        AWGAWave = 'stairstep'
        duty1lab.config(text="%")
        BAWGAPhaseDelay()
    if AWGAShape.get() > 5:
        AWGAWave = 'arbitrary'
    
# Split 2X sampled AWGAwaveform array into odd and even sample arrays
def SplitAWGAwaveform():
    global AWG_2X, AWGA2X, AWGAwaveform
    
    if AWG_2X.get() == 1:
        Tempwaveform = []
        AWGA2X = []
        AWGA2X = AWGAwaveform[1::2] # odd numbered samples
        Tempwaveform = AWGAwaveform[::2] # even numbered samples Tempwaveform
        AWGAwaveform = Tempwaveform

def AWGAMakeFMSine():
    global AWGAwaveform, AWGSAMPLErate, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAperiodvalue
    global AWGADutyCyclevalue, AWGAFreqvalue, duty1lab, AWGAgain, AWGAoffset, AWGAPhaseDelay, AWGAMode
    global AWGA2X, AWG_2X, SAMPLErate, BaseSampleRate, phasealab, AWG_Amp_Mode
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset
    
    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
# uses dyty cycle entry for Modulation index and phase entry for Modulation frequency
    duty1lab.config(text = "M Index")
    phasealab.config(text = "M Freq")

    if AWGAFreqvalue > 0.0:
        if AWG_2X.get() == 1:
            AWGAperiodvalue = (BaseSampleRate*2)/AWGAFreqvalue
        else:
            AWGAperiodvalue = BaseSampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 10.0
        
    try:
        ModFreq = float(eval(AWGAPhaseEntry.get()))
    except:
        ModFreq = 10
        AWGAPhaseEntry.delete(0,"tk.END")
        AWGAPhaseEntry.insert(0, ModFreq)
        
    if ModFreq < 10:
        ModFreq = 10
        AWGAPhaseEntry.delete(0,"tk.END")
        AWGAPhaseEntry.insert(0, ModFreq)
        
    if AWG_2X.get() == 1:
        MODperiodvalue = (BaseSampleRate*2)/ModFreq
    else:
        MODperiodvalue = BaseSampleRate/ModFreq

    try:
        ModIndex = float(eval(AWGADutyCycleEntry.get()))
    except:
        ModIndex = 1.0
        AWGADutyCycleEntry.delete(0,"tk.END")
        AWGADutyCycleEntry.insert(0, ModIndex)
        
    ModCycles = int(32768/MODperiodvalue) # find a whole number of cycles 
    if ModCycles < 1:
        ModCycles = 1
    RecLength = int(ModCycles * MODperiodvalue)
    if RecLength % 2 != 0: # make sure record length is even so 2X mode works for all Freq
        RecLength = RecLength + 1
    CarCycles = int(RecLength/AWGAperiodvalue) # insure a whole number of carrier cycles in record
    AWGAwaveform = []
    AWGAwaveform = np.sin( (np.linspace(0, CarCycles*2*np.pi, RecLength)) - ModIndex*np.cos(np.linspace(0, ModCycles*2*np.pi, RecLength)) )
    if AWG_Amp_Mode.get() == 0:
        if AWGAMode.get() == 1: # convert to mA
            amplitude = (AWGAOffsetvalue-AWGAAmplvalue) / -2000.0
            offset = (AWGAOffsetvalue+AWGAAmplvalue) / 2000.0
        else:
            amplitude = (AWGAOffsetvalue-AWGAAmplvalue) / -2.0
            offset = (AWGAOffsetvalue+AWGAAmplvalue) / 2.0
    else:
        if AWGAMode.get() == 1: # convert to mA
            amplitude = AWGAAmplvalue/1000.0
            offset = AWGAOffsetvalue/1000.0
        else:
            amplitude = AWGAAmplvalue*AWGA_Ext_Gain.get()
            offset = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get()
    AWGAwaveform = (AWGAwaveform * amplitude) + offset # scale and offset the waveform
    AWGAwaveform = np.roll(AWGAwaveform, int(AWGAdelayvalue))
    SplitAWGAwaveform() # if needed
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()

def AWGAMakeAMSine():
    global AWGAwaveform, AWGSAMPLErate, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAperiodvalue
    global AWGADutyCyclevalue, AWGAFreqvalue, duty1lab, AWGAgain, AWGAoffset, AWGAPhaseDelay, AWGAMode
    global AWGA2X, AWG_2X, SAMPLErate, BaseSampleRate, phasealab, AWG_Amp_Mode
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset
    
    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
# uses dyty cycle entry for Modulation index and phase entry for Modulation frequency
    duty1lab.config(text = "M Index")
    phasealab.config(text = "M Freq")

    if AWGAFreqvalue > 0.0:
        if AWG_2X.get() == 1:
            AWGAperiodvalue = (BaseSampleRate*2)/AWGAFreqvalue
        else:
            AWGAperiodvalue = BaseSampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 10.0
        
    try:
        ModFreq = float(eval(AWGAPhaseEntry.get()))
    except:
        ModFreq = 10
        AWGAPhaseEntry.delete(0,"tk.END")
        AWGAPhaseEntry.insert(0, ModFreq)
        
    if ModFreq < 10:
        ModFreq = 10
        AWGAPhaseEntry.delete(0,"tk.END")
        AWGAPhaseEntry.insert(0, ModFreq)
        
    if AWG_2X.get() == 1:
        MODperiodvalue = (BaseSampleRate*2)/ModFreq
    else:
        MODperiodvalue = BaseSampleRate/ModFreq

    try:
        ModIndex = float(eval(AWGADutyCycleEntry.get()))/200.0
    except:
        ModIndex = 50.0
        AWGADutyCycleEntry.delete(0,"tk.END")
        AWGADutyCycleEntry.insert(0, ModIndex)
        
    ModCycles = int(32768/MODperiodvalue) # find a whole number of cycles 
    if ModCycles < 1:
        ModCycles = 1
    RecLength = int(ModCycles * MODperiodvalue)
    if RecLength % 2 != 0: # make sure record length is even so 2X mode works for all Freq
        RecLength = RecLength + 1
    CarCycles = int(RecLength/AWGAperiodvalue) # insure a whole number of carrier cycles in record
    AWGAwaveform = []
    AWGAwaveform = np.sin(np.linspace(0, CarCycles*2*np.pi, RecLength)) * (0.5+(ModIndex*(np.cos(np.linspace(0, ModCycles*2*np.pi, RecLength)))))
    if AWG_Amp_Mode.get() == 0:
        if AWGAMode.get() == 1: # convert to mA
            amplitude = (AWGAOffsetvalue-AWGAAmplvalue) / -2000.0
            offset = (AWGAOffsetvalue+AWGAAmplvalue) / 2000.0
        else:
            amplitude = (AWGAOffsetvalue-AWGAAmplvalue) / -2.0
            offset = (AWGAOffsetvalue+AWGAAmplvalue) / 2.0
    else:
        if AWGAMode.get() == 1: # convert to mA
            amplitude = AWGAAmplvalue/1000.0
            offset = AWGAOffsetvalue/1000.0
        else:
            amplitude = AWGAAmplvalue*AWGA_Ext_Gain.get()
            offset = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get()
    AWGAwaveform = (AWGAwaveform * amplitude) + offset # scale and offset the waveform
    AWGAwaveform = np.roll(AWGAwaveform, int(AWGAdelayvalue))
    SplitAWGAwaveform() # if needed
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
    
def AWGAMakePWMSine():
    global AWGAwaveform, AWGSAMPLErate, AWGAAmplvalue, AWGAOffsetvalue, AWGALength
    global AWGADutyCyclevalue, AWGAFreqvalue, duty1lab, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
    BAWGAPhase(0)
    BAWGADutyCycle(0)

    if AWGAFreqvalue > 0.0:
        if AWG_2X.get() == 1:
            AWGAperiodvalue = int((BaseSampleRate*2)/AWGAFreqvalue)
        else:
            AWGAperiodvalue = BaseSampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() + (AWGAAmplvalue * AWGA_Ext_Gain.get())
        MinV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() - (AWGAAmplvalue * AWGA_Ext_Gain.get())
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    
    PulseWidth = int(AWGADutyCyclevalue*100)
    PulseSamples = int(AWGAperiodvalue/PulseWidth)
    AWGAwaveform = []
    for i in range(PulseSamples): #(i = 0; i < cPulse; i++)
        v = round(PulseWidth/2*(1+np.sin(i*2*np.pi/PulseSamples)))
    # print(v)
        for j in range(PulseWidth): #(j = 0; j < cLength; j++)
            if j >= v:
                AWGAwaveform.apptk.END(MaxV) # j>=v?1:0
            else:
                AWGAwaveform.apptk.END(MinV) # j>=v?1:0
    SplitAWGAwaveform()
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    duty1lab.config(text="PWidth")
    UpdateAwgCont()

def AWGAMakeTrapazoid():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay, phasealab, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGSAMPLErate, AWGADutyCyclevalue, AWGAPhasevalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
    BAWGAPhase(0)
    BAWGADutyCycle(0)
    
    if AWGAFreqvalue > 0.0:
        if AWG_2X.get() == 1:
            AWGAperiodvalue = int((BaseSampleRate*2)/AWGAFreqvalue)
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = BaseSampleRate/AWGAFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() + (AWGAAmplvalue * AWGA_Ext_Gain.get())
        MinV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() - (AWGAAmplvalue * AWGA_Ext_Gain.get())
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue*SamplesPermS) # convert mS to samples
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
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay, phasealab, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGSAMPLErate, AWGADutyCyclevalue, AWGAPhasevalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
    BAWGAPhase(0)

    try:
        AWGADutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))
    except:
        AWGADutyCycleEntry.delete(0,"tk.END")
        AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue)
        
    if AWGAFreqvalue > 0.0:
        if AWG_2X.get() == 1:
            AWGAperiodvalue = int((BaseSampleRate*2)/AWGAFreqvalue)
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = BaseSampleRate/AWGAFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() + (AWGAAmplvalue * AWGA_Ext_Gain.get())
        MinV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() - (AWGAAmplvalue * AWGA_Ext_Gain.get())
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue*SamplesPermS) # convert mS to samples
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGADutyCyclevalue*SamplesPermS) # convert mS to samples
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
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay, phasealab, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGSAMPLErate, AWGADutyCyclevalue, AWGAPhasevalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
    BAWGAPhase(0)
    BAWGADutyCycle(0)
    
    if AWGAFreqvalue > 0.0:
        if AWG_2X.get() == 1:
            AWGAperiodvalue = int((BaseSampleRate*2)/AWGAFreqvalue)
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = BaseSampleRate/AWGAFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() + (AWGAAmplvalue * AWGA_Ext_Gain.get())
        MinV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() - (AWGAAmplvalue * AWGA_Ext_Gain.get())
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue*SamplesPermS) # convert mS to samples
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
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGSAMPLErate, AWGADutyCyclevalue, AWGAPhasevalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
    BAWGAPhase(0)
    BAWGADutyCycle(0)
    
    if AWGAFreqvalue > 0.0:
        if AWG_2X.get() == 1:
            AWGAperiodvalue = int((BaseSampleRate*2)/AWGAFreqvalue)
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() + (AWGAAmplvalue * AWGA_Ext_Gain.get())
        MinV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() - (AWGAAmplvalue * AWGA_Ext_Gain.get())
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue

    if AWGAPhaseDelay.get() == 0:
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * SAMPLErate / 1000

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
    BAWGAPhaseDelay()
    duty1lab.config(text = "Symmetry")
    UpdateAwgCont()

def AWGAMakeImpulse():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGAFreqvalue, AWGAperiodvalue, AWGSAMPLErate, AWGADutyCyclevalue, AWGAPhasevalue
    global AWGA2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
    BAWGAPhase(0)
    BAWGADutyCycle(0)
    
    if AWGAFreqvalue > 0.0:
        if AWG_2X.get() == 1:
            AWGAperiodvalue = int((BaseSampleRate*2)/AWGAFreqvalue)
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = BaseSampleRate/AWGAFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() + (AWGAAmplvalue * AWGA_Ext_Gain.get())
        MinV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() - (AWGAAmplvalue * AWGA_Ext_Gain.get())
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    AWGAwaveform = []
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue / 2.0)
    if AWGAPhaseDelay.get() == 0:
        DelayValue = int(AWGAperiodvalue*(AWGAPhasevalue/360))
    elif AWGAPhaseDelay.get() == 1:
        DelayValue = int(AWGAPhasevalue*SamplesPermS)
    for i in range(DelayValue-PulseWidth):
        AWGAwaveform.apptk.END((MinV+MaxV)/2.0)
    for i in range(PulseWidth):
        AWGAwaveform.apptk.END(MaxV)
    for i in range(PulseWidth):
        AWGAwaveform.apptk.END(MinV)
    DelayValue = int(AWGAperiodvalue-DelayValue)
    for i in range(DelayValue-PulseWidth):
        AWGAwaveform.apptk.END((MinV+MaxV)/2.0)
    SplitAWGAwaveform()
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
    
def AWGAMakeUUNoise():
    global AWGAwaveform, AWGSAMPLErate, AWGAAmplvalue, AWGAOffsetvalue, AWGAFreqvalue
    global AWGALength, AWGAperiodvalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
    
    if AWGAFreqvalue > 0.0:
        if AWG_2X.get() == 1:
            AWGAperiodvalue = int((BaseSampleRate*2)/AWGAFreqvalue)
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = BaseSampleRate/AWGAFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() + (AWGAAmplvalue * AWGA_Ext_Gain.get())
        MinV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() - (AWGAAmplvalue * AWGA_Ext_Gain.get())
    else:
        if AWGAAmplvalue > AWGAOffsetvalue:
            MinV = AWGAOffsetvalue
            MaxV = AWGAAmplvalue
        else:
            MaxV = AWGAOffsetvalue
            MinV = AWGAAmplvalue
    AWGAwaveform = []
    AWGAwaveform = np.random.uniform(MinV, MaxV, int(AWGAperiodvalue))
    Mid = (MaxV+MinV)/2.0
    SplitAWGAwaveform()
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
    
def AWGAMakeUGNoise():
    global AWGAwaveform, AWGSAMPLErate, AWGAAmplvalue, AWGAOffsetvalue, AWGAFreqvalue
    global AWGALength, AWGAperiodvalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
    
    if AWGAFreqvalue > 0.0:
        if AWG_2X.get() == 1:
            AWGAperiodvalue = int((BaseSampleRate*2)/AWGAFreqvalue)
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
            if AWGAperiodvalue % 2 != 0: # make sure record length is even so 2X mode works for all Freq
                AWGAperiodvalue = AWGAperiodvalue + 1
        else:
            AWGAperiodvalue = BaseSampleRate/AWGAFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() + (AWGAAmplvalue * AWGA_Ext_Gain.get())
        MinV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() - (AWGAAmplvalue * AWGA_Ext_Gain.get())
    else:
        if AWGAAmplvalue > AWGAOffsetvalue:
            MinV = AWGAOffsetvalue
            MaxV = AWGAAmplvalue
        else:
            MaxV = AWGAOffsetvalue
            MinV = AWGAAmplvalue
    AWGAwaveform = []
    AWGAwaveform = np.random.normal((MinV+MaxV)/2, (MaxV-MinV)/3, int(AWGAperiodvalue))
    Mid = (MaxV+MinV)/2.0
    SplitAWGAwaveform()
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
    
def BAWGAModeLabel():
    global AWGAMode, AWGAModeLabel, DevID, session, devx, DevOne, CHA, HWRevOne
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset


    # Hier werden Modi der Channels gesetzt: Ref D und F Boards reagieren hier unterschiedlich
    if AWGAMode.get() == 0: # Source Voltage measure current mode
        label_txt = "SVMI"
    elif AWGAMode.get() == 1: # Source current measure voltage mode
        label_txt = "SIMV"
    elif AWGAMode.get() == 2: # High impedance mode
        label_txt = "Hi-Z" 
    label_txt = label_txt + " Mode"
    AWGAModeLabel.config(text = label_txt ) # change displayed value
    ReMakeAWGwaves()
    #UpdateAwgCont()

def UpdateAWGA():
    global AWGAAmplvalue, AWGAOffsetvalue
    global AWGAFreqvalue, AWGAPhasevalue, AWGAPhaseDelay
    global AWGADutyCyclevalue, FSweepMode, AWGARepeatFlag, AWGSync
    global AWGAWave, AWGAMode, AWGATerm, AWGAwaveform
    global CHA, CHB, AWGSAMPLErate, DevID, devx, HWRevOne, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global amp1lab, off1lab, AWGA2X, AWGA2X, AWGBWave, AWGBRepeatFlag
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset
    
    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
    BAWGAPhase(0)
    BAWGADutyCycle(0)
    BAWGAShape()

    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode, 1 = Amp/Offset
        amp1lab.config(text = "Min Ch A" ) # change displayed value
        off1lab.config(text = "Max Ch A" ) # change displayed value
    else:
        amp1lab.config(text = "Amp Ch A" )
        off1lab.config(text = "Off Ch A" )
        
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
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
        devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
    elif AWGATerm.get() == 1: # 50 Ohm termination to GND
        devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x50, 33, 0, 0, 0, 100) # set GND switch to closed
    elif AWGATerm.get() == 2: # 50 Ohm termination to +2.5 Volts
        devx.ctrl_transfer( 0x40, 0x50, 32, 0, 0, 0, 100) # set 2.5 V switch to closed
        devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
        
    if AWGAWave == 'dc':
        if AWG_2X.get() == 2:
            AWGAWave == 'arbitrary'
            CHA.arbitrary(AWGB2X, AWGBRepeatFlag.get())
        else:
            if AWGAMode.get() == 0: # Source Voltage measure current mode
                CHA.mode = smu.Mode.SVMI # Put CHA in SVMI mode
                CHA.constant(AWGAOffsetvalue)
            if AWGAMode.get() == 1: # Source current measure voltage mode
                CHA.mode = smu.Mode.SIMV # Put CHA in SIMV mode
                CHA.constant(AWGAOffsetvalue/1000)
            if AWGAMode.get() == 2: # High impedance mode
                CHA.mode = smu.Mode.HI_Z # Put CHA in Hi Z mode

    else:
        if AWGAMode.get() == 0: # Source Voltage measure current mode
            CHA.mode = smu.Mode.SVMI # Put CHA in SVMI mode
        if AWGAMode.get() == 1: # Source current measure voltage mode
            CHA.mode = smu.Mode.SIMV # Put CHA in SIMV mode
            AWGAOffsetvalue = AWGAOffsetvalue/1000
            AWGAAmplvalue = AWGAAmplvalue/1000
        if AWGAMode.get() == 2: # High impedance mode
            CHA.mode = smu.Mode.HI_Z # Put CHA in Hi Z mode
        else:
            if AWG_Amp_Mode.get() == 1:
                MaxV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() + (AWGAAmplvalue * AWGA_Ext_Gain.get())
                MinV = (AWGAOffsetvalue * AWGA_Ext_Gain.get()) + AWGA_Ext_Offset.get() - (AWGAAmplvalue * AWGA_Ext_Gain.get())
            else:
                MaxV = AWGAOffsetvalue
                MinV = AWGAAmplvalue
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
                    if AWGSync.get() == 0:
                        AWGARepeatFlag.set(1)
                    if AWG_2X.get() == 2:
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
    global AWGAAmplEntry, AWGBAmplEntry, AWGAOffsetEntry, AWGBOffsetEntry, AWGAFreqEntry, AWGBFreqEntry
    global AWGAPhaseEntry, AWGBPhaseEntry, AWGADutyCycleEntry, AWGBDutyCycleEntry, AWGAShape, AWGBShape
    # sawp Min and Max values
    AWGBAmplvalue = float(eval(AWGAAmplEntry.get()))
    AWGBOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    AWGBAmplEntry.delete(0,"tk.END")
    AWGBAmplEntry.insert(0, AWGBOffsetvalue)
    AWGBOffsetEntry.delete(0,"tk.END")
    AWGBOffsetEntry.insert(0, AWGBAmplvalue)
    # copy everything else
    AWGBFreqvalue = float(eval(AWGAFreqEntry.get()))
    AWGBFreqEntry.delete(0,"tk.END")
    AWGBFreqEntry.insert(0, AWGBFreqvalue)
    AWGBPhasevalue = float(eval(AWGAPhaseEntry.get()))
    AWGBPhaseEntry.delete(0,"tk.END")
    AWGBPhaseEntry.insert(0, AWGBPhasevalue)
    AWGBDutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))
    AWGBDutyCycleEntry.delete(0,"tk.END")
    AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)
    AWGBShape.set(AWGAShape.get())
   
def BAWGBAmpl(temp):
    global AWGBAmplEntry, AWGBAmplvalue, AWGBMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset
    
    try:
        AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
    except:
        AWGBAmplEntry.delete(0,"tk.END")
        AWGBAmplEntry.insert(0, AWGBAmplvalue)
    #
    if AWGBMode.get() == 0: # Source Voltage measure current mode
        if AWG_Amp_Mode.get() == 0: # 0 = Min/Max
            if AWGBAmplvalue > 5.00:
                AWGBAmplvalue = 5.00
                AWGBAmplEntry.delete(0,"tk.END")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
            if AWGBAmplvalue < 0.00:
                AWGBAmplvalue = 0.00
                AWGBAmplEntry.delete(0,"tk.END")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
        elif AWG_Amp_Mode.get() == 1: # 1 = Amp/Offset
            if AWGBAmplvalue > (2.5 / AWGB_Ext_Gain.get()):
                AWGBAmplvalue = 2.5 / AWGB_Ext_Gain.get()
                AWGBAmplEntry.delete(0,"tk.END")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
            if AWGBAmplvalue < (-2.50 / AWGB_Ext_Gain.get()):
                AWGBAmplvalue = -2.50 / AWGB_Ext_Gain.get() 
                AWGBAmplEntry.delete(0,"tk.END")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
    elif AWGBMode.get() == 1: # Source current measure voltage mode
        if AWGBAmplvalue > 200.00:
            AWGBAmplvalue = 200.00
            AWGBAmplEntry.delete(0,"tk.END")
            AWGBAmplEntry.insert(0, AWGBAmplvalue)
        if AWGBAmplvalue < -200.00:
            AWGBAmplvalue = -200.00
            AWGBAmplEntry.delete(0,"tk.END")
            AWGBAmplEntry.insert(0, AWGBAmplvalue)

def BAWGBOffset(temp):
    global AWGBOffsetEntry, AWGBOffsetvalue, AWGBMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset
    
    try:
        AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
    except:
        AWGBOffsetEntry.delete(0,"tk.END")
        AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode
        if AWGBMode.get() == 0: # Source Voltage measure current mode
            if AWGBOffsetvalue > 5.00:
                AWGBOffsetvalue = 5.00
                AWGBOffsetEntry.delete(0,"tk.END")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
            if AWGBOffsetvalue < 0.00:
                AWGBOffsetvalue = 0.00
                AWGBOffsetEntry.delete(0,"tk.END")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
        elif AWG_Amp_Mode.get() == 1: # 1 = Amp/Offset
            if AWGBOffsetvalue > (2.50-AWGB_Ext_Offset.get()):
                AWGBOffsetvalue = 2.50-AWGB_Ext_Offset.get()
                AWGBOffsetEntry.delete(0,"tk.END")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
            if AWGBOffsetvalue < (-2.50-AWGB_Ext_Offset.get()):
                AWGBOffsetvalue = -2.50-AWGB_Ext_Offset.get()
                AWGBOffsetEntry.delete(0,"tk.END")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
    if AWGBMode.get() == 1: # Source current measure voltage mode
        if AWGBOffsetvalue > 200.00:
            AWGBOffsetvalue = 200.00
            AWGBOffsetEntry.delete(0,"tk.END")
            AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
        if AWGBOffsetvalue < -200.00:
            AWGBOffsetvalue = -200.00
            AWGBOffsetEntry.delete(0,"tk.END")
            AWGBOffsetEntry.insert(0, AWGBOffsetvalue)

def BAWGBFreq(temp):
    global AWGBFreqEntry, AWGBFreqvalue, AWG_2X
    global BodeScreenStatus, BodeDisp

    try:
        AWGBFreqvalue = float(eval(AWGBFreqEntry.get()))
    except:
        AWGBFreqEntry.delete(0,"tk.END")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if AWG_2X.get() == 2:
        if BodeScreenStatus.get() > 0 and BodeDisp.get() > 0:
            if AWGBFreqvalue > 90000: # max freq is 90KHz for Bode plotting
                AWGBFreqvalue = 90000
                AWGBFreqEntry.delete(0,"tk.END")
                AWGBFreqEntry.insert(0, AWGBFreqvalue)
        else:
            if AWGBFreqvalue > 50000: # max freq is 50KHz
                AWGBFreqvalue = 50000
                AWGBFreqEntry.delete(0,"tk.END")
                AWGBFreqEntry.insert(0, AWGBFreqvalue)
    else:
        if AWGBFreqvalue > 25000: # max freq is 25KHz
            AWGBFreqvalue = 25000
            AWGBFreqEntry.delete(0,"tk.END")
            AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if AWGBFreqvalue < 0: # Set negative frequency entry to 0
        AWGBFreqvalue = 10
        AWGBFreqEntry.delete(0,"tk.END")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)

def BAWGBPhaseDelay():
    global AWGbPhaseDelay, phaseblab, awgbph, awgbdel

    if AWGBPhaseDelay.get() == 0:
        phaseblab.configure(text="Deg")
        awgbph.configure(style="WPhase.TRadiobutton")
        awgbdel.configure(style="GPhase.TRadiobutton")
    elif AWGBPhaseDelay.get() == 1:
        phaseblab.configure(text="mSec")
        awgbph.configure(style="GPhase.TRadiobutton")
        awgbdel.configure(style="WPhase.TRadiobutton")
        
def BAWGBPhase(temp):
    global AWGBPhaseEntry, AWGBPhasevalue

    try:
        AWGBPhasevalue = float(eval(AWGBPhaseEntry.get()))
    except:
        AWGBPhaseEntry.delete(0,"tk.END")
        AWGBPhaseEntry.insert(0, AWGBPhasevalue)

    if AWGBPhasevalue > 360: # max phase is 360 degrees
        AWGBPhasevalue = 360
        AWGBPhaseEntry.delete(0,"tk.END")
        AWGBPhaseEntry.insert(0, AWGBPhasevalue)
    if AWGBPhasevalue < 0: # min phase is 0 degrees
        AWGBPhasevalue = 0
        AWGBPhaseEntry.delete(0,"tk.END")
        AWGBPhaseEntry.insert(0, AWGBPhasevalue)
    
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
    global AWGBShape, AWGBWave, duty2lab, AWG_2X, CHA, CHB
    
    if AWGBShape.get() == 0:
        AWGBWave = 'dc'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() == 1:
        AWGBWave = 'sine'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() == 2:
        AWGBWave = 'triangle'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() == 3:
        AWGBWave = 'sawtooth'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() == 4:
        AWGBWave = 'square'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() == 5:
        AWGBWave = 'stairstep'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() > 5:
        AWGBWave = 'arbitrary'
    if AWG_2X.get() == 1:
        CHB.mode = CHA.mode
        AWGBWave = 'arbitrary'
    
# Split 2X sampled AWGBwaveform array into odd and even sample arrays 
def SplitAWGBwaveform():
    global AWG_2X, AWGB2X, AWGBwaveform
    
    if AWG_2X.get() == 2:
        Tempwaveform = []
        AWGB2X = []
        AWGB2X = AWGBwaveform[::2] # even numbered samples
        Tempwaveform = AWGBwaveform[1::2] # odd numbered samples Tempwaveform
        AWGBwaveform = Tempwaveform
    
def AWGBMakePWMSine():
    global AWGBwaveform, AWGSAMPLErate, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength
    global AWGBDutyCyclevalue, AWGBFreqvalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGB2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGBAmpl(0)
    BAWGBOffset(0)
    BAWGBFreq(0)
    BAWGBPhase(0)
    BAWGBDutyCycle(0)

    if AWGBFreqvalue > 0.0:
        if AWG_2X.get() == 2:
            AWGBperiodvalue = (BaseSampleRate*2)/AWGBFreqvalue
        else:
            AWGBperiodvalue = BaseSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() + (AWGBAmplvalue * AWGB_Ext_Gain.get())
        MinV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() - (AWGBAmplvalue * AWGB_Ext_Gain.get())
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    
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
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGSAMPLErate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGB2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGBAmpl(0)
    BAWGBOffset(0)
    BAWGBFreq(0)
    BAWGBPhase(0)
    BAWGBDutyCycle(0)
    
    if AWGBFreqvalue > 0.0:
        if AWG_2X.get() == 2:
            AWGBperiodvalue = (BaseSampleRate*2)/AWGBFreqvalue
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = BaseSampleRate/AWGBFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() + (AWGBAmplvalue * AWGB_Ext_Gain.get())
        MinV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() - (AWGBAmplvalue * AWGB_Ext_Gain.get())
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue*SamplesPermS) # convert mS to samples
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
    phaseblab.config(text = "Rise Time")
    UpdateAwgCont()

def AWGBMakePulse():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGSAMPLErate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGB2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGBAmpl(0)
    BAWGBOffset(0)
    BAWGBFreq(0)
    BAWGBPhase(0)
    
    try:
        AWGBDutyCyclevalue = float(eval(AWGBDutyCycleEntry.get()))
    except:
        AWGBDutyCycleEntry.delete(0,"tk.END")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)
        
    if AWGBFreqvalue > 0.0:
        if AWG_2X.get() == 2:
            AWGBperiodvalue = (BaseSampleRate*2)/AWGBFreqvalue
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = BaseSampleRate/AWGBFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() + (AWGBAmplvalue * AWGB_Ext_Gain.get())
        MinV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() - (AWGBAmplvalue * AWGB_Ext_Gain.get())
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue*SamplesPermS) # convert mS to samples
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGBDutyCyclevalue*SamplesPermS) # convert mS to samples
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
    phaseblab.config(text = "Rise Time")
    UpdateAwgCont()

def AWGBMakeRamp():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGSAMPLErate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGB2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGBAmpl(0)
    BAWGBOffset(0)
    BAWGBFreq(0)
    BAWGBPhase(0)
    BAWGBDutyCycle(0)
    
    if AWGBFreqvalue > 0.0:
        if AWG_2X.get() == 2:
            AWGBperiodvalue = (BaseSampleRate*2)/AWGBFreqvalue
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = BaseSampleRate/AWGBFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() + (AWGBAmplvalue * AWGB_Ext_Gain.get())
        MinV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() - (AWGBAmplvalue * AWGB_Ext_Gain.get())
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue*SamplesPermS)
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
    phaseblab.config(text = "Slope Time")
    UpdateAwgCont()

def AWGBMakeUpDownRamp():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGSAMPLErate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGB2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGBAmpl(0)
    BAWGBOffset(0)
    BAWGBFreq(0)
    BAWGBPhase(0)
    BAWGBDutyCycle(0)
    
    if AWGBFreqvalue > 0.0:
        if AWG_2X.get() == 2:
            AWGBperiodvalue = (BaseSampleRate*2)/AWGBFreqvalue
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = BaseSampleRate/AWGBFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() + (AWGBAmplvalue * AWGB_Ext_Gain.get())
        MinV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() - (AWGBAmplvalue * AWGB_Ext_Gain.get())
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    #
    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGSAMPLErate / 1000
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
    BAWGBPhaseDelay()
    duty2lab.config(text = "Symmetry")
    UpdateAwgCont()

def AWGBMakeImpulse():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGSAMPLErate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGB2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGBAmpl(0)
    BAWGBOffset(0)
    BAWGBFreq(0)
    BAWGBPhase(0)
    BAWGBDutyCycle(0)
    
    if AWGBFreqvalue > 0.0:
        if AWG_2X.get() == 2:
            AWGBperiodvalue = (BaseSampleRate*2)/AWGBFreqvalue
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = BaseSampleRate/AWGBFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() + (AWGBAmplvalue * AWGB_Ext_Gain.get())
        MinV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() - (AWGBAmplvalue * AWGB_Ext_Gain.get())
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    AWGBwaveform = []
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue / 2)
    if AWGBPhaseDelay.get() == 0:
        DelayValue = int(AWGBperiodvalue*(AWGBPhasevalue/360))
    elif AWGBPhaseDelay.get() == 1:
        DelayValue = int(AWGBPhasevalue*SamplesPermS)
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
    global AWGBwaveform, AWGSAMPLErate, AWGBAmplvalue, AWGBOffsetvalue, AWGBFreqvalue
    global AWGBLength, AWGBperiodvalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGB2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGBAmpl(0)
    BAWGBOffset(0)
    BAWGBFreq(0)
    
    if AWGBFreqvalue > 0.0:
        if AWG_2X.get() == 2:
            AWGBperiodvalue = (BaseSampleRate*2)/AWGBFreqvalue
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = BaseSampleRate/AWGBFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0

    if AWGBAmplvalue > AWGBOffsetvalue:
        MinV = AWGBOffsetvalue
        MaxV = AWGBAmplvalue
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() + (AWGBAmplvalue * AWGB_Ext_Gain.get())
        MinV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() - (AWGBAmplvalue * AWGB_Ext_Gain.get())
    AWGBwaveform = []
    AWGBwaveform = np.random.uniform(MinV, MaxV, int(AWGBperiodvalue))
    Mid = (MaxV+MinV)/2
    SplitAWGBwaveform()
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    UpdateAwgCont()
    
def AWGBMakeUGNoise():
    global AWGBwaveform, AWGSAMPLErate, AWGBAmplvalue, AWGBOffsetvalue, AWGBFreqvalue
    global AWGBLength, AWGBperiodvalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGB2X, AWG_2X, SAMPLErate, BaseSampleRate
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset

    BAWGBAmpl(0)
    BAWGBOffset(0)
    BAWGBFreq(0)
    
    if AWGBFreqvalue > 0.0:
        if AWG_2X.get() == 2:
            AWGBperiodvalue = (BaseSampleRate*2)/AWGBFreqvalue
            SamplesPermS = int((BaseSampleRate*2)/1000) # 200
        else:
            AWGBperiodvalue = BaseSampleRate/AWGBFreqvalue
            SamplesPermS = int(BaseSampleRate/1000) # 100
    else:
        AWGBperiodvalue = 0.0
    if AWGBAmplvalue > AWGBOffsetvalue:
        MinV = AWGBOffsetvalue
        MaxV = AWGBAmplvalue
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() + (AWGBAmplvalue * AWGB_Ext_Gain.get())
        MinV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() - (AWGBAmplvalue * AWGB_Ext_Gain.get())
    AWGBwaveform = []
    AWGBwaveform = np.random.normal((MinV+MaxV)/2, (MaxV-MinV)/3, int(AWGBperiodvalue))
    Mid = (MaxV+MinV)/2
    SplitAWGBwaveform()
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    UpdateAwgCont()

def BAWGBModeLabel():
    global AWGBMode, AWGBModeLabel, DevID, devx, DevOne, CHB, HWRevOne

    if AWGBMode.get() == 0: # Source Voltage measure current mode
        label_txt = "SVMI"
    elif AWGBMode.get() == 1: # Source current measure voltage mode
        label_txt = "SIMV"
    elif AWGBMode.get() == 2: # High impedance mode
        label_txt = "Hi-Z" 
    label_txt = label_txt + " Mode"
    AWGBModeLabel.config(text = label_txt ) # change displayed value
    ReMakeAWGwaves()
    #UpdateAwgCont()
    
def UpdateAWGB():
    global AWGBAmplvalue, AWGBOffsetvalue, AWGA2X, AWG_2X
    global AWGBFreqvalue, AWGBPhasevalue, AWGBPhaseDelay
    global AWGBDutyCyclevalue, FSweepMode, AWGBRepeatFlag, AWGSync
    global AWGBWave, AWGBMode, AWGBTerm, AWGBwaveform
    global CHA, CHB, AWGSAMPLErate, DevID, devx, HWRevOne
    global amp2lab, off2lab, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGA2X, AWGB2X, AWGAWave, AWGARepeatFlag
    global AWGA_Ext_Gain, AWGA_Ext_Offset, AWGB_Ext_Gain, AWGB_Ext_Offset
    
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode, 1 = Amp/Offset
        amp2lab.config(text = "Min Ch B" ) # change displayed value
        off2lab.config(text = "Max Ch B" ) # change displayed value
    else:
        amp2lab.config(text = "Amp Ch B" )
        off2lab.config(text = "Off Ch B" )

    if AWG_2X.get() == 1:
        AWGBWave = 'arbitrary'
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGSAMPLErate/AWGBFreqvalue
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
        devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set GND switch to open
    elif AWGBTerm.get() == 1: # 50 Ohm termination to GND
        devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x50, 38, 0, 0, 0, 100) # set GND switch to closed
    elif AWGBTerm.get() == 2: # 50 Ohm termination to +2.5 Volts
        devx.ctrl_transfer( 0x40, 0x50, 37, 0, 0, 0, 100) # set 2.5 V switch to closed
        devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set GND switch to open
        
    if AWGBWave == 'dc':
        if AWG_2X.get() == 1:
            AWGBWave == 'arbitrary'
            CHB.arbitrary(AWGA2X, AWGARepeatFlag.get())
        else:
            if AWGBMode.get() == 0: # Source Voltage measure current mode
                CHB.mode = smu.Mode.SVMI # Put CHB in SVMI mode
                CHB.constant(AWGBOffsetvalue)
            if AWGBMode.get() == 1: # Source current measure Voltage mode
                CHB.mode = smu.Mode.SIMV # Put CHB in SIMV mode
                CHB.constant(AWGBOffsetvalue/1000)
            if AWGBMode.get() == 2: # Hi impedance mode:
                CHB.mode = smu.Mode.HI_Z # Put CHB in Hi Z mode
    else:
        if AWGBMode.get() == 0: # Source Voltage measure current mode
            CHB.mode = smu.Mode.SVMI # Put CHB in SVMI mode
        if AWGBMode.get() == 1: # Source current measure Voltage mode
            CHB.mode = smu.Mode.SIMV # Put CHB in SIMV mode
            AWGBOffsetvalue = AWGBOffsetvalue/1000
            AWGBAmplvalue = AWGBAmplvalue/1000
        if AWGBMode.get() == 2: # Hi impedance mode
            CHB.mode = smu.Mode.HI_Z # Put CHB in Hi Z mode
        else:
            if AWG_Amp_Mode.get() == 1:
                MaxV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() + (AWGBAmplvalue * AWGB_Ext_Gain.get())
                MinV = (AWGBOffsetvalue * AWGB_Ext_Gain.get()) + AWGB_Ext_Offset.get() - (AWGBAmplvalue * AWGB_Ext_Gain.get())
            else:
                MaxV = AWGBOffsetvalue
                MinV = AWGBAmplvalue
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
                    if AWGSync.get() == 0:
                        AWGBRepeatFlag.set(1)
                    if AWG_2X.get() == 1:
                        AWGBWave == 'arbitrary'
                        CHB.arbitrary(AWGA2X, AWGARepeatFlag.get())
                    else:
                        CHB.arbitrary(AWGBwaveform, AWGBRepeatFlag.get()) # set repeat flag
            except:
                pass

def UpdateAwgCont():
    global session, CHA, CHB, AWGSync
    # if running and in continuous streaming mode temp stop, flush buffer and restart to change AWG settings
    if (RUNstatus.get() == 1) and AWGSync.get() == 0:
        if session.continuous:
            session.tk.END()
            BAWGEnab() # set-up new AWG settings
            time.sleep(0.01) # wait awhile here for some reason
            session.start(0)

def UpdateAwgContRet(temp):
    ReMakeAWGwaves()
    
def BAWGEnab():
    global AWGAMode, AWGBMode, AWGSync
    global CHA, CHB, discontloop, contloop, session

    # Stream = False
    # print "Updateing AWGs"
    BAWGAAmpl(0)
    BAWGAOffset(0)
    BAWGAFreq(0)
    BAWGAPhase(0)
    BAWGADutyCycle(0)
    BAWGAShape()
    BAWGBAmpl(0)
    BAWGBOffset(0)
    BAWGBFreq(0)
    BAWGBPhase(0)
    BAWGBDutyCycle(0)
    BAWGBShape()
    UpdateAWGA()
    UpdateAWGB()
            
def BAWGSync():
    global RUNstatus, AWGSync, session, CHA, CHB, IAScreenStatus, IADisp

    if (RUNstatus.get() == 1): # do this only if running
        if IAScreenStatus.get() > 0 and IADisp.get() > 0:
            AWGSync.set(1)
            return
        if AWGSync.get() == 0:
            #UpdateAwgCont()
            session.flush()
            CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z mode
            CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z mode
            BAWGEnab()
            session.start(0)
            time.sleep(0.02) # wait awhile here for some reason
        elif session.continuous:
            session.tk.END()
            session.flush()
            CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z mode
            CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z mode