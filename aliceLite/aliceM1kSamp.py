#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 15.9.20
"""
import time
import numpy as np
import tkinter as tk
import config as cf
from aliceAwgFunc import UpdateAwgCont
import aliceMenus as am
from aliceOsciFunc import (BStop, BStart, UpdateTimeAll, UpdateTimeTrace,
UpdateTimeScreen,ReInterploateTrigger, FindTriggerSample)
import logging

ADsignal1 = []              # Ain signal array channel A and B

TRACEresetTime = True # True for first new trace, False for averageing

InOffA = InGainA = InOffB = InGainB = 0.0 # Variablen für Input aus UI
CurOffA = CurOffB = CurGainA = CurGainB = 0.0

Alternate_Sweep_Mode = 1 # 1 wenn drei oder mehr Signale gesampelt werden, 200 kS/s nur bei = 0

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# M1K Samplingfunktionen
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++       
def Analog_In():
    logging.debug("Analog_In()")
    while (cf.running):
        if (cf.RUNstatus.get() == 1) or (cf.RUNstatus.get() == 2):
            if cf.SettingsStatus.get() == 1:
                am.UpdateSettingsMenu() # Make sure current entries in Settings controls are up to date
            Analog_Time_In()
        cf.root.update()
    logging.debug("Analog_In() exiting while loop")

#---Read the analog data and store the data into the arrays
def Analog_Time_In():
    #logging.debug("Analog_Time_In()")
    global InOffA, InGainA, InOffB, InGainB
    global CurOffA, CurOffB, CurGainA, CurGainB 
    # get time scale
    try:
        cf.TIMEdiv = float(eval(cf.TMsb.get()))
    except:
        cf.TIMEdiv = 0.5
        cf.TMsb.delete(0,tk.END)
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
        
    Sample()



#---
def Sample():
    global ADsignal1, Alternate_Sweep_Mode
    global TRACEresetTime
    global TIMEdiv1x
    global TRACErefresh
    global SCREENrefresh, DCrefresh
    global InOffA, InGainA, InOffB, InGainB, CurOffA, CurOffB, CurGainA, CurGainB
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global cal, Last_ADC_Mux_Mode
    global PIO_0, PIO_1, PIO_2, PIO_3, PIO_4, PIO_5, PIO_6, PIO_7
    logging.warning("Sample() Sample Rate={} alternate_sweep_mode={} ADC_Mux_Mode={} Two_X_Sample={}".format(cf.SampRate, Alternate_Sweep_Mode,cf.ADC_Mux_Mode.get(),cf.Two_X_Sample))

    # Anzahl Abtastpunkte 3x so viel wie darstellbar und auf 6000...90000 begrenzen  
    cf.NTrace = int(cf.SampRate * 30.0 * cf.TIMEdiv / 1000.0)
    if cf.NTrace > cf.MaxSamples: # or a Max of 90,000 samples
        cf.NTrace = cf.MaxSamples
    if cf.NTrace < 6000: # or a Min of 2000 samples
        cf.NTrace = 6000
    if cf.SampRate == 200000:
        NSamp = int(cf.NTrace/2) # Da 200 kS/s via Mux realisiert werden
    else:
        NSamp = int(cf.NTrace)
    logging.warning('sample(): # of Samples per Trace cf.NTace={}, NSamp={}'.format(cf.NTrace,NSamp))
                    
    
    
    VmemoryA = np.zeros(cf.NTrace)       # The memory for averaging
    VmemoryB = np.zeros(cf.NTrace)
    ImemoryA = np.zeros(cf.NTrace)       # The memory for averaging
    ImemoryB = np.zeros(cf.NTrace)
    
    # Nach dem ersten Trace steht TRACEresetTime = False für Average-Modus
    if cf.TRACEmodeTime.get() == 0 and TRACEresetTime == False: # Kein Average-Modus in UI und erster Trace
        TRACEresetTime = True               # Clear the memory for averaging
    elif cf.TRACEmodeTime.get() == 1: # Average-Modus in UI und erster Trace
        if TRACEresetTime == True:
            TRACEresetTime = False
    # Save previous trace in memory for average trace und falls kein Triggerereignis, damit letzter Trace nochmals angezeigt wird
    VmemoryA = cf.VBuffA
    VmemoryB = cf.VBuffB
    ImemoryA = cf.IBuffA
    ImemoryB = cf.IBuffB
    prevTRIGGERsample = cf.TRIGGERsample # wird benötigt, falls kein Triggerereignis gefunden wird
  



    # Starting acquisition
    if cf.session.continuous:
        logging.debug("Sample() session continuous")
        ADsignal1 = cf.devx.read(NSamp, -1, True) # get samples for both channel A and B
        # Bei 200 kS/s sind am Ende aber doppelt so viele Samples vorhanden!
    else:
        ADsignal1 = cf.devx.get_samples(NSamp) # , True) # get samples for both channel A and B
        # waite to finish then return to open termination
        cf.devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
        cf.devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
        cf.devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
        cf.devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    # 200 kS/s und >2 Traces kommt eigentlich nicht vor: Hier passiert auch nichts...
    if Alternate_Sweep_Mode == 1 and cf.Two_X_Sample == 1:
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
    
    if NSamp != len(ADsignal1): # manchmal gibt ADC weniger Samples zurück als angefordert
        NSamp = len(ADsignal1)
        
    while index < NSamp:
        # 200 kS/s und <= 2 Traces (d.h.Alternate_Sweep_Mode = 0)
        if cf.Two_X_Sample == 1 and cf.ADC_Mux_Mode.get() < 6:
            logging.warning("Sample() cf.Two_X_Sample == 1 and cf.ADC_Mux_Mode.get() < 6")
            if cf.ADC_Mux_Mode.get() == 0: # VA and VB
                logging.debug("ADC_Mux_Mode.get() == 0")
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
            #? Wieso hier diese Skalierung?
            elif cf.ADC_Mux_Mode.get() == 2: # VA and IB
                cf.VBuffA.append((ADsignal1[index][0][1])/1024.0)
                cf.VBuffA.append((ADsignal1[index][1][0])/1024.0)
               
                cf.IBuffB.append( ((ADsignal1[index][0][0])/4096.0)-0.5 )
                cf.IBuffB.append( ((ADsignal1[index][1][1])/4096.0)-0.5 ) 
               
                if Alternate_Sweep_Mode == 0:
                    cf.VBuffB.append(0.0) # fill as a place holder
                    cf.VBuffB.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode.get() == 3: # VB and IA
                cf.VBuffB.append((ADsignal1[index][0][0])/1024.0)
                cf.VBuffB.append((ADsignal1[index][1][1])/1024.0)
                
                cf.IBuffA.append( ((ADsignal1[index][0][1])/4096.0)-0.5 )
                cf.IBuffA.append( ((ADsignal1[index][1][0])/4096.0)-0.5 )
              
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
            logging.warning("Sample() cf.Two_X_Sample != 1 and cf.ADC_Mux_Mode.get() >= 6 len(ADsignal1)={}, index={}".format(len(ADsignal1),index))
            cf.VBuffA.append(ADsignal1[index][0][0])
            cf.IBuffA.append(ADsignal1[index][0][1])
            cf.VBuffB.append(ADsignal1[index][1][0])
            cf.IBuffB.append(ADsignal1[index][1][1])
        index = index + increment

    cf.NTrace = len(cf.VBuffA) # bei 200 kS/s verdopplung
     # kommt eigentlich nicht vor...
    if Alternate_Sweep_Mode == 1 and cf.Two_X_Sample == 1:
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
   
    else:
        # nur Umrechnung in mA für I-Kanäle
        cf.VBuffA = np.array(cf.VBuffA)
        cf.VBuffB = np.array(cf.VBuffB)
        cf.IBuffA = np.array(cf.IBuffA) * 1000 # convert to mA
        cf.IBuffB = np.array(cf.IBuffB) * 1000 # convert to mA
        cf.VBuffA = (cf.VBuffA - InOffA) * InGainA
        cf.VBuffB = (cf.VBuffB - InOffB) * InGainB
        cf.IBuffA = (cf.IBuffA - CurOffA) * CurGainA
        cf.IBuffB = (cf.IBuffB - CurOffB) * CurGainB
   
# Find trigger sample point if necessary
    #cf.TRIGGERsample = int(cf.NTrace/3) # Triggerereignis nur im mittleren Drittel Samgling Trace suchen
    cf.LShift = 0
    if cf.TgInput.get() == 1:
        FindTriggerSample(cf.VBuffA)
    if cf.TgInput.get() == 2:
        FindTriggerSample(cf.IBuffA)
    if cf.TgInput.get() == 3:
        FindTriggerSample(cf.VBuffB)
    if cf.TgInput.get() == 4:
        FindTriggerSample(cf.IBuffB)

    if (cf.TgInput.get()==0 or cf.Is_Triggered == 1): # Falls kein Trigger oder Trigger und Triggerereignis gefunden
        logging.warning('sample(): Trigger event found or Tigger Option None. cf.TRIGGERsample={}'.format(cf.TRIGGERsample))
        if cf.TRACEmodeTime.get() == 1 and TRACEresetTime == False: # Average Modus und nicht erster Trace
            if cf.TgInput.get() > 0: # if triggering left shift all arrays such that trigger point is at index 0
                cf.LShift = - cf.TRIGGERsample
                cf.VBuffA = np.roll(cf.VBuffA, cf.LShift)
                cf.VBuffB = np.roll(cf.VBuffB, cf.LShift)
                cf.IBuffA = np.roll(cf.IBuffA, cf.LShift)
                cf.IBuffB = np.roll(cf.IBuffB, cf.LShift)
                NHozPos = int(cf.HozPos * cf.SampRate/1000)
                cf.TRIGGERsample = NHozPos # set trigger sample to index 0 offset by horizontal position # Wieso das?
            try: # Neue Traces in Mittelung einberechnen
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
        Endsample = cf.NTrace - 10 # average over all samples
        ## Berechnung Messwerte für jeden Trace            
        cf.DCV1 = np.mean(cf.VBuffA[10:Endsample])
        cf.DCV2 = np.mean(cf.VBuffB[10:Endsample])
        # convert current values to mA
        cf.DCI1 = np.mean(cf.IBuffA[10:Endsample])
        cf.DCI2 = np.mean(cf.IBuffB[10:Endsample])
        # find min and max values
        cf.MinV1 = np.amin(cf.VBuffA[10:Endsample])
        cf.MaxV1 = np.amax(cf.VBuffA[10:Endsample])
        cf.MinV2 = np.amin(cf.VBuffB[10:Endsample])
        cf.MaxV2 = np.amax(cf.VBuffB[10:Endsample])
        cf.MinI1 = np.amin(cf.IBuffA[10:Endsample])
        cf.MaxI1 = np.amax(cf.IBuffA[10:Endsample])
        cf.MinI2 = np.amin(cf.IBuffB[10:Endsample])
        cf.MaxI2 = np.amax(cf.IBuffB[10:Endsample])
        # RMS value = square root of average of the data record squared
        cf.SV1 = np.sqrt(np.mean(np.square(cf.VBuffA[10:Endsample])))
        cf.SI1 = np.sqrt(np.mean(np.square(cf.IBuffA[10:Endsample])))
        cf.SV2 = np.sqrt(np.mean(np.square(cf.VBuffB[10:Endsample])))
        cf.SI2 = np.sqrt(np.mean(np.square(cf.IBuffB[10:Endsample])))
        cf.SVA_B = np.sqrt(np.mean(np.square(cf.VBuffA[10:Endsample]-cf.VBuffB[10:Endsample])))
    else: # Falls kein Triggerereignis gefunden, vorherigen Trace nochmals anzeigen    
        cf.VBuffA = VmemoryA
        cf.VBuffB = VmemoryB
        cf.IBuffA = ImemoryA
        cf.IBuffB = ImemoryB
        cf.TRIGGERsample = prevTRIGGERsample
        logging.warning('###################sample(): No trigger event found. cf.TRIGGERsample={}'.format(cf.TRIGGERsample))
        
    UpdateTimeAll()         # Update Data, trace and time screen
       # Update Data, trace
    if cf.SingleShot.get() > 0 and cf.Is_Triggered == 1: # Singel Shot trigger is on
        BStop()  
        cf.SingleShot.set(0)
    if (cf.RUNstatus.get() == 3) or (cf.RUNstatus.get() == 4):
        if cf.RUNstatus.get() == 3:
            cf.RUNstatus.set(0)
        if cf.RUNstatus.get() == 4:          
            cf.RUNstatus.set(1)
    UpdateTimeScreen()
            
            
# Einstellen der Samplingrate, falls im Fenster diese geändert wurde oder 200 kS/s gewählt
def SetSampleRate():
    WasRunning = 0
    if (cf.RUNstatus.get() == 1):
        WasRunning = 1
        BStop() # Force Stop loop if running
    try:
        NewRate = int(cf.SampRatesb.get())
        # Samplingrate kann nicht größer als 200.000 S/s sein
        # 200.000 S/s geht nur wenn ein oder zwei Kanäle gesampelt werden
        if (NewRate > 200000) or (NewRate == 200000 and Alternate_Sweep_Mode == 1): 
            # Bei zu großer Samplinrate diese in Spinbox auf 100 kS/s zurücksetzen
            cf.SampRate = 100000
            cf.SampRatesb.delete(0,tk.END)
            cf.SampRatesb.insert(0,cf.SampRate)
        else:            
            cf.SampRate = NewRate
            logging.warning("SetSampleRate() NewRate={} S/s".format(cf.SampRate))
    except:
        logging.warning('Exception in SetSampleRate()')
    if NewRate == 200000:
        cf.Two_X_Sample = 1
    else:
        cf.Two_X_Sample = 0
    SetADC_Mux()
    cf.session.configure(sample_rate=cf.SampRate) # bei 200 kS/s wegen Mux nur 100 kS/s einstellen
    #cf.SampRate = cf.session.sample_rate # Wieso zurücklesen aus M1K?
    cf.SampRatesb.delete(0,tk.END)
    cf.SampRatesb.insert(0,cf.SampRate)
    UpdateAwgCont() # remake AWG waveforms for new rate
    if (WasRunning == 1):
        WasRunning = 0
        BStart() # restart loop if was running
          
#**************************************************
# Hier Einstellung der Abtastrate auf 200.000 S/s
#**************************************************
def SetADC_Mux():
# Der ADC_Mux _Mode wird über unterschiedliche Menüs gesetzt: Samplinrate oder hier das Aktivieren der unterschiedlichen Kanäle.
# Das ist wohl der Grund wieso für die Hardware der Mux-Mode mit cf.devx.set_mux_mode() eingestellt wird. Die Tkinter-Variable ADC_Mux_Mode
# ist in erster Linie dafür da, die Buttons auszulesen und deren Zustand zu setzen.
    v1_adc_conf = 0x20F1 # ADC Mux defaults
    i1_adc_conf = 0x20F7
    v2_adc_conf = 0x20F7
    i2_adc_conf = 0x20F1
    # Achtung! ADC_Mux_Mode und cf.devx Mux Mode teils nicht gleich
    logging.debug('SetADC_Mux() ADC_Mux_Mode={} SampRate={}'.format(cf.ADC_Mux_Mode.get(), cf.SampRate))
    if cf.SampRate == 200000: # Wenn Option 200 kS/s angeklickt und nur Zweierkombination aktiv
    # Mux-Mode: Welche Kombination von CA-V/-I, CB-V/-I abgetastet wird, siehe auch TraceSelectADC_Mux()
        if cf.ADC_Mux_Mode.get() == 0: # CA-V and/or CB-V
            cf.devx.set_adc_mux(1)
        elif cf.ADC_Mux_Mode.get() == 1: # CA-I and/or CB-I
            cf.devx.set_adc_mux(2)
        elif cf.ADC_Mux_Mode.get() == 2: # CA-V and CB-I
            cf.devx.set_adc_mux(2) # ein work around?
            cf.devx.set_adc_mux(7)
            cf.devx.ctrl_transfer(0x40, 0x20, v1_adc_conf, 0, 0, 0, 100) # U12
            cf.devx.ctrl_transfer(0x40, 0x21, i1_adc_conf, 0, 0, 0, 100) # U12
            cf.devx.ctrl_transfer(0x40, 0x22, v2_adc_conf, 0, 0, 0, 100) # U11
            cf.devx.ctrl_transfer(0x40, 0x22, i2_adc_conf, 0, 0, 0, 100) # U11
            time.sleep(0.1)
        elif cf.ADC_Mux_Mode.get() == 3: # CB-V and CA-I
            cf.devx.set_adc_mux(7)
            cf.devx.ctrl_transfer(0x40, 0x20, v1_adc_conf, 0, 0, 0, 100) # U12
            cf.devx.ctrl_transfer(0x40, 0x21, i1_adc_conf, 0, 0, 0, 100) # U12
            cf.devx.ctrl_transfer(0x40, 0x22, v2_adc_conf, 0, 0, 0, 100) # U11
            cf.devx.ctrl_transfer(0x40, 0x22, i2_adc_conf, 0, 0, 0, 100) # U11
            time.sleep(0.1)
        elif cf.ADC_Mux_Mode.get() == 4: # CA-V and CA-I
            cf.devx.set_adc_mux(4)
        elif cf.ADC_Mux_Mode.get() == 5: # CB-V and CB-I
            cf.devx.set_adc_mux(5)
    else: # cf.Two_X_Sample = 0 setzen da mehr als Zweierkombination
        if (cf.SampRate == 200000):
            logging.debug('SetADC_Mux(): cf.Two_X_Sample set to 0 since more than 2 channels')
        cf.Two_X_Sample = 0
        cf.devx.set_adc_mux(0)


# je nachdem welche Signale (jeweils V oder I der der beiden Kanäle A und B) abgetastet werden sollen, wird entsprechend
# das Multiplexing des ADS gesetzt, MakeSampleRateMenu() macht das Gleiche für die Zweierkombinationen mit 2x Abtastrate
def TraceSelectADC_Mux():
    global Alternate_Sweep_Mode # bei drei oder mehr abzutastenden Signalen
    if cf.devx != None:
        if cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # All four traces
            Alternate_Sweep_Mode = 1
            cf.Two_X_Sample = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(0) # three traces
            Alternate_Sweep_Mode = 1
            cf.Two_X_Sample = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # three traces
            Alternate_Sweep_Mode = 1
            cf.Two_X_Sample = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # three traces
            Alternate_Sweep_Mode = 1
            cf.Two_X_Sample = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # three traces
            Alternate_Sweep_Mode = 1
            cf.Two_X_Sample = 0

        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(4) # CA-V and CA-I
            Alternate_Sweep_Mode = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(5) # CB-V and CB-I
            Alternate_Sweep_Mode = 0 
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(1) # CA-I and CB-I
            Alternate_Sweep_Mode = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(0) # CA-V and CB-V
            Alternate_Sweep_Mode = 0        
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(2) # CA-V and CB-I
            Alternate_Sweep_Mode = 0        
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(3) # CA-I and CB-V
            Alternate_Sweep_Mode = 0
            
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(0) # just CA-V
            Alternate_Sweep_Mode = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(0) # just CB-V
            Alternate_Sweep_Mode = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(1) # just CA-I
            Alternate_Sweep_Mode = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(1) # just CB-I
            Alternate_Sweep_Mode = 0

        else:
            cf.ADC_Mux_Mode.set(0) # wenn nur -V und nicht zusätzlich -I abgetastet werden soll
            Alternate_Sweep_Mode = 0
        if (cf.SampRate == 200000) and (cf.Two_X_Sample == 0): # falls während 200 kS/s Wechsel auf >Zweierkombi
            cf.SampRate = 100000
            cf.SampRatesb.delete(0,tk.END) # Samplinrate-Menü ändern
            cf.SampRatesb.insert(0,cf.SampRate)
            
        logging.debug('TraceSelectADC_Mux() with ADC_Mux_Mode = {}, Alternate_Sweep_Mode = {}'.format(cf.ADC_Mux_Mode.get(),Alternate_Sweep_Mode))
        SetADC_Mux()
        UpdateTimeTrace()
        
   
# Function to left (-num) or right (+num) shift buffer and fill with a value
# returns same length buffer
# preallocate empty array and assign slice
def shift_buffer(arr, num, fill_value=np.nan):
    logging.debug('shift_buffer()')
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