#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skript zum Plotten der Impedanzkurve aus bat-fit-freq-sweep-phase.py
sowie der Ortskurve daraus
S. Mack, 24.1.2021
"""

import numpy as np
import matplotlib.pyplot as plt

LOG = True # Flag für logarithmische Darstellung der Frequenz

# Werte aus Textdatei in Array einlesen: Erste 6 Zeilen ignorieren, ';' als
# Trennzeichen verwenden und nur Spalten 0, 5 und 6 einlesen.
data = np.loadtxt('bat-freq-sweep-phase_10.txt',skiprows=6, usecols=(0,5,6), delimiter=';')
freq = data[:,0]
abs_z = data[:,1] # Betrag
ph_z = data[:,2] # Phase

re_z = abs_z * np.cos(np.pi/180*ph_z) # Realteil
im_z = abs_z * np.sin(np.pi/180*ph_z) # Imaginärteil

#plt.rcParams["text.usetex"] =True
fig, ax = plt.subplots(2,1)

if LOG:
    ax[0].semilogx(freq, abs_z, '-',color='C0', label='$|Z_{Bat}|$')
else:
    ax[0].plot(freq, abs_z, '-',color='C0', label='$|Z_{Bat}|$')
ax[0].set_xlabel('Frequenz (Hz)')
ax[0].set_ylabel('$|Z_{Bat}|$'+' $[\Omega]$') # Latex Omega

ax_phase = ax[0].twinx() # Zweite Y-Achse mit gemeinsamer X-Achse
if LOG:
    ax_phase.semilogx(freq, ph_z, '-',color='C1',label='φ  $Z_{Bat}$')
else:
    ax_phase.plot(freq, ph_z, '-',color='C1',label='φ $Z_{Bat}$')
ax_phase.set_ylabel('$φ [°]$') # Unicode Phi, Latex /varphi funktioniert nicht

ax[1].plot(re_z, -im_z, '.',color='C2')
ax[1].set_xlabel('$Re(Z_{Bat})$'+' $[\Omega]$')
ax[1].set_ylabel('$-Im(Z_{Bat})$'+' $[\Omega]$')
ax[1].set_ylim(0,0.6)
ax[1].annotate('{:.2f} Hz'.format(freq[0]),xy=(re_z[0],-im_z[0]+0.05),size=7,rotation=90,ha='center',va='bottom')
ax[1].annotate('{:.1f} Hz'.format(freq[30]),xy=(re_z[30],-im_z[30]+0.05),size=7,rotation=90,ha='center',va='bottom')
ax[1].annotate('{:.0f} Hz'.format(freq[60]),xy=(re_z[60],-im_z[60]+0.05),size=7,rotation=90,ha='center',va='bottom')

#Legende innerhalb Plotbereich setzen
fig.legend(loc='upper left', bbox_to_anchor=(0.0,0.6), bbox_transform=ax[0].transAxes)
fig.tight_layout()
plt.show()