#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 22.9.20
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
#FirstSampTrace = True # True for first new trace, False for averageing
TwoPlusActiveCH = 1 # 1 wenn drei oder mehr Signale gesampelt werden, 200 kS/s nur bei = 0

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# M1K Samplingfunktionen
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++       
#--- Hauptendlosschleife für UI und Messfunktionen
def ScopeGo():
    logging.debug("ScopeGo()")
    while (cf.running):
        if (cf.RUNstatus.get() == 1) or (cf.RUNstatus.get() == 2):
            if cf.SettingsStatus.get() == 1:
                am.UpdateSettingsMenu() # Make sure current entries in Settings controls are up to date
            Sample()
        cf.root.update()
    logging.debug("ScopeGo() exiting while loop")

#--- Abtastvorgang mit anschließender Gain-/Offsetkorrektur (Kalibrierung)
def Sample():
    global ADsignal1, TwoPlusActiveCH
    global TIMEdiv1x
    global TRACErefresh
    global SCREENrefresh, DCrefresh
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global cal, Last_ADC_Mux_Mode
    global PIO_0, PIO_1, PIO_2, PIO_3, PIO_4, PIO_5, PIO_6, PIO_7
    logging.debug("Sample() Sample Rate={} TwoPlusActiveCH={} ADC_Mux_Mode={} Two_X_Sample={}".format(cf.SampRate, TwoPlusActiveCH,cf.ADC_Mux_Mode.get(),cf.Two_X_Sample))

    # Anzahl Abtastpunkte 3x so viel wie darstellbar und auf 6000...90000 begrenzen  
    cf.NSamples = int(cf.SampRate * 30.0 * cf.TIMEdiv / 1000.0)
    if cf.NSamples > cf.MaxSamples: # or a Max of 90,000 samples
        cf.NSamples = cf.MaxSamples
    if cf.NSamples < cf.MinSamples: # or a Min of 2000 samples
        cf.NSamples = cf.MinSamples
    if cf.SampRate == 200000:
        NSamp = int(cf.NSamples/2) # Da 200 kS/s via Mux realisiert werden
    else:
        NSamp = int(cf.NSamples)
    logging.debug('sample(): # of Samples per Trace cf.NTace={}, NSamp={}'.format(cf.NSamples,NSamp))
                           
    # Nach dem ersten Trace steht FirstSampTrace = False für Average-Modus
    if cf.TraceAvgMode.get() == 0 and cf.FirstSampTrace == False: # Kein Average-Modus in UI und erster Trace
        cf.FirstSampTrace = True               # Clear the memory for averaging
#    elif cf.TraceAvgMode.get() == 1: # Average-Modus in UI und erster Trace
#        if FirstSampTrace == True:
#            FirstSampTrace = False
    # Save previous trace in memory for average trace und falls kein Triggerereignis, damit letzter Trace nochmals angezeigt wird
    cf.VBuffAPrev = cf.VBuffA
    cf.VBuffBPrev = cf.VBuffB
    cf.IBuffAPrev = cf.IBuffA
    cf.IBuffBPrev = cf.IBuffB
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
    if TwoPlusActiveCH == 1 and cf.Two_X_Sample == 1:
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
        # 200 kS/s und <= 2 Traces (d.h.TwoPlusActiveCH = 0)
        if cf.Two_X_Sample == 1 and cf.ADC_Mux_Mode.get() < 6:
            logging.debug("Sample() cf.Two_X_Sample == 1 and cf.ADC_Mux_Mode.get() < 6")
            if cf.ADC_Mux_Mode.get() == 0: # VA and VB
                logging.debug("ADC_Mux_Mode.get() == 0")
                cf.VBuffA.append(ADsignal1[index][0][0])
                cf.VBuffA.append(ADsignal1[index][1][1])
                cf.VBuffB.append(ADsignal1[index][0][1])
                cf.VBuffB.append(ADsignal1[index][1][0])
                if TwoPlusActiveCH == 0:
                    cf.IBuffA.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode.get() == 1: # IA and IB
                cf.IBuffA.append(ADsignal1[index][0][1])
                cf.IBuffA.append(ADsignal1[index][1][0])
                cf.IBuffB.append(ADsignal1[index][0][0])
                cf.IBuffB.append(ADsignal1[index][1][1])
                if TwoPlusActiveCH == 0:
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
               
                if TwoPlusActiveCH == 0:
                    cf.VBuffB.append(0.0) # fill as a place holder
                    cf.VBuffB.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode.get() == 3: # VB and IA
                cf.VBuffB.append((ADsignal1[index][0][0])/1024.0)
                cf.VBuffB.append((ADsignal1[index][1][1])/1024.0)
                
                cf.IBuffA.append( ((ADsignal1[index][0][1])/4096.0)-0.5 )
                cf.IBuffA.append( ((ADsignal1[index][1][0])/4096.0)-0.5 )
              
                if TwoPlusActiveCH == 0:
                    cf.VBuffA.append(0.0) # fill as a place holder
                    cf.VBuffA.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode.get() == 4: # VA and IA
                cf.VBuffA.append(ADsignal1[index][0][0])
                cf.VBuffA.append(ADsignal1[index][1][1])
                cf.IBuffA.append(ADsignal1[index][0][1])
                cf.IBuffA.append(ADsignal1[index][1][0])
                if TwoPlusActiveCH == 0:
                    cf.VBuffB.append(0.0) # fill as a place holder
                    cf.VBuffB.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
                    cf.IBuffB.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode.get() == 5: # VB and IB
                cf.VBuffB.append(ADsignal1[index][0][1])
                cf.VBuffB.append(ADsignal1[index][1][0])
                cf.IBuffB.append(ADsignal1[index][0][0])
                cf.IBuffB.append(ADsignal1[index][1][1])
                if TwoPlusActiveCH == 0:
                    cf.VBuffA.append(0.0) # fill as a place holder
                    cf.VBuffA.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
                    cf.IBuffA.append(0.0) # fill as a place holder
        else:
            logging.debug("Sample() cf.Two_X_Sample != 1 and cf.ADC_Mux_Mode.get() >= 6 len(ADsignal1)={}, index={}".format(len(ADsignal1),index))
            cf.VBuffA.append(ADsignal1[index][0][0])
            cf.IBuffA.append(ADsignal1[index][0][1])
            cf.VBuffB.append(ADsignal1[index][1][0])
            cf.IBuffB.append(ADsignal1[index][1][1])
        index = index + increment
    logging.debug('sample(): CA-V # of samples read={} CA-V[100] ={}'.format(len(cf.VBuffA),cf.VBuffA[100]))
    cf.NSamples = len(cf.VBuffA) # bei 200 kS/s verdopplung
    
    # nur Umrechnung in mA für I-Kanäle, Wandlung in Numpy-Arrays da oben evtl. als Listen neu instanziert
    cf.VBuffA = np.array(cf.VBuffA)
    cf.VBuffB = np.array(cf.VBuffB)
    cf.IBuffA = np.array(cf.IBuffA) * 1000 # convert to mA
    cf.IBuffB = np.array(cf.IBuffB) * 1000 # convert to mA

    # Offset und Gain-Korrektur aus Kalibrierung
    logging.debug('sample(): cf.CHAVOffset={}, cf.CHAVGain={}'.format(cf.CHAVOffset,cf.CHAVGain))
    cf.VBuffA = (cf.VBuffA - cf.CHAVOffset) * cf.CHAVGain
    cf.VBuffB = (cf.VBuffB - cf.CHBVOffset) * cf.CHBVGain
    cf.IBuffA = (cf.IBuffA - cf.CHAIOffset) * cf.CHAIGain
    cf.IBuffB = (cf.IBuffB - cf.CHBIOffset) * cf.CHBIGain
        
    logging.debug('sample(): Trigger Input TgInput = {}'.format(cf.TgInput.get()))
# Find trigger sample point if necessary

    if cf.TgInput.get() == 1:
        FindTriggerSample(cf.VBuffA)
    if cf.TgInput.get() == 2:
        FindTriggerSample(cf.IBuffA)
    if cf.TgInput.get() == 3:
        FindTriggerSample(cf.VBuffB)
    if cf.TgInput.get() == 4:
        FindTriggerSample(cf.IBuffB)

    if (cf.TgInput.get()==0 or cf.Is_Triggered == 1): # Falls kein Trigger oder Trigger und Triggerereignis gefunden
        logging.debug('sample(): Trigger event found or Tigger Option None. cf.TRIGGERsample={}'.format(cf.TRIGGERsample))
        if cf.TraceAvgMode.get() == 1: # Trace Average Modus
            logging.debug('sample(): Average Modus left shift all arrays.')
            cf.VBuffA = np.roll(cf.VBuffA, -cf.TRIGGERsample) # Beim Mitteln müssen alle Traces den Triggerzeitpunkt beim gleichen Index haben
            cf.VBuffB = np.roll(cf.VBuffB, -cf.TRIGGERsample)
            cf.IBuffA = np.roll(cf.IBuffA, -cf.TRIGGERsample)
            cf.IBuffB = np.roll(cf.IBuffB, -cf.TRIGGERsample)
            if cf.TgInput.get() > 0  and cf.FirstSampTrace == True: # Getriggert und erster Trace
                logging.debug('sample(): First averaging trace')
                cf.AveVBuffA = cf.VBuffA   
                cf.AveVBuffB = cf.VBuffB
                cf.AveIBuffA = cf.IBuffA
                cf.AveIBuffB = cf.IBuffB
                cf.FirstSampTrace = False
            if cf.TgInput.get() > 0 and cf.FirstSampTrace == False: # Getriggert und nicht erster Trace
                try: # Neue Traces in Mittelung einberechnen
                    logging.debug('sample(): Calculating averages for all traces')
                    cf.AveVBuffA = cf.AveVBuffA + (cf.VBuffA - cf.AveVBuffA) / cf.NAveTrace.get()
                    cf.AveIBuffA = cf.AveIBuffA + (cf.IBuffA - cf.AveIBuffA) / cf.NAveTrace.get()
                    cf.AveVBuffB = cf.AveVBuffB + (cf.VBuffB - cf.AveVBuffB) / cf.NAveTrace.get()
                    cf.AveIBuffB = cf.AveIBuffB + (cf.IBuffB - cf.AveIBuffB) / cf.NAveTrace.get()
                except:
                    # buffer size mismatch so reset memory buffers
                    logging.debug('sample(): Averaging exception')
                    cf.AveVBuffA = cf.VBuffA   
                    cf.AveVBuffB = cf.VBuffB
                    cf.AveIBuffA = cf.IBuffA
                    cf.AveIBuffB = cf.IBuffB
            # Triggerzeitpunkt wieder an ursprünglichen Index verschieben
            cf.VBuffA = np.roll(cf.AveVBuffA, cf.TRIGGERsample) 
            cf.VBuffB = np.roll(cf.AveVBuffB, cf.TRIGGERsample)
            cf.IBuffA = np.roll(cf.AveIBuffA, cf.TRIGGERsample)
            cf.IBuffB = np.roll(cf.AveIBuffB, cf.TRIGGERsample)           
            
            # Da Triggerzeitpunkt wegen Mitteln auf Index 0 geschoben wurde muss dieser neu gesetzt werden
            if cf.TgInput.get() == 1:
                ReInterploateTrigger(cf.VBuffA)
            if cf.TgInput.get() == 2:
                ReInterploateTrigger(cf.IBuffA)
            if cf.TgInput.get() == 3:
                ReInterploateTrigger(cf.VBuffB)
            if cf.TgInput.get() == 4:
                ReInterploateTrigger(cf.IBuffB)
        # DC value = average of the data record
        Endsample = cf.NSamples - 10 # average over all samples
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
    else: # Falls Trigger und kein Triggerereignis gefunden, vorherigen Trace nochmals anzeigen    
        cf.VBuffA = cf.VBuffAPrev
        cf.VBuffB = cf.VBuffBPrev
        cf.IBuffA = cf.IBuffAPrev
        cf.IBuffB = cf.IBuffBPrev
        cf.TRIGGERsample = prevTRIGGERsample
        logging.debug('sample(): No trigger event found.')
        
    UpdateTimeAll()         # Update Data, trace and time screen
       # Update Data, trace
    if cf.SingleShot.get() > 0 and cf.Is_Triggered == 1: # Singel Shot trigger is on
        BStop()  
        cf.SingleShot.set(0)
    if (cf.RUNstatus.get() == 3) or (cf.RUNstatus.get() == 4): # 3: stop now, 4: stop and restart
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
        if (NewRate not in cf.SampRateList) or (NewRate == 200000 and TwoPlusActiveCH == 1):
        # Samplingrate muss kleiner 200 kS/s, 200 kS/s nur Sampling 1 oder 2 Kanäle (TwoPlusActiveCH)
            cf.SampRate = 100000 # wenn Eingabe unzulässig, auf 100 kS/s zurücksetzen
            cf.SampRatesb.delete(0,tk.END)
            cf.SampRatesb.insert(0,cf.SampRate)
        else:            
            cf.SampRate = NewRate
            logging.debug("SetSampleRate() NewRate={} S/s".format(cf.SampRate))
    except:
        logging.debug('Exception in SetSampleRate()')
    if cf.SampRate == 200000:
        cf.Two_X_Sample = 1
        HWSampRate = 100000 # wegen TwoPlusActiveCH Hardware Samplingrate nur halb so groß
    else:
        cf.Two_X_Sample = 0
        HWSampRate = cf.SampRate # kein TwoPlusActiveCH Hardware Samplingrate = echte Samplingrate
    SetADC_Mux()
    cf.session.configure(sample_rate=HWSampRate) # bei 200 kS/s wegen Mux nur 100 kS/s einstellen

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
# Abhänig von aktiven Kanänen (UI) und Samplingrate (UI) setzen des ADC-Mux
# Mux-Mode: Welche Kombination von CA-V/-I, CB-V/-I abgetastet wird, siehe auch TraceSelectADC_Mux()
# Achtung! Werte ADC_Mux_Mode und "devx Mux Mode" teils nicht gleich
    v1_adc_conf = 0x20F1 # ADC Mux defaults
    i1_adc_conf = 0x20F7
    v2_adc_conf = 0x20F7
    i2_adc_conf = 0x20F1
    
    logging.debug('SetADC_Mux() ADC_Mux_Mode={} SampRate={}'.format(cf.ADC_Mux_Mode.get(), cf.SampRate))
    if cf.SampRate == 200000: # Wenn Option 200 kS/s angeklickt und nur Zweierkombination aktiv

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
# das Multiplexing des ADC gesetzt
def TraceSelectADC_Mux():
    global TwoPlusActiveCH # bei drei oder mehr abzutastenden Signalen
    if cf.devx != None:
        if cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # All four traces
            TwoPlusActiveCH = 1
            cf.Two_X_Sample = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(0) # three traces
            TwoPlusActiveCH = 1
            cf.Two_X_Sample = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # three traces
            TwoPlusActiveCH = 1
            cf.Two_X_Sample = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # three traces
            TwoPlusActiveCH = 1
            cf.Two_X_Sample = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(0) # three traces
            TwoPlusActiveCH = 1
            cf.Two_X_Sample = 0

        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(4) # CA-V and CA-I
            TwoPlusActiveCH = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(5) # CB-V and CB-I
            TwoPlusActiveCH = 0 
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(1) # CA-I and CB-I
            TwoPlusActiveCH = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(0) # CA-V and CB-V
            TwoPlusActiveCH = 0        
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(2) # CA-V and CB-I
            TwoPlusActiveCH = 0        
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(3) # CA-I and CB-V
            TwoPlusActiveCH = 0
            
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(0) # just CA-V
            TwoPlusActiveCH = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(0) # just CB-V
            TwoPlusActiveCH = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode.set(1) # just CA-I
            TwoPlusActiveCH = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode.set(1) # just CB-I
            TwoPlusActiveCH = 0

        else:
            cf.ADC_Mux_Mode.set(0) # wenn nur -V und nicht zusätzlich -I abgetastet werden soll
            TwoPlusActiveCH = 0
        if (cf.SampRate == 200000) and (cf.Two_X_Sample == 0): # falls während 200 kS/s Wechsel auf >Zweierkombi
            cf.SampRate = 100000
            cf.SampRatesb.delete(0,tk.END) # Samplinrate-Menü ändern
            cf.SampRatesb.insert(0,cf.SampRate)
            
        logging.debug('TraceSelectADC_Mux() with ADC_Mux_Mode = {}, TwoPlusActiveCH = {}'.format(cf.ADC_Mux_Mode.get(),TwoPlusActiveCH))
        SetADC_Mux()
        UpdateTimeTrace()
