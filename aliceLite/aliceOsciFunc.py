#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 7.9.20
"""
import math
import time
import numpy as np
import tkinter as tk
import tkinter.messagebox as tkm
import pysmu as smu
from aliceTimeFunc import MakeTimeTrace, MakeTimeScreen
from aliceAwgFunc import BAWGEnab
import aliceM1kSamp as m1k
import config as cf
import logging

PowerStatus = 1 # 0 stopped, 1 start, 2 running, 3 stop and restart, 4 stop
HozPoss = 0 #

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Oszilloskop Funktionen Vertikal-/Horizontaldarstellung
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
## Stop (pause) scope tool
def BStop():
    logging.debug('BStop()')
    if (cf.RUNstatus.get() == 1):
        # print("Stoping")
        cf.RUNstatus.set(0)
        cf.CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        cf.CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
        cf.CHA.constant(0.0)
        cf.CHB.constant(0.0)
        if cf.session.continuous:
            cf.session.end()

    UpdateTimeScreen()          # Always Update screens as necessary

# Set Hor time scale from entry widget
def BTime():
    logging.debug('BTime()')
    try: # get time scale in mSec/div
        cf.TIMEdiv = float(eval(cf.TMsb.get()))
        if cf.TIMEdiv < 0.0002:
            cf.TIMEdiv = 0.01
            cf.TMsb.delete(0,"end")
            cf.TMsb.insert(0,cf.TIMEdiv)
    except:
        cf.TIMEdiv = 0.5
        cf.TMsb.delete(0,"end")
        cf.TMsb.insert(0,cf.TIMEdiv)
    # Switch to 2X sampleling if time scale small enough
    Samples_per_div = cf.TIMEdiv * 100.0 # samples per mSec @ base sample rate
    if Samples_per_div < 20.0:
        cf.Two_X_Sample.set(1)
    else:
        cf.Two_X_Sample.set(0)
    m1k.SetADC_Mux()
    #
    if cf.RUNstatus.get() == 2:      # Restart if running
        cf.RUNstatus.set(4)
    UpdateTimeTrace()           # Always Update

#---Set Horx possition from entry widget
def BHozPoss(event):
    logging.debig('BHozPoss()')
    global HozPoss
    try:
        HozPoss = float(eval(cf.HozPossentry.get()))
        logging.debug('BHozPoss() with HozPoss = {}'.format(float(eval(cf.HozPossentry.get()))))
    except:
        cf.HozPossentry.delete(0,tk.END)
        cf.HozPossentry.insert(0, HozPoss)

def BCHAlevel():
    logging.debug('BCHAlevel()')
    try:
        CH1vpdvLevel = float(eval(cf.CHAsb.get()))
    except:
        cf.CHAsb.delete(0,tk.END)
        cf.CHAsb.insert(0, CH1vpdvLevel)
    UpdateTimeTrace()           # Always Update

def BCHAIlevel():
    logging.debug('BCHAIlevel()')
    try:
        CH1ipdvLevel = float(eval(cf.CHAIsb.get()))
    except:
        cf.CHAIsb.delete(0,tk.END)
        cf.CHAIsb.insert(0, CH1ipdvLevel)
    UpdateTimeTrace()           # Always Update

def BCHBlevel():
    logging.debug('BCHBlevel()')
    try:
        CH2vpdvLevel = float(eval(cf.CHBsb.get()))
    except:
        cf.CHBsb.delete(0,tk.END)
        cf.CHBsb.insert(0, CH2vpdvLevel)
    UpdateTimeTrace()           # Always Update    

def BCHBIlevel():
    logging.debug('BCHBIlevel()')
    try:
        CH2ipdvLevel = float(eval(cf.CHBIsb.get()))
    except:
        cf.CHBIsb.delete(0,tk.END)
        cf.CHBIsb.insert(0, CH2ipdvLevel)
    UpdateTimeTrace()           # Always Update    

def BOffsetA(event):
    logging.debug('BOffsetA()')
    try:
        CHAVOffset = float(eval(cf.CHAVPosEntry.get()))
    except:
        cf.CHAVPosEntry.delete(0,tk.END)
        cf.CHAVPosEntry.insert(0, CHAVOffset)
    UpdateTimeTrace()           # Always Update

def BIOffsetA(event):
    logging.debug('BIOffsetA()')
    try:
        CHAIOffset = float(eval(cf.CHAIPosEntry.get()))
    except:
        cf.CHAIPosEntry.delete(0,tk.END)
        cf.CHAIPosEntry.insert(0, CHAIOffset)
    UpdateTimeTrace()           # Always Update

def BOffsetB(event):
    logging.debug('BOffsetB()')
    try:
        CHBVOffset = float(eval(cf.CHBVPosEntry.get()))
    except:
        cf.CHBVPosEntry.delete(0,tk.END)
        cf.CHBVPosEntry.insert(0, CHBVOffset)
    UpdateTimeTrace()           # Always Update

def BIOffsetB(event):
    logging.debug('BIOffsetB()')
    try:
        CHBIOffset = float(eval(cf.CHBIPosEntry.get()))
    except:
        cf.CHBIPosEntry.delete(0,tk.END)
        cf.CHBIPosEntry.insert(0, CHBIOffset)
    UpdateTimeTrace()           # Always Update

## Start aquaring scope time data
def BStart():
    logging.debug('BStart()')
    global PowerStatus
    global First_Slow_sweep
    if cf.DevID == "No Device":
        tkm.showwarning("WARNING","No Device Plugged In!")
        return
    else:
        if (cf.RUNstatus.get() == 0):
            cf.RUNstatus.set(1)
            cf.session.flush()
            cf.CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z mode
            cf.CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z mode
            BAWGEnab()
            if not cf.session.continuous:
                cf.session.start(0)
            time.sleep(0.02) # wait awhile here for some reason                   
    # UpdateTimeScreen()          # Always Update
    if cf.TIMEdiv >= 100:
        First_Slow_sweep = 0
    else:
        First_Slow_sweep = 1
      
## Update Data, trace and time screen
def UpdateTimeAll():
    logging.debug('UpdateTimeAll()')         
    MakeTimeTrace()         # Update the traces
    UpdateTimeScreen()      # Update the screen 

## Update time trace and screen
def UpdateTimeTrace():      
    logging.debug('UpdateTimeTrace()')
    MakeTimeTrace()         # Update traces
    UpdateTimeScreen()      # Update the screen

## Update time screen with trace and text
def UpdateTimeScreen():
    logging.debug('UpdateTimeScreen()')
    MakeTimeScreen() # Update the screen
    cf.MarkerNum = 0 # Marker wurden durch MakeTimeScreen() gelöscht, jetzt noch Position 1. Marker wieder zurücksetzen 
    cf.root.update() # Activate updated screens    

        
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Oszilloskop Tiggerfunktionen
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#--- Set Trigger level to 50% (mid) point of current waveform
def BTrigger50p():
    logging.debug('BTrigger50p()')
    # set new trigger level to mid point of waveform    
    MidV1 = (cf.MaxV1+cf.MinV1)/2
    MidV2 = (cf.MaxV2+cf.MinV2)/2
    MidI1 = (cf.MaxI1+cf.MinI1)/2
    MidI2 = (cf.MaxI2+cf.MinI2)/2
    if (cf.TgInput.get() == 0):
        DCString = "0.0"
    elif (cf.TgInput.get() == 1 ):
        DCString = ' {0:.2f} '.format(MidV1)
    elif (cf.TgInput.get() == 2 ):
        DCString = ' {0:.2f} '.format(MidI1)
    elif (cf.TgInput.get() == 3 ):
        DCString = ' {0:.2f} '.format(MidV2)
    elif (cf.TgInput.get() == 4 ):
        DCString = ' {0:.2f} '.format(MidI2)
    cf.TRIGGERlevel = eval(DCString)
    cf.TRIGGERentry.delete(0,tk.END)
    cf.TRIGGERentry.insert(4, DCString)    
    UpdateTimeTrace()           # Always Update
   
#---Auf Eingabe neue Triggerschwelle reagieren
def BTriglevel(event):
    logging.debug('BTriglevel()')
    # evalute entry string to a numerical value
    try:
        cf.TRIGGERlevel = float(eval(cf.TRIGGERentry.get()))
    except:
        cf.TRIGGERentry.delete(0,tk.END)
        cf.TRIGGERentry.insert(0, cf.TRIGGERlevel)
    # set new trigger level
    
    UpdateTimeTrace()           # Always Update

#--- Set Hold off time from entry widget
def BHoldOff(event):
    logging.debug('BHoldOff()')
    try:
        cf.HoldOff = float(eval(cf.HoldOffentry.get()))
    except:
        cf.HoldOffentry.delete(0,tk.END)
        cf.HoldOffentry.insert(0, cf.HoldOff)
        
#---Triggerzeitpunkt für gegebene Schwelle ermitteln
def SetTriggerPoss(): # vermutlich überflüssig
    logging.debug('SetTriggerPoss()')
    try: # get time scale
        cf.TIMEdiv = float(eval(cf.TMsb.get()))
    except:
        cf.TIMEdiv = 0.5
        cf.TMsb.delete(0,tk.END)
        cf.TMsb.insert(0,cf.TIMEdiv)
    # prevent divide by zero error
    if cf.TIMEdiv < 0.0002:
        cf.TIMEdiv = 0.01
    if cf.TgInput.get() > 0:
        HozPoss = -5 * cf.TIMEdiv
        cf.HozPossentry.delete(0,tk.END)
        cf.HozPossentry.insert(0, HozPoss)
        
# Routine to find rising edge of traces
def FindRisingEdge(Trace1, Trace2):
    logging.debug('FindRisingEdge()')
    global CHAperiod, CHAfreq, CHBperiod, CHBfreq
    global CHAHW, CHALW, CHADCy, CHBHW, CHBLW, CHBDCy
    global CHABphase, CHBADelayR1, CHBADelayR2, CHBADelayF
    
    anr1 = bnr1 = 0
    anf1 = bnf1 = 1
    anr2 = bnr2 = 2
    hldn = int(cf.HoldOff * cf.SAMPLErate/1000)

    if cf.TgInput.get() > 0: # if triggering right shift arrays to undo trigger left shift
        Trace1 = np.roll(Trace1, -cf.LShift)
        Trace2 = np.roll(Trace2, -cf.LShift)
    else:
        Trace1 = np.roll(Trace1, -hldn)
        Trace2 = np.roll(Trace2, -hldn)
    try:
        MidV1 = (np.amax(Trace1)+np.amin(Trace1))/2.0
        MidV2 = (np.amax(Trace2)+np.amin(Trace2))/2.0
    except:
        MidV1 = (cf.MinV1+cf.MaxV1)/2
        MidV2 = (cf.MinV2+cf.MaxV2)/2

    Arising = [i for (i, val) in enumerate(Trace1) if val >= MidV1 and Trace1[i-1] < MidV1]
    Afalling = [i for (i, val) in enumerate(Trace1) if val <= MidV1 and Trace1[i-1] > MidV1]
    AIrising = [i - (Trace1[i] - MidV1)/(Trace1[i] - Trace1[i-1]) for i in Arising]
    AIfalling = [i - (MidV1 - Trace1[i])/(Trace1[i-1] - Trace1[i]) for i in Afalling]
    
    CHAfreq = cf.SAMPLErate / np.mean(np.diff(AIrising))
    CHAperiod = (np.mean(np.diff(AIrising)) * 1000.0) / cf.SAMPLErate # time in mSec
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
                anr2 = cf.SHOWsamples
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
                anr2 = cf.SHOWsamples
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

    CHBfreq = cf.SAMPLErate / np.mean(np.diff(BIrising))
    CHBperiod = (np.mean(np.diff(BIrising)) * 1000.0) / cf.SAMPLErate # time in mSec
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
                bnr2 = cf.SHOWsamples
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
                bnr2 = cf.SHOWsamples
            try:
                if BIfalling[1] < BIrising[1]:
                    bnf1 = BIfalling[2]
                else:
                    bnf1 = BIfalling[1]
            except:
                bnf1 = 1
    
    CHAHW = float(((anf1 - anr1) * 1000.0) / cf.SAMPLErate)
    CHALW = float(((anr2 - anf1) * 1000.0) / cf.SAMPLErate)
    CHADCy = float(anf1 - anr1) / float(anr2 - anr1) * 100.0 # in percent
    CHBHW = float(((bnf1 - bnr1) * 1000.0) / cf.SAMPLErate)
    CHBLW = float(((bnr2 - bnf1) * 1000.0) / cf.SAMPLErate)
    CHBDCy = float(bnf1 - bnr1) / float(bnr2 - bnr1) * 100.0 # in percent

    if bnr1 > anr1:
        CHBADelayR1 = float((bnr1 - anr1) * 1000.0 / cf.SAMPLErate)
    else:
        CHBADelayR1 = float((bnr2 - anr1) * 1000.0 / cf.SAMPLErate)
    CHBADelayR2 = float((bnr2 - anr2) * 1000.0 / cf.SAMPLErate)
    CHBADelayF = float((bnf1 - anf1) * 1000.0 / cf.SAMPLErate)
    try:
        CHABphase = 360.0*(float((bnr1 - anr1) * 1000.0 / cf.SAMPLErate))/CHAperiod
    except:
        CHABphase = 0.0
    if CHABphase < 0.0:
        CHABphase = CHABphase + 360.0

# Interpolate time between samples around trigger event
def ReInterploateTrigger(TrgBuff):
    logging.debug('ReInterploateTrigger()')
    cf.trgIpol = 0
    n = cf.TRIGGERsample
    DY = TrgBuff[int(n)] - TrgBuff[int(n+1)]
    if DY != 0.0:
        cf.trgIpol = (cf.TRIGGERlevel - TrgBuff[int(n+1)])/DY # calculate interpolated trigger point
    else:
        cf.trgIpol = 0
# Find the sample where trigger event happened 
def FindTriggerSample(TrgBuff): # find trigger time sample point of passed waveform array
    logging.debug('FindTriggerSample()')
    global TRACEsize, HozPoss, hozpos  
    # Set the TRACEsize variable
    TRACEsize = cf.SHOWsamples               # Set the trace length
    cf.trgIpol = 0
    cf.Is_Triggered = 0
    if cf.LPFTrigger.get() > 0:
        TFiltCoef = [] # empty coef array
        for n in range(cf.Trigger_LPF_length.get()):
            TFiltCoef.append(float(1.0/cf.Trigger_LPF_length.get()))
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
        cf.TRIGGERlevel = float(eval(cf.TRIGGERentry.get()))
    except:
        cf.TRIGGERentry.delete(0,tk.END)
        cf.TRIGGERentry.insert(0, cf.TRIGGERlevel)
    try: # Start from first sample after cf.HoldOff
        cf.HoldOff = float(eval(cf.HoldOffentry.get()))
        if cf.HoldOff < 0:
            cf.HoldOff = 0
            cf.HoldOffentry.delete(0,tk.END)
            cf.HoldOffentry.insert(0, cf.HoldOff)
    except:
        cf.HoldOffentry.delete(0,tk.END)
        cf.HoldOffentry.insert(0, cf.HoldOff)
    try: # slide trace left right by HozPoss
        HozPoss = float(eval(cf.HozPossentry.get()))
    except:
        cf.HozPossentry.delete(0,tk.END)
        cf.HozPossentry.insert(0, HozPoss)    
    hldn = int(cf.HoldOff * cf.SAMPLErate/1000)
    hozpos = int(HozPoss * cf.SAMPLErate/1000)
    if hozpos >= 0:
        cf.TRIGGERsample = hldn
    else:
        cf.TRIGGERsample = abs(hozpos)     
    Nmax = int(TRACEsize / 1.5) # first 2/3 of data set
    cf.trgIpol = 0
    n = cf.TRIGGERsample
    TRIGGERlevel2 = 0.99 * cf.TRIGGERlevel # Hysteresis to avoid triggering on noise
    if TRIGGERlevel2 < TrgMin:
        TRIGGERlevel2 = TrgMin
    if TRIGGERlevel2 > TrgMax:
        TRIGGERlevel2 = TrgMax
    ChInput = TrgBuff[int(n)]
    Prev = ChInput
    while ( ChInput >= TRIGGERlevel2) and n < Nmax:
        n = n + 1
        ChInput = TrgBuff[int(n)]
    while (ChInput <= cf.TRIGGERlevel) and n < Nmax:
        Prev = ChInput
        n = n + 1
        ChInput = TrgBuff[int(n)]
    DY = ChInput - Prev
    if DY != 0.0:
        cf.trgIpol = (cf.TRIGGERlevel - Prev)/DY # calculate interpolated trigger point
    else:
        cf.trgIpol = 0
    if cf.TgEdge.get() == 1:
        TRIGGERlevel2 = 1.01 * cf.TRIGGERlevel
        if TRIGGERlevel2 < TrgMin:
            TRIGGERlevel2 = TrgMin
        if TRIGGERlevel2 > TrgMax:
            TRIGGERlevel2 = TrgMax
        ChInput = TrgBuff[int(n)]
        Prev = ChInput
        while (ChInput <= TRIGGERlevel2) and n < Nmax:
            n = n + 1
            ChInput = TrgBuff[int(n)]
        while (ChInput >= cf.TRIGGERlevel) and n < Nmax:
            Prev = ChInput
            n = n + 1
            ChInput = TrgBuff[int(n)]
        DY = Prev - ChInput
        try:
            cf.trgIpol = (Prev - cf.TRIGGERlevel)/DY # calculate interpolated trigger point
        except:
            cf.trgIpol = 0             
    if n < Nmax: # check to insure trigger point is in bounds
        cf.TRIGGERsample = n - 1
        cf.Is_Triggered = 1
    elif n > Nmax: # Didn't find edge in first 2/3 of data set
        cf.TRIGGERsample = 1 + hldn # reset to begining
        cf.Is_Triggered = 0
    if cf.trgIpol > 1:
        cf.trgIpol = 1 # never more than 100% of a sample period
    elif cf.trgIpol < 0:
        cf.trgIpol = 0 # never less than 0% of a sample period
    if math.isnan(cf.trgIpol):
        cf.trgIpol = 0
    cf.TRIGGERsample = cf.TRIGGERsample + hozpos