#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu smuc
S. Mack, 22.1.21
"""
import math
import time
import numpy as np
import tkinter as tk
import tkinter.messagebox as tkm
import pysmu as smu
from smucTimeFunc import MakeTimeTrace, MakeTimeScreen
from smucAwgFunc import setup_awg
import config as cf
import logging

PowerStatus = 1 # 0 stopped, 1 start, 2 running, 3 stop and restart, 4 stop

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Oszilloskop Funktionen Vertikal-/Horizontaldarstellung
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
# Kontinuierliches Sampling beenden (Stopp-Taste in UI betätigt)
def stop_samp():
    logging.debug('stop_samp()')
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
def set_hscale(*event): # * damit mit und ohne Übergabe von Argumenten (z.B. Event)
    try: # get time scale in mSec/div
        cf.TIMEdiv = float(eval(cf.TMsb.get()))
    except:
        cf.TIMEdiv = 0.5
        cf.TMsb.delete(0,"end")
        cf.TMsb.insert(0,cf.TIMEdiv)
    logging.debug('set_hscale() with TIMEdiv={}'.format(cf.TIMEdiv))
    if cf.RUNstatus.get() == 2:      # Restart if running
        cf.RUNstatus.set(4)
    UpdateTimeTrace()           # Always Update

#---Set Horx position from entry widget
def set_hpos(event):
    logging.debug('set_hpos()')
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
        logging.debug('set_hpos() with cf.HozPos={} HowPosVal={}'.format(HozPosVal,cf.HozPos))
    except:
        cf.HozPosentry.delete(0,tk.END)
        cf.HozPosentry.insert(0, cf.HozPos)


## Start aquaring scope time data
def start_samp():
    logging.debug('start_samp()')
    if cf.DevID == "No Device":
        tkm.showwarning("WARNING","No Device Plugged In!")
        return
    else:
        if (cf.RUNstatus.get() == 0):
            cf.RUNstatus.set(1)
            cf.session.flush()
            time.sleep(0.02)
            cf.CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z mode
            cf.CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z mode
            time.sleep(0.02)
            setup_awg()
            if not cf.session.continuous:
                cf.session.start(0)
            time.sleep(0.02) # wait awhile here for some reason                   
    UpdateTimeScreen()          # Always Update
      
## Update Data, trace and time screen
def UpdateTimeAll():
    logging.debug('UpdateTimeAll()')         
    MakeTimeTrace()         # Update the traces
    UpdateTimeScreen()      # Update the screen 

## Update time trace and screen
def UpdateTimeTrace():     
    logging.debug('UpdateTimeTrace() with MathTrace={}'.format(cf.MathTrace.get()))
    # Prüfen of für gewählten Mathtrace nötige CA/CB Traces aktiv
    if cf.MathTrace.get() in [1,2,3,10]: # Kombi CA-V, CB-V
        if (cf.ShowC1_V.get() and cf.ShowC2_V.get()) == 0: # falls nicht
            cf.MathTrace.set(0) # Math Trace ausschalten
    if cf.MathTrace.get() in [8,9,11]: # Kombi CA-I, CB-I
        if (cf.ShowC1_I.get() and cf.ShowC2_I.get()) == 0:
            cf.MathTrace.set(0)
    if cf.MathTrace.get() in [4,6]: # Kombi CA-V, CA-I
        if (cf.ShowC1_V.get() and cf.ShowC1_I.get()) == 0:
            cf.MathTrace.set(0)
    if cf.MathTrace.get() in [5,7]: # Kombi CB-V, CB-I
        if (cf.ShowC2_V.get() and cf.ShowC2_I.get()) == 0:
            cf.MathTrace.set(0)
    MakeTimeTrace()         # Update traces
    UpdateTimeScreen()      # Update the screen

# Update time screen with trace and text
def UpdateTimeScreen():
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
    logging.debug('BTriglevel() with cf.TRIGGERlevel={}'.format(cf.TRIGGERlevel))
    UpdateTimeTrace()           # Always Update


# Interpolate time between samples around trigger event
# Im Averagemodus Triggerzeitpunkt aktueller Mittelwert interpolieren
def ReInterploateTrigger(TrgBuff):
    cf.trgIpol = 0
    n = cf.TRIGGERsample # Index letzter Wert unterhalb (+) bzw. oberhalb (-) Schwelle
    deltaY = TrgBuff[int(n+1)] - TrgBuff[int(n)] # Differenz Signal direkt unter/über (+) Schwelle
    logging.debug('ReInterploateTrigger(): TrgBuff[n]={} TrgBuff[n+1]={} deltaY={}'.format(TrgBuff[int(n)],TrgBuff[int(n+1)],deltaY))
    if abs(deltaY) > 0.01:
        cf.trgIpol = (TrgBuff[int(n+1)]-cf.TRIGGERlevel)/deltaY # calculate interpolated trigger point
    else:
        cf.trgIpol = 0
    logging.debug('ReInterploateTrigger(): cf.trgIpol={}'.format(cf.trgIpol))

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
    # Umrechnen in Indexwert
    #NHozPos = int(cf.HozPos * cf.SampRate/1000)
   
    n = int(cf.NSamples * 0.25) # Startindex für Triggersuche
    Nmax = int(cf.NSamples * 0.75) # Endindex für Triggersuche
    
    # Triggern auf steigender Flanke:
    if cf.TgEdge.get() == 0:
        TRIGGERlevel2 = 0.99 * cf.TRIGGERlevel # Hystere Trigger  
        if TRIGGERlevel2 < TrgMin: # Hystereseintervall auf min/max Signalwert begrenzen
            TRIGGERlevel2 = TrgMin
        if TRIGGERlevel2 > TrgMax:
            TRIGGERlevel2 = TrgMax
        ChInput = TrgBuff[int(n)]
        SampBelow = ChInput
        while (ChInput >= TRIGGERlevel2) and n < Nmax: # Iterieren bis Signalwert kleiner 99 % Trigger Level
            n = n + 1
            ChInput = TrgBuff[int(n)]
        while (ChInput <= cf.TRIGGERlevel) and n < Nmax: 
            SampBelow = ChInput # Ende while: Letzter Signalwert unterhalb Triggerschwelle
            n = n + 1 # Ende while: Index erster Signalwert oberhalb Triggerschwelle
            ChInput = TrgBuff[int(n)] # Ende while: Erster Signalwert oberhalb Triggerschwelle
        if n < Nmax: # Triggerereignis gefunden
            deltaY = ChInput - SampBelow # Differenz Signalwerte direkt ober- und unterhalb Triggerschwelle, immer positiv
            if deltaY != 0.0:
                cf.trgIpol = (cf.TRIGGERlevel - SampBelow)/deltaY # relative Lage Trigger Level im Intervall [s_min,s_max] 0: SampBelow liegt auf Triggerschwelle
                logging.debug('Trigger rising edge: SampBelow={}, deltaY={}, cf.trgIpol={}'.format(SampBelow,deltaY,cf.trgIpol))
            else:
                logging.debug('Trigger rising edge: deltaY = 0.0')
                cf.trgIpol = 0
    # Triggern auf fallende Flanke, Algorithmus sonst wie oben
    if cf.TgEdge.get() == 1:
        TRIGGERlevel2 = 1.01 * cf.TRIGGERlevel
        if TRIGGERlevel2 < TrgMin:
            TRIGGERlevel2 = TrgMin
        if TRIGGERlevel2 > TrgMax:
            TRIGGERlevel2 = TrgMax
        ChInput = TrgBuff[int(n)]
        SampAbove = ChInput
        while (ChInput <= TRIGGERlevel2) and n < Nmax: # Iterieren bis Signalwert größer 101 % Trigger Level
            n = n + 1
            ChInput = TrgBuff[int(n)]
        while (ChInput >= cf.TRIGGERlevel) and n < Nmax: # Triggerereignis finden
            SampAbove = ChInput # Ende while: Letzter Signalwert oberhalb Schwelle
            n = n + 1 # Ende while: Index erster Signalwert unterhalb Schwelle
            ChInput = TrgBuff[int(n)] # Ende while: Erster Signalwert unterhalb Schwelle
        if n < Nmax: # Triggerereignis gefunden 
            deltaY = SampAbove - ChInput # Differenz Signalwerte direkt ober- und unterhalb Triggerschwelle, immer positiv
            if deltaY != 0.0:
                cf.trgIpol = (SampAbove - cf.TRIGGERlevel)/deltaY # calculate interpolated trigger point
            else:
                cf.trgIpol = 0
            
    if n < Nmax: # Tiggerereignis innerhalb 0..Nmax (erste 2/3 der Abtastpunkte)
        cf.TRIGGERsample = n - 1 # Indexposition des Triggerereignisses: letzter unterhalb (+) bzw. oberhalb (-) Schwelle
        cf.Is_Triggered = 1
        logging.debug('FindTriggerSample(): Found raw trigger event: Index TRIGGERsample={}'.format(cf.TRIGGERsample))
    elif n >= Nmax: # Didn't find edge in first 2/3 of data set
        logging.debug('FindTriggerSample(): Found **no** trigger event.')
        cf.TRIGGERsample = 0 # war 1
        cf.Is_Triggered = 0
    if cf.trgIpol > 1:
        cf.trgIpol = 1 # never more than 100% of a sample period
    elif cf.trgIpol < 0:
        cf.trgIpol = 0 # never less than 0% of a sample period
    if math.isnan(cf.trgIpol):
        cf.trgIpol = 0
    logging.debug('FindTriggerSample(): cf.trgIpol={}'.format(cf.trgIpol))