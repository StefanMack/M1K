#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 15.9.20
"""
import math
import time
import numpy as np
import tkinter as tk
import tkinter.messagebox as tkm
import pysmu as smu
from aliceTimeFunc import MakeTimeTrace, MakeTimeScreen
from aliceAwgFunc import BAWGEnab
import config as cf
import logging

PowerStatus = 1 # 0 stopped, 1 start, 2 running, 3 stop and restart, 4 stop

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Oszilloskop Funktionen Vertikal-/Horizontaldarstellung
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
# Kontinuierliches Sampling beenden (Stopp-Taste in UI betätigt)
def BStop():
    logging.debug('BStop()')
    if (cf.RUNstatus.get() == 1):
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

    if cf.RUNstatus.get() == 2:      # Restart if running
        cf.RUNstatus.set(4)
    UpdateTimeTrace()           # Always Update

#---Set Horx possition from entry widget
def BHozPoss(event):
    logging.debug('BHozPoss()')
    HozPosLim = 5.0 * cf.TIMEdiv # Horizontaloffset maximal halbe Breite Grid
    try:
        HozPosVal = float(eval(cf.HozPosentry.get()))
        if HozPosVal > HozPosLim:
            cf.HozPos = HozPosLim
            cf.HozPosentry.delete(0,tk.END)
            cf.HozPosentry.insert(0, cf.HozPos)
        elif HozPosVal < -HozPosLim:
            cf.HozPos = -HozPosLim
            cf.HozPosentry.delete(0,tk.END)
            cf.HozPosentry.insert(0, cf.HozPos)
        else:
            cf.HozPos = HozPosVal
        logging.debug('BHozPoss() with cf.HozPos={} HowPosVal={}'.format(HozPosVal,cf.HozPos))
    except:
        cf.HozPosentry.delete(0,tk.END)
        cf.HozPosentry.insert(0, cf.HozPos)

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
#    global First_Slow_sweep
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
    UpdateTimeScreen()          # Always Update
#    if cf.TIMEdiv >= 100:
#        First_Slow_sweep = 0
#    else:
#        First_Slow_sweep = 1
      
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

# Update time screen with trace and text: Nur wenn Trigger>None oder Triggerereignis (noch nicht optimal)
def UpdateTimeScreen():
    if True:
    #if (cf.Is_Triggered == 1 and cf.TgInput.get() > 0) or (cf.TgInput.get() == 0):
        logging.debug('UpdateTimeScreen()')
        MakeTimeScreen() # Update the screen
        cf.MarkerNum = 0 # Marker wurden durch MakeTimeScreen() gelöscht, jetzt noch Position 1. Marker wieder zurücksetzen 
        if cf.running == 1: # damit keine Fehlermeldung bei Exit mit laufendem Oszi
            cf.root.update() # Activate updated screens
            #cf.root.update_idletasks() # Wieso ist das hier nötig?
    
    
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
    # evalute entry string to a numerical value
    try:
        cf.TRIGGERlevel = float(eval(cf.TRIGGERentry.get()))
    except:
        cf.TRIGGERentry.delete(0,tk.END)
        cf.TRIGGERentry.insert(0, cf.TRIGGERlevel)
    # set new trigger level 
    logging.warning('BTriglevel() with cf.TRIGGERlevel={}'.format(cf.TRIGGERlevel))
    UpdateTimeTrace()           # Always Update


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

# Innerhalb der ersten 2/3 der Abtastpunkte wird nach Triggerereignis gesucht
def FindTriggerSample(TrgBuff):
    logging.debug('FindTriggerSample()')
    
    cf.trgIpol = 0
    cf.Is_Triggered = 0
    if cf.LPFTrigger.get() > 0: # Tiefpassfiltern des Triggereingangssignals
        TFiltCoef = []
        for n in range(cf.Trigger_LPF_length.get()):
            TFiltCoef.append(float(1.0/cf.Trigger_LPF_length.get()))
        TFiltCoef = np.array(TFiltCoef)
        TrgBuff = np.convolve(TrgBuff, TFiltCoef)
        
    if len(TrgBuff) == 0:
        return
    try:
        TrgMin = np.amin(TrgBuff) # kleinster Signalwert
    except:
        TrgMin = 0.0
    try:
        TrgMax = np.amax(TrgBuff) # größter Signalwert
    except:
        TrgMax = 0.0
    try: # Trigger Level aus UI lesen
        cf.TRIGGERlevel = float(eval(cf.TRIGGERentry.get()))
    except:
        cf.TRIGGERentry.delete(0,tk.END)
        cf.TRIGGERentry.insert(0, cf.TRIGGERlevel)
    try: # Horizontaloffset aus UI lesen
        cf.HozPos = float(eval(cf.HozPosentry.get()))
    except:
        cf.HozPosentry.delete(0,tk.END)
        cf.HozPosentry.insert(0, cf.HozPos)    
    # Umrechnen in Indexwert
    NHozPos = int(cf.HozPos * cf.SampRate/1000)
   
    cf.trgIpol = 0
    n = int(cf.NTrace * 0.25) # Startindex für Triggersuche
    Nmax = int(cf.NTrace * 0.75) # Endindex für Triggersuche
    # Triggern auf steigender Flanke:
    TRIGGERlevel2 = 0.99 * cf.TRIGGERlevel # Hystere Trigger  
    if TRIGGERlevel2 < TrgMin: # Hystereseintervall auf min/max Signalwert begrenzen
        TRIGGERlevel2 = TrgMin
    if TRIGGERlevel2 > TrgMax:
        TRIGGERlevel2 = TrgMax
    ChInput = TrgBuff[int(n)]
    Prev = ChInput
    while ( ChInput >= TRIGGERlevel2) and n < Nmax: # erster Signalwert s_min kleiner 99 % Trigger Level
        n = n + 1
        ChInput = TrgBuff[int(n)]
    while (ChInput <= cf.TRIGGERlevel) and n < Nmax: # darauf folgender erster Signalwert s_max größer Trigger Level 
        Prev = ChInput # = s_min
        n = n + 1
        ChInput = TrgBuff[int(n)] # = s_max
    DY = ChInput - Prev # Differenz erste Signalwerte unter- und oberhalb Triggerintervall
    if DY != 0.0:
        cf.trgIpol = (cf.TRIGGERlevel - Prev)/DY # %-Wert Lage Trigger Level im Intervall [s_min,s_max]
    else:
        cf.trgIpol = 0
    # Triggern auf fallende Flanke, Algorithmus sonst wie oben
    if cf.TgEdge.get() == 1:
        TRIGGERlevel2 = 1.01 * cf.TRIGGERlevel
        if TRIGGERlevel2 < TrgMin:
            TRIGGERlevel2 = TrgMin
        if TRIGGERlevel2 > TrgMax:
            TRIGGERlevel2 = TrgMax
        ChInput = TrgBuff[int(n)]
        Prev = ChInput
        while (ChInput <= TRIGGERlevel2) and n < Nmax: # erster Signalwert größer 101 % Trigger Level
            n = n + 1
            ChInput = TrgBuff[int(n)]
        while (ChInput >= cf.TRIGGERlevel) and n < Nmax: # darauf folgender erster Signalwert kleiner Triggerlevel
            Prev = ChInput
            n = n + 1
            ChInput = TrgBuff[int(n)]
        DY = Prev - ChInput
        try:
            cf.trgIpol = (Prev - cf.TRIGGERlevel)/DY # calculate interpolated trigger point
        except:
            cf.trgIpol = 0
            
    if n < Nmax: # Tiggerereignis innerhalb 0..Nmax (erste 2/3 der Abtastpunkte)
        logging.warning('FindTriggerSample(TrgBuff): Found trigger event.')
        cf.TRIGGERsample = n - 1 # Indexposition des Triggerereignisses
        cf.Is_Triggered = 1
        # Triggerzeitpunkt in Mitte des Grids setzen, falls Horz Pos 0 0 ms
        cf.TRIGGERsample = cf.TRIGGERsample + NHozPos - int(cf.SampRate * 5.0 * cf.TIMEdiv / 1000.0) 
    elif n >= Nmax: # Didn't find edge in first 2/3 of data set
        logging.warning('FindTriggerSample(TrgBuff): Found **no** trigger event.')
        cf.TRIGGERsample = 0 # war 1
        cf.Is_Triggered = 0
    if cf.trgIpol > 1:
        cf.trgIpol = 1 # never more than 100% of a sample period
    elif cf.trgIpol < 0:
        cf.trgIpol = 0 # never less than 0% of a sample period
    if math.isnan(cf.trgIpol):
        cf.trgIpol = 0
    # Triggerzeitpunkt in Mitte des Grids setzen, falls Horz Pos 0 0 ms
    #cf.TRIGGERsample = cf.TRIGGERsample + NHozPos - int(cf.SampRate * 5.0 * cf.TIMEdiv / 1000.0) 