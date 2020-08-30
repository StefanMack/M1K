#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 30.8.20
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
from aliceAwgFunc import ReMakeAWGwaves
from aliceAwgFunc import BAWGAAmpl, BAWGAOffset, BAWGAFreq, BAWGAPhaseDelay,
BAWGAPhase, BAWGADutyCycle, BAWGAShape, SplitAWGAwaveform, AWGANumCycles,
AWGAMakeFMSine, AWGAMakeAMSine, AWGAMakePWMSine, AWGAMakeTrapazoid, AWGAMakePulse,
AWGAMakeRamp, AWGAMakeUpDownRamp, AWGAMakeImpulse, AWGAMakeUUNoise, AWGAMakeUGNoise,
BAWGAModeLabel, UpdateAWGA
from aliceAwgFunc import BAWGBAmpl, BAWGBOffset, BAWGBFreq, BAWGBPhaseDelay,
BAWGBPhase, BAWGBDutyCycle, BAWGBShape, SplitAWGBwaveform, AWGBNumCycles,
AWGBMakeFMSine, AWGBMakeAMSine, AWGBMakePWMSine, AWGBMakeTrapazoid, AWGBMakePulse,
AWGBMakeRamp, AWGBMakeUpDownRamp, AWGBMakeImpulse, AWGBMakeUUNoise, AWGBMakeUGNoise,
BAWGBModeLabel, UpdateAWGB,SetBCompA
from aliceMenus import MakeAWGMenu, UpdateAWGMenu, DestroyAWGMenu, MakeSampleRateMenu,
DestroySampleRateMenu, MakeSettingsMenu, UpdateSettingsMenu, DestroySettingsMenu,
MakeMeasureMenu, UpdateMeasureMenu, MakeMathMenu, DestroyMathMenu

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# M1K Samplingfunktionen
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
def Analog_In():
    global RUNstatus, SingleShot, ManualTrigger, TimeDisp, XYDisp, FreqDisp, SpectrumScreenStatus, HWRevOne
    global IADisp, IAScree, nStatus, CutDC, DevOne, AWGBMode, MuxEnb, BodeScreenStatus, BodeDisp
    global VBuffA, VBuffB, MuxSync
    global ShowC1_V, ShowC2_V, ShowC2_I, SMPfft
    global PIO_0, PIO_1, PIO_2, PIO_3, PIO_4, PIO_5, PIO_6, PIO_7
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2
    global SV1, SI1, SV2, SI2, SVA_B
    global FregPoint, FBins, FStep
    global TRACEresetTime, TRACEmodeTime, SettingsStatus
    
    while (True):       # Main loop
        # RUNstatus = 1 : Open Acquisition
        if (RUNstatus.get() == 1) or (RUNstatus.get() == 2):
            if SettingsStatus.get() == 1:
                UpdateSettingsMenu() # Make sure current entries in Settings controls are up to date
            if TimeDisp.get() > 0:
                Analog_Time_In()
        root.update_idletasks()
        root.update()

#---Read the analog data and store the data into the arrays
def Analog_Time_In():
    global TIMEdiv, TMsb, TRACEmodeTime, TRACEresetTime, TRACEaverage
    global VBuffMA, VmemoryMuxA, VBuffMB, VmemoryMuxB, VBuffMC, VmemoryMuxC, VBuffMD, VmemoryMuxD
    global CHAVOffsetEntry, CHAVGainEntry, CHBVOffsetEntry, CHBVGainEntry
    global CHAIOffsetEntry, CHBIOffsetEntry, CHAIGainEntry, CHBIGainEntry
    global InOffA, InGainA, InOffB, InGainB
    global CurOffA, CurOffB, CurGainA, CurGainB
    global PhADisp, PhAScreenStatus
    
    # get time scale
    try:
        TIMEdiv = eval(TMsb.get())
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"tk.END")
        TMsb.insert(0,TIMEdiv)
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.01
# Do input divider Calibration CH1VGain, CH2VGain, CH1VOffset, CH2VOffset
    try:
        InOffA = float(eval(CHAVOffsetEntry.get()))
    except:
        CHAVOffsetEntry.delete(0,tk.END)
        CHAVOffsetEntry.insert(0, InOffA)
    try:
        InGainA = float(eval(CHAVGainEntry.get()))
    except:
        CHAVGainEntry.delete(0,tk.END)
        CHAVGainEntry.insert(0, InGainA)
    try:
        InOffB = float(eval(CHBVOffsetEntry.get()))
    except:
        CHBVOffsetEntry.delete(0,tk.END)
        CHBVOffsetEntry.insert(0, InOffB)
    try:
        InGainB = float(eval(CHBVGainEntry.get()))
    except:
        CHBVGainEntry.delete(0,tk.END)
        CHBVGainEntry.insert(0, InGainB)
    try:
        CurOffA = float(CHAIOffsetEntry.get()) #/1000.0 # convert to Amps # leave in mA
    except:
        CurOffA = 0.0
    try:
        CurOffB = float(CHBIOffsetEntry.get())#/1000.0 # convert to Amps
    except:
        CurOffB = 0.0
    try:
        CurGainA = float(CHAIGainEntry.get())
    except:
        CurGainA = 1.0
    try:
        CurGainB = float(CHBIGainEntry.get())
    except:
        CurGainB = 1.0
## Es gibt wohl zwei verschiedene Samplingmethoden: slow und fast
## slow wird bei >500 ms/Div verwtk.ENDet, fast bei einer größeren Zeitablenkung
# Dedecide which Fast or Slow sweep routine to call
    if TIMEdiv > 500:
        Analog_Slow_time() # failed attempt as rolling trace
    else:
        Analog_Fast_time()


#---Right now this is a failed attempt to plot slow sweeps.
def Analog_Slow_time():
    global ADsignal1, VBuffA, VBuffB, IBuffA, IBuffB
    global VmemoryA, VmemoryB, ImemoryA, ImemoryB
    global AWGSync, AWGAMode, AWGBMode, TMsb, HoldOff, HoldOffentry, HozPoss, HozPossentry
    global TRACEresetTime, TRACEmodeTime, TRACEaverage, TRIGGERsample, TgInput, LShift
    global CHA, CHB, session, devx, discontloop, contloop
    global TRACEsize, First_Slow_sweep, ShiftPointer
    global RUNstatus, SingleShot, ManualTrigger, TimeDisp, XYDisp, FreqDisp
    global TIMEdiv1x, TIMEdiv, hldn, Is_Triggered
    global SAMPLErate, SHOWsamples, MinSamples, MaxSamples, AWGSAMPLErate
    global TRACErefresh, AWGScreenStatus, XYScreenStatus, MeasureStatus
    global SCREENrefresh, DCrefresh
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2
    global SV1, SI1, SV2, SI2, SVA_B
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAIPosEntry, CHBVPosEntry, CHBIPosEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global InOffA, InGainA, InOffB, InGainB, CurOffA, CurOffB, CurGainA, CurGainB
    global DigFiltA, DigFiltB, DFiltACoef, DFiltBCoef, DigBuffA, DigBuffB
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global VAets, VBets, Samples_Cycle, MulX, Fmin, FminE, eqivsamplerate
    global DivXEntry, FOffEntry, FminDisp, FOff, DivX, FMulXEntry, FBase
    global cal, Two_X_Sample, ADC_Mux_Mode, Alternate_Sweep_Mode, Last_ADC_Mux_Mode
    global MeasGateLeft, MeasGateRight, MeasGateNum, MeasGateStatus
    global PIO_0, PIO_1, PIO_2, PIO_3, PIO_4, PIO_5, PIO_6, PIO_7

    # Starting acquisition
    DCVA0 = DCVB0 = DCIA0 = DCIB0= 0.0 # initalize measurment variable
    #
    NumSamples = 1 # int(SAMPLErate/TIMEdiv)
    if First_Slow_sweep == 0:
        BufferLen = TIMEdiv*12.0
        VBuffA = np.ones(BufferLen)       
        VBuffB = np.ones(BufferLen)
        IBuffA = np.ones(BufferLen)       
        IBuffB = np.ones(BufferLen)
        First_Slow_sweep = 1
    #
    if AWGScreenStatus.get() == 1: # don't try to start AWG is AWG screen is closed
        if AWGSync.get() > 0: # awg syn flag set so run in discontinuous mode
            if discontloop > 0:
                session.flush()
            else:
                discontloop = 1
            BAWGEnab()
            ADsignal1 = devx.get_samples(NumSamples) # get samples for both channel A and B
            # waite to finish then return to open termination
            devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
            devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
            devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
            devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open

        else: # running in continuous mode
            if session.continuous:
                ADsignal1 = devx.read(NumSamples, -1, True) # get samples for both channel A and B
    #
    else:
        ADsignal1 = devx.get_samples(NumSamples) # , True) # get samples for both channel A and B

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
    VBuffA = shift_buffer(VBuffA, -1, DCVA0)
    VBuffB = shift_buffer(VBuffB, -1, DCVB0)
    IBuffA = shift_buffer(IBuffA, -1, DCIA0)
    IBuffB = shift_buffer(IBuffB, -1, DCIB0)
# Calculate measurement values
    DCV1 = np.mean(VBuffA)
    DCV2 = np.mean(VBuffB)
    DCI1 = np.mean(IBuffA)
    DCI2 = np.mean(IBuffB)
# find min and max values
    MinV1 = np.amin(VBuffA)
    MaxV1 = np.amax(VBuffA)
    MinV2 = np.amin(VBuffB)
    MaxV2 = np.amax(VBuffB)
    MinI1 = np.amin(IBuffA)
    MaxI1 = np.amax(IBuffA)
    MinI2 = np.amin(IBuffB)
    MaxI2 = np.amax(IBuffB)
# RMS value = square root of average of the data record squared
    SV1 = np.sqrt(np.mean(np.square(VBuffA)))
    SI1 = np.sqrt(np.mean(np.square(IBuffA)))
    SV2 = np.sqrt(np.mean(np.square(VBuffB)))
    SI2 = np.sqrt(np.mean(np.square(IBuffB)))
    SVA_B = np.sqrt(np.mean(np.square(VBuffA-VBuffB)))
#
    if TimeDisp.get() > 0:
        UpdateTimeAll()         # Update Data, trace and time screen
    if MeasureStatus.get() > 0:
        UpdateMeasureMenu()
    if (RUNstatus.get() == 3) or (RUNstatus.get() == 4):
        if RUNstatus.get() == 3:
            RUNstatus.set(0)
        if RUNstatus.get() == 4:          
            RUNstatus.set(1)
        if TimeDisp.get() > 0:
            UpdateTimeScreen()
        # update screens

## Wie unterscheidet sich dieses Sampling vom Slow Mode?
#---routine for time scales faster than 500 mSec/Div
def Analog_Fast_time():
    global ADsignal1, VBuffA, VBuffB, IBuffA, IBuffB
    global VmemoryA, VmemoryB, ImemoryA, ImemoryB
    global AWGSync, AWGAMode, AWGBMode, TMsb, HoldOff, HoldOffentry, HozPoss, HozPossentry
    global TRACEresetTime, TRACEmodeTime, TRACEaverage, TRIGGERsample, TgInput, LShift
    global CHA, CHB, session, devx, discontloop, contloop, DeBugMode
    global TRACEsize
    global RUNstatus, SingleShot, ManualTrigger, TimeDisp, XYDisp, FreqDisp
    global TIMEdiv1x, TIMEdiv, hldn, Is_Triggered, Trigger_LPF_length, LPFTrigger
    global SAMPLErate, SHOWsamples, SMPfft, MinSamples, MaxSamples, AWGSAMPLErate
    global TRACErefresh, AWGScreenStatus, XYScreenStatus, MeasureStatus
    global SCREENrefresh, DCrefresh
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2
    global SV1, SI1, SV2, SI2, SVA_B
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAIPosEntry, CHBVPosEntry, CHBIPosEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global InOffA, InGainA, InOffB, InGainB, CurOffA, CurOffB, CurGainA, CurGainB
    global DigFiltA, DigFiltB, DFiltACoef, DFiltBCoef, DigBuffA, DigBuffB
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2, CHAI_RC_HP, CHBI_RC_HP
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global VAets, VBets, Samples_Cycle, MulX, Fmin, FminE, eqivsamplerate
    global DivXEntry, FOffEntry, FminDisp, FOff, DivX, FMulXEntry, FBase 
    global cal, Two_X_Sample, ADC_Mux_Mode, Alternate_Sweep_Mode, Last_ADC_Mux_Mode
    global MeasGateLeft, MeasGateRight, MeasGateNum, MeasGateStatus    
    global PIO_0, PIO_1, PIO_2, PIO_3, PIO_4, PIO_5, PIO_6, PIO_7

    if TRACEmodeTime.get() == 0 and TRACEresetTime == False:
        TRACEresetTime = True               # Clear the memory for averaging
    elif TRACEmodeTime.get() == 1:
        if TRACEresetTime == True:
            TRACEresetTime = False
        # Save previous trace in memory for average trace
        VmemoryA = VBuffA
        VmemoryB = VBuffB
        ImemoryA = IBuffA
        ImemoryB = IBuffB

    try:
        HoldOff = float(eval(HoldOffentry.get()))
        if HoldOff < 0:
            HoldOff = 0
            HoldOffentry.delete(0,tk.END)
            HoldOffentry.insert(0, HoldOff)
    except:
        HoldOffentry.delete(0,tk.END)
        HoldOffentry.insert(0, HoldOff)
#
    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,tk.END)
        HozPossentry.insert(0, HozPoss)

    hldn = int(HoldOff * SAMPLErate/1000 )
    hozpos = int(HozPoss * SAMPLErate/1000 )
    if hozpos < 0:
        hozpos = 0
    twoscreens = int(SAMPLErate * 20.0 * TIMEdiv / 1000.0) # number of samples to acquire, 2 screen widths
    onescreen = int(twoscreens/2)
    if hldn+hozpos > MaxSamples-twoscreens:
        hldn = MaxSamples-twoscreens-hozpos
        HoldOffentry.delete(0,tk.END)
        HoldOffentry.insert(0, hldn*1000/SAMPLErate)
      
    SHOWsamples = twoscreens + hldn + hozpos
    if SHOWsamples > MaxSamples: # or a Max of 100,000 samples
        SHOWsamples = MaxSamples
    if SHOWsamples < MinSamples: # or a Min of 1000 samples
        SHOWsamples = MinSamples
    if PhAScreenStatus.get() > 0:
        if SHOWsamples < SMPfft:
            SHOWsamples = SMPfft + hldn + hozpos
    if hozpos >= 0:
        TRIGGERsample = hldn
    else:
        TRIGGERsample = abs(hozpos)
    TRIGGERsample = TRIGGERsample + hozpos #
# Starting acquisition
    if AWGScreenStatus.get() == 1: # don't try to start AWG is AWG screen is closed
        if AWGSync.get() > 0: # awg syn flag set so run in discontinuous mode
            if discontloop > 0:
                session.flush()
            else:
                discontloop = 1
            time.sleep(0.01)
            BAWGEnab()
            ADsignal1 = devx.get_samples(SHOWsamples) # get samples for both channel A and B
            # waite to finish then return to open termination
            devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
            devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
            devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
            devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
        else: # running in continuous mode
            if session.continuous:
                ADsignal1 = devx.read(SHOWsamples, -1, True) # get samples for both channel A and B
    #
    else:
        ADsignal1 = devx.get_samples(SHOWsamples) # , True) # get samples for both channel A and B
        # waite to finish then return to open termination
        devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
        devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    
    # MUX-Modi: Modus 0 macht für Sensortechnik am meisten Sinn, wenn für Ultraschallsensor mit 200.000 S/s
    if Alternate_Sweep_Mode.get() == 1 and Two_X_Sample.get() == 1:
        if ADC_Mux_Mode.get() == 0: # VA and VB
            VBuffA = [] # Clear the V Buff array for trace A
            VBuffB = [] # Clear the V Buff array for trace B
        elif ADC_Mux_Mode.get() == 1: # IA and IB
            IBuffA = [] # Clear the I Buff array for trace A
            IBuffB = [] # Clear the I Buff array for trace B
        elif ADC_Mux_Mode.get() == 4: # VA and IA
            VBuffA = [] # Clear the V Buff array for trace A
            IBuffA = [] # Clear the I Buff array for trace A
        elif ADC_Mux_Mode.get() == 5: # VB and IB
            VBuffB = [] # Clear the V Buff array for trace B
            IBuffB = [] # Clear the I Buff array for trace B
    else:
        VBuffA = [] # Clear the V Buff array for trace A
        IBuffA = [] # Clear the I Buff array for trace A
        VBuffB = [] # Clear the V Buff array for trace B
        IBuffB = [] # Clear the I Buff array for trace B
    increment = 1
    index = 0
    if SHOWsamples != len(ADsignal1):
        SHOWsamples = len(ADsignal1)
    while index < SHOWsamples: # build arrays and decimate if needed
    ## Samplingrate 200.000 S/s geht nur, wenn nur zwei der 4 möglichen Größen
    ## VA, IA, VB, IB gemessen werden. Welche das sind wird über den ADC_Mux_Mode
    ## bestimmt.
    
        if Two_X_Sample.get() == 1 and ADC_Mux_Mode.get() < 6:
            if ADC_Mux_Mode.get() == 0: # VA and VB
                VBuffA.apptk.END(ADsignal1[index][0][0])
                VBuffA.apptk.END(ADsignal1[index][1][1])
                VBuffB.apptk.END(ADsignal1[index][0][1])
                VBuffB.apptk.END(ADsignal1[index][1][0])
                if Alternate_Sweep_Mode.get() == 0:
                    IBuffA.apptk.END(0.0) # fill as a place holder
                    IBuffA.apptk.END(0.0) # fill as a place holder
                    IBuffB.apptk.END(0.0) # fill as a place holder
                    IBuffB.apptk.END(0.0) # fill as a place holder
            elif ADC_Mux_Mode.get() == 1: # IA and IB
                IBuffA.apptk.END(ADsignal1[index][0][1])
                IBuffA.apptk.END(ADsignal1[index][1][0])
                IBuffB.apptk.END(ADsignal1[index][0][0])
                IBuffB.apptk.END(ADsignal1[index][1][1])
                if Alternate_Sweep_Mode.get() == 0:
                    VBuffA.apptk.END(0.0) # fill as a place holder
                    VBuffA.apptk.END(0.0) # fill as a place holder
                    VBuffB.apptk.END(0.0) # fill as a place holder
                    VBuffB.apptk.END(0.0) # fill as a place holder
            elif ADC_Mux_Mode.get() == 2: # VA and IB
                VBuffA.apptk.END((ADsignal1[index][0][1])/1024.0)
                VBuffA.apptk.END((ADsignal1[index][1][0])/1024.0)
                #
                IBuffB.apptk.END( ((ADsignal1[index][0][0])/4096.0)-0.5 )
                IBuffB.apptk.END( ((ADsignal1[index][1][1])/4096.0)-0.5 ) 
                #
                if Alternate_Sweep_Mode.get() == 0:
                    VBuffB.apptk.END(0.0) # fill as a place holder
                    VBuffB.apptk.END(0.0) # fill as a place holder
                    IBuffA.apptk.END(0.0) # fill as a place holder
                    IBuffA.apptk.END(0.0) # fill as a place holder
            elif ADC_Mux_Mode.get() == 3: # VB and IA
                VBuffB.apptk.END((ADsignal1[index][0][0])/1024.0)
                VBuffB.apptk.END((ADsignal1[index][1][1])/1024.0)
                #
                IBuffA.apptk.END( ((ADsignal1[index][0][1])/4096.0)-0.5 )
                IBuffA.apptk.END( ((ADsignal1[index][1][0])/4096.0)-0.5 )
                #
                if Alternate_Sweep_Mode.get() == 0:
                    VBuffA.apptk.END(0.0) # fill as a place holder
                    VBuffA.apptk.END(0.0) # fill as a place holder
                    IBuffB.apptk.END(0.0) # fill as a place holder
                    IBuffB.apptk.END(0.0) # fill as a place holder
            elif ADC_Mux_Mode.get() == 4: # VA and IA
                VBuffA.apptk.END(ADsignal1[index][0][0])
                VBuffA.apptk.END(ADsignal1[index][1][1])
                IBuffA.apptk.END(ADsignal1[index][0][1])
                IBuffA.apptk.END(ADsignal1[index][1][0])
                if Alternate_Sweep_Mode.get() == 0:
                    VBuffB.apptk.END(0.0) # fill as a place holder
                    VBuffB.apptk.END(0.0) # fill as a place holder
                    IBuffB.apptk.END(0.0) # fill as a place holder
                    IBuffB.apptk.END(0.0) # fill as a place holder
            elif ADC_Mux_Mode.get() == 5: # VB and IB
                VBuffB.apptk.END(ADsignal1[index][0][1])
                VBuffB.apptk.END(ADsignal1[index][1][0])
                IBuffB.apptk.END(ADsignal1[index][0][0])
                IBuffB.apptk.END(ADsignal1[index][1][1])
                if Alternate_Sweep_Mode.get() == 0:
                    VBuffA.apptk.END(0.0) # fill as a place holder
                    VBuffA.apptk.END(0.0) # fill as a place holder
                    IBuffA.apptk.END(0.0) # fill as a place holder
                    IBuffA.apptk.END(0.0) # fill as a place holder
        else:
            VBuffA.apptk.END(ADsignal1[index][0][0])
            IBuffA.apptk.END(ADsignal1[index][0][1])
            VBuffB.apptk.END(ADsignal1[index][1][0])
            IBuffB.apptk.END(ADsignal1[index][1][1])
        index = index + increment
#
    SHOWsamples = len(VBuffA)
    if Alternate_Sweep_Mode.get() == 1 and Two_X_Sample.get() == 1:
        if ADC_Mux_Mode.get() == 0: # VA and VB
            VBuffA = np.array(VBuffA)
            VBuffB = np.array(VBuffB)
            VBuffA = (VBuffA - InOffA) * InGainA
            VBuffB = (VBuffB - InOffB) * InGainB
            ADC_Mux_Mode.set(1) # switch mode
            Last_ADC_Mux_Mode = 0
        elif ADC_Mux_Mode.get() == 1: # IA and IB
            IBuffA = np.array(IBuffA) * 1000 # convert to mA
            IBuffB = np.array(IBuffB) * 1000 # convert to mA
            IBuffA = (IBuffA - CurOffA) * CurGainA
            IBuffB = (IBuffB - CurOffB) * CurGainB
            ADC_Mux_Mode.set(Last_ADC_Mux_Mode) # switch mode
        elif ADC_Mux_Mode.get() == 4: # VA and IA
            VBuffA = np.array(VBuffA)
            IBuffA = np.array(IBuffA) * 1000 # convert to mA
            IBuffA = (IBuffA - CurOffA) * CurGainA
            VBuffA = (VBuffA - InOffA) * InGainA
            ADC_Mux_Mode.set(1) # switch mode
            Last_ADC_Mux_Mode = 4
        elif ADC_Mux_Mode.get() == 5: # VB and IB
            VBuffB = np.array(VBuffB)
            VBuffB = (VBuffB - InOffB) * InGainB
            IBuffB = np.array(IBuffB) * 1000 # convert to mA
            IBuffB = (IBuffB - CurOffB) * CurGainB
            ADC_Mux_Mode.set(1) # switch mode
            Last_ADC_Mux_Mode = 5
        SetADC_Mux()
    #
    else:
        VBuffA = np.array(VBuffA)
        VBuffB = np.array(VBuffB)
        IBuffA = np.array(IBuffA) * 1000 # convert to mA
        IBuffB = np.array(IBuffB) * 1000 # convert to mA
        VBuffA = (VBuffA - InOffA) * InGainA
        VBuffB = (VBuffB - InOffB) * InGainB
        IBuffA = (IBuffA - CurOffA) * CurGainA
        IBuffB = (IBuffB - CurOffB) * CurGainB

    
# Find trigger sample point if necessary
    LShift = 0
    if TgInput.get() == 1:
        FindTriggerSample(VBuffA)
    if TgInput.get() == 2:
        FindTriggerSample(IBuffA)
    if TgInput.get() == 3:
        FindTriggerSample(VBuffB)
    if TgInput.get() == 4:
        FindTriggerSample(IBuffB)
    if TRACEmodeTime.get() == 1 and TRACEresetTime == False:
        # Average mode 1, add difference / TRACEaverage to array
        if TgInput.get() > 0: # if triggering left shift all arrays such that trigger point is at index 0
            LShift = 0 - TRIGGERsample
            VBuffA = np.roll(VBuffA, LShift)
            VBuffB = np.roll(VBuffB, LShift)
            IBuffA = np.roll(IBuffA, LShift)
            IBuffB = np.roll(IBuffB, LShift)
            TRIGGERsample = hozpos # set trigger sample to index 0 offset by horizontal position
        try:
            VBuffA = VmemoryA + (VBuffA - VmemoryA) / TRACEaverage.get()
            IBuffA = ImemoryA + (IBuffA - ImemoryA) / TRACEaverage.get()
            VBuffB = VmemoryB + (VBuffB - VmemoryB) / TRACEaverage.get()
            IBuffB = ImemoryB + (IBuffB - ImemoryB) / TRACEaverage.get()
        except:
            # buffer size mismatch so reset memory buffers
            VmemoryA = VBuffA
            VmemoryB = VBuffB
            ImemoryA = IBuffA
            ImemoryB = IBuffB
        if TgInput.get() == 1:
            ReInterploateTrigger(VBuffA)
        if TgInput.get() == 2:
            ReInterploateTrigger(IBuffA)
        if TgInput.get() == 3:
            ReInterploateTrigger(VBuffB)
        if TgInput.get() == 4:
            ReInterploateTrigger(IBuffB)
# DC value = average of the data record
    if CHA_RC_HP.get() == 1 or CHB_RC_HP.get() == 1:
        tk.ENDsample = hldn+onescreen # average over only one screen's worth of samples ?Ist das vielleicht der große Unterschied zu slow?
    else:
        tk.ENDsample = SHOWsamples - 10 # average over all samples
    if MeasGateStatus.get() == 1:
        if (MeasGateRight-MeasGateLeft) > 0:
            hldn = int(MeasGateLeft * SAMPLErate/1000) + TRIGGERsample
            tk.ENDsample = int(MeasGateRight * SAMPLErate/1000) + TRIGGERsample
            if tk.ENDsample <= hldn:
                tk.ENDsample = hldn + 2
    ## Berechnung Messwerte im Fast Scan Modus auch für jeden Trace            
    DCV1 = np.mean(VBuffA[hldn:tk.ENDsample])
    DCV2 = np.mean(VBuffB[hldn:tk.ENDsample])
    # convert current values to mA
    DCI1 = np.mean(IBuffA[hldn:tk.ENDsample])
    DCI2 = np.mean(IBuffB[hldn:tk.ENDsample])
# find min and max values
    MinV1 = np.amin(VBuffA[hldn:tk.ENDsample])
    MaxV1 = np.amax(VBuffA[hldn:tk.ENDsample])
    MinV2 = np.amin(VBuffB[hldn:tk.ENDsample])
    MaxV2 = np.amax(VBuffB[hldn:tk.ENDsample])
    MinI1 = np.amin(IBuffA[hldn:tk.ENDsample])
    MaxI1 = np.amax(IBuffA[hldn:tk.ENDsample])
    MinI2 = np.amin(IBuffB[hldn:tk.ENDsample])
    MaxI2 = np.amax(IBuffB[hldn:tk.ENDsample])
# RMS value = square root of average of the data record squared
    SV1 = np.sqrt(np.mean(np.square(VBuffA[hldn:tk.ENDsample])))
    SI1 = np.sqrt(np.mean(np.square(IBuffA[hldn:tk.ENDsample])))
    SV2 = np.sqrt(np.mean(np.square(VBuffB[hldn:tk.ENDsample])))
    SI2 = np.sqrt(np.mean(np.square(IBuffB[hldn:tk.ENDsample])))
    SVA_B = np.sqrt(np.mean(np.square(VBuffA[hldn:tk.ENDsample]-VBuffB[hldn:tk.ENDsample])))

    if TimeDisp.get() > 0:
        UpdateTimeAll()         # Update Data, trace and time screen
       # Update Data, trace
    if SingleShot.get() > 0 and Is_Triggered == 1: # Singel Shot trigger is on
        BStop() # 
        SingleShot.set(0)
    if ManualTrigger.get() == 1: # Manual trigger is on
        BStop() # 
    if MeasureStatus.get() > 0:
        UpdateMeasureMenu()
    if (RUNstatus.get() == 3) or (RUNstatus.get() == 4):
        if RUNstatus.get() == 3:
            RUNstatus.set(0)
        if RUNstatus.get() == 4:          
            RUNstatus.set(1)
        if TimeDisp.get() > 0:
            UpdateTimeScreen()
            
            
# Einstellen der Samplingrate, falls im Fenster diese geändert wurde
def SetSampleRate():
    global SAMPLErate, BaseSampleRate, AWGSAMPLErate, session, etssrlab, BaseRatesb
    global Two_X_Sample, ADC_Mux_Mode, rtsrlab, RUNstatus
    #
    WasRunning = 0
    if (RUNstatus.get() == 1):
        WasRunning = 1
        BStop() # Force Stop loop if running
    try:
        NewRate = int(BaseRatesb.get())
        # Basis-Samplingrate kann nicht größer als 100.000 S/s sein wenn diese direkt über
        # die Benutzeroberfläche eingegeben wird. Der Wert 200.000 S/s geht nur über den
        # Button "Two_X_Sample"
        if NewRate <= 100000: # rate has to be less than or equal to 100,000
            BaseSampleRate = NewRate
        else:
        # Bei zu großer Samplinrate wird diese im Fenster auf 100000 zurück gesetzt
            BaseSampleRate = 100000
            BaseRatesb.delete(0,"tk.END")
            BaseRatesb.insert(0,BaseSampleRate)
        SAMPLErate = BaseSampleRate # Scope sample rate
    except:
        pass
    # Samplingrate wird tatsächlich direkt am M1K eingestellt
    session.configure(sample_rate=BaseSampleRate)
    BaseSampleRate = session.sample_rate
    #print("Session sample rate: " + str(session.sample_rate), BaseSampleRate)
    SAMPLErate = BaseSampleRate # Scope sample rate
    #print("Session sample rate: " + str(session.sample_rate), SAMPLErate)
    AWGSAMPLErate = BaseSampleRate
    BaseRatesb.delete(0,"tk.END")
    BaseRatesb.insert(0,BaseSampleRate)
    ReMakeAWGwaves() # remake AWG waveforms for new rate
    if (WasRunning == 1):
        WasRunning = 0
        BStart() # restart loop if was running
          
#**************************************************
# Hier Einstellung der Samplingrate auf 200.000 S/s
#**************************************************
# Wieso wird zwischen ADC_Mux_Mode und devx.set_adc_mux() unterschieden, bzw.
# wieso stimmen die Nummern nicht bei jedem Modus überein?
def SetADC_Mux():
# Der ADC_Mux _Mode wird über unterschiedliche Menüs gesetzt: Samplinrate oder hier das Aktivieren der unterschiedlichen Kanäle.
# Das ist wohl der Grund wieso für die Hardware der Mux-Mode mit devx.set_mux_mode() eingestellt wird. Die Tkinter-Variable ADC_Mux_Mode
# ist in erster Linie dafür da, die Buttons auszulesen und deren Zustand zu setzen.
    global devx, SAMPLErate, BaseSampleRate, Two_X_Sample, ADC_Mux_Mode, CHA, CHB
    global v1_adc_conf, i1_adc_conf, v2_adc_conf, i2_adc_conf
    #!! ADC_Mux_Mode und devx Mux Mode teils nicht gleich
    if Two_X_Sample.get() == 1:
    # Der Mux-Mode hat was damit zu tun, welche Kombination von VA, IA, VB und IB abgetastet wird
        if ADC_Mux_Mode.get() == 0: # VA and VB
            devx.set_adc_mux(1)
        elif ADC_Mux_Mode.get() == 1: # IA and IB
            devx.set_adc_mux(2)
        #Wieso hier so kompliziert?
        elif ADC_Mux_Mode.get() == 2: # VA and IB
            # cycle trhough default mux values as starting point
            devx.set_adc_mux(2)
            # now set new mux values
            devx.set_adc_mux(7)
            devx.ctrl_transfer(0x40, 0x20, v1_adc_conf, 0, 0, 0, 100) # U12
            devx.ctrl_transfer(0x40, 0x21, i1_adc_conf, 0, 0, 0, 100) # U12
            devx.ctrl_transfer(0x40, 0x22, v2_adc_conf, 0, 0, 0, 100) # U11
            devx.ctrl_transfer(0x40, 0x22, i2_adc_conf, 0, 0, 0, 100) # U11
            time.sleep(0.1)
        elif ADC_Mux_Mode.get() == 3: # VB and IA
            # cycle trhough default mux values as starting point
            # now set new mux values
            devx.set_adc_mux(7)
            devx.ctrl_transfer(0x40, 0x20, v1_adc_conf, 0, 0, 0, 100) # U12
            devx.ctrl_transfer(0x40, 0x21, i1_adc_conf, 0, 0, 0, 100) # U12
            devx.ctrl_transfer(0x40, 0x22, v2_adc_conf, 0, 0, 0, 100) # U11
            devx.ctrl_transfer(0x40, 0x22, i2_adc_conf, 0, 0, 0, 100) # U11
            time.sleep(0.1)
        elif ADC_Mux_Mode.get() == 4: # VA and IA
            # now set new mux values
            devx.set_adc_mux(4)
        elif ADC_Mux_Mode.get() == 5: # VB and IB
            # now set new mux values
            devx.set_adc_mux(5)
        # Eigentlich wird für die globale Variable SAMPLErate die Samplingrate auf 200000 gesetzt.
        SAMPLErate = BaseSampleRate * 2 # set to 2X sample mode
    else:
        # Wenn Samplingrate < 100.000 S/s muss kein gesonderter Mux Modus für devx eingestellt werden.
        devx.set_adc_mux(0)
        SAMPLErate = BaseSampleRate

def TraceSelectADC_Mux():
# Im Wesentlichen wird hier der ADC_Mux_Mode Wert gesetzt.
    global ADC_Mux_Mode, Alternate_Sweep_Mode, ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I
    if ShowC1_V.get() == 1 and ShowC1_I.get() == 1 and ShowC2_V.get() == 1 and ShowC2_I.get() == 1:
        ADC_Mux_Mode.set(0) # All four traces
        Alternate_Sweep_Mode.set(1)
    elif ShowC1_V.get() == 1 and ShowC1_I.get() == 1 and ShowC2_V.get() == 1 and ShowC2_I.get() == 0:
        ADC_Mux_Mode.set(0) # three traces
        Alternate_Sweep_Mode.set(1)
    elif ShowC1_V.get() == 1 and ShowC1_I.get() == 1 and ShowC2_V.get() == 0 and ShowC2_I.get() == 1:
        ADC_Mux_Mode.set(0) # three traces
        Alternate_Sweep_Mode.set(1)
    elif ShowC1_V.get() == 0 and ShowC1_I.get() == 1 and ShowC2_V.get() == 1 and ShowC2_I.get() == 1:
        ADC_Mux_Mode.set(0) # three traces
        Alternate_Sweep_Mode.set(1)
    elif ShowC1_V.get() == 1 and ShowC1_I.get() == 0 and ShowC2_V.get() == 1 and ShowC2_I.get() == 1:
        ADC_Mux_Mode.set(0) # three traces
        Alternate_Sweep_Mode.set(1)
    elif ShowC1_V.get() == 0 and ShowC1_I.get() == 1 and ShowC2_V.get() == 0 and ShowC2_I.get() == 1:
        ADC_Mux_Mode.set(1) # IA and IB
        Alternate_Sweep_Mode.set(0)
    elif ShowC1_V.get() == 0 and ShowC1_I.get() == 1 and ShowC2_V.get() == 0 and ShowC2_I.get() == 0:
        ADC_Mux_Mode.set(1) # just IA
        Alternate_Sweep_Mode.set(0)
    elif ShowC1_V.get() == 0 and ShowC1_I.get() == 0 and ShowC2_V.get() == 0 and ShowC2_I.get() == 1:
        ADC_Mux_Mode.set(1) # just IB
        Alternate_Sweep_Mode.set(0)
    elif ShowC1_V.get() == 1 and ShowC1_I.get() == 1 and ShowC2_V.get() == 0 and ShowC2_I.get() == 0:
        ADC_Mux_Mode.set(4) # VA and IA
        Alternate_Sweep_Mode.set(0)
    elif ShowC1_V.get() == 0 and ShowC1_I.get() == 0 and ShowC2_V.get() == 1 and ShowC2_I.get() == 1:
        ADC_Mux_Mode.set(5) # VB and IB
        Alternate_Sweep_Mode.set(0)
        # VA und IB (Mux Mode 2) bzw. VB und IA (3) sind nicht vorgesehen.
    else:
        ADC_Mux_Mode.set(0)
        Alternate_Sweep_Mode.set(0)
    SetADC_Mux()
    UpdateTimeTrace()
    
    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Hier wird für den AWG die doppelte Samplingrate eingestellt:
# Wie macht man VA und VB mit doppelter Samplingrate?
def BAWG2X():
    global AWG_2X, devx

    ReMakeAWGwaves()
    if AWG_2X.get() == 0: # configure board for both AWG channels at 1X sampling
        devx.ctrl_transfer(0x40, 0x24, 0x0, 0, 0, 0, 100) # set to addr DAC A 
        devx.ctrl_transfer(0x40, 0x25, 0x1, 0, 0, 0, 100) # set to addr DAC B
    elif AWG_2X.get() == 1: # configure board for single AWG channel A at 2X sampling
        devx.ctrl_transfer(0x40, 0x24, 0x0, 0, 0, 0, 100) # set to addr DAC A 
        devx.ctrl_transfer(0x40, 0x25, 0x0, 0, 0, 0, 100) # set t0 addr DAC A
        devx.ctrl_transfer(0x40, 0x51, 40, 0, 0, 0, 100) # set IN3 switch to open
        devx.ctrl_transfer(0x40, 0x51, 52, 0, 0, 0, 100) # set IN3 switch to open
    elif AWG_2X.get() == 2: # configure board for single AWG channel B at 2X sampling
        devx.ctrl_transfer(0x40, 0x24, 0x1, 0, 0, 0, 100) # set to addr DAC B 
        devx.ctrl_transfer(0x40, 0x25, 0x1, 0, 0, 0, 100) # set to addr DAC B
        devx.ctrl_transfer(0x40, 0x51, 35, 0, 0, 0, 100) # set IN3 switch to open
        devx.ctrl_transfer(0x40, 0x51, 51, 0, 0, 0, 100) # set IN3 switch to open
        
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