#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laden eines Akkus mit dem M1K mit einem Sinus-modulierten Gleichstrom:
Kanal A ist im High Impedance Modus und misst die Spannung am Akku.
Kanal B ist eine Stromquelle mit sinusförmigen Stromverlauf, mit dem der Akku
über einen Vorwiderstand von ca. 10 Ohm aufgeladen wird.

Ausgegeben wird jeweils der Mittelwert und die Standardabweichung der Spannung
von Kanal A (Akkuspannung U_Bat) und des Stroms von Kanal B (Ladestrom I_Bat).
Berechnet wird der differenzielle Widerstand Wechselanteil(U_Bat)/Wechselanteil(I_Bat).

Der Verlauf der Strom- und Spannungswerte wird im Plot dargestellt und es wird
für jeden Velauf eine Sinusfunktion angefittet und der Phasenunterschied beider
Funktionen wird ausgegeben.

Gut geeignet zum Test ob Kurvenfit funktioniert.

16.1.2021, S Mack
"""

import time
import numpy as np
from pysmu import Session, Mode
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


SAMP_RATE = 100000
AWGB_IVAL_MIN = 20 # mA! 20 Minimum Sinus in mA
AWGB_IVAL_MAX = 60 # mA ! 60 Maximum Sinus in mA
FREQ = 140 # Frequenz in Hz
WAIT_SATURATION = 10 # s 10 Wartezeit für Sättigung Batteriespannung
NUM_PERIOD = 4 # 4 Anzahl der zu vermessenden Perioden
CURR_OFFSET = 0 # mA! M1K Offsetfehler Strommessung

NUM_SAMPLES = np.round(SAMP_RATE*NUM_PERIOD/FREQ,0)

def my_sin(x, omega, amplitude, phase, offset): # Sinusfunktion fuer Fit
    return np.sin(x * omega + phase) * amplitude + offset

try:
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
        periodval = SAMP_RATE/FREQ
        min_i = AWGB_IVAL_MIN/1000
        max_i = AWGB_IVAL_MAX/1000
        CHB.sine(max_i, min_i, periodval, 0)    
        session.start(0)
        print('Anlegen des Sinusstroms für {} Sekunden zur Saettigung der Batteriespannung...'.format(WAIT_SATURATION))
        for time_step in range(0,WAIT_SATURATION,1):
            print('\rnoch {} Sekunden'.format(WAIT_SATURATION-time_step), end='\r')
            time.sleep(1)
        print('')
        print('Start Messung: Frequenz={} Hz, i_min={} mA, i_max={} mA'.format(FREQ,AWGB_IVAL_MIN,AWGB_IVAL_MAX))
    
        adc_signal = dev.read(10000, -1, True)  # Dummy Abtasten sonst fehlerhafte Werte im Array
        time.sleep(0.2)
        adc_signal = dev.read(NUM_SAMPLES, -1, True) # Samples aller vier Kanaele auslesen
    
        cha_u_vals = [] # Buffer loeschen
        cha_i_vals = []
        chb_u_vals = []
        chb_i_vals = []
      
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
        u_std = cha_u_vals.std()
        i_std = chb_i_vals.std()
        r_std = u_std / i_std
    
        print("DC: U={:6.3f} V, I={:7.4f} mA   AC: U={:8.6f} V, I={:7.4f} mA, R={:8.4f} Ohm"\
        .format(u_ave, i_ave*1000, u_std, i_std*1000, r_std))
    
        voltage_norm = (cha_u_vals-u_ave)*2/(cha_u_vals.max()-cha_u_vals.min())
        current_norm = (chb_i_vals-i_ave)*2/(chb_i_vals.max()-chb_i_vals.min())
        t = np.arange(0, NUM_SAMPLES/SAMP_RATE, 1/SAMP_RATE)*1000 # Abtastzeiten in ms
        
        fit_start_vals=[FREQ*2*np.pi, 1.0, 0.0, 0.0] # Startwerte Fit (Freq, Ampl, Phase, Offset)
        voltage_fit_result = curve_fit(my_sin, t/1000, voltage_norm, p0=fit_start_vals) # bounds funktionieren nicht richtig
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
        if(phase_shift_rad<0): phase_shift_rad = phase_shift_rad + 2*np.pi # Phasenversatz u zu I immer positiv
        phase_shift_deg = 180*phase_shift_rad/np.pi
        
        print('Phase U (rad): {:4.3f}  Phase I (rad): {:4.3f}'.format(phase_voltage,phase_current))
        print('I zu U: Phasenversatz (rad/deg): {:4.3f}/{:4.3f}'.format(phase_shift_rad,phase_shift_deg))
        
        voltage_fit = my_sin(t/1000, *voltage_fit_result[0])
        current_fit = my_sin(t/1000, *current_fit_result[0])
        
        fig, ax = plt.subplots(2,1)
    
        ax[0].plot(t, voltage_norm, color='C0', label='Spannung')
        ax[0].plot(t, current_norm, color='C1', label='Strom')
        ax[0].set_xlabel('Zeit (ms)')
        ax[0].set_ylabel('Messwert (a.u.)')  
        ax[0].legend()
    
        ax[1].plot(t,voltage_fit,color='C0', label='Spannung')
        ax[1].plot(t,current_fit,color='C1', label='Strom')
        ax[1].set_xlabel('Zeit (ms)')
        ax[1].set_ylabel('Fit (a.u.)')
        ax[1].legend()
        
        fig.tight_layout()
        plt.show()
    
    else:
        print('kein M1K angeschlossen')
except:
    print('...da ging wohl was schief...')

finally:
    # damit M1K nach Beenden im sicheren Zustand
    CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
    CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
    CHA.constant(0.0)
    CHB.constant(0.0)
    if session.continuous:
        session.end()
    time.sleep(0.2)
    session.remove(dev) # damit kein Problem  beim erneuten Start.   