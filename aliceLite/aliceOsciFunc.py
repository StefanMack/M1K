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

from aliceM1kSamp import Analog_In, Analog_Time_In, Analog_Slow_time, shift_buffer,
Analog_Fast_time, SetSampleRate, SetADC_Mux, TraceSelectADC_Mux, BAWG2X

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Oszilloskop Funktionen Vertikal-/Horizontaldarstellung
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Ask user for new Marker text location on screen
def BSetMarkerLocation():
    global MarkerLoc
    TempString = MarkerLoc
    MarkerLoc = askstring("Marker Text Location", "Current Marker Text Location: " + MarkerLoc + "\n\nNew Location: (UL, UR, LL, LR)\n", initialvalue=MarkerLoc)
    if (MarkerLoc == None):         # If Cancel pressed, then None
        MarkerLoc = TempString
    UpdateTimeTrace()

# Set to display all time waveforms
def BShowCurvesAll():
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I
    ShowC1_V.set(1)
    ShowC1_I.set(1)
    ShowC2_V.set(1)
    ShowC2_I.set(1)
    UpdateTimeTrace()
    
## Turn off display of all time waveforms
def BShowCurvesNone():
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I
    ShowC1_V.set(0)
    ShowC1_I.set(0)
    ShowC2_V.set(0)
    ShowC2_I.set(0)
    UpdateTimeTrace()
    
## Stop (pause) scope tool
def BStop():
    global RUNstatus, TimeDisp, session, AWGSync
    global CHA, CHB, contloop, discontloop  
    if (RUNstatus.get() == 1):
        # print("Stoping")
        RUNstatus.set(0)
        CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
        if AWGSync.get() == 0: # running in continuous mode
            CHA.constant(0.0)
            CHB.constant(0.0)
            # print("Stoping continuous mode")
            # session.cancel() # cancel continuous session mode while paused
            if session.continuous:
                #print( "Is Continuous? ", session.continuous)
                session.end()
                #time.sleep(0.02)
                #print( "Is Continuous? ", session.continuous)
        else:
            contloop = 0
            discontloop = 1
            session.cancel()
    if TimeDisp.get() > 0:
        UpdateTimeScreen()          # Always Update screens as necessary

# Set Hor time scale from entry widget
def BTime():
    global TIMEdiv, TMsb, RUNstatus, Two_X_Sample
    try: # get time scale in mSec/div
        TIMEdiv = float(eval(TMsb.get()))
        if TIMEdiv < 0.0002:
            TIMEdiv = 0.01
            TMsb.delete(0,"end")
            TMsb.insert(0,TIMEdiv)
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
    # Switch to 2X sampleling if time scale small enough
    Samples_per_div = TIMEdiv * 100.0 # samples per mSec @ base sample rate
    if Samples_per_div < 20.0:
        Two_X_Sample.set(1)
    else:
        Two_X_Sample.set(0)
    SetADC_Mux()
    #
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)
    UpdateTimeTrace()           # Always Update

#---Set Horx possition from entry widget
def BHozPoss(event):
    global HozPoss, HozPossentry
    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,tk.END)
        HozPossentry.insert(0, HozPoss)

def SetVAPoss():
    global CHAVPosEntry, DCV1    
    CHAVPosEntry.delete(0,"tk.END")
    CHAVPosEntry.insert(0, ' {0:.2f} '.format(DCV1))

def SetVBPoss():
    global CHBVPosEntry, DCV2  
    CHBVPosEntry.delete(0,"tk.END")
    CHBVPosEntry.insert(0, ' {0:.2f} '.format(DCV2))

def SetIAPoss():
    global CHAIPosEntry, DCI1    
    CHAIPosEntry.delete(0,"tk.END")
    CHAIPosEntry.insert(0, ' {0:.2f} '.format(DCI1))

def SetIBPoss():
    global CHBIPosEntry, DCI2   
    CHBIPosEntry.delete(0,"tk.END")
    CHBIPosEntry.insert(0, ' {0:.2f} '.format(DCI2))

def BCHAlevel():
    global CHAsb   
    try:
        CH1vpdvLevel = float(eval(CHAsb.get()))
    except:
        CHAsb.delete(0,tk.END)
        CHAsb.insert(0, CH1vpdvLevel)
    UpdateTimeTrace()           # Always Update

def BCHAIlevel():
    global CHAIsb   
    try:
        CH1ipdvLevel = float(eval(CHAIsb.get()))
    except:
        CHAIsb.delete(0,tk.END)
        CHAIsb.insert(0, CH1ipdvLevel)
    UpdateTimeTrace()           # Always Update

def BCHBlevel():
    global CHBsb   
    try:
        CH2vpdvLevel = float(eval(CHBsb.get()))
    except:
        CHBsb.delete(0,tk.END)
        CHBsb.insert(0, CH2vpdvLevel)
    UpdateTimeTrace()           # Always Update    

def BCHBIlevel():
    global CHBIsb    
    try:
        CH2ipdvLevel = float(eval(CHBIsb.get()))
    except:
        CHBIsb.delete(0,tk.END)
        CHBIsb.insert(0, CH2ipdvLevel)
    UpdateTimeTrace()           # Always Update    

def BOffsetA(event):
    global CHAOffset, CHAVPosEntry
    try:
        CHAOffset = float(eval(CHAVPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHAVPosEntry.delete(0,tk.END)
        CHAVPosEntry.insert(0, CHAOffset)
    # set new offset level
    UpdateTimeTrace()           # Always Update

def BIOffsetA(event):
    global CHAIOffset, CHAIPosEntry
    try:
        CHAIOffset = float(eval(CHAIPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHAIPosEntry.delete(0,tk.END)
        CHAIPosEntry.insert(0, CHAIOffset)
    # set new offset level
    UpdateTimeTrace()           # Always Update

def BOffsetB(event):
    global CHBOffset, CHBVPosEntry
    try:
        CHBOffset = float(eval(CHBVPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHBVPosEntry.delete(0,tk.END)
        CHBVPosEntry.insert(0, CHBOffset)
    # set new offset level
    UpdateTimeTrace()           # Always Update

def BIOffsetB(event):
    global CHBIOffset, CHBIPosEntry
    try:
        CHBIOffset = float(eval(CHBIPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHBIPosEntry.delete(0,tk.END)
        CHBIPosEntry.insert(0, CHBIOffset)
    # set new offset level
    UpdateTimeTrace()           # Always Update

## Start aquaring scope time data
def BStart():
    global RUNstatus, PowerStatus, devx, PwrBt, DevID, session, AWGSync
    global contloop, discontloop, TIMEdiv, First_Slow_sweep
    
    if DevID == "No Device":
        tk.showwarning("WARNING","No Device Plugged In!")
    elif FWRevOne < 2.17:
        tk.showwarning("WARNING","Out of data Firmware! 2.17 oder higher needed.")
    else:
        if PowerStatus == 0:
            PowerStatus = 1
            PwrBt.config(style="Pwr.TButton",text="PWR-On")
            devx.ctrl_transfer( 0x40, 0x51, 49, 0, 0, 0, 100) # turn on analog power
        if (RUNstatus.get() == 0):
            RUNstatus.set(1)
            if AWGSync.get() == 0:
                session.flush()
                CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z mode
                CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z mode
                BAWGEnab()
                if not session.continuous:
                    session.start(0)
                time.sleep(0.02) # wait awhile here for some reason
            elif session.continuous:
                session.tk.END()
                session.flush()
                CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z mode
                CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z mode
                BAWGEnab()
            else:
                contloop = 0
                discontloop = 1
                if session.continuous:
                    session.tk.END() # tk.END continuous session mode
                    
    # UpdateTimeScreen()          # Always Update
    if TIMEdiv >= 100:
        First_Slow_sweep = 0
    else:
        First_Slow_sweep = 1
      

## Update Data, trace and time screen
def UpdateTimeAll():         
    MakeTimeTrace()         # Update the traces
    UpdateTimeScreen()      # Update the screen 

## Update time trace and screen
def UpdateTimeTrace():      
    MakeTimeTrace()         # Update traces
    UpdateTimeScreen()      # Update the screen

## Update time screen with trace and text
def UpdateTimeScreen():      
    MakeTimeScreen()        # Update the screen
    root.update()       # Activate updated screens    
## Update Data, trace and XY screen


def SetScaleA():
    global MarkerScale, CHAlab, CHBlab, CHAIlab, CHBIlab
    if MarkerScale.get() != 1:
        MarkerScale.set(1)
        CHAlab.config(style="Rtrace1.TButton")
        CHBlab.config(style="Strace2.TButton")
        CHAIlab.config(style="Strace3.TButton")
        CHBIlab.config(style="Strace4.TButton")
    else:
        MarkerScale.set(0)

def SetScaleIA():
    global MarkerScale, CHAlab, CHBlab, CHAIlab, CHBIlab

    if MarkerScale.get() != 3:
        MarkerScale.set(3)
        CHAlab.config(style="Strace1.TButton")
        CHBlab.config(style="Strace2.TButton")
        CHAIlab.config(style="Rtrace3.TButton")
        CHBIlab.config(style="Strace4.TButton")
    else:
        MarkerScale.set(0)

def SetScaleB():
    global MarkerScale, CHAlab, CHBlab, CHAIlab, CHBIlab

    if MarkerScale.get() != 2:
        MarkerScale.set(2)
        CHAlab.config(style="Strace1.TButton")
        CHBlab.config(style="Rtrace2.TButton")
        CHAIlab.config(style="Strace3.TButton")
        CHBIlab.config(style="Strace4.TButton")
    else:
        MarkerScale.set(0)

def SetScaleIB():
    global MarkerScale, CHAlab, CHBlab, CHAIlab, CHBIlab

    if MarkerScale.get() != 3:
        MarkerScale.set(4)
        CHAlab.config(style="Strace1.TButton")
        CHBlab.config(style="Strace2.TButton")
        CHAIlab.config(style="Strace3.TButton")
        CHBIlab.config(style="Rtrace4.TButton")
    else:
        MarkerScale.set(0)
        


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Oszilloskop Tiggerfunktionen
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#--- Set Trigger level to 50% (mid) point of current waveform
def BTrigger50p():
    global TgInput, TRIGGERlevel, TRIGGERentry
    global MaxV1, MinV1, MaxV2, MinV2
    global MaxI1, MinI1, MaxI2, MinI2
    # set new trigger level to mid point of waveform    
    MidV1 = (MaxV1+MinV1)/2
    MidV2 = (MaxV2+MinV2)/2
    MidI1 = (MaxI1+MinI1)/2
    MidI2 = (MaxI2+MinI2)/2
    if (TgInput.get() == 0):
        DCString = "0.0"
    elif (TgInput.get() == 1 ):
        DCString = ' {0:.2f} '.format(MidV1)
    elif (TgInput.get() == 2 ):
        DCString = ' {0:.2f} '.format(MidI1)
    elif (TgInput.get() == 3 ):
        DCString = ' {0:.2f} '.format(MidV2)
    elif (TgInput.get() == 4 ):
        DCString = ' {0:.2f} '.format(MidI2)
    TRIGGERlevel = eval(DCString)
    TRIGGERentry.delete(0,tk.END)
    TRIGGERentry.insert(4, DCString)    
    UpdateTimeTrace()           # Always Update
   
#---Auf Eingabe neue Triggerschwelle reagieren
def BTriglevel(event):
    global TRIGGERlevel, TRIGGERentry
    # evalute entry string to a numerical value
    try:
        TRIGGERlevel = float(eval(TRIGGERentry.get()))
    except:
        TRIGGERentry.delete(0,tk.END)
        TRIGGERentry.insert(0, TRIGGERlevel)
    # set new trigger level
    
    UpdateTimeTrace()           # Always Update

#--- Set Hold off time from entry widget
def BHoldOff(event):
    global HoldOff, HoldOffentry

    try:
        HoldOff = float(eval(HoldOffentry.get()))
    except:
        HoldOffentry.delete(0,tk.END)
        HoldOffentry.insert(0, HoldOff)
        
#---Triggerzeitpunkt für gegebene Schwelle ermitteln
def SetTriggerPoss():
    global HozPossentry, TgInput, TMsb
    # get time scale
    try:
        TIMEdiv = float(eval(TMsb.get()))
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"tk.END")
        TMsb.insert(0,TIMEdiv)
    # prevent divide by zero error
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.01
    if TgInput.get() > 0:
        HozPoss = -5 * TIMEdiv
        HozPossentry.delete(0,tk.END)
        HozPossentry.insert(0, HozPoss)

#---Trigger Holdoff
def IncHoldOff():
    global HoldOffentry, HoldOff, TgInput, TMsb
# get time scale
    try:
        TIMEdiv = float(eval(TMsb.get()))
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"tk.END")
        TMsb.insert(0,TIMEdiv)
    # prevent divide by zero error
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.01
    if TgInput.get() == 0:
        HoldOff = HoldOff + TIMEdiv
        HoldOffentry.delete(0,tk.END)
        HoldOffentry.insert(0, HoldOff)
        
## Routine to find rising edge of traces
def FindRisingEdge(Trace1, Trace2):
    global MinV1, MaxV1, MinV2, MaxV2, HoldOff, TRIGGERsample, TgInput, LShift
    global SHOWsamples, SAMPLErate, CHAperiod, CHAfreq, CHBperiod, CHBfreq
    global CHAHW, CHALW, CHADCy, CHBHW, CHBLW, CHBDCy, ShowC1_V, ShowC2_V
    global CHABphase, CHBADelayR1, CHBADelayR2, CHBADelayF
    
    anr1 = bnr1 = 0
    anf1 = bnf1 = 1
    anr2 = bnr2 = 2
    hldn = int(HoldOff * SAMPLErate/1000)

    if TgInput.get() > 0: # if triggering right shift arrays to undo trigger left shift
        Trace1 = np.roll(Trace1, -LShift)
        Trace2 = np.roll(Trace2, -LShift)
    else:
        Trace1 = np.roll(Trace1, -hldn)
        Trace2 = np.roll(Trace2, -hldn)
    try:
        MidV1 = (np.amax(Trace1)+np.amin(Trace1))/2.0
        MidV2 = (np.amax(Trace2)+np.amin(Trace2))/2.0
    except:
        MidV1 = (MinV1+MaxV1)/2
        MidV2 = (MinV2+MaxV2)/2

    Arising = [i for (i, val) in enumerate(Trace1) if val >= MidV1 and Trace1[i-1] < MidV1]
    Afalling = [i for (i, val) in enumerate(Trace1) if val <= MidV1 and Trace1[i-1] > MidV1]
    AIrising = [i - (Trace1[i] - MidV1)/(Trace1[i] - Trace1[i-1]) for i in Arising]
    AIfalling = [i - (MidV1 - Trace1[i])/(Trace1[i-1] - Trace1[i]) for i in Afalling]
    
    CHAfreq = SAMPLErate / np.mean(np.diff(AIrising))
    CHAperiod = (np.mean(np.diff(AIrising)) * 1000.0) / SAMPLErate # time in mSec
    # Catch zero length array?
    if len(Arising) == 0:
        return
    if len(Arising) > 0 or len(Afalling) > 0:
        if Arising[0] > 0:
            try:
                anr1 = AIrising[0]
            except:
                anr1 = 0
            try:
                anr2 = AIrising[1]
            except:
                anr2 = SHOWsamples
            try:
                if AIfalling[0] < AIrising[0]:
                    anf1 = AIfalling[1]
                else:
                    anf1 = AIfalling[0]
            except:
                anf1 = 1
        else:
            try:
                anr1 = AIrising[1]
            except:
                anr1 = 0
            try:
                anr2 = AIrising[2]
            except:
                anr2 = SHOWsamples
            try:
                if AIfalling[1] < AIrising[1]:
                    anf1 = AIfalling[2]
                else:
                    anf1 = AIfalling[1]
            except:
                anf1 = 1

    Brising = [i for (i, val) in enumerate(Trace2) if val >= MidV2 and Trace2[i-1] < MidV2]
    Bfalling = [i for (i, val) in enumerate(Trace2) if val <= MidV2 and Trace2[i-1] > MidV2]
    BIrising = [i - (Trace2[i] - MidV2)/(Trace2[i] - Trace2[i-1]) for i in Brising]
    BIfalling = [i - (MidV2 - Trace2[i])/(Trace2[i-1] - Trace2[i]) for i in Bfalling]

    CHBfreq = SAMPLErate / np.mean(np.diff(BIrising))
    CHBperiod = (np.mean(np.diff(BIrising)) * 1000.0) / SAMPLErate # time in mSec
# Catch zero length array?
    if len(Brising) == 0:
        return
    if len(Brising) > 0 or len(Bfalling) > 0:
        if Brising[0] > 0:
            try:
                bnr1 = BIrising[0]
            except:
                bnr1 = 0
            try:
                bnr2 = BIrising[1]
            except:
                bnr2 = SHOWsamples
            try:
                if BIfalling[0] < BIrising[0]:
                    bnf1 = BIfalling[1]
                else:
                    bnf1 = BIfalling[0]
            except:
                bnf1 = 1
        else:
            try:
                bnr1 = BIrising[1]
            except:
                bnr1 = 0
            try:
                bnr2 = BIrising[2]
            except:
                bnr2 = SHOWsamples
            try:
                if BIfalling[1] < BIrising[1]:
                    bnf1 = BIfalling[2]
                else:
                    bnf1 = BIfalling[1]
            except:
                bnf1 = 1
    #
    CHAHW = float(((anf1 - anr1) * 1000.0) / SAMPLErate)
    CHALW = float(((anr2 - anf1) * 1000.0) / SAMPLErate)
    CHADCy = float(anf1 - anr1) / float(anr2 - anr1) * 100.0 # in percent
    CHBHW = float(((bnf1 - bnr1) * 1000.0) / SAMPLErate)
    CHBLW = float(((bnr2 - bnf1) * 1000.0) / SAMPLErate)
    CHBDCy = float(bnf1 - bnr1) / float(bnr2 - bnr1) * 100.0 # in percent
#
    if bnr1 > anr1:
        CHBADelayR1 = float((bnr1 - anr1) * 1000.0 / SAMPLErate)
    else:
        CHBADelayR1 = float((bnr2 - anr1) * 1000.0 / SAMPLErate)
    CHBADelayR2 = float((bnr2 - anr2) * 1000.0 / SAMPLErate)
    CHBADelayF = float((bnf1 - anf1) * 1000.0 / SAMPLErate)
    try:
        CHABphase = 360.0*(float((bnr1 - anr1) * 1000.0 / SAMPLErate))/CHAperiod
    except:
        CHABphase = 0.0
    if CHABphase < 0.0:
        CHABphase = CHABphase + 360.0

# Interpolate time between samples around trigger event
def ReInterploateTrigger(TrgBuff):
    global DX, TRIGGERsample, TRIGGERlevel
    DX = 0
    n = TRIGGERsample
    DY = TrgBuff[int(n)] - TrgBuff[int(n+1)]
    if DY != 0.0:
        DX = (TRIGGERlevel - TrgBuff[int(n+1)])/DY # calculate interpolated trigger point
    else:
        DX = 0
# Find the sample where trigger event happened 
def FindTriggerSample(TrgBuff): # find trigger time sample point of passed waveform array
    global AutoLevel, TgInput, TRIGGERlevel, TRIGGERentry, DX, SAMPLErate, Is_Triggered
    global HoldOffentry, HozPossentry, TRIGGERsample, TRACEsize, HozPoss, hozpos
    global Trigger_LPF_length, LPFTrigger    
    # Set the TRACEsize variable
    TRACEsize = SHOWsamples               # Set the trace length
    DX = 0
    Is_Triggered = 0
    if LPFTrigger.get() > 0:
        TFiltCoef = [] # empty coef array
        for n in range(Trigger_LPF_length.get()):
            TFiltCoef.apptk.END(float(1.0/Trigger_LPF_length.get()))
        TFiltCoef = np.array(TFiltCoef)
        TrgBuff = np.convolve(TrgBuff, TFiltCoef)
        
    if len(TrgBuff) == 0:
        return
    try:
        TrgMin = np.amin(TrgBuff)
    except:
        TrgMin = 0.0
    try:
        TrgMax = np.amax(TrgBuff)
    except:
        TrgMax = 0.0
    try: # Find trigger sample
        if AutoLevel.get() == 1:
            TRIGGERlevel = (TrgMin + TrgMax)/2
            TRIGGERentry.delete(0,"tk.END")
            TRIGGERentry.insert(0, ' {0:.4f} '.format(TRIGGERlevel))
        else:
            TRIGGERlevel = eval(TRIGGERentry.get())
    except:
        TRIGGERentry.delete(0,tk.END)
        TRIGGERentry.insert(0, TRIGGERlevel)
    try: # Start from first sample after HoldOff
        HoldOff = float(eval(HoldOffentry.get()))
        if HoldOff < 0:
            HoldOff = 0
            HoldOffentry.delete(0,tk.END)
            HoldOffentry.insert(0, HoldOff)
    except:
        HoldOffentry.delete(0,tk.END)
        HoldOffentry.insert(0, HoldOff)
    try: # slide trace left right by HozPoss
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,tk.END)
        HozPossentry.insert(0, HozPoss)    
    hldn = int(HoldOff * SAMPLErate/1000)
    hozpos = int(HozPoss * SAMPLErate/1000)
    if hozpos >= 0:
        TRIGGERsample = hldn
    else:
        TRIGGERsample = abs(hozpos)     
    Nmax = int(TRACEsize / 1.5) # first 2/3 of data set
    DX = 0
    n = TRIGGERsample
    TRIGGERlevel2 = 0.99 * TRIGGERlevel # Hysteresis to avoid triggering on noise
    if TRIGGERlevel2 < TrgMin:
        TRIGGERlevel2 = TrgMin
    if TRIGGERlevel2 > TrgMax:
        TRIGGERlevel2 = TrgMax
    ChInput = TrgBuff[int(n)]
    Prev = ChInput
    while ( ChInput >= TRIGGERlevel2) and n < Nmax:
        n = n + 1
        ChInput = TrgBuff[int(n)]
    while (ChInput <= TRIGGERlevel) and n < Nmax:
        Prev = ChInput
        n = n + 1
        ChInput = TrgBuff[int(n)]
    DY = ChInput - Prev
    if DY != 0.0:
        DX = (TRIGGERlevel - Prev)/DY # calculate interpolated trigger point
    else:
        DX = 0
    if TgEdge.get() == 1:
        TRIGGERlevel2 = 1.01 * TRIGGERlevel
        if TRIGGERlevel2 < TrgMin:
            TRIGGERlevel2 = TrgMin
        if TRIGGERlevel2 > TrgMax:
            TRIGGERlevel2 = TrgMax
        ChInput = TrgBuff[int(n)]
        Prev = ChInput
        while (ChInput <= TRIGGERlevel2) and n < Nmax:
            n = n + 1
            ChInput = TrgBuff[int(n)]
        while (ChInput >= TRIGGERlevel) and n < Nmax:
            Prev = ChInput
            n = n + 1
            ChInput = TrgBuff[int(n)]
        DY = Prev - ChInput
        try:
            DX = (Prev - TRIGGERlevel)/DY # calculate interpolated trigger point
        except:
            DX = 0             
    if n < Nmax: # check to insure trigger point is in bounds
        TRIGGERsample = n - 1
        Is_Triggered = 1
    elif n > Nmax: # Didn't find edge in first 2/3 of data set
        TRIGGERsample = 1 + hldn # reset to begining
        Is_Triggered = 0
    if DX > 1:
        DX = 1 # never more than 100% of a sample period
    elif DX < 0:
        DX = 0 # never less than 0% of a sample period
    if math.isnan(DX):
        DX = 0
    TRIGGERsample = TRIGGERsample + hozpos
