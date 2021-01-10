#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laden eines Akkus mit dem M1K mit einem Sinus-modulierten Gleichstrom:
Kanal A ist im High Impedance Modus und misst die Spannung am Akku.
Kanal B ist eine Stromquelle mit sinusförmigen Stromverlauf, mit dem der Akku
über einen Vorwiderstand von ca. 10 Ohm aufgeladen wird.

Ausgegeben wird jeweils der Mittelwert und die Standardabweichung der Spannung
von Kanal A (Akkuspannung U_Bat) und des Stroms von Kanal B (Ladestrom I_Bat).
Berechnet werden der Widerstand U_Bat/I_Bat sowie der differenzielle Widerstand
Wechselanteil(U_Bat)/Wechselanteil(I_Bat).
Damit beide Widerstandswerte übereinstimmen, müsste von U_Batt noch die 
Leerlaufspannung abgezogen werden. Diese ist aber nicht bekannt.

9.1.2021, S Mack
"""

import time
import threading as th # damit im getrennten Thread Return-Eingabe erkannt wird
import numpy as np
from pysmu import Session, Mode


SAMP_RATE = 100000
NUM_SAMPLES = 10000
AWGB_IVAL_MIN = 100 # 140
AWGB_IVAL_MAX = 120 # 180
FREQ = 100
TIME_STEP = 5 # Messzuyklus in Sekunden
FILE_NAME = 'bat-charge.txt'
CURR_OFFSET = 14.7 # M1K current measurement offset

keep_going = True # Flag um While-Schleife der Messung zu beenden

# wird als 2. Thread ausgeführt um Return-Eingabe zu erkennen
def key_capture_thread(): 
    global keep_going
    input()
    keep_going = False
    
meas_file = open(FILE_NAME,'w')

meas_file.write('Messreihe Ladevorgang Akku: AC ist Effektivwert\n')
meas_file.write('Frequenz: {} Hz, Sin-Min: {} mA, Sin-Max: {} mA\n\n'.format(FREQ,AWGB_IVAL_MIN,AWGB_IVAL_MAX))
meas_file.write('t [s]; U_DC [v]; I_DC [mA]; R_DC [Ohm]; U_AC [v]; I_AC [mA]; R_Diff [Ohm]; C [mAh] \n\n')

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
        print("WARNING: Firmware version > 2.16 required!")

    session.flush()
    CHA = dev.channels['A']    # Open CHA
    CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
    CHB = dev.channels['B']    # Open CHB
    CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode  
    dev.set_adc_mux(0) # kein ADC-Mux, d.h. Abtasten CA-V/I und CB-V/I

    CHA.mode = Mode.HI_Z
    CHB.mode = Mode.SIMV # Put CHA in SIMV mode
    periodval = SAMP_RATE/FREQ
    min_i = AWGB_IVAL_MIN/1000
    max_i = AWGB_IVAL_MAX/1000
    CHB.sine(max_i, min_i, periodval, 0)    
    session.start(0)

    print("Spannung (V) Strom (mA) Widerstand (Ohm)")
    print("----------------------------------------")
    start_time = time.time()
    charge_val = 0
    while keep_going:
        # Starting acquisition
        adc_signal = dev.read(NUM_SAMPLES, -1, True) # Samples aller vier Kanäle auslesen 

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
        chb_i_vals = np.asarray(chb_i_vals)
        
        u_ave = cha_u_vals.mean()
        i_ave = chb_i_vals.mean() - CURR_OFFSET/1000 # Offset correction
        r_ave = u_ave / i_ave
        u_std = cha_u_vals.std()
        i_std = chb_i_vals.std()
        r_std = u_std / i_std
        charge_val = charge_val + TIME_STEP * i_ave
        meas_time = int(time.time() - start_time)
        print("t={:4}: DC: U={:6.3f} V, I={:7.4f} mA, R={:7.3f} Ohm   AC: U={:8.6f} V, I={:7.4f} mA, R={:8.4f} Ohm, C={:4.1f} mAh"\
        .format(meas_time, u_ave, i_ave*1000, r_ave, u_std, i_std*1000, r_std, charge_val))
        meas_file.write("{};{:.3f};{:.4f};{:.3f};{:.6f};{:.4f};{:.4f};{:4.1f}\n"\
        .format(meas_time, u_ave, i_ave*1000, r_ave,u_std, i_std*1000, r_std, charge_val))
        time.sleep(TIME_STEP)

    print('Programm wurde durch Return-Eingabe beendet.')
    meas_file.close()
    time.sleep(2)
    # Damit M1K nach Beenden im sicheren Zustand
    CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
    CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
    CHA.constant(0.0)
    CHB.constant(0.0)
    if session.continuous:
        session.end()
else:
    print('no devices attached')
