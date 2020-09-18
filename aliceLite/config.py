#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enthält die für alle Module zugreifbaren globalen Variablen
S. Mack, 15.9.20
"""
import tkinter as tk
import numpy as np

root=tk.Tk() # Tkinter Root Fenster (gesamte Anwendung)     

ca = None # Canvas (gesamter Bildschirmbereich)
session = None # Zugriff auf die M1K-Session
devx = None # Zugriff auf das M1K der Session
CHA = CHB = None # M1K Instanzen für die beiden Kanäle A und B

DevID = "No Device" # Seriennummer des M1K bzw. dieser String falls kein M1K angeschlossen
running = 1 # wechselt auf 0, wenn exit-Button angeklickt oder Fenster geschlossen wird

FontSize = 8 # Fontgröße falls nicht woanders wie in Styles explizit angegeben
GRW = 720 # Width of the time grid 720 default, X-Richtung geht nach Rechts
GRH = 390 # Height of the time grid 390 default, Y-Richtung geht nach Unten
X0L = FontSize * 7 # Minimum X-Postion des Grids, (Position linke Seite)
Y0T = 25 # Minimum Y-Position des Grids, (Position Oberseite)
MouseX = MouseY = -10 # initiale Mausposition

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Oszilloskop UI-Widgets, Messeinstellungs- und Initialisierungswerte
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#---Sampling und Darstellung
# Mögliche Samplingraten (Hardwareeinstellungen am M1K)
# Samplingrate der AWGs ist immer identisch zur ADC-Samplingrate
SampRateList = (1024, 2048, 4096, 8192, 16384, 32765, 64000, 100000, 200000)
SampRate = 100000 # maximaler Wert kann noch verdoppelt werden falls Mux<=2

#SAMPLErate = SampRate # Scope sample rate
SampRatesb = None # Eingabe-Spinbox für die Samplingrate
MaxSamples = 90000 # Maximale Zahl Samples für Darstellung (# Hardwaresamples pro Loop)
Two_X_Sample = 0 # wird 1 bei 200 kS/s
NTrace = 4000 # Anzahl der Abtastpunkte (3x Anzeigebereich Grid)  
MarkerNum = 0 # Zähler für die Marker bei Maus-Rechsklick im Oszibild, wird bei UpdateTimeScreen() zurückgesetzt

#---Vertikaleinstellungen aus dem UI Boxes und Spinboxes
CHAsb = None # V Vertikalskalierung V/Div CH A Eingabefenster UI Spinbox ("sb")
CHBsb = None # V Vertikalskalierung V/Div CH B Eingabefenster UI Spinbox ("sb")
CHAIsb = None # I Vertikalskalierung A/Div CH A Eingabefenster UI Spinbox ("sb")
CHBIsb = None # I Vertikalskalierung A/Div CH B Eingabefenster UI Spinbox ("sb")
CHAVPosEntry = None # Eingabefenster Nulllinie V CH A in UI neben Skalierung
CHBVPosEntry = None
CHAIPosEntry = None
CHBIPosEntry = None 
CHAVScale = CHBVScale = 0.5 #Aktuelle Werte für Vertikalskalierung und -offset
CHAVOffset = CHBVOffset = 2.5
CHAIScale = CHBIScale =  50.0
CHAIOffset = CHBIOffset = 0.0

#---Horizontaleinstellungen aus dem UI Boxes und Spinboxes
HozPosentry = None # Eingabefeld horizontale Position mS
HozPos = 0.0 # aktueller Wert horizontale Position
TMsb = None # Spinbox mit Wert Horizontalskalierung
TIMEdiv = 0.5 # aktueller Wert Horizontalskalierung

#---Trigger, Cursor
TRIGGERentry = None # Eingabefeld Triggerlevel in V bzw. mA
TRIGGERlevel = 2.5 # Initialwert Triggerlevel in V
TgEdge = None # Auswahl Trigger auf steigende oder fallende Flanke
Is_Triggered = 0 # 1 = Trigger gefunden
TRIGGERsample = 0 # Index des Triggerzeitpunkts im Array mit gesampelten Werten
LShift = 0 # = -TRIGGERsample - für Verschiebung Signalverlauf in Darstellung
trgIpol = 0 # zw. Samples interpo. Wert (0...1) Triggerzeitpunkt damit kein horiz. Wackeln Darstellung Signal
TCursor = VCursor = 0 #

#---Kalibrierwerte Offset/Gain CHA und CHB aus Fenster rechts neben Oszibild
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

#--- Farben von Signalverläufen, Text und Buttons
ButtonGreen = "#00ff00"   # 100% green
ButtonRed = "#ff0000" # 100% red
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

#--- UI Arbiträrgenerator innerhalb Scopefenster
AWGAMenus = None
AWGASet = None
AWGBMenus = None
AWGBSet = None
AWGAMinEntry = None # Eingabefenster Min-Wert
AWGBMinEntry = None
AWGAMaxEntry = None # Eingabefenster Max-Wert
AWGBMaxEntry = None
AWGAFreqEntry = None  # Eingabefenster Frequenz
AWGBFreqEntry = None
AWGADutyCycleEntry = None #  # Eingabefenster Duty Cacle Wert für Rechtecksignal
AWGBDutyCycleEntry = None


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter Instanzierungen
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
RUNstatus = tk.IntVar(0) # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
SettingsStatus = tk.IntVar(0) # = 1 wenn Settings Menü aktiv

#--- Darstellung Oszilloskopbild
ShowC1_V = tk.IntVar(0) # Anzuzeigende Signalverläufe
ShowC1_V.set(0)
ShowC1_I = tk.IntVar(0)
ShowC1_I.set(0)
ShowC2_V = tk.IntVar(0)
ShowC2_V.set(0)
ShowC2_I = tk.IntVar(0)
ShowC2_I.set(0)
ShowMath = tk.IntVar(0)
ColorMode = tk.IntVar(0) # schwarzer (0) oder weißer (1) Hintergrund Oszibild
ColorMode.set(0)
GridWidth = tk.IntVar(0)
GridWidth.set(1) # Linienbreite Gitter
TRACEwidth = tk.IntVar(0)
TRACEwidth.set(1) # Linienbreite Signalverlaufsdarstellung
#MouseWidget = None # vermutlich Überbleibsel

#--- Trigger
Trigger_LPF_length  = tk.IntVar(0)
Trigger_LPF_length.set(10) # Anzahl gleitender Mittelung für Trigger Tiefpassfilter
TgInput = tk.IntVar(0)   # Trigger Input-Signal
SingleShot = tk.IntVar(0) # Single shot triger
#ManualTrigger = tk.IntVar(0) # Manual trigger
TgEdge = tk.IntVar(0)   # Triggerflanke steigend oder fallend

#--- Abtastung, Acquire, Cursor
ADC_Mux_Mode = tk.IntVar(0) # Wert 0...5 je nachdem welche Zweier-Signalkombination gesampelt wird
ADC_Mux_Mode.set(0) # bis 2-fach Mux 200 kS/s falls im Samplerate-Menü ausgewählt
TRACEaverage = tk.IntVar(0)
TRACEaverage.set(8) # Anzahl Mittelungen Sampingperioden im Average-Modus
TRACEmodeTime = tk.IntVar(0) # Flag für Average-Modus
TRACEmodeTime.set(0)
SmoothCurves = tk.IntVar(0) # Glättung Darstellung (Spline zwischen Samplingpunkten)
ZOHold = tk.IntVar(0) # Impulsinterpolierte Darstellung (wagerechte Linien zwischen Samplingpunkten), ansonsten linearinterpoliert
LPFTrigger = tk.IntVar(0) # Trigger Tiefpassfilter on/off
ShowCur = tk.IntVar(0) # Auswahl welcher Signalverlauf für Cursor

#--- Mess- und Mathefunktionen
MathTrace = tk.IntVar(0) # Im Menü ausgewählte Messfunktionen, 1 = CHA, 2 = CHB
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

#--- Arbiträrgenerator Modi (generell max 100 kS/s Aktualisierungsrate)
AWGAMode = tk.IntVar(0) # AWG A Modus SMVI (0), SIMV (1) oder Hi-Z (2)
AWGAMode.set(2)
AWGBMode = tk.IntVar(0) # AWG B Modus SMVI (0), SIMV (1) oder Hi-Z (2)
AWGBMode.set(2)
AWGAShape = tk.IntVar(0) # Signalform AWGA
AWGAShape.set(0) # Initialwert 0 = DC
AWGBShape = tk.IntVar(0) # Signalform AWGB
AWGBShape.set(0) # Initialwert 0 = DC

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Buffer-Variablen für eingelesene Messwerte
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
VBuffA = []
VBuffA = np.ones(MaxSamples)*2 # ungleich 0 damit Signalverläufe vor Run einzeln sichtbar
VBuffB = []
VBuffB = np.ones(MaxSamples)*3 # zum Testen
IBuffA = []
IBuffA = np.ones(MaxSamples)*150 # zum Testen
IBuffB = []
IBuffB = np.ones(MaxSamples)*(-150) # zum Testen