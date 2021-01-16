#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot der Messung des differentiellen Widerstands von bat-freq-sweep-absval.py
S. Mack, 16.1.2021
"""

import numpy as np
import matplotlib.pyplot as plt

# Werte aus Textdatei in Array einlesen: Erste 5 Zeilen ignorieren, ';' als Trennzeichen
# verwenden und nur die Spalten 0,1,6 und 7 einlesen.
data = np.loadtxt('bat-freq-sweep-absval.txt',skiprows=6, usecols=(1,2,6), delimiter=';')
freq = data[:,0]
bat_volt = data[:,1]
bat_resistance = data[:,2]

fig, ax1 = plt.subplots()

ax1.plot(freq, bat_volt, '-',color='C0', label='Batteriespannung', zorder=10)
ax1.set_xlabel('Frequenz (Hz)')
ax1.set_ylabel('U [mV]', color='C0')
ax1.tick_params('y', colors='C0')

ax2 = ax1.twinx() # Zweite Y-Achse mit gemeinsamer X-Achse
ax2.plot(freq, bat_resistance, '-',color='C1',label='Innenwiderstand', zorder=1)
ax2.set_ylabel('R [Ohm]', color='C1')
ax2.tick_params('y', colors='C1')

fig.legend(loc='upper left', bbox_to_anchor=(0,1), bbox_transform=ax1.transAxes)
fig.tight_layout()