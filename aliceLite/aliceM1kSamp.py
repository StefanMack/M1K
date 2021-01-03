#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 28.12.20
"""
import time
import numpy as np
import config as cf
#from aliceAwgFunc import update_awg
import aliceMenus as am
from aliceOsciFunc import (stop_samp, start_samp, UpdateTimeAll, UpdateTimeTrace,
UpdateTimeScreen,ReInterploateTrigger, FindTriggerSample)
import logging

ADsignal1 = []              # Ain signal array channel A and B
twoXSampAllow = 0 # 1 falls 200 kS/s moeglich, abgefragt bei Einstellung Samplingrate

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
    global ADsignal1, twoXSampAllow
    global TIMEdiv1x
    global TRACErefresh
    global SCREENrefresh, DCrefresh
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry,cal
    global PIO_0, PIO_1, PIO_2, PIO_3, PIO_4, PIO_5, PIO_6, PIO_7
    logging.debug("Sample() Sample Rate={} twoXSampAllow={} ADC_Mux_Mode={}".format(cf.SampRate, twoXSampAllow,cf.ADC_Mux_Mode))

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
    # Save previous trace in memory for average trace und falls kein Triggerereignis, damit letzter Trace nochmals angezeigt wird
    cf.VBuffAPrev = cf.VBuffA
    cf.VBuffBPrev = cf.VBuffB
    cf.IBuffAPrev = cf.IBuffA
    cf.IBuffBPrev = cf.IBuffB
    prevTRIGGERsample = cf.TRIGGERsample # wird benötigt, falls kein Triggerereignis gefunden wird

    # Starting acquisition
    ADsignal1 = cf.devx.read(NSamp, -1, True) # Samples aller vier Kanäle auslesen 

#    if cf.session.continuous:
#        logging.debug("Sample() session continuous")
#        ADsignal1 = cf.devx.read(NSamp, -1, True) # get samples for both channel A and B
#        # Bei 200 kS/s sind am Ende aber doppelt so viele Samples vorhanden!
#    else:
#        logging.warning('Session NOT contineous!! Hä?')
#        ADsignal1 = cf.devx.get_samples(NSamp) # get samples for both channel A and B
#        # waite to finish then return to open termination
#        cf.devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
#        cf.devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
#        cf.devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
#        cf.devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open

    cf.VBuffA = [] # Clear the V Buff array for trace A
    cf.IBuffA = [] # Clear the I Buff array for trace A
    cf.VBuffB = [] # Clear the V Buff array for trace B
    cf.IBuffB = [] # Clear the I Buff array for trace B

    increment = 1   
    index = 0
    
    if NSamp != len(ADsignal1): # manchmal gibt ADC weniger Samples zurück als angefordert
        NSamp = len(ADsignal1)
        
    while index < NSamp:     
        if cf.SampRate == 200000: # 200 kS/s: 2 ausgelesene "Kanäle" zu einem echten Kanal zusammenfassen
            if cf.ADC_Mux_Mode == 0: # VA and/or VB
                logging.debug("ADC_Mux_Mode == 0")
                cf.VBuffA.append(ADsignal1[index][0][0])
                cf.VBuffA.append(ADsignal1[index][1][1])
                cf.VBuffB.append(ADsignal1[index][0][1])
                cf.VBuffB.append(ADsignal1[index][1][0])
                cf.IBuffA.append(0.0) # fill as a place holder - wirklich noetig?
                cf.IBuffA.append(0.0) # fill as a place holder
                cf.IBuffB.append(0.0) # fill as a place holder
                cf.IBuffB.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode == 1: # IA and/or IB
                logging.debug("ADC_Mux_Mode == 1")
                cf.IBuffA.append(ADsignal1[index][0][1])
                cf.IBuffA.append(ADsignal1[index][1][0])
                cf.IBuffB.append(ADsignal1[index][0][0])
                cf.IBuffB.append(ADsignal1[index][1][1])
                cf.VBuffA.append(0.0) # fill as a place holder
                cf.VBuffA.append(0.0) # fill as a place holder
                cf.VBuffB.append(0.0) # fill as a place holder
                cf.VBuffB.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode == 4: # VA and IA
                logging.debug("ADC_Mux_Mode == 4")
                cf.VBuffA.append(ADsignal1[index][0][0])
                cf.VBuffA.append(ADsignal1[index][1][1])
                cf.IBuffA.append(ADsignal1[index][0][1])
                cf.IBuffA.append(ADsignal1[index][1][0])
                cf.VBuffB.append(0.0) # fill as a place holder
                cf.VBuffB.append(0.0) # fill as a place holder
                cf.IBuffB.append(0.0) # fill as a place holder
                cf.IBuffB.append(0.0) # fill as a place holder
            elif cf.ADC_Mux_Mode == 5: # VB and IB
                logging.debug("ADC_Mux_Mode == 5")
                cf.VBuffB.append(ADsignal1[index][0][1])
                cf.VBuffB.append(ADsignal1[index][1][0])
                cf.IBuffB.append(ADsignal1[index][0][0])
                cf.IBuffB.append(ADsignal1[index][1][1])
                cf.VBuffA.append(0.0) # fill as a place holder
                cf.VBuffA.append(0.0) # fill as a place holder
                cf.IBuffA.append(0.0) # fill as a place holder
                cf.IBuffA.append(0.0) # fill as a place holder
        else: # <=100 kS/s: Ausgelesener Kanal gleich echter Kanal
            cf.VBuffA.append(ADsignal1[index][0][0])
            cf.IBuffA.append(ADsignal1[index][0][1])
            cf.VBuffB.append(ADsignal1[index][1][0])
            cf.IBuffB.append(ADsignal1[index][1][1])
        index = index + increment
    logging.debug('sample(): CA-I/CB-I # of samples read = {}/{} CA-I[100]/CB-I[100] = {}/{}'.format(len(cf.IBuffA),len(cf.IBuffB),cf.IBuffA[100],cf.IBuffB[100]))
    cf.NSamples = len(cf.VBuffA) # bei 200 kS/s Verdopplung
    cf.NSamples = len(cf.VBuffA) # bei 200 kS/s Verdopplung
    
    # nur Umrechnung in mA für I-Kanäle, Wandlung in Numpy-Arrays da oben evtl. als Listen neu instanziert
    cf.VBuffA = np.array(cf.VBuffA)
    cf.VBuffB = np.array(cf.VBuffB)
    cf.IBuffA = np.array(cf.IBuffA) * 1000 # convert to mA
    cf.IBuffB = np.array(cf.IBuffB) * 1000 # convert to mA

    # Offset und Gain-Korrektur aus Calibrate Gain / Offset
    logging.debug('sample(): cf.CHAVOffset={}, cf.CHAVGain={}'.format(cf.CHAVOffset,cf.CHAVGain))
    cf.VBuffA = (cf.VBuffA - cf.CHAVOffset) * cf.CHAVGain
    cf.VBuffB = (cf.VBuffB - cf.CHBVOffset) * cf.CHBVGain
    cf.IBuffA = (cf.IBuffA - cf.CHAIOffset) * cf.CHAIGain
    cf.IBuffB = (cf.IBuffB - cf.CHBIOffset) * cf.CHBIGain
        
    logging.debug('sample(): Trigger Input TgInput = {}'.format(cf.TgInput.get()))
    # Find trigger sample point if necessary
    if cf.TgInput.get() == 0: # Falls kein Trigger trotzdem Trace Averaging aber ohne Versatz 
        cf.TRIGGERsample = 0
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

            if cf.FirstSampTrace == True: # erster Trace
                logging.debug('sample(): First averaging trace')
                cf.AveVBuffA = cf.VBuffA   
                cf.AveVBuffB = cf.VBuffB
                cf.AveIBuffA = cf.IBuffA
                cf.AveIBuffB = cf.IBuffB
                cf.FirstSampTrace = False

            if cf.FirstSampTrace == False: # nicht erster Trace
                try: # Neue Traces in Mittelung einberechnen
                    logging.debug('sample(): Calculating N = {} averages for all traces'.format(cf.NAveTrace.get()))
                    cf.AveVBuffA = cf.AveVBuffA + (cf.VBuffA - cf.AveVBuffA) / cf.NAveTrace.get()
                    cf.AveIBuffA = cf.AveIBuffA + (cf.IBuffA - cf.AveIBuffA) / cf.NAveTrace.get()
                    cf.AveVBuffB = cf.AveVBuffB + (cf.VBuffB - cf.AveVBuffB) / cf.NAveTrace.get()
                    cf.AveIBuffB = cf.AveIBuffB + (cf.IBuffB - cf.AveIBuffB) / cf.NAveTrace.get()
                except:
                    # buffer size mismatch so reset memory buffers
                    logging.warning('sample(): Averaging exception')
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
        stop_samp()  
        cf.SingleShot.set(0)
    if (cf.RUNstatus.get() == 3) or (cf.RUNstatus.get() == 4): # 3: stop now, 4: stop and restart
        if cf.RUNstatus.get() == 3:
            cf.RUNstatus.set(0)
        if cf.RUNstatus.get() == 4:          
            cf.RUNstatus.set(1)
    UpdateTimeScreen()
            
            
# Einstellen der Samplingrate, falls Wahl in Spinbox oder Änderung CH-Kombi
def SetSampleRate():
    WasRunning = 0
    if (cf.RUNstatus.get() == 1):
        WasRunning = 1
        stop_samp() # bewirkt u.a. session.end()
    try:
        rateSet = int(cf.SampRatesb.get())
        if (rateSet == 200000 and twoXSampAllow == 0): # 200 kS/s nicht für CH-Kombi erlaubt
            logging.debug("200 kS/s not possible for this combination of active channels.")
            cf.SampRate = 100000 # wenn Eingabe unzulässig, auf 100 kS/s zurücksetzen
            cf.SampRatesb.invoke('buttondown') # Wert Spinbox vermindern auf 100 kS/s
        else:
            cf.SampRate = rateSet
            logging.debug("SetSampleRate() NewRate={} S/s".format(cf.SampRate))
    except:
        logging.warning('Exception in SetSampleRate()')
    cf.session.configure(sample_rate=min(100000,cf.SampRate)) # bei 200 kS/s wegen Mux nur 100 kS/s einstellen
    time.sleep(0.1)
    if (WasRunning == 1):
        WasRunning = 0
        start_samp() # bewirkt u.a. setup_awg() und session.start(0)
        SetADC_Mux() # muss NACH session.start(0) (kont. Modus) erfolgen
          
#**************************************************
# Hier Einstellung der Abtastrate auf 200.000 S/s
#**************************************************
def SetADC_Mux():
# Abhänig von aktiven Kanänen (UI) und Samplingrate (UI) setzen des ADC-Mux
# Mux-Mode: Welche Kombination von CA-V/-I, CB-V/-I abgetastet wird, siehe auch TraceSelectADC_Mux()
# Achtung! Werte ADC_Mux_Mode und "devx Mux Mode" teils nicht gleich 
    logging.debug('SetADC_Mux() ADC_Mux_Mode={} SampRate={} twoXSampAllow={}'.format(cf.ADC_Mux_Mode, cf.SampRate,twoXSampAllow))
    if (cf.SampRate == 200000 and twoXSampAllow == 1): # Wenn Option 200 kS/s angeklickt und aufgrund Kombi erlaubt
        if cf.ADC_Mux_Mode == 0: # CA-V and/or CB-V
            cf.devx.set_adc_mux(1)
            logging.debug('devx.set_adc_mux(1)')
            time.sleep(0.02)
        elif cf.ADC_Mux_Mode == 1: # CA-I and/or CB-I
            cf.devx.set_adc_mux(2)
            logging.debug('devx.set_adc_mux(2)')
            time.sleep(0.02)
        elif cf.ADC_Mux_Mode == 4: # CA-V and CA-I
            cf.devx.set_adc_mux(4)
            logging.debug('devx.set_adc_mux(4)')
            time.sleep(0.02)
        elif cf.ADC_Mux_Mode == 5: # CB-V and CB-I
            cf.devx.set_adc_mux(5)
            logging.debug('devx.set_adc_mux(5)')
            time.sleep(0.02)
    else: # 100 kS/s oder weniger egal welche Kombi
        cf.devx.set_adc_mux(0)
        logging.debug('devx.set_adc_mux(0)')


# je nachdem welche Signale (jeweils V oder I der der beiden Kanaele A und B) abgetastet werden sollen, wird entsprechend
# das Multiplexing des ADC gesetzt. Achtung: Bei 200 kS/s funktionieren nur Zweierkombinationen ohne CA-V/CB-I und CB-V/CA-I
def TraceSelectADC_Mux():
    global twoXSampAllow # bei drei oder mehr abzutastenden Signalen und CA-V/CB-I bzw. CB-V/CA-I keine 200 kS/s moeglich
    if cf.devx != None:
        if cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode = 0 # All four traces
            twoXSampAllow = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode = 0 # three traces
            twoXSampAllow = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode = 0 # three traces
            twoXSampAllow = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode = 0 # three traces
            twoXSampAllow = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode = 0 # three traces
            twoXSampAllow = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode = 4 # CA-V and CA-I
            twoXSampAllow = 1
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode = 5 # CB-V and CB-I
            twoXSampAllow = 1 
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode = 1 # CA-I and CB-I
            twoXSampAllow = 1
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode = 0 # CA-V and CB-V
            twoXSampAllow = 1        
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode = 2 # CA-V and CB-I kein 200 kS/s möglich
            twoXSampAllow = 0
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode = 3 # CA-I and CB-V kein 200 kS/s möglich
            twoXSampAllow = 0
        elif cf.ShowC1_V.get() == 1 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode = 0 # just CA-V
            twoXSampAllow = 1
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 1 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode = 0 # just CB-V
            twoXSampAllow = 1
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 1 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 0:
            cf.ADC_Mux_Mode = 1 # just CA-I
            twoXSampAllow = 1
        elif cf.ShowC1_V.get() == 0 and cf.ShowC1_I.get() == 0 and cf.ShowC2_V.get() == 0 and cf.ShowC2_I.get() == 1:
            cf.ADC_Mux_Mode = 1 # just CB-I
            twoXSampAllow = 1
        else:
            cf.ADC_Mux_Mode = 0 # gar keine Traces
            twoXSampAllow = 1
        if (cf.SampRate == 200000) and (twoXSampAllow == 0): # falls während 200 kS/s Wechsel auf nicht erlaubte Kombi
            logging.debug('Sampling rate reuced to 100 kS/s.')
            SetSampleRate() # reduziert Samplingrate auf 100 kS/s
            
        logging.debug('TraceSelectADC_Mux() with ADC_Mux_Mode = {}, twoXSampAllow = {}'.format(cf.ADC_Mux_Mode,twoXSampAllow))
        SetADC_Mux()
        UpdateTimeTrace()
