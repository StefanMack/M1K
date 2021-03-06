#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laden eines Akkus mit dem M1K mit einem Sinus-modulierten Gleichstrom und sich
ändernder Modulationsfrequenz.
Kanal A ist im High Impedance Modus und misst die Spannung am Akku.
Kanal B ist eine Stromquelle mit sinusförmigen Stromverlauf, mit dem der Akku
über einen Vorwiderstand von ca. 10 Ohm aufgeladen wird.

Ausgegeben wird für jede Frequenz der Mittelwert und die Standardabweichung der Spannung
von Kanal A (Akkuspannung U_Bat) und des Stroms von Kanal B (Ladestrom I_Bat).
Berechnet wird der differenzielle Widerstand = Wechselanteil(U_Bat)/Wechselanteil(I_Bat).

16.1.2021, S Mack
"""

import time
import threading as th # damit im getrennten Thread Return-Eingabe erkannt wird
import numpy as np
from pysmu import Session, Mode


SAMP_RATE = 100000
NUM_SAMPLES = 40000
AWGB_IVAL_MIN = 10 # 40 sollte gering sein damit während Sweep ähnlicher Ladezustand
AWGB_IVAL_MAX = 60 # 60
START_FREQ = 50
STOP_FREQ = 1000
FREQ_STEP = 50
TIME_STEP = 2 # Messzuyklus in Sekunden
FILE_NAME = 'bat-freq-sweep-absval.txt'
CURR_OFFSET = 14.7 # M1K current measurement offset

keep_going = True # Flag um While-Schleife der Messung zu beenden
first_step = True # Flag für längere Start-Ladezeit vor dem ersten Frquenzwert 

# wird als 2. Thread ausgeführt um Return-Eingabe zu erkennen
def key_capture_thread(): 
    global keep_going
    input()
    keep_going = False
    
meas_file = open(FILE_NAME,'w')

meas_file.write('Messreihe Frequenzsweep Ladestrom Akku: AC ist Effektivwert\n')
meas_file.write('Frequenz Start/Stopp: {}/{} Hz, Sin-Min: {} mA, Sin-Max: {} mA\n\n'.format(START_FREQ,STOP_FREQ,AWGB_IVAL_MIN,AWGB_IVAL_MAX))
meas_file.write('t [s]; f [Hz]; U_DC [V]; I_DC [mA]; U_AC [V]; I_AC [mA]; R_Diff [Ohm]; C [mAh] \n\n')

# 2. Thread starten
th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
print('Zum Beenden Return drücken...')
print()

session = Session(ignore_dataflow=True, sample_rate=SAMP_RATE, queue_size=NUM_SAMPLES)
if session.devices:
    dev = session.devices[0]
    DevID = dev.serial
    print("Device ID:" + str(DevID))
    FWRev = float(dev.fwver)
    HWRev = str(dev.hwver)
    print('Firmware Revision: {}, Hardware Revision: {}'.format(FWRev, HWRev))
    print()
    if FWRev < 2.17:
        print("WARNUNG: Firmware version > 2.16 noetig!")

    session.flush()
    CHA = dev.channels['A']    # Open CHA
    CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
    CHB = dev.channels['B']    # Open CHB
    CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode  
    dev.set_adc_mux(0) # kein ADC-Mux, d.h. Abtasten CA-V/I und CB-V/I

    CHA.mode = Mode.HI_Z
    CHB.mode = Mode.SIMV # Put CHA in SIMV mode
    freq = START_FREQ
    min_i = AWGB_IVAL_MIN/1000
    max_i = AWGB_IVAL_MAX/1000
    charge_val = 0
    
    
    for freq in range(START_FREQ,STOP_FREQ,FREQ_STEP):
        if(keep_going):
            periodval = SAMP_RATE/freq
            CHB.sine(max_i, min_i, periodval, 0)    
            session.start(0)
            if first_step:
                print("Initiale Ladung vor der ersten Messung...")
                time.sleep(10)
                print("Messzeit (s) Frequenz (HZ) DC/AC Spannung (V) Strom (mA) AC Widerstand (Ohm) Ladung (mAh)")
                print("-----------------------------------------------------------------------------------------")
                first_step = False
                start_time = time.time()
            
            time.sleep(TIME_STEP)
            # Starting acquisition
            adc_signal = dev.read(NUM_SAMPLES, -1, True) # Samples aller vier Kanäle auslesen (blocking) 
    
            cha_u_vals = [] # Clear the V Buff array for trace A
            cha_i_vals = [] # Clear the I Buff array for trace A
            chb_u_vals = [] # Clear the V Buff array for trace B
            chb_i_vals = [] # Clear the I Buff array for trace B
      
            index = 0
            num_samples_real = NUM_SAMPLES
    
            if num_samples_real != len(adc_signal): # manchmal gibt ADC weniger Samples zurück als angefordert
                num_samples_real = len(adc_signal)
                
            while index < num_samples_real:
                cha_u_vals.append(adc_signal[index][0][0])
                cha_i_vals.append(adc_signal[index][0][1])
                chb_u_vals.append(adc_signal[index][1][0])
                chb_i_vals.append(adc_signal[index][1][1])
                index = index + 1
            
            cha_u_vals = np.asarray(cha_u_vals)
            chb_i_vals = np.asarray(chb_i_vals) - CURR_OFFSET/1000 # Offset Korrektur
            
            u_ave = cha_u_vals.mean()
            i_ave = chb_i_vals.mean()
            r_ave = u_ave / i_ave
            u_std = cha_u_vals.std()
            i_std = chb_i_vals.std()
            r_std = u_std / i_std
            charge_val = charge_val + TIME_STEP * i_ave
            meas_time = int(time.time() - start_time)
            print("t={:4}: f={:4}  DC: U={:6.3f} V, I={:7.4f} mA  AC: U={:8.6f} V, I={:7.4f} mA, R={:5.4f} Ohm, C={:4.1f} mAh"\
            .format(meas_time, freq, u_ave, i_ave*1000, u_std, i_std*1000, r_std, charge_val))
            meas_file.write("{};{};{:.3f};{:.4f};{:.6f};{:.4f};{:.4f};{:4.1f}\n"\
            .format(meas_time, freq, u_ave, i_ave*1000,u_std, i_std*1000, r_std, charge_val))
            session.end()
            time.sleep(0.5)
        else:
            print('Programm wurde durch Return-Eingabe beendet.')
            break
    meas_file.close()
    time.sleep(2)
    # Damit M1K nach Beenden im sicheren Zustand
    CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
    CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
    CHA.constant(0.0)
    CHB.constant(0.0)
    if session.continuous:
        session.end()
    session.remove(dev) # damit kein Problem beim erneuten Start
else:
    print('kein M1K angeschlossen')
