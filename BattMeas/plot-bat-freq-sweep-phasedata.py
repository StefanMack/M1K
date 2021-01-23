#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skript zum Plotten der Impedanzkurve aus bat-fit-freq-sweep-phase.py
S. Mack, 16.1.2021
"""

import numpy as np
import matplotlib.pyplot as plt

# Werte aus Textdatei in Array einlesen: Erste 6 Zeilen ignorieren, ';' als
# Trennzeichen verwenden und nur Spalten 0, 5 und 6 einlesen.
data = np.loadtxt('bat-freq-sweep-phase_5.txt',skiprows=6, usecols=(0,5,6), delimiter=';')
freq = data[:,0]
bat_resistance = data[:,1]
bat_phase = data[:,2]

fig, ax1 = plt.subplots()

ax1.plot(freq, bat_resistance, '-',color='C0', label='Innenwiderstand', zorder=10)
ax1.set_xlabel('Frequenz (Hz)')
ax1.set_ylabel('R [Ohm]')


ax2 = ax1.twinx() # Zweite Y-Achse mit gemeinsamer X-Achse
ax2.plot(freq, bat_phase, '-',color='C1',label='Phase Spannung zu Strom', zorder=1)
ax2.set_ylabel('Phi [Grad]')


#Legende innerhalb Plotbereich setzen
fig.legend(loc='upper left', bbox_to_anchor=(0.4,1), bbox_transform=ax1.transAxes)
fig.tight_layout()
plt.show()