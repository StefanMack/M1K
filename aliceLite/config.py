#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enthält die für alle Module zugreifbaren globalen Variablen
S. Mack, 1.9.20
"""
import tkinter as tk
import numpy as np

root=tk.Tk()
ca = None # Canvas (gesamter Bildschirmbereich)
session = None # Zugriff auf die M1K-Session
devx = None # Zugriff auf das M1K der Session
AWG_2X = 0 # Flag für Verdopplung Samplingrage (war vorher Checkbox)

DevID = "No Device" # Seriennummer des M1K bzw. dieser String falls kein M1K angeschlossen


FontSize = 8
GRW = 720 # Width of the time grid 720 default, X-Richtung geht nach Rechts
GRH = 390 # Height of the time grid 390 default, Y-Richtung geht nach Unten
X0L = FontSize * 7 # Minimum X-Postion des Grids, (Position linke Seite)
Y0T = 25 # Minimum Y-Position des Grids, (Position Oberseite)
MouseX = MouseY = -10

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Oszilloskop Messeinstellungs- und Initialisierungswerte
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#---Sampling und Darstellung
# Mögliche Samplingraten (Hardwareeinstellungen am M1K)
SampRateList = (1024, 2048, 4096, 8192, 16384, 32765, 64000, 93023, 93385, 93750, 94118,
                96385, 96774, 97166, 97561, 97959, 98361, 98765, 99174, 99585, 100000)
BaseSampleRate = 100000 # maximaler Wert kann noch verdoppelt werden falls Mux<=2
AWGSAMPLErate = BaseSampleRate # Sample rate of the AWG channels
SAMPLErate = BaseSampleRate # Scope sample rate can be decimated

MaxSamples = 200000 # Maximale Zahl Samples für Darstellung (# Hardwaresamples pro Loop)
SHOWsamples = 4000 # Number of samples on the screen  
MarkerNum = 0 # Zähler für die Marker bei Maus-Rechsklick im Oszibild, wird bei UpdateTimeScreen() zurückgesetzt

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Buffer-Variablen für eingelesene Messwerte
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
VBuffA = []
#VBuffA = np.zeros(MaxSamples)
VBuffA = np.ones(MaxSamples)*2 # zum Testen
VBuffB = []
#VBuffB = np.zeros(MaxSamples)
VBuffB = np.ones(MaxSamples)*3 # zum Testen
IBuffA = []
#IBuffA = np.zeros(MaxSamples)
IBuffA = np.ones(MaxSamples)*150 # zum Testen
IBuffB = []
#IBuffB = np.zeros(MaxSamples)
IBuffB = np.ones(MaxSamples)*(-150) # zum Testen

#---Vertikal- und Horizontaleinstellungen aus dem UI Boxes und Spinboxes
CHAsb = None # V Vertikalskalierung V/Div CH A Eingabefenster UI Spinbox ("sb")
CHBsb = None # V Vertikalskalierung V/Div CH B Eingabefenster UI Spinbox ("sb")
CHAIsb = None # I Vertikalskalierung A/Div CH A Eingabefenster UI Spinbox ("sb")
CHBIsb = None # I Vertikalskalierung A/Div CH B Eingabefenster UI Spinbox ("sb")
CHAVPosEntry = None # Eingabefenster Nulllinie V CH A in UI neben Skalierung
CHBVPosEntry = None
CHAIPosEntry = None
CHBIPosEntry = None 

HozPossentry = None # Horizontale Position mS
TMsb = None # Spinbox mit Zeitablenkungswert

HozPoss = 0.0 # horizontaler Offset Oszidarstellung
LShift = 0 # hat was mit Trigger zu tun

TIMEdiv = 0.5 # current spin box value
#---Trigger, Cursor
HoldOffentry = None # Eingabefenster mS für Trigger Holdoff
HoldOff = 0.0
TRIGGERlevel = 2.5 # set initial trigger level in V
Is_Triggered = 0
TRIGGERsample = 0           # AD sample trigger point
trgIpol = 0 # interpolated trigger point Wert 0...1 (wieso nötig?)
hldn = 0
TCursor = VCursor = 0

#---Korrektur Offset und Gain (z.B. Kalibrierung oder Tastköpfe) für CHA und CHB
# aus Fenster rechts neben Oszibild
CHAVGainEntry = None
CHBVGainEntry = None
CHAIGainEntry = None
CHBIGainEntry = None
CHAVOffsetEntry = None
CHBVOffsetEntry = None
CHAIOffsetEntry = None
CHBIOffsetEntry = None

#---Initialisierung der Messwertvariablen
DCV1 = DCV2 = MinV1 = MaxV1 = MinV2 = MaxV2 = MidV1 = PPV1 = MidV2 = PPV2 = SV1 = SI1 = 0
PeakVA = PeakVB = PeakIA = PeakIB = 0.0
DCI1 = DCI2 = MinI1 = MaxI1 = MinI2 = MaxI2 = MidI1 = PPI1 = MidI2 = PPI2 = SV2 = SI2 = 0
CHAperiod = CHAfreq = CHBperiod = CHBfreq = 0

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter UI Initialisierswerte, globale Variable
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
CANVASwidth = GRW + 2 * X0L # canvas width
CANVASheight = GRH + Y0T + (FontSize * 10) # canvas height (lokale Variable), 10 Fontgrößen Raum für Darstellungen Messwerte u.A.
# Colors that can be modified (lokale Variablen)
ButtonGreen = "#00ff00"   # 100% green
ButtonRed = "#ff0000" # 100% red
# Colors that can be modified (globale Variablen)


COLORtrace1 = "#00ff00"   # 100% green
COLORtrace2 = "#ff8000"   # 100% orange
COLORtrace3 = "#00ffff"   # 100% cyan
COLORtrace4 = "#ffff00"   # 100% yellow
COLORtrace5 = "#ff00ff"   # 100% magenta
COLORtrace6 = "#C80000"   # 90% red
COLORtrace7 = "#8080ff"   # 100% purple
COLORtraceR1 = "#008000"   # 50% green
COLORtraceR2 = "#905000"   # 50% orange
COLORtext = "#ffffff"     # 100% white
COLORtrigger = "#ff0000"  # 100% red

# UI Arbiträrgenerator innerhalb Scopefenster
AWGAMenus = None
AWGASet = None
AWGBMenus = None
AWGBSet = None
AWGAMinEntry = None
AWGBMinEntry = None
AWGAMaxEntry = None
AWGBMaxEntry = None
AWGAFreqEntry = None
AWGBFreqEntry = None

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter Instanzierungen
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#--- Oszilloskopbild
GridWidth = tk.IntVar(0)
GridWidth.set(1)
TRACEwidth = tk.IntVar(0)
TRACEwidth.set(1)
MouseWidget = None
#--- Ozsilloskop Trigger, Aquire, Abtastung
TRACEaverage = tk.IntVar(0) # Number of average sweeps for average mode
TRACEaverage.set(8)
LPFTrigger = tk.IntVar(0) # trigger lpf on/off
Trigger_LPF_length  = tk.IntVar(0)
Trigger_LPF_length.set(10) # Length of Trigger box car LPF in samples
Two_X_Sample = tk.IntVar(0) # selection variable to set ADC channes for 2X samplerate mode
Two_X_Sample.set(0)

ShowCur = tk.IntVar(0)



RUNstatus = tk.IntVar(0) # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
TgInput = tk.IntVar(0)   # Trigger Input variable
SingleShot = tk.IntVar(0) # variable for single shot triger
ManualTrigger = tk.IntVar(0) # variable for Manual trigger
AutoLevel = tk.IntVar(0) # variable for Auto Level trigger at mid point
TgEdge = tk.IntVar(0)   # Trigger edge variable
# Show channels variables
ShowC1_V = tk.IntVar(0)   # curves to display variables
ShowC1_I = tk.IntVar(0)
ShowC2_V = tk.IntVar(0)
ShowC2_I = tk.IntVar(0)
ShowMath = tk.IntVar(0)

AutoCenterA = tk.IntVar(0)
AutoCenterB = tk.IntVar(0)
SmoothCurves = tk.IntVar(0)

ZOHold = tk.IntVar(0)
TRACEmodeTime = tk.IntVar(0)
TRACEmodeTime.set(0)
ColorMode = tk.IntVar(0)
MathTrace = tk.IntVar(0)
# Im Menü ausgewählte Messfunktionen, werden in aliceTimeFunc benötigt
MeasDCV1 = tk.IntVar(0)
MeasMinV1 = tk.IntVar(0)
MeasMaxV1 = tk.IntVar(0)
MeasPPV1 = tk.IntVar(0)
MeasRMSV1 = tk.IntVar(0)
MeasDCI1 = tk.IntVar(0)
MeasMinI1 = tk.IntVar(0)
MeasMaxI1 = tk.IntVar(0)
MeasPPI1 = tk.IntVar(0)
MeasRMSI1 = tk.IntVar(0)
MeasDCV2 = tk.IntVar(0)
MeasMinV2 = tk.IntVar(0)
MeasMaxV2 = tk.IntVar(0)
MeasPPV2 = tk.IntVar(0)
MeasRMSV2 = tk.IntVar(0)
MeasDCI2 = tk.IntVar(0)
MeasMinI2 = tk.IntVar(0)
MeasMaxI2 = tk.IntVar(0)
MeasPPI2 = tk.IntVar(0)
MeasRMSI2 = tk.IntVar(0)
MeasAPER = tk.IntVar(0)
MeasAFREQ = tk.IntVar(0)
MeasBPER = tk.IntVar(0)
MeasBFREQ = tk.IntVar(0)
MarkerScale = tk.IntVar(0)
MarkerScale.set(1)
SettingsStatus = tk.IntVar(0)

# Arbiträrgenerator ADC-Mux-Modus
ADC_Mux_Mode = tk.IntVar(0) # selection variable to set ADC CHA for voltagr or current 2X samplerate mode
ADC_Mux_Mode.set(0)
AWGAMode = tk.IntVar(0)   # AWG A mode SMVI (0), SIMV (1) oder Hi-Z (2)
AWGAMode.set(2)
AWGBMode = tk.IntVar(0)   # AWG B mode SMVI (0), SIMV (1) oder Hi-Z (2)
AWGBMode.set(2)