#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laden eines Akkus mit dem M1K mit einem Sinus-modulierten Gleichstrom:
Kanal A ist im High Impedance Modus und misst die Spannung am Akku.
Kanal B ist eine Stromquelle mit sinusförmigen Stromverlauf, mit dem der Akku
über einen Vorwiderstand von ca. 10 Ohm aufgeladen wird.

Ausgegeben wird jeweils der Mittelwert und die Standardabweichung der Spannung
von Kanal A (Akkuspannung U_Bat) und des Stroms von Kanal B (Ladestrom I_Bat).
Berechnet wird der differenzielle Widerstand = Wechselanteil(U_Bat)/Wechselanteil(I_Bat).

Der Verlauf der Strom- und Spannungswerte wird im Plot dargestellt und es wird
die Kreuzkorrelation dieser beiden Signale berechnet und im zweiten Plot dargestellt.

Version bat-fit-phase-plot.py funktioniert wia Kurvenfit wesentlich besser.

16.1.2021, S Mack
"""

import time
import numpy as np
from pysmu import Session, Mode
import matplotlib.pyplot as plt
from scipy.signal import correlate


SAMP_RATE = 100000
AWGB_IVAL_MIN = 20 # Minimum Sinus in mA
AWGB_IVAL_MAX = 60 # Maximum Sinus in mA
FREQ = 7 # Frequenz in Hz
WAIT_SATURATION = 5 # 20 s Wartezeit für Sättigung Batteriespannung
NUM_PERIOD = 4 # Anzahl der zu vermessenden Perioden
CURR_OFFSET = 0 # M1K current measurement offset mA

NUM_SAMPLES = np.round(SAMP_RATE*NUM_PERIOD/FREQ,0)

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
    
        adc_signal = dev.read(10000, -1, True)  # Dummy Abtasten um fehlerhafte Werte im Array zu verindern
        time.sleep(0.2)
        adc_signal = dev.read(NUM_SAMPLES, -1, True) # Samples aller vier Kanäle auslesen
    
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
        chb_i_vals = 1000*np.asarray(chb_i_vals)
        
        u_ave = cha_u_vals.mean()
        i_ave = chb_i_vals.mean() - CURR_OFFSET # Offset correction
        r_ave = u_ave / i_ave * 1000
        u_std = cha_u_vals.std()
        i_std = chb_i_vals.std()
        r_std = u_std / i_std * 1000
    
        print("DC: U={:6.3f} V, I={:7.4f} mA  AC: U={:8.6f} V, I={:7.4f} mA, R={:8.4f} Ohm"\
        .format(u_ave, i_ave, u_std, i_std, r_std))
    
        voltage_norm = (cha_u_vals-u_ave)*2/(cha_u_vals.max()-cha_u_vals.min())
        current_norm = (chb_i_vals-i_ave)*2/(chb_i_vals.max()-chb_i_vals.min())
        t = np.arange(0, NUM_SAMPLES/SAMP_RATE, 1/SAMP_RATE)*1000 # Abtastzeiten
        
        xcorr = correlate(voltage_norm, current_norm) # Kreuzkorrelation
        dt = np.linspace(-t[-1], t[-1], 2*NUM_SAMPLES-1) # Zeiten Kreuzkorrelation
        time_shift = dt[xcorr.argmax()]
        phase_shift_rad = 2*np.pi*time_shift/1000*FREQ
        phase_shift_deg = 360*time_shift/1000*FREQ
        
        print('U zu I: Zeitversatz (ms): {:4.3f}, Phasenversatz (rad/deg): {:4.3f}/{:4.3f}'.format(time_shift,phase_shift_rad,phase_shift_deg))
        
        fig, ax = plt.subplots(2,1)
    
        ax[0].plot(t, voltage_norm,color='C0', label='Spannung', zorder=10)
        ax[0].set_xlabel('Zeit (ms)')
        ax[0].set_ylabel('Spannung (norm)')
    
        ax_twin = ax[0].twinx()
        ax_twin.plot(t, current_norm,color='C1',label='Strom', zorder=1)
        ax_twin.set_ylabel('Strom (norm)')
    
        ax[0].legend(loc='upper left', bbox_to_anchor=(0,1), bbox_transform=ax[0].transAxes)
        ax_twin.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax_twin.transAxes)
        
        ax[1].plot(dt,xcorr,color='C0', label='Cross Correlation')
        ax[1].set_xlabel('Zeitversatz (ms)')
        ax[1].set_ylabel('Kreuzkorrelation')
        
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
    session.remove(dev) # damit kein Problem beim erneuten Start    