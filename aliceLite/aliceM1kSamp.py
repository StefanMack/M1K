#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 30.8.20
"""
import time
import numpy as np
import tkinter as tk
import tkinter.messagebox as tkm
import config as cf
from aliceAwgFunc import ReMakeAWGwaves
import aliceMenus as am
from aliceOsciFunc import (BStop, BStart, UpdateTimeAll, UpdateTimeTrace,
UpdateTimeScreen,ReInterploateTrigger, FindTriggerSample)

VmemoryA = np.ones(1)       # The memory for averaging
VmemoryB = np.ones(1)
ImemoryA = np.ones(1)       # The memory for averaging
ImemoryB = np.ones(1)
ADsignal1 = []              # Ain signal array channel A and B
TRACEresetTime = True # True for first new trace, False for averageing

InOffA = InGainA = InOffB = InGainB = 0.0 # Variablen für Input aus UI
CurOffA = CurOffB = CurGainA = CurGainB = 0.0

Alternate_Sweep_Mode = 1 # 1 wenn drei oder mehr Signale gesampelt werden
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# M1K Samplingfunktionen
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
def Analog_In():  
    while (True):
        if (cf.RUNstatus.get() == 1) or (cf.RUNstatus.get() == 2):
            if cf.SettingsStatus.get() == 1:
                am.UpdateSettingsMenu() # Make sure current entries in Settings controls are up to date
            Analog_Time_In()
        cf.root.update_idletasks()
        cf.root.update()

#---Read the analog data and store the data into the arrays
def Analog_Time_In():
    global InOffA, InGainA, InOffB, InGainB
    global CurOffA, CurOffB, CurGainA, CurGainB 
    # get time scale
    try:
        cf.TIMEdiv = eval(cf.TMsb.get())
    except:
        cf.TIMEdiv = 0.5
        cf.TMsb.delete(0,"tk.END")
        cf.TMsb.insert(0,cf.TIMEdiv)
    if cf.TIMEdiv < 0.0002:
        cf.TIMEdiv = 0.01
# Do input divider Calibration CH1VGain, CH2VGain, CH1VOffset, CH2VOffset
    try:
        InOffA = float(eval(cf.CHAVOffsetEntry.get()))
    except:
        cf.CHAVOffsetEntry.delete(0,tk.END)
        cf.CHAVOffsetEntry.insert(0, InOffA)
    try:
        InGainA = float(eval(cf.CHAVGainEntry.get()))
    except:
        cf.CHAVGainEntry.delete(0,tk.END)
        cf.CHAVGainEntry.insert(0, InGainA)
    try:
        InOffB = float(eval(cf.CHBVOffsetEntry.get()))
    except:
        cf.CHBVOffsetEntry.delete(0,tk.END)
        cf.CHBVOffsetEntry.insert(0, InOffB)
    try:
        InGainB = float(eval(cf.CHBVGainEntry.get()))
    except:
        cf.CHBVGainEntry.delete(0,tk.END)
        cf.CHBVGainEntry.insert(0, InGainB)
    try:
        CurOffA = float(cf.CHAIOffsetEntry.get()) #/1000.0 # convert to Amps # leave in mA
    except:
        CurOffA = 0.0
    try:
        CurOffB = float(cf.CHBIOffsetEntry.get())#/1000.0 # convert to Amps
    except:
        CurOffB = 0.0
    try:
        CurGainA = float(cf.CHAIGainEntry.get())
    except:
        CurGainA = 1.0
    try:
        CurGainB = float(cf.CHBIGainEntry.get())
    except:
        CurGainB = 1.0
# Dedecide which Fast or Slow sweep routine to call
    if cf.TIMEdiv > 500:
        Analog_Slow_time() # failed attempt as rolling trace
    else:
        Analog_Fast_time()


#---Right now this is a failed attempt to plot slow sweeps.
def Analog_Slow_time():
    global ADsignal1
    global VmemoryA, VmemoryB, ImemoryA, ImemoryB
    global HozPoss
    global TRACEsize, First_Slow_sweep, ShiftPointer
    global hldn
    global TRACErefresh
    global SCREENrefresh, DCrefresh
    global InOffA, InGainA, InOffB, InGainB, CurOffA, CurOffB, CurGainA, CurGainB
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global cal, Last_ADC_Mux_Mode
    global PIO_0, PIO_1, PIO_2, PIO_3, PIO_4, PIO_5, PIO_6, PIO_7

    # Starting acquisition
    DCVA0 = DCVB0 = DCIA0 = DCIB0= 0.0 # initalize measurment variable
    #
    NumSamples = 1 # int(cf.SAMPLErate/cf.TIMEdiv)
    if First_Slow_sweep == 0:
        BufferLen = cf.TIMEdiv*12.0
        cf.VBuffA = np.ones(BufferLen)       
        cf.VBuffB = np.ones(BufferLen)
        cf.IBuffA = np.ones(BufferLen)       
        cf.IBuffB = np.ones(BufferLen)
        First_Slow_sweep = 1

    if cf.session.continuous:
        ADsignal1 = cf.devx.read(NumSamples, -1, True) # get samples for both channel A and B
    #
    else:
        ADsignal1 = cf.devx.get_samples(NumSamples) # , True) # get samples for both channel A and B

    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(NumSamples): # calculate average
        DCVA0 += ADsignal1[index][0][0] # Sum for average CA voltage 
        DCVB0 += ADsignal1[index][1][0] # Sum for average CB voltage
        DCIA0 += ADsignal1[index][0][1] # Sum for average CA current 
        DCIB0 += ADsignal1[index][1][1] # Sum for average CB current
    
    ## Messwerte werden wohl bei jedem Trace alle automatisch berechnet
    ## Messwerte sind globale Variablen
    
    DCVA0 = DCVA0/(NumSamples) # calculate V average
    DCVB0 = DCVB0/(NumSamples) # calculate V average
    DCVA0 = (DCVA0 - InOffA) * InGainA
    DCVB0 = (DCVB0 - InOffB) * InGainB
    DCIA0 = DCIA0/(NumSamples) # calculate I average
    DCIB0 = DCIB0/(NumSamples) # calculate I average
    DCIA0 = DCIA0 * 1000 # convert to mA
    DCIB0 = DCIB0 * 1000 # convert to mA
    DCIA0 = (DCIA0 - CurOffA) * CurGainA
    DCIB0 = (DCIB0 - CurOffB) * CurGainB
# Shift in next new sample
    cf.VBuffA = shift_buffer(cf.VBuffA, -1, DCVA0)
    cf.VBuffB = shift_buffer(cf.VBuffB, -1, DCVB0)
    cf.IBuffA = shift_buffer(cf.IBuffA, -1, DCIA0)
    cf.IBuffB = shift_buffer(cf.IBuffB, -1, DCIB0)
# Calculate measurement values
    cf.DCV1 = np.mean(cf.VBuffA)
    cf.DCV2 = np.mean(cf.VBuffB)
    cf.DCI1 = np.mean(cf.IBuffA)
    cf.DCI2 = np.mean(cf.IBuffB)
# find min and max values
    cf.MinV1 = np.amin(cf.VBuffA)
    cf.MaxV1 = np.amax(cf.VBuffA)
    cf.MinV2 = np.amin(cf.VBuffB)
    cf.MaxV2 = np.amax(cf.VBuffB)
    cf.MinI1 = np.amin(cf.IBuffA)
    cf.MaxI1 = np.amax(cf.IBuffA)
    cf.MinI2 = np.amin(cf.IBuffB)
    cf.MaxI2 = np.amax(cf.IBuffB)
# RMS value = square root of average of the data record squared
    cf.SV1 = np.sqrt(np.mean(np.square(cf.VBuffA)))
    cf.SI1 = np.sqrt(np.mean(np.square(cf.IBuffA)))
    cf.SV2 = np.sqrt(np.mean(np.square(cf.VBuffB)))
    cf.SI2 = np.sqrt(np.mean(np.square(cf.IBuffB)))
    cf.SVA_B = np.sqrt(np.mean(np.square(cf.VBuffA-cf.VBuffB)))
#
    UpdateTimeAll()         # Update Data, trace and time screen
    if (cf.RUNstatus.get() == 3) or (cf.RUNstatus.get() == 4):
        if cf.RUNstatus.get() == 3:
            cf.RUNstatus.set(0)
        if cf.RUNstatus.get() == 4:          
            cf.RUNstatus.set(1)
        UpdateTimeScreen()
        # update screens

## Wie unterscheidet sich dieses Sampling vom Slow Mode?
#---routine for time scales faster than 500 mSec/Div
def Analog_Fast_time():
    global ADsignal1, Alternate_Sweep_Mode
    global VmemoryA, VmemoryB, ImemoryA, ImemoryB
    global HozPoss
    global TRACEresetTime
    global TIMEdiv1x, hldn
    global TRACErefresh
    global SCREENrefresh, DCrefresh
    global InOffA, InGainA, InOffB, InGainB, CurOffA, CurOffB, CurGainA, CurGainB
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global cal, Last_ADC_Mux_Mode
    global PIO_0, PIO_1, PIO_2, PIO_3, PIO_4, PIO_5, PIO_6, PIO_7

    if cf.TRACEmodeTime.get() == 0 and TRACEresetTime == False:
        TRACEresetTime = True               # Clear the memory for averaging
    elif cf.TRACEmodeTime.get() == 1:
        if TRACEresetTime == True:
            TRACEresetTime = False
        # Save previous trace in memory for average trace
        VmemoryA = cf.VBuffA
        VmemoryB = cf.VBuffB
        ImemoryA = cf.IBuffA
        ImemoryB = cf.IBuffB

    try:
        cf.HoldOff = float(eval(cf.HoldOffentry.get()))
        if cf.HoldOff < 0:
            cf.HoldOff = 0
            cf.HoldOffentry.delete(0,tk.END)
            cf.HoldOffentry.insert(0, cf.HoldOff)
    except:
        cf.HoldOffentry.delete(0,tk.END)
        cf.HoldOffentry.insert(0, cf.HoldOff)
#
    try:
        HozPoss = float(eval(cf.HozPossentry.get()))
    except:
        cf.HozPossentry.delete(0,tk.END)
        cf.HozPossentry.insert(0, HozPoss)

    hldn = int(cf.HoldOff * cf.SAMPLErate/1000 )
    hozpos = int(HozPoss * cf.SAMPLErate/1000 )
    if hozpos < 0:
        hozpos = 0
    twoscreens = int(cf.SAMPLErate * 20.0 * cf.TIMEdiv / 1000.0) # number of samples to acquire, 2 screen widths
    #onescreen = int(twoscreens/2)
    if hldn+hozpos > cf.MaxSamples-twoscreens:
        hldn = cf.MaxSamples-twoscreens-hozpos
        cf.HoldOffentry.delete(0,tk.END)
        cf.HoldOffentry.insert(0, hldn*1000/cf.SAMPLErate)
      
    cf.SHOWsamples = twoscreens + hldn + hozpos
    if cf.SHOWsamples > cf.MaxSamples: # or a Max of 100,000 samples
        cf.SHOWsamples = cf.MaxSamples
    if cf.SHOWsamples < 2000: # or a Min of 2000 samples
        cf.SHOWsamples = 2000
    if hozpos >= 0:
        cf.TRIGGERsample = hldn
    else:
        cf.TRIGGERsample = abs(hozpos)
    cf.TRIGGERsample = cf.TRIGGERsample + hozpos #
# Starting acquisition
    if cf.session.continuous:
        ADsignal1 = cf.devx.read(cf.SHOWsamples, -1, True) # get samples for both channel A and B
    #
    else:
        ADsignal1 = cf.devx.get_samples(cf.SHOWsamples) # , True) # get samples for both channel A and B
        # waite to finish then return to open termination
        cf.devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
        cf.devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
        cf.devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
        cf.devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    
    # MUX-Modi: Modus 0 macht für Sensortechnik am meisten Sinn, wenn für Ultraschallsensor mit 200.000 S/s
    if Alternate_Sweep_Mode == 1 and cf.Two_X_Sample.get() == 1:
        if cf.ADC_Mux_Mode.get() == 0: # VA and VB
            cf.VBuffA = [] # Clear the V Buff array for trace A
            cf.VBuffB = [] # Clear the V Buff array for trace B
        elif cf.ADC_Mux_Mode.get() == 1: # IA and IB
            cf.IBuffA = [] # Clear the I Buff array for trace A
            cf.IBuffB = [] # Clear the I Buff array for trace B
        elif cf.ADC_Mux_Mode.get() == 4: # VA and IA
            cf.VBuffA = [] # Clear the V Buff array for trace A
            cf.IBuffA = [] # Clear the I Buff array for trace A
        elif cf.ADC_Mux_Mode.get() == 5: # VB and IB
            cf.VBuffB = [] # Clear the V Buff array for trace B
            cf.IBuffB = [] # Clear the I Buff array for trace B
    else:
        cf.VBuffA = [] # Clear the V Buff array for trace A
        cf.IBuffA = [] # Clear the I Buff array for trace A
        cf.VBuffB = [] # Clear the V Buff array for trace B
        cf.IBuffB = [] # Clear the I Buff array for trace B
    increment = 1
    index = 0
    if cf.SHOWsamples != len(ADsignal1):
        cf.SHOWsamples = len(ADsignal1)
    while index < cf.SHOWsamples: # build arrays and decimate if needed
    ## Samplingrate 200.000 S/s geht nur, wenn nur zwei der 4 möglichen Größen
    ## VA, IA, VB, IB gemessen werden. Welche das sind wird über den ADC_Mux_Mode
    ## bestimmt.
    
        if cf.Two_X_Sample.get() == 1 and cf.ADC_Mux_Mode.get() < 6:
            if cf.ADC_Mux_Mode.get() == 0: # VA and VB
                cf.VBuffA.append(ADsignal1[index][0][0])
                cf.VBuffA.append(ADsignal1[index][1][1])
                cf.VBuffB.append(ADsignal1[index][0][1])
                cf.VBuffB.append(ADsignal1[index][1][0])
                if Alternate_Sweep_Mode == 0:
                    cf.IBuffA.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode.get() == 1: # IA and IB
                cf.IBuffA.append(ADsignal1[index][0][1])
                cf.IBuffA.append(ADsignal1[index][1][0])
                cf.IBuffB.append(ADsignal1[index][0][0])
                cf.IBuffB.append(ADsignal1[index][1][1])
                if Alternate_Sweep_Mode == 0:
                    cf.VBuffA.append(0.0) # fill as a place holder
                    cf.VBuffA.append(0.0) # fill as a place holder
                    cf.VBuffB.append(0.0) # fill as a place holder
                    cf.VBuffB.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode.get() == 2: # VA and IB
                cf.VBuffA.append((ADsignal1[index][0][1])/1024.0)
                cf.VBuffA.append((ADsignal1[index][1][0])/1024.0)
                #
                cf.IBuffB.append( ((ADsignal1[index][0][0])/4096.0)-0.5 )
                cf.IBuffB.append( ((ADsignal1[index][1][1])/4096.0)-0.5 ) 
                #
                if Alternate_Sweep_Mode == 0:
                    cf.VBuffB.append(0.0) # fill as a place holder
                    cf.VBuffB.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode.get() == 3: # VB and IA
                cf.VBuffB.append((ADsignal1[index][0][0])/1024.0)
                cf.VBuffB.append((ADsignal1[index][1][1])/1024.0)
                #
                cf.IBuffA.append( ((ADsignal1[index][0][1])/4096.0)-0.5 )
                cf.IBuffA.append( ((ADsignal1[index][1][0])/4096.0)-0.5 )
                #
                if Alternate_Sweep_Mode == 0:
                    cf.VBuffA.append(0.0) # fill as a place holder
                    cf.VBuffA.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode.get() == 4: # VA and IA
                cf.VBuffA.append(ADsignal1[index][0][0])
                cf.VBuffA.append(ADsignal1[index][1][1])
                cf.IBuffA.append(ADsignal1[index][0][1])
                cf.IBuffA.append(ADsignal1[index][1][0])
                if Alternate_Sweep_Mode == 0:
                    cf.VBuffB.append(0.0) # fill as a place holder
                    cf.VBuffB.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode.get() == 5: # VB and IB
                cf.VBuffB.append(ADsignal1[index][0][1])
                cf.VBuffB.append(ADsignal1[index][1][0])
                cf.IBuffB.append(ADsignal1[index][0][0])
                cf.IBuffB.append(ADsignal1[index][1][1])
                if Alternate_Sweep_Mode == 0:
                    cf.VBuffA.append(0.0) # fill as a place holder
                    cf.VBuffA.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
        else:
            cf.VBuffA.append(ADsignal1[index][0][0])
            cf.IBuffA.append(ADsignal1[index][0][1])
            cf.VBuffB.append(ADsignal1[index][1][0])
            cf.IBuffB.append(ADsignal1[index][1][1])
        index = index + increment
#
    cf.SHOWsamples = len(cf.VBuffA)
    if Alternate_Sweep_Mode == 1 and cf.Two_X_Sample.get() == 1:
        if cf.ADC_Mux_Mode.get() == 0: # VA and VB
            cf.VBuffA = np.array(cf.VBuffA)
            cf.VBuffB = np.array(cf.VBuffB)
            cf.VBuffA = (cf.VBuffA - InOffA) * InGainA
            cf.VBuffB = (cf.VBuffB - InOffB) * InGainB
            cf.ADC_Mux_Mode.set(1) # switch mode
            Last_ADC_Mux_Mode = 0
        elif cf.ADC_Mux_Mode.get() == 1: # IA and IB
            cf.IBuffA = np.array(cf.IBuffA) * 1000 # convert to mA
            cf.IBuffB = np.array(cf.IBuffB) * 1000 # convert to mA
            cf.IBuffA = (cf.IBuffA - CurOffA) * CurGainA
            cf.IBuffB = (cf.IBuffB - CurOffB) * CurGainB
            cf.ADC_Mux_Mode.set(Last_ADC_Mux_Mode) # switch mode
        elif cf.ADC_Mux_Mode.get() == 4: # VA and IA
            cf.VBuffA = np.array(cf.VBuffA)
            cf.IBuffA = np.array(cf.IBuffA) * 1000 # convert to mA
            cf.IBuffA = (cf.IBuffA - CurOffA) * CurGainA
            cf.VBuffA = (cf.VBuffA - InOffA) * InGainA
            cf.ADC_Mux_Mode.set(1) # switch mode
            Last_ADC_Mux_Mode = 4
        elif cf.ADC_Mux_Mode.get() == 5: # VB and IB
            cf.VBuffB = np.array(cf.VBuffB)
            cf.VBuffB = (cf.VBuffB - InOffB) * InGainB
            cf.IBuffB = np.array(cf.IBuffB) * 1000 # convert to mA
            cf.IBuffB = (cf.IBuffB - CurOffB) * CurGainB
            cf.ADC_Mux_Mode.set(1) # switch mode
            Last_ADC_Mux_Mode = 5
        SetADC_Mux()
    #
    else:
        cf.VBuffA = np.array(cf.VBuffA)
        cf.VBuffB = np.array(cf.VBuffB)
        cf.IBuffA = np.array(cf.IBuffA) * 1000 # convert to mA
        cf.IBuffB = np.array(cf.IBuffB) * 1000 # convert to mA
        cf.VBuffA = (cf.VBuffA - InOffA) * InGainA
        cf.VBuffB = (cf.VBuffB - InOffB) * InGainB
        cf.IBuffA = (cf.IBuffA - CurOffA) * CurGainA
        cf.IBuffB = (cf.IBuffB - CurOffB) * CurGainB

    
# Find trigger sample point if necessary
    cf.LShift = 0
    if cf.TgInput.get() == 1:
        FindTriggerSample(cf.VBuffA)
    if cf.TgInput.get() == 2:
        FindTriggerSample(cf.IBuffA)
    if cf.TgInput.get() == 3:
        FindTriggerSample(cf.VBuffB)
    if cf.TgInput.get() == 4:
        FindTriggerSample(cf.IBuffB)
    if cf.TRACEmodeTime.get() == 1 and TRACEresetTime == False:
        # Average mode 1, add difference / TRACEaverage to array
        if cf.TgInput.get() > 0: # if triggering left shift all arrays such that trigger point is at index 0
            cf.LShift = 0 - cf.TRIGGERsample
            cf.VBuffA = np.roll(cf.VBuffA, cf.LShift)
            cf.VBuffB = np.roll(cf.VBuffB, cf.LShift)
            cf.IBuffA = np.roll(cf.IBuffA, cf.LShift)
            cf.IBuffB = np.roll(cf.IBuffB, cf.LShift)
            cf.TRIGGERsample = hozpos # set trigger sample to index 0 offset by horizontal position
        try:
            cf.VBuffA = VmemoryA + (cf.VBuffA - VmemoryA) / cf.TRACEaverage.get()
            cf.IBuffA = ImemoryA + (cf.IBuffA - ImemoryA) / cf.TRACEaverage.get()
            cf.VBuffB = VmemoryB + (cf.VBuffB - VmemoryB) / cf.TRACEaverage.get()
            cf.IBuffB = ImemoryB + (cf.IBuffB - ImemoryB) / cf.TRACEaverage.get()
        except:
            # buffer size mismatch so reset memory buffers
            VmemoryA = cf.VBuffA
            VmemoryB = cf.VBuffB
            ImemoryA = cf.IBuffA
            ImemoryB = cf.IBuffB
        if cf.TgInput.get() == 1:
            ReInterploateTrigger(cf.VBuffA)
        if cf.TgInput.get() == 2:
            ReInterploateTrigger(cf.IBuffA)
        if cf.TgInput.get() == 3:
            ReInterploateTrigger(cf.VBuffB)
        if cf.TgInput.get() == 4:
            ReInterploateTrigger(cf.IBuffB)
    # DC value = average of the data record
    Endsample = cf.SHOWsamples - 10 # average over all samples
    ## Berechnung Messwerte im Fast Scan Modus auch für jeden Trace            
    cf.DCV1 = np.mean(cf.VBuffA[hldn:Endsample])
    cf.DCV2 = np.mean(cf.VBuffB[hldn:Endsample])
    # convert current values to mA
    cf.DCI1 = np.mean(cf.IBuffA[hldn:Endsample])
    cf.DCI2 = np.mean(cf.IBuffB[hldn:Endsample])
    # find min and max values
    cf.MinV1 = np.amin(cf.VBuffA[hldn:Endsample])
    cf.MaxV1 = np.amax(cf.VBuffA[hldn:Endsample])
    cf.MinV2 = np.amin(cf.VBuffB[hldn:Endsample])
    cf.MaxV2 = np.amax(cf.VBuffB[hldn:Endsample])
    cf.MinI1 = np.amin(cf.IBuffA[hldn:Endsample])
    cf.MaxI1 = np.amax(cf.IBuffA[hldn:Endsample])
    cf.MinI2 = np.amin(cf.IBuffB[hldn:Endsample])
    cf.MaxI2 = np.amax(cf.IBuffB[hldn:Endsample])
    # RMS value = square root of average of the data record squared
    cf.SV1 = np.sqrt(np.mean(np.square(cf.VBuffA[hldn:Endsample])))
    cf.SI1 = np.sqrt(np.mean(np.square(cf.IBuffA[hldn:Endsample])))
    cf.SV2 = np.sqrt(np.mean(np.square(cf.VBuffB[hldn:Endsample])))
    cf.SI2 = np.sqrt(np.mean(np.square(cf.IBuffB[hldn:Endsample])))
    cf.SVA_B = np.sqrt(np.mean(np.square(cf.VBuffA[hldn:Endsample]-cf.VBuffB[hldn:Endsample])))

    UpdateTimeAll()         # Update Data, trace and time screen
       # Update Data, trace
    if cf.SingleShot.get() > 0 and cf.Is_Triggered == 1: # Singel Shot trigger is on
        BStop() # 
        cf.SingleShot.set(0)
    if cf.ManualTrigger.get() == 1: # Manual trigger is on
        BStop() # 
    if (cf.RUNstatus.get() == 3) or (cf.RUNstatus.get() == 4):
        if cf.RUNstatus.get() == 3:
            cf.RUNstatus.set(0)
        if cf.RUNstatus.get() == 4:          
            cf.RUNstatus.set(1)
    UpdateTimeScreen()
            
            
# Einstellen der Samplingrate, falls im Fenster diese geändert wurde
def SetSampleRate():
    global etssrlab, BaseRatesb
    global rtsrlab
    #
    WasRunning = 0
    if (cf.RUNstatus.get() == 1):
        WasRunning = 1
        BStop() # Force Stop loop if running
    try:
        NewRate = int(BaseRatesb.get())
        # Basis-Samplingrate kann nicht größer als 100.000 S/s sein wenn diese direkt über
        # die Benutzeroberfläche eingegeben wird. Der Wert 200.000 S/s geht nur über den
        # Button "Two_X_Sample"
        if NewRate <= 100000: # rate has to be less than or equal to 100,000
            cf.BaseSampleRate = NewRate
        else:
        # Bei zu großer Samplinrate wird diese im Fenster auf 100000 zurück gesetzt
            cf.BaseSampleRate = 100000
            BaseRatesb.delete(0,"tk.END")
            BaseRatesb.insert(0,cf.BaseSampleRate)
        cf.SAMPLErate = cf.BaseSampleRate # Scope sample rate
    except:
        pass
    # Samplingrate wird tatsächlich direkt am M1K eingestellt
    cf.session.configure(sample_rate=cf.BaseSampleRate)
    cf.BaseSampleRate = cf.session.sample_rate
    cf.SAMPLErate = cf.BaseSampleRate # Scope sample rate
    cf.AWGSAMPLErate = cf.BaseSampleRate
    BaseRatesb.delete(0,"tk.END")
    BaseRatesb.insert(0,cf.BaseSampleRate)
    ReMakeAWGwaves() # remake AWG waveforms for new rate
    if (WasRunning == 1):
        WasRunning = 0
        BStart() # restart loop if was running
          
#**************************************************
# Hier Einstellung der Samplingrate auf 200.000 S/s
#**************************************************
# Wieso wird zwischen ADC_Mux_Mode und cf.devx.set_adc_mux() unterschieden, bzw.
# wieso stimmen die Nummern nicht bei jedem Modus überein?
def SetADC_Mux():
# Der ADC_Mux _Mode wird über unterschiedliche Menüs gesetzt: Samplinrate oder hier das Aktivieren der unterschiedlichen Kanäle.
# Das ist wohl der Grund wieso für die Hardware der Mux-Mode mit cf.devx.set_mux_mode() eingestellt wird. Die Tkinter-Variable ADC_Mux_Mode
# ist in erster Linie dafür da, die Buttons auszulesen und deren Zustand zu setzen.
#    if not cf.DevID == "No Device":
#        tkm.showwarning("WARNING","No Device Plugged In!")
#        return 
    v1_adc_conf = 0x20F1 # ADC Mux defaults
    i1_adc_conf = 0x20F7
    v2_adc_conf = 0x20F7
    i2_adc_conf = 0x20F1
    #!! ADC_Mux_Mode und cf.devx Mux Mode teils nicht gleich
    if cf.Two_X_Sample.get() == 1:
    # Der Mux-Mode hat was damit zu tun, welche Kombination von VA, IA, VB und IB abgetastet wird
        if cf.ADC_Mux_Mode.get() == 0: # VA and VB
            cf.devx.set_adc_mux(1)
        elif cf.ADC_Mux_Mode.get() == 1: # IA and IB
            cf.devx.set_adc_mux(2)
        #Wieso hier so kompliziert?
        elif cf.ADC_Mux_Mode.get() == 2: # VA and IB
            # cycle trhough default mux values as starting point
            cf.devx.set_adc_mux(2)
            # now set new mux values
            cf.devx.set_adc_mux(7)
            cf.devx.ctrl_transfer(0x40, 0x20, v1_adc_conf, 0, 0, 0, 100) # U12
            cf.devx.ctrl_transfer(0x40, 0x21, i1_adc_conf, 0, 0, 0, 100) # U12
            cf.devx.ctrl_transfer(0x40, 0x22, v2_adc_conf, 0, 0, 0, 100) # U11
            cf.devx.ctrl_transfer(0x40, 0x22, i2_adc_conf, 0, 0, 0, 100) # U11
            time.sleep(0.1)
        elif cf.ADC_Mux_Mode.get() == 3: # VB and IA
            # cycle trhough default mux values as starting point
            # now set new mux values
            cf.devx.set_adc_mux(7)
            cf.devx.ctrl_transfer(0x40, 0x20, v1_adc_conf, 0, 0, 0, 100) # U12
            cf.devx.ctrl_transfer(0x40, 0x21, i1_adc_conf, 0, 0, 0, 100) # U12
            cf.devx.ctrl_transfer(0x40, 0x22, v2_adc_conf, 0, 0, 0, 100) # U11
            cf.devx.ctrl_transfer(0x40, 0x22, i2_adc_conf, 0, 0, 0, 100) # U11
            time.sleep(0.1)
        elif cf.ADC_Mux_Mode.get() == 4: # VA and IA
            # now set new mux values
            cf.devx.set_adc_mux(4)
        elif cf.ADC_Mux_Mode.get() == 5: # VB and IB
            # now set new mux values
            cf.devx.set_adc_mux(5)
        # Eigentlich wird für die globale Variable cf.SAMPLErate die Samplingrate auf 200000 gesetzt.
        cf.SAMPLErate = cf.BaseSampleRate * 2 # set to 2X sample mode
    else:
        # Wenn Samplingrate < 100.000 S/s muss kein gesonderter Mux Modus für cf.devx eingestellt werden.
        cf.devx.set_adc_mux(0)
        cf.SAMPLErate = cf.BaseSampleRate

def TraceSelectADC_Mux():
# Im Wesentlichen wird hier der ADC_Mux_Mode Wert gesetzt.
    global Alternate_Sweep_Mode
    if cf.devx != None:
        if cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # All four traces
            Alternate_Sweep_Mode = 1
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(0) # three traces
            Alternate_Sweep_Mode = 1
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # three traces
            Alternate_Sweep_Mode = 1
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # three traces
            Alternate_Sweep_Mode = 1
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # three traces
            Alternate_Sweep_Mode = 1
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(1) # IA and IB
            Alternate_Sweep_Mode = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(1) # just IA
            Alternate_Sweep_Mode = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(1) # just IB
            Alternate_Sweep_Mode = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(4) # VA and IA
            Alternate_Sweep_Mode = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(5) # VB and IB
            Alternate_Sweep_Mode = 0
            # VA und IB (Mux Mode 2) bzw. VB und IA (3) sind nicht vorgesehen.
        else:
            cf.ADC_Mux_Mode.set(0)
            Alternate_Sweep_Mode = 0
        SetADC_Mux()
        UpdateTimeTrace()
        
    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Hier wird für den AWG die doppelte Samplingrate eingestellt:
# Wie macht man VA und VB mit doppelter Samplingrate?
#def BAWG2X():
#    ReMakeAWGwaves()
#    if cf.AWG_2X == 0: # configure board for both AWG channels at 1X sampling
#        cf.devx.ctrl_transfer(0x40, 0x24, 0x0, 0, 0, 0, 100) # set to addr DAC A 
#        cf.devx.ctrl_transfer(0x40, 0x25, 0x1, 0, 0, 0, 100) # set to addr DAC B
#    elif cf.AWG_2X == 1: # configure board for single AWG channel A at 2X sampling
#        cf.devx.ctrl_transfer(0x40, 0x24, 0x0, 0, 0, 0, 100) # set to addr DAC A 
#        cf.devx.ctrl_transfer(0x40, 0x25, 0x0, 0, 0, 0, 100) # set t0 addr DAC A
#        cf.devx.ctrl_transfer(0x40, 0x51, 40, 0, 0, 0, 100) # set IN3 switch to open
#        cf.devx.ctrl_transfer(0x40, 0x51, 52, 0, 0, 0, 100) # set IN3 switch to open
#    elif cf.AWG_2X == 2: # configure board for single AWG channel B at 2X sampling
#        cf.devx.ctrl_transfer(0x40, 0x24, 0x1, 0, 0, 0, 100) # set to addr DAC B 
#        cf.devx.ctrl_transfer(0x40, 0x25, 0x1, 0, 0, 0, 100) # set to addr DAC B
#        cf.devx.ctrl_transfer(0x40, 0x51, 35, 0, 0, 0, 100) # set IN3 switch to open
#        cf.devx.ctrl_transfer(0x40, 0x51, 51, 0, 0, 0, 100) # set IN3 switch to open
        
# Function to left (-num) or right (+num) shift buffer and fill with a value
# returns same length buffer
# preallocate empty array and assign slice
def shift_buffer(arr, num, fill_value=np.nan):
    result = np.empty_like(arr)
    if num > 0:
        result[:num] = fill_value
        result[num:] = arr[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = arr[-num:]
    else:
        result[:] = arr
    return result