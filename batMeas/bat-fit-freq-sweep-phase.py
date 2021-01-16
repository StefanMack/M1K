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

Über einen Sinusfit jeweils von Spannung und Strom wird der Phasenversatz der
beiden Werteverläufe bestimmt.

16.1.2021, S Mack
"""

import time
import threading as th # damit im getrennten Thread Return-Eingabe erkannt wird
import numpy as np
from pysmu import Session, Mode
from scipy.optimize import curve_fit


SAMP_RATE = 100000
WAIT_FIRST_CHARGE = 10 # 10 Initiale Ladezeit vor der ersten Messung
AWGB_IVAL_MIN = 20 # mA! 20 sollte gering sein damit während Sweep ähnlicher Ladezustand
AWGB_IVAL_MAX = 60 # mA! 60 sollte ca. 20-40 mA groeßer sein als AWGB_IVAL_MIN
START_FREQ = 4
STOP_FREQ = 100
FREQ_STEP = 2
NUM_PERIOD = 4 # 4 Anzahl der zu vermessenden Perioden pro Frequenz
TIME_STEP = 2 # 2 Wartezeit in Sekunden damit neue Frequenz eingeschwungen
FILE_NAME = 'bat-freq-sweep-phase.txt' # Datei zum Abspeichern Messwerte
CURR_OFFSET = 0 # mA! Offsetfehler M1K Strommessung
NUM_SAMPLES_MAX = 100000 # maximale Zahl von Abtastungen

keep_going = True # Flag um While-Schleife der Messung zu beenden
first_step = True # Flag für laengere Start-Ladezeit vor dem ersten Frquenzwert 

# wird als 2. Thread ausgeführt um Return-Eingabe zu erkennen
def key_capture_thread(): 
    global keep_going
    input()
    keep_going = False
    
def my_sin(x, omega, amplitude, phase, offset): # Sinusfunktion fuer Fit
    return np.sin(x * omega + phase) * amplitude + offset

    
meas_file = open(FILE_NAME,'w') 

meas_file.write('Messreihe Frequenzsweep Ladestrom Akku: AC ist Effektivwert\n')
meas_file.write('Frequenz Start/Stopp/Delta: {}/{}/{} Hz, Sin-Min: {} mA, Sin-Max: {} mA\n\n'
                .format(START_FREQ,STOP_FREQ,FREQ_STEP,AWGB_IVAL_MIN,AWGB_IVAL_MAX))
meas_file.write('f [Hz]; U_DC [v]; I_DC [mA]; U_AC [v]; I_AC [mA]; R_Diff [Ohm]; Phi [deg]; Phi [rad] \n\n')

# 2. Thread starten
th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
print('Zum Beenden Return drücken...')
print()



session = Session(ignore_dataflow=True, sample_rate=SAMP_RATE, queue_size=NUM_SAMPLES_MAX)
if session.devices:
    dev = session.devices[0]
    DevID = dev.serial
    print("Device ID:" + str(DevID))
    FWRev = float(dev.fwver)
    HWRev = str(dev.hwver)
    print('Firmware Revision: {}, Hardware Revision: {}'.format(FWRev, HWRev))
    print()
    if FWRev < 2.17:
        print("WARNUNG: Firmware Version > 2.16 notwendig!")

    session.flush()
    CHA = dev.channels['A']    # Open CHA
    CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
    CHB = dev.channels['B']    # Open CHB
    CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode  
    dev.set_adc_mux(0) # kein ADC-Mux, d.h. Abtasten CA-V/I und CB-V/I

    CHA.mode = Mode.HI_Z
    CHB.mode = Mode.SIMV # Put CHA in SIMV mode
    freq = START_FREQ
    min_i = AWGB_IVAL_MIN/1000 # da Konstante in mA
    max_i = AWGB_IVAL_MAX/1000 # da Konstante in mA
    
    for freq in range(START_FREQ,STOP_FREQ,FREQ_STEP):
        num_samples = np.round(SAMP_RATE*NUM_PERIOD/freq,0)
        if(keep_going):
            periodval = np.round(SAMP_RATE/freq,0)
            CHB.sine(max_i, min_i, periodval, 0)    
            session.start(0)
            if first_step: # laengeres Aufladen vor Start Messung
                print("Initiales Laden vor der ersten Messung...")
                for time_step in range(0,WAIT_FIRST_CHARGE,1):
                    print('\rnoch {} Sekunden'.format(WAIT_FIRST_CHARGE-time_step), end='\r')
                    time.sleep(1)
                print('')
                print('Start Messung: Frequenz Start/Stopp/Delta: {}/{}/{} Hz, i_min={} mA, i_max={} mA'
                      .format(START_FREQ,STOP_FREQ,FREQ_STEP,AWGB_IVAL_MIN,AWGB_IVAL_MAX))
                print('')
                print("Frequenz (HZ) -- DC/AC Spannung (V) Strom (mA) -- AC Widerstand (Ohm) -- Phase (Grad/Rad)")
                print("--------------------------------------------------------------------------------------")
                first_step = False
            time.sleep(TIME_STEP)
            adc_signal = dev.read(10000, -1, True)  # Dummy Auslesen, sonst fehlerhafte Werte im Array
            time.sleep(0.2)
            adc_signal = dev.read(num_samples, -1, True) # Samples aller vier Kanäle auslesen (blocking) 
    
            cha_u_vals = [] # Buffer loeschen
            cha_i_vals = []
            chb_u_vals = []
            chb_i_vals = []
      
            index = 0
    
            if num_samples != len(adc_signal): # manchmal gibt ADC weniger Samples zurück als angefordert
                num_samples = len(adc_signal)
                
            while index < num_samples:
                cha_u_vals.append(adc_signal[index][0][0])
                cha_i_vals.append(adc_signal[index][0][1])
                chb_u_vals.append(adc_signal[index][1][0])
                chb_i_vals.append(adc_signal[index][1][1])
                index = index + 1
            
            cha_u_vals = np.asarray(cha_u_vals)
            chb_i_vals = 1000*np.asarray(chb_i_vals) - CURR_OFFSET # Offset Korrektur
            
            u_ave = cha_u_vals.mean()
            i_ave = chb_i_vals.mean()
            r_ave = u_ave / i_ave * 1000
            u_std = cha_u_vals.std()
            i_std = chb_i_vals.std()
            r_std = u_std / i_std * 1000
            
            voltage_norm = (cha_u_vals-u_ave)*2/(cha_u_vals.max()-cha_u_vals.min())
            current_norm = (chb_i_vals-i_ave)*2/(chb_i_vals.max()-chb_i_vals.min())
            t = np.arange(0, num_samples/SAMP_RATE, 1/SAMP_RATE)*1000 # Abtastzeiten in ms (!)
            
            fit_start_vals=[freq*2*np.pi, 1.0, 0.0, 0.0] # Startwerte Fit (Freq, Ampl, Phase, Offset)
            voltage_fit_result = curve_fit(my_sin, t/1000, voltage_norm, p0=fit_start_vals) # /1000 da ms
            current_fit_result = curve_fit(my_sin, t/1000, current_norm, p0=fit_start_vals)
            
            if(voltage_fit_result[0][1]>=0):
                phase_voltage = voltage_fit_result[0][2]
            else: # falls negative Amplitude als Fit Umrechnung Phase auf positive Ampliude
                phase_voltage = voltage_fit_result[0][2] + np.pi
            if(current_fit_result[0][1]>=0):
                phase_current = current_fit_result[0][2]
            else: # s.o.
                phase_current = current_fit_result[0][2] + np.pi
            
            phase_shift_rad = (phase_current - phase_voltage)
            if(phase_shift_rad<0): phase_shift_rad = phase_shift_rad + 2*np.pi # Phasenversatz ist immer positiv
            phase_shift_deg = 180*phase_shift_rad/np.pi
            
            print("f={:4} Hz  DC: U={:5.3f} V, I={:7.4f} mA  AC: U={:8.6f} V, I={:7.4f} mA, R={:6.4f} Ohm  Phi={:5.3f} deg / {:4.4f} rad"\
            .format(freq, u_ave, i_ave, u_std, i_std, r_std, phase_shift_deg, phase_shift_rad))
            meas_file.write("{};{:.3f};{:.4f};{:.4f};{:.4f};{:.3f};{:.4f};{:.5f}\n"\
            .format(freq, u_ave, i_ave, u_std, i_std, r_std, phase_shift_deg, phase_shift_rad))
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
else:
    print('kein M1K angeschlossen')
    
session.remove(dev) # damit kein Problem beim erneutem Programmstart. 