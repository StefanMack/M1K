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

Über die Kreuzkorrelation von Spannung und Strom wird der Phasenversatz der
beiden Werteverläufe bestimmt. Funktioniert nicht so gut, weil Samglingrate
zu gering. Version bat-fit-freq-sweep-phase.py via Anpassen einer Sinusfunktion
funktioniert wesentlich besser.

16.1.2021, S Mack
"""

import time
import threading as th # damit im getrennten Thread Return-Eingabe erkannt wird
import numpy as np
from pysmu import Session, Mode
from scipy.signal import correlate


SAMP_RATE = 100000
WAIT_FIRST_CHARGE = 10 # Initiale Ladezeit vor der ersten Messung
WAIT_SATURATION = 5 # 20 s Wartezeit für Sättigung Batteriespannung
AWGB_IVAL_MIN = 20 # 40 sollte gering sein damit während Sweep ähnlicher Ladezustand
AWGB_IVAL_MAX = 60 # 60
START_FREQ = 4
STOP_FREQ = 10
FREQ_STEP = 2
NUM_PERIOD = 4 # Anzahl der zu vermessenden Perioden
TIME_STEP = 2 # Messzuyklus in Sekunden damit neue Frequenz eingeschwungen
FILE_NAME = 'bat-corr-freq-sweep-phase.txt'
CURR_OFFSET = 0 # M1K current measurement offset
NUM_SAMPLES_MAX = 100000 # maximale Zahl von Abtastungen


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
    
    for freq in range(START_FREQ,STOP_FREQ,FREQ_STEP):
        num_samples = np.round(SAMP_RATE*NUM_PERIOD/freq,0)
        if(keep_going):
            periodval = SAMP_RATE/freq
            CHB.sine(max_i, min_i, periodval, 0)    
            session.start(0)
            if first_step:
                print("Initiales Laden vor der ersten Messung...")
                for time_step in range(0,WAIT_FIRST_CHARGE,1):
                    print('\rnoch {} Sekunden'.format(WAIT_FIRST_CHARGE-time_step), end='\r')
                    time.sleep(1)
                    
                print('')
                print("Frequenz (HZ) -- DC/AC Spannung (V) Strom (mA) -- AC Widerstand (Ohm) -- Phase (Grad/Rad/ms)")
                print("--------------------------------------------------------------------------------------")
                first_step = False
            time.sleep(TIME_STEP)
            adc_signal = dev.read(10000, -1, True)  # Dummy Abastung da sonst fehlerhafte Messwerte im Array
            time.sleep(0.2)

            adc_signal = dev.read(num_samples, -1, True) # Samples aller vier Kanaele auslesen (blocking) 
    
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
            t = np.arange(0, num_samples/SAMP_RATE, 1/SAMP_RATE)*1000 # Abtastzeiten in ms
            
            xcorr = correlate(voltage_norm, current_norm) # Kreuzkorrelation
            dt = np.linspace(-t[-1], t[-1], 2*num_samples-1) # Zeiten Kreuzkorrelation
            time_shift = dt[xcorr.argmax()] # Zei der Kreuzkorrelation mit hoechstem Wert = Zeitversatz beider Messkurven
            phase_shift_deg = 360*time_shift/1000*freq
            phase_shift_rad = 2*np.pi*time_shift/1000*freq

            print("f={:4} Hz DC: U={:5.3f} V, I={:7.4f} mA   AC: U={:8.6f} V, I={:7.4f} mA, R={:6.4f} Ohm, Phi={:5.3f} deg / {:4.4f} rad, Dt={:3.2f} ms"\
            .format(freq, u_ave, i_ave, u_std, i_std, r_std, phase_shift_deg, phase_shift_rad, time_shift))
            meas_file.write("{};{:.3f};{:.4f};{:.4f};{:.4f};{:.3f};{:.4f};{:.4f}\n"\
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
    
session.remove(dev) # damit kein Problem beim erneuten Start