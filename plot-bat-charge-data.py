#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 10:18:15 2021

@author: mackst
"""

import numpy as np
import matplotlib.pyplot as plt

# Werte aus Textdatei in Array einlesen: Erste 5 Zeilen ignorieren, ';' als Trennzeichen
# verwenden und nur die Spalten 0,1,6 und 7 einlesen.
data = np.loadtxt('bat-charge_4.txt',skiprows=6, usecols=(0,1,6,7), delimiter=';')
t = data[:,0]
bat_charge = data[:,3]
bat_volt = data[:,1]
bat_resistance = data[:,2]
DELTA = 1 # Bug Workaround, sonst 1. und letzter Tic sek. X-Achse falsches Lable

def forward(x): # Transformation Ladezeiten (Spalte 0) auf Ladung (Spalte3)
    return np.interp(x, t, bat_charge)
def inverse(x): # Transformation  Ladung (Spalte3) auf Ladezeiten (Spalte 0)
    return np.interp(x, bat_charge, t)

fig, ax1 = plt.subplots()

ax1.plot(t, bat_volt, '-',color='C0', label='Batteriespannung', zorder=10)
ax1.set_xlabel('Ladezeit (s)')
ax1.set_ylabel('U [V]', color='C0')
ax1.tick_params('y', colors='C0')
ax1.set_xlim(DELTA,max(t)-DELTA) # Bug Workaround wegen Tics s.o.
# Zweite X-Achse unterhalb der ersten über Transformationen s.o.
secax1 = ax1.secondary_xaxis(location = -0.2,functions=(forward, inverse))
secax1.set_xlabel('Ladung (mAh)')

ax2 = ax1.twinx() # Zweite Y-Achse mit gemeinsamer X-Achse
ax2.plot(t, bat_resistance, '-',color='C1',label='Innenwiderstand', zorder=1)
ax2.set_ylabel('R [Ohm]', color='C1')
ax2.tick_params('y', colors='C1')
ax2.set_xlim(DELTA,max(t)-DELTA) # Bug Workaround wegen Tics s.o.

fig.legend(loc='upper left', bbox_to_anchor=(0,1), bbox_transform=ax1.transAxes)
fig.tight_layout()