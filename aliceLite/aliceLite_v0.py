#!/usr/bin/python3
# -*- coding: utf-8 -*-
# With external module pysmu ( libsmu >= 1.0.2 for ADALM1000 )
# Uses new firmware (2.17 or >) that support control of ADC mux configure
# Created by D Mercer ()
#
# *****************************************************************************
# Light Version alice-desctop 1.38, S. Mack, 29.8.2020
# *****************************************************************************

import math
import time
import numpy as np
import sys
import tkinter as tk
import tkinter.font as tkf
import tkinter.messagebox as tkm
import tkinter.ttk as tkt
from tkinter.filedialog import asksaveasfilename
from tkinter.simpledialog import askstring
import pysmu as smu
import platform

from aliceIcons import hipulse, lowpulse, TBicon # Bilddateien der Icons
from aliceTimeFunc import MakeTimeTrace, MakeTimeScreen # Darstellung Traces
# AWG Funktionen
from aliceAwgFunc import ReMakeAWGwaves
from aliceAwgFunc import BAWGAAmpl, BAWGAOffset, BAWGAFreq, BAWGAPhaseDelay,
BAWGAPhase, BAWGADutyCycle, BAWGAShape, SplitAWGAwaveform, AWGANumCycles,
AWGAMakeFMSine, AWGAMakeAMSine, AWGAMakePWMSine, AWGAMakeTrapazoid, AWGAMakePulse,
AWGAMakeRamp, AWGAMakeUpDownRamp, AWGAMakeImpulse, AWGAMakeUUNoise, AWGAMakeUGNoise,
BAWGAModeLabel, UpdateAWGA
from aliceAwgFunc import BAWGBAmpl, BAWGBOffset, BAWGBFreq, BAWGBPhaseDelay,
BAWGBPhase, BAWGBDutyCycle, BAWGBShape, SplitAWGBwaveform, AWGBNumCycles,
AWGBMakeFMSine, AWGBMakeAMSine, AWGBMakePWMSine, AWGBMakeTrapazoid, AWGBMakePulse,
AWGBMakeRamp, AWGBMakeUpDownRamp, AWGBMakeImpulse, AWGBMakeUUNoise, AWGBMakeUGNoise,
BAWGBModeLabel, UpdateAWGB,SetBCompA
# Thinter UI Menüs
from aliceMenus import MakeAWGMenu, UpdateAWGMenu, DestroyAWGMenu, MakeSampleRateMenu,
DestroySampleRateMenu, MakeSettingsMenu, UpdateSettingsMenu, DestroySettingsMenu,
MakeMeasureMenu, UpdateMeasureMenu, MakeMathMenu, DestroyMathMenu, CreateToolTip
# Samplingfunktionen des M1K
from aliceM1kSamp import Analog_In, Analog_Time_In, Analog_Slow_time, shift_buffer,
Analog_Fast_time, SetSampleRate, SetADC_Mux, TraceSelectADC_Mux, BAWG2X
# Oszillsokopfunktionen
from aliceOsciFunc import BSetMarkerLocation, BShowCurvesAll, BShowCurvesNone,
BStop, BTime, BHozPoss, SetVAPoss, SetVBPoss, SetIAPoss, SetIBPoss, BCHAlevel,
BCHAIlevel, BCHBlevel, BCHBIlevel, BOffsetA, BIOffsetA, BOffsetB, BIOffsetB,
BStart, UpdateTimeAll, UpdateTimeTrace, UpdateTimeScreen, SetScaleA, SetScaleIA,
SetScaleB, SetScaleIB,
BTrigger50p, BTriglevel, BHoldOff, SetTriggerPoss, IncHoldOff, FindRisingEdge,
ReInterploateTrigger, FindTriggerSample

RevDate = "(30 Aug 2020)"
SWRev = "1.38lite"
DeBugMode = 0


# Vertical Sensitivity list in v/div "Channel Voltage Per Division"
CHvpdiv = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)
# Vertical Sensitivity list in mA/div und Defaultwert "Channel I(Current) Per Division"
CHipdiv = (0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)
# Time list in ms/div
TMpdiv = (0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)

#------------------------------------------------------------------------------
# Gobale Variable Beginn
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Initialisierungenwerte Programmstart 
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Window graph area Values that can be modified
FontSize = 8
GRW = 720                   # Width of the time grid 720 default
GRH = 390                   # Height of the time grid 390 default
X0L = FontSize * 7          # Left top X value of time grid
Y0T = 25                    # Left top Y value of time grid
MouseX = MouseY = -10
MouseCAV = MouseCAI = MouseCBV = MouseCBI = -10
contloop = 0 # kontinuierliches Sampling
discontloop = 0 # diskontinuierliches Sampling
MarkerLoc = 'UL' # can be UL, UR, LL or LR

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
MinSamples = 2000
MaxSamples = 200000
DISsamples = GRW # Number of samples to display? "grid width"
TRACEresetTime = True # True for first new trace, False for averageing
#---Vertikal- und Horizontaleinstellungen
CHAOffset = CHBOffset = 2.5
CHAIOffset = CHBIOffset = 0
InOffA = InGainA = InOffB = InGainB = 0.0 # Vermutlich Inputwerte des UI
HozPoss = 0.0 # horizontaler Offset Oszidarstellung
LShift = 0 # hat was mit Trigger zu tun
# Vertical Sensitivity Defaultwert
CH1vpdvRange = CH2vpdvRange = CHvpdiv[-1] # Vermutlich Defaultwert falls Error durch Eingabemaske
TIMEdiv = 0.5 # Default Zeitablenkung?
#---Trigger, Cursor
HoldOff = 0.0
TRIGGERlevel = 2.5 # set initial trigger level in V
Is_Triggered = 0
TRIGGERsample = 0           # AD sample trigger point
DX = 0                      # interpolated trigger point Wert 0...1
hldn = 0
TCursor = VCursor = 0
#---Sonstiges
PowerStatus = 1 # 0 stopped, 1 start, 2 running, 3 stop and restart, 4 stop

#---Mathefunktionen:
MathAxis = "V-A"

#---Messfunktionen Berechnungsformeln:
ChaMeasString1 = "DCV1"
ChaMeasString2 = "DCI1"
ChaMeasString3 = "SV1"
ChaMeasString4 = "MaxV1-MinV1"
ChaMeasString5 = "MaxI1-MinI1"
ChaMeasString6 = "math.sqrt(SV1**2 - DCV1**2)"
ChbMeasString1 = "DCV2"
ChbMeasString2 = "DCI2"
ChbMeasString3 = "SV2"
ChbMeasString4 = "MaxV2-MinV2"
ChbMeasString5 = "MaxI2-MinI2"
ChbMeasString6 = "math.sqrt(SV2**2 - DCV2**2)"
#---Messfunktionen Anzeigetext im Menü:
ChaLableSrring1 = "CHA-DCV "
ChaLableSrring2 = "CHA-DCI "
ChaLableSrring3 = "CHA-TRMS "
ChaLableSrring4 = "CHA-VP-P "
ChaLableSrring5 = "CHA-IP-P "
ChaLableSrring6 = "CHA-ACRMS "
ChbLableSrring1 = "CHB-DCV "
ChbLableSrring2 = "CHB-DCI "
ChbLableSrring3 = "CHB-TRMS "
ChbLableSrring4 = "CHB-VP-P "
ChbLableSrring5 = "CHB-IP-P "
ChbLableSrring6 = "CHB-ACRMS "
#---Initialisierung der Messwertvariablen
DCV1 = DCV2 = MinV1 = MaxV1 = MinV2 = MaxV2 = MidV1 = PPV1 = MidV2 = PPV2 = SV1 = SI1 = 0
PeakVA = PeakVB = PeakIA = PeakIB = 0.0
CHADCy = CHBDCy = 0
DCI1 = DCI2 = MinI1 = MaxI1 = MinI2 = MaxI2 = MidI1 = PPI1 = MidI2 = PPI2 = SV2 = SI2 = 0
CHAperiod = CHAfreq = CHBperiod = CHBfreq = 0

MeasGateLeft = 0.0
MeasGateRight = 0.0 # in mSec
MeasGateNum = 0
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Arbiträrgenerator Messeinstellungs- und Initialisierungswerte
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
AWGAAmplvalue = 0.0
AWGAOffsetvalue = 0.0
AWGAFreqvalue = 0.0
AWGAPhasevalue = 0
AWGAdelayvalue = 0
AWGADutyCyclevalue = 50
AWGAWave = 'dc'
AWGBAmplvalue = 0.0
AWGBOffsetvalue = 0.0
AWGBFreqvalue = 0.0
AWGBPhasevalue = 0
AWGBdelayvalue = 0
AWGBDutyCyclevalue = 50
AWGBWave = 'dc'

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter UI Initialisierswerte, globale Variable
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
CANVASwidth = GRW + 2 * X0L # canvas width
CANVASheight = GRH + Y0T + (FontSize * 7) # canvas height (lokale Variable)
# Colors that can be modified (lokale Variablen)
COLORframes = "#000080"   # Color = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
COLORcanvas = "#000000"   # 100% black
ButtonGreen = "#00ff00"   # 100% green
ButtonRed = "#ff0000" # 100% red
# Colors that can be modified (globale Variablen)
COLORgrid = "#808080"     # 50% Gray
COLORzeroline = "#0000ff" # 100% blue
COLORtrace1 = "#00ff00"   # 100% green
COLORtrace2 = "#ff8000"   # 100% orange
COLORtrace3 = "#00ffff"   # 100% cyan
COLORtrace4 = "#ffff00"   # 100% yellow
COLORtrace5 = "#ff00ff"   # 100% magenta
COLORtrace6 = "#C80000"   # 90% red
COLORtrace7 = "#8080ff"   # 100% purple
COLORtext = "#ffffff"     # 100% white
COLORtrigger = "#ff0000"  # 100% red



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter Instanzierungen
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#--- Oszilloskopbild
GridWidth = tk.IntVar(0)
GridWidth.set(1)
TRACEwidth = tk.IntVar(0)
TRACEwidth.set(1)
#--- Ozsilloskop Trigger, Aquire, Abtastung
TRACEaverage = tk.IntVar(0) # Number of average sweeps for average mode
TRACEaverage.set(8)
LPFTrigger = tk.IntVar(0) # trigger lpf on/off
Trigger_LPF_length  = tk.IntVar(0)
Trigger_LPF_length.set(10) # Length of Trigger box car LPF in samples
Two_X_Sample = tk.IntVar(0) # selection variable to set ADC channes for 2X samplerate mode
Two_X_Sample.set(0)
# Arbiträrgenerator
AWG_Amp_Mode = tk.IntVar(0)
AWG_Amp_Mode.set(0) # 0 = Min/Max mode, 1 = Amp/Offset
AWGA_Ext_Gain = tk.DoubleVar(0)
AWGA_Ext_Gain.set(1.0)
AWGA_Ext_Offset = tk.DoubleVar(0)
AWGA_Ext_Offset.set(0.0)
AWGB_Ext_Gain = tk.DoubleVar(0)
AWGB_Ext_Gain.set(1.0)
AWGB_Ext_Offset = tk.DoubleVar(0)
AWGB_Ext_Offset.set(0.0)
AWG_2X = tk.IntVar(0) # selection variable to set AWG DAC channes for 2X samplerate modes
# ADC-Mux-Modus
ADC_Mux_Mode = tk.IntVar(0) # selection variable to set ADC CHA for voltagr or current 2X samplerate mode
ADC_Mux_Mode.set(0)
Last_ADC_Mux_Mode = 0
v1_adc_conf = 0x20F1 # ADC Mux defaults
i1_adc_conf = 0x20F7
v2_adc_conf = 0x20F7
i2_adc_conf = 0x20F1

MathScreenStatus = tk.IntVar(0)
ScreenTrefresh = tk.IntVar(0) # Persistenz Display
SampleRateStatus = tk.IntVar(0)
AWGScreenStatus = tk.IntVar(0)
ShowTCur = tk.IntVar(0)
ShowVCur = tk.IntVar(0)

RUNstatus = tk.IntVar(0) # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
MeasGateStatus = tk.IntVar(0) # Was bedeutet das?
MeasGateStatus.set(0)

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
# define vertical measurment variables
MeasDCV1 = tk.IntVar(0)
MeasMinV1 = tk.IntVar(0)
MeasMaxV1 = tk.IntVar(0)
MeasMidV1 = tk.IntVar(0)
MeasPPV1 = tk.IntVar(0)
MeasRMSV1 = tk.IntVar(0)
MeasRMSVA_B = tk.IntVar(0)
MeasDCI1 = tk.IntVar(0)
MeasMinI1 = tk.IntVar(0)
MeasMaxI1 = tk.IntVar(0)
MeasMidI1 = tk.IntVar(0)
MeasPPI1 = tk.IntVar(0)
MeasRMSI1 = tk.IntVar(0)
MeasDiffAB = tk.IntVar(0)
MeasDCV2 = tk.IntVar(0)
MeasMinV2 = tk.IntVar(0)
MeasMaxV2 = tk.IntVar(0)
MeasMidV2 = tk.IntVar(0)
MeasPPV2 = tk.IntVar(0)
MeasRMSV2 = tk.IntVar(0)
MeasDCI2 = tk.IntVar(0)
MeasMinI2 = tk.IntVar(0)
MeasMaxI2 = tk.IntVar(0)
MeasMidI2 = tk.IntVar(0)
MeasPPI2 = tk.IntVar(0)
MeasRMSI2 = tk.IntVar(0)
MeasDiffBA = tk.IntVar(0)
MeasUserA = tk.IntVar(0)
MeasAHW = tk.IntVar(0)
MeasALW = tk.IntVar(0)
MeasADCy = tk.IntVar(0)
MeasAPER = tk.IntVar(0)
MeasAFREQ = tk.IntVar(0)
MeasBHW = tk.IntVar(0)
MeasBLW = tk.IntVar(0)
MeasBDCy = tk.IntVar(0)
MeasBPER = tk.IntVar(0)
MeasBFREQ = tk.IntVar(0)
MeasPhase = tk.IntVar(0)
MeasTopV1 = tk.IntVar(0)
MeasBaseV1 = tk.IntVar(0)
MeasTopV2 = tk.IntVar(0)
MeasBaseV2 = tk.IntVar(0)
MeasUserB = tk.IntVar(0)
MeasDelay = tk.IntVar(0)
TimeDisp = tk.IntVar(0)
TimeDisp.set(1)
CommandStatus = tk.IntVar(0)
CommandStatus.set(0)
MeasureStatus = tk.IntVar(0)
MeasureStatus.set(0)
MarkerScale = tk.IntVar(0)
MarkerScale.set(1)
SettingsStatus = tk.IntVar(0)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Buffer-Variablen für eingelesene Messwerte
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++       
ADsignal1 = []              # Ain signal array channel A and B
VBuffA = []
VBuffB = []
IBuffA = []
IBuffB = []
AWGAwaveform = []
AWGA2X = [] # array for odd numbers samples when in 2x sample rate
AWGBwaveform = []
AWGB2X = [] # array for odd numbers samples when in 2x sample rate
VmemoryA = np.ones(1)       # The memory for averaging
VmemoryB = np.ones(1)
ImemoryA = np.ones(1)       # The memory for averaging
ImemoryB = np.ones(1)
## Trace line Array Variables used
T1Vline = []                # Voltage Trace line channel A
T2Vline = []                # Voltage Trace line channel B
T1Iline = []                # Current Trace line channel A
T2Iline = []                # Current Trace line channel B
Tmathline = []              # Math trace line
Triggerline = []            # Triggerline
Triggersymbol = []          # Trigger symbol
#------------------------------------------------------------------------------
# Gobale Variable Ende
#------------------------------------------------------------------------------


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter UI Initialisierungen und Styles
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
root=tk.Tk()
if (root.tk.call('tk', 'windowingsystem')=='aqua'):
    Style_String = 'aqua'
else:
    Style_String = 'alt'
default_font = tkf.nametofont("TkDefaultFont")
default_font.configure(size=FontSize)

root.title("ALICE DeskTop Lite " + SWRev + RevDate + ": ALM1000 Oscilloscope")
img = tk.PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, '-default', img)
print("Windowing System is " + str(root.tk.call('tk', 'windowingsystem')))
root.style = tkt.Style()

try:
    root.style.theme_use(Style_String)
except:
    root.style.theme_use('default')
    
hipulseimg = tk.PhotoImage(data=hipulse)
lowpulseimg = tk.PhotoImage(data=lowpulse)

SHOWsamples = 4000          # Number of samples on the screen   
SCstart = 0                 # Start sample of the trace

#--- Eigene Styles für Buttons usw.
root.style.configure("W3.TButton", width=3, relief=tk.RAISED)
root.style.configure("W4.TButton", width=4, relief=tk.RAISED)
root.style.configure("W5.TButton", width=5, relief=tk.RAISED)
root.style.configure("W6.TButton", width=6, relief=tk.RAISED)
root.style.configure("W7.TButton", width=7, relief=tk.RAISED)
root.style.configure("W8.TButton", width=8, relief=tk.RAISED)
root.style.configure("W16.TButton", width=16, relief=tk.RAISED)
root.style.configure("Stop.TButton", background=ButtonRed, width=4, relief=tk.RAISED)
root.style.configure("Run.TButton", background=ButtonGreen, width=4, relief=tk.RAISED)
root.style.configure("Pwr.TButton", background=ButtonGreen, width=7, relief=tk.RAISED)
root.style.configure("PwrOff.TButton", background=ButtonRed, width=7, relief=tk.RAISED)
root.style.configure("RConn.TButton", background=ButtonRed, width=5, relief=tk.RAISED)
root.style.configure("GConn.TButton", background=ButtonGreen, width=5, relief=tk.RAISED)
root.style.configure("Rtrace1.TButton", background=COLORtrace1, width=7, relief=tk.RAISED)
root.style.configure("Strace1.TButton", background=COLORtrace1, width=7, relief=tk.SUNKEN)
root.style.configure("Rtrace2.TButton", background=COLORtrace2, width=7, relief=tk.RAISED)
root.style.configure("Strace2.TButton", background=COLORtrace2, width=7, relief=tk.SUNKEN)
root.style.configure("Rtrace3.TButton", background=COLORtrace3, width=7, relief=tk.RAISED)
root.style.configure("Strace3.TButton", background=COLORtrace3, width=7, relief=tk.SUNKEN)
root.style.configure("Rtrace4.TButton", background=COLORtrace4, width=7, relief=tk.RAISED)
root.style.configure("Strace4.TButton", background=COLORtrace4, width=7, relief=tk.SUNKEN)
root.style.configure("A10R1.TLabelframe.Label", foreground=COLORtraceR1, font=('Arial', 10, 'bold'))
root.style.configure("A10R1.TLabelframe", borderwidth=5, relief=tk.RIDGE)
root.style.configure("A10R2.TLabelframe.Label", foreground=COLORtraceR2, font=('Arial', 10, 'bold'))
root.style.configure("A10R2.TLabelframe", borderwidth=5, relief=tk.RIDGE)
root.style.configure("A10B.TLabel", foreground=COLORcanvas, font="Arial 10 bold") # Black text
root.style.configure("A10R.TLabel", foreground=ButtonRed, font="Arial 10 bold") # Red text
root.style.configure("A12B.TLabel", foreground=COLORcanvas, font="Arial 12 bold") # Black text
root.style.configure("Strace1.TCheckbutton", background=COLORtrace1)
root.style.configure("Strace2.TCheckbutton", background=COLORtrace2)
root.style.configure("Strace3.TCheckbutton", background=COLORtrace3)
root.style.configure("Strace4.TCheckbutton", background=COLORtrace4)
root.style.configure("WPhase.TRadiobutton", width=5, background="white", indicatorcolor=("red", "green"))
root.style.configure("GPhase.TRadiobutton", width=5, background="gray", indicatorcolor=("red", "green"))

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# M1K Spezifisches
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
DevID = "No Device" # Initialisierung

def ConSingDev():
    global devx, session, CHA, CHB, DevID, MaxSamples, bcon, SAMPLErate
    global PIO_0, PIO_1, PIO_2, PIO_3, PIO_4, PIO_5, PIO_6, PIO_7
    if DevID == "No Device":
        #print("Request sample rate: " + str(SAMPLErate))
        session = smu.Session(ignore_dataflow=True, sample_rate=SAMPLErate, queue_size=MaxSamples)
        # session.add_all()
        # SAMPLErate = 200000 #AWGSAMPLErate # Scope sample rate
        if not session.devices:
            print( 'No Device plugged IN!')
            DevID = "No Device"
            FWRevOne = 0.0
            bcon.configure(text="Recon", style="RConn.TButton")
            return
        session.configure(sample_rate=SAMPLErate)
        print("Session sample rate: " + str(session.sample_rate))      
        devx = session.devices[0] 
        DevID = devx.serial
        print("Device ID:" + str(DevID))
        FWRevOne = float(devx.fwver)
        HWRevOne = str(devx.hwver)
        print( FWRevOne, HWRevOne)
        # print("Session sample rate: " + str(session.sample_rate))    
        if FWRevOne < 2.17:
            tk.showwarning("WARNING","This ALICE version Requires Firmware version > 2.16")
        CHA = devx.channels['A']    # Open CHA
        CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        CHB = devx.channels['B']    # Open CHB
        CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode  
        # Hier unterscheiden sich die beiden Hardware-Revisions
        devx.set_adc_mux(0)
        if devx.hwver == "F":
            print( "Rev F Board I/O ports set")
            PIO_0 = 28
            PIO_1 = 29
            PIO_2 = 47
            PIO_3 = 3
            PIO_4 = 4
            PIO_5 = 5
            PIO_6 = 6
            PIO_7 = 7
        else:
            print( "Rev D Board I/O ports set")
            PIO_0 = 0
            PIO_1 = 1
            PIO_2 = 2
            PIO_3 = 3
            PIO_4 = 4
            PIO_5 = 5
            PIO_6 = 6
            PIO_7 = 7           
        devx.set_adc_mux(0)
        devx.ctrl_transfer(0x40, 0x24, 0x0, 0, 0, 0, 100) # set to addr DAC A 
        devx.ctrl_transfer(0x40, 0x25, 0x1, 0, 0, 0, 100) # set not addr DAC B
        try:
            session.start(0)
            devx.set_led(0b010) # set LED.green
            bcon.configure(text="Conn", style="GConn.TButton")
        except:
            tk.showwarning("M1K could not be connected.")
        

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen UI
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
# Toggle the Background and text colors based on ColorMode
def BgColor():
    global COLORtext, COLORcanvas, ColorMode, COLORtrace4, COLORtraceR4, ca
    if ColorMode.get() > 0:
        COLORtext = "#000000"   # 100% black
        COLORtrace4 = "#a0a000" # 50% yellow
        COLORtraceR4 = "#606000"   # 25% yellow
        COLORcanvas = "#ffffff"     # 100% white
    else:
        COLORcanvas = "#000000"   # 100% black
        COLORtrace4 = "#ffff00" # 100% yellow
        COLORtraceR4 = "#808000"   # 50% yellow
        COLORtext = "#ffffff"     # 100% white
    ca.config(background=COLORcanvas)
    UpdateTimeScreen()

# Save scope canvas as encapsulated postscript file
# To do: in PNG ändern
def BSaveScreen():
    global CANVASwidth, CANVASheight
    global COLORtext, MarkerNum, ColorMode
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")])
    Orient = tkm.askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n")
    if MarkerNum > 0 or ColorMode.get() > 0:
        ca.postscript(file=filename, height=CANVASheight, width=CANVASwidth, colormode='color', rotate=Orient)
    else:    # temp chnage text corlor to black
        COLORtext = "#000000"
        UpdateTimeScreen()
        # first save postscript file
        ca.postscript(file=filename, height=CANVASheight, width=CANVASwidth, colormode='color', rotate=Orient)
        # now convert to bit map
        #img = Image.open("screen_shot.eps")
        #img.save("screen_shot.gif", "gif")
        COLORtext = "#ffffff"
        UpdateTimeScreen()

## Save scope all time array data to file
def BSaveData():
    global VBuffA, VBuffB, IBuffA, IBuffB, SAMPLErate
    # open file to save data
    filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
    DataFile = open(filename, 'w')
    DataFile.write( 'Sample-#, CA-V, CA-I, CB-V, CB-I \n' )
    for index in range(len(VBuffA)):
        TimePnt = float((index+0.0)/SAMPLErate)
        DataFile.write( str(TimePnt) + ', ' + str(VBuffA[index]) + ', ' + str(IBuffA[index]) + ', '
                        + str(VBuffB[index]) + ', ' + str(IBuffB[index]) + '\n')
    DataFile.close()
 

        
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Tkinter Callback-Funktionen
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def onCanvasClickRight(event):
    global ShowTCur, ShowVCur, TCursor, VCursor, RUNstatus, ca

    TCursor = event.x
    VCursor = event.y
    if RUNstatus.get() == 0:
        UpdateTimeScreen()
    ca.bind_all('<MouseWheel>', onCanvasClickScroll)

## Shift Time or vertical cursors if on or shift gated measurement cursors if enabled
def onCanvasClickScroll(event):
    global ShowTCur, ShowVCur, TCursor, VCursor, RUNstatus, ca, MWcount
    global MeasGateStatus, MeasGateLeft, MeasGateRight, TIMEdiv, GRW

    ShiftKeyDwn = event.state & 1
    if event.widget == ca:
        if ShowTCur.get() > 0 or ShowVCur.get() > 0: # move cursors if shown
            if ShowTCur.get() > 0 and ShiftKeyDwn == 0:
            # respond to Linux or Windows wheel event
                if event.num == 5 or event.delta == -120:
                    TCursor -= 1
                if event.num == 4 or event.delta == 120:
                    TCursor += 1
            elif ShowVCur.get() > 0 or ShiftKeyDwn == 1:
            # respond to Linux or Windows wheel event
                if event.num == 5 or event.delta == -120:
                    VCursor += 1
                if event.num == 4 or event.delta == 120:
                    VCursor -= 1
        else:
            if MeasGateStatus.get() == 1:
                Tstep = (TIMEdiv / GRW) / 10 # time in mS per pixel
                if ShiftKeyDwn == 0:
                    if event.num == 5 or event.delta == -120:
                        MeasGateLeft = MeasGateLeft + (-100 * Tstep)
                    if event.num == 4 or event.delta == 120:
                        MeasGateLeft = MeasGateLeft + (100 * Tstep)
                    # MeasGateLeft = MeasGateLeft + (event.delta * Tstep) #+ HoldOff
                if ShiftKeyDwn == 1:
                    if event.num == 5 or event.delta == -120:
                        MeasGateRight = MeasGateRight + (-100 * Tstep)
                    if event.num == 4 or event.delta == 120:
                        MeasGateRight = MeasGateRight + (100 * Tstep)
                    #MeasGateRight = MeasGateRight + (event.delta * Tstep) #+ HoldOff
            try:
                onSpinBoxScroll(event) # if cursor are not showing scroll the Horx time base
            except:
                pass
        if RUNstatus.get() == 0:
            UpdateTimeScreen()

## Move Vertical cursors up 1 or 5
def onCanvasUpArrow(event):
    global ShowVCur, VCursor, YCursor, dBCursor, BdBCursor, RUNstatus, ca

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowVCur.get() > 0 and shift_key == 0:
            VCursor = VCursor - 1
        elif ShowVCur.get() > 0 and shift_key == 1:
            VCursor = VCursor - 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()

## Move Vertical cursors down 1 or 5
def onCanvasDownArrow(event):
    global ShowVCur, VCursor, RUNstatus, ca

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowVCur.get() > 0 and shift_key == 0:
            VCursor = VCursor + 1
        elif ShowVCur.get() > 0 and shift_key == 1:
            VCursor = VCursor + 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
   
## Move Time curcors left 1 or 5
def onCanvasLeftArrow(event):
    global ShowTCur, TCursor, RUNstatus, ca

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowTCur.get() > 0 and shift_key == 0:
            TCursor = TCursor - 1
        elif ShowTCur.get() > 0 and shift_key == 1:
            TCursor = TCursor - 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()

## Move Time curcors right 1 or 5
def onCanvasRightArrow(event):
    global ShowTCur, TCursor, RUNstatus, ca

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowTCur.get() > 0 and shift_key == 0:
            TCursor = TCursor + 1
        elif ShowTCur.get() > 0 and shift_key == 1:
            TCursor = TCursor + 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()

def onCanvasClickLeft(event):
    global X0L          # Left top X value
    global Y0T          # Left top Y value
    global GRW          # Screenwidth
    global GRH          # Screenheight
    global FontSize
    global ca, MarkerLoc, Mulx
    global HoldOffentry,  COLORgrid, COLORtext
    global TMsb, CHAsb, CHBsb, CHAIsb, CHBIsb, MarkerScale
    global CHAVPosEntry, CHAIPosEntry, CHBVPosEntry, CHBIPosEntry
    global SAMPLErate, RUNstatus, MarkerNum, PrevV, PrevT
    global COLORtrace1, COLORtrace2
    global CH1pdvRange, CH2pdvRange, CH1IpdvRange, CH2IpdvRange
    global CHAOffset, CHAIOffset, CHBOffset, CHBIOffset
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
    global MeasGateLeft, MeasGateRight, MeasGateStatus, MeasGateNum, TMsb, SAMPLErate  
    try:
        HoldOff = float(eval(HoldOffentry.get()))
        if HoldOff < 0:
            HoldOff = 0
    except:
        HoldOffentry.delete(0,tk.END)
        HoldOffentry.insert(0, HoldOff)
    # get time scale
    try:
        TIMEdiv = float(eval(TMsb.get()))
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"tk.END")
        TMsb.insert(0,TIMEdiv)
    # prevent divide by zero error
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.01
    # add markers only if stopped
    if (RUNstatus.get() == 0):
        MarkerNum = MarkerNum + 1
        # get the vertical ranges
        try:
            CH1pdvRange = float(eval(CHAsb.get()))
        except:
            CHAsb.delete(0,tk.END)
            CHAsb.insert(0, CH1vpdvRange)
        try:
            CH2pdvRange = float(eval(CHBsb.get()))
        except:
            CHBsb.delete(0,tk.END)
            CHBsb.insert(0, CH2vpdvRange)
        try:
            CH1IpdvRange = float(eval(CHAIsb.get()))
        except:
            CHAIsb.delete(0,tk.END)
            CHAIsb.insert(0, CH1IpdvRange)
        try:
            CH2IpdvRange = float(eval(CHBIsb.get()))
        except:
            CHBIsb.delete(0,tk.END)
            CHBIsb.insert(0, CH2IpdvRange)
        # get the vertical offsets
        try:
            CHAOffset = float(eval(CHAVPosEntry.get()))
        except:
            CHAVPosEntry.delete(0,tk.END)
            CHAVPosEntry.insert(0, CHAOffset)
        try:
            CHAIOffset = float(eval(CHAIPosEntry.get()))
        except:
            CHAIPosEntry.delete(0,tk.END)
            CHAIPosEntry.insert(0, CHAIOffset)
        try:
            CHBOffset = float(eval(CHBVPosEntry.get()))
        except:
            CHBVPosEntry.delete(0,tk.END)
            CHBVPosEntry.insert(0, CHBOffset)
        try:
            CHBIOffset = float(eval(CHBIPosEntry.get()))
        except:
            CHBIPosEntry.delete(0,tk.END)
            CHBIPosEntry.insert(0, CHBIOffset)
        # prevent divide by zero error
        if CH1pdvRange < 0.001:
            CH1pdvRange = 0.001
        if CH2pdvRange < 0.001:
            CH2pdvRange = 0.001
        if CH1IpdvRange < 1.0:
            CH1IpdvRange = 1.0
        if CH2IpdvRange < 1.0:
            CH2IpdvRange = 1.0
        Yoffset1 = CHAOffset
        if MarkerScale.get() == 1:
            Yconv1 = float(GRH/10.0) / CH1pdvRange
            Yoffset1 = CHAOffset
            COLORmarker = COLORtrace1
            Units = " V"
        elif MarkerScale.get() == 2:
            Yconv1 = float(GRH/10.0) / CH2pdvRange
            Yoffset1 = CHBOffset
            COLORmarker = COLORtrace2
            Units = " V"
        elif MarkerScale.get() == 3:
            Yconv1 = float(GRH/10.0) / CH1IpdvRange
            Yoffset1 = CHAIOffset
            COLORmarker = COLORtrace3
            Units = " mA"
        elif MarkerScale.get() == 4:
            Yconv1 = float(GRH/10.0) / CH2IpdvRange
            Yoffset1 = CHBIOffset
            COLORmarker = COLORtrace4
            Units = " mA"
            
        c1 = GRH / 2.0 + Y0T    # fixed correction channel A
        # draw X at marker point and number
        ca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=COLORtext)
        ca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=COLORtext)
        Tstep = (10.0 * TIMEdiv) / GRW # time in mS per pixel
        Tpoint = ((event.x-X0L) * Tstep) + HoldOff

        Tpoint = Tpoint/Mulx
        if Tpoint >= 1000:
            axis_value = Tpoint / 1000.0
            TString = ' {0:.2f} '.format(axis_value) + " S "
        if Tpoint < 1000 and Tpoint >= 1:
            axis_value = Tpoint
            TString = ' {0:.2f} '.format(axis_value) + " mS "
        if Tpoint < 1:
            axis_value = Tpoint * 1000.0
            TString = ' {0:.2f} '.format(axis_value) + " uS "
        # TString = ' {0:.2f} '.format(Tpoint)
        yvolts = ((event.y-c1)/Yconv1) - Yoffset1
        if MarkerScale.get() == 1 or MarkerScale.get() == 2:
            V1String = ' {0:.3f} '.format(-yvolts)
        else:
            V1String = ' {0:.1f} '.format(-yvolts)
        V_label = str(MarkerNum) + " " + TString + V1String
        V_label = V_label + Units
        if MarkerNum > 1:
            if MarkerScale.get() == 1 or MarkerScale.get() == 2:
                DeltaV = ' {0:.3f} '.format(PrevV-yvolts)
            else:
                DeltaV = ' {0:.1f} '.format(PrevV-yvolts)
            DT = (Tpoint-PrevT)
            if Tpoint >= 1000:
                axis_value = DT / 1000.0
                DeltaT = ' {0:.2f} '.format(axis_value) + " S "
            if Tpoint < 1000 and Tpoint >= 1:
                axis_value = DT
                DeltaT = ' {0:.2f} '.format(axis_value) + " mS "
            if Tpoint < 1:
                axis_value = DT * 1000.0
                DeltaT = ' {0:.2f} '.format(axis_value) + " uS "
            # DeltaT = ' {0:.3f} '.format(Tpoint-PrevT)
            DFreq = ' {0:.3f} '.format(1.0/(Tpoint-PrevT))
            V_label = V_label + " Delta " + DeltaT + DeltaV
            V_label = V_label + Units
            V_label = V_label + ", Freq " + DFreq + " KHz"
        # place in upper left unless specified otherwise
        x = X0L + 5
        y = Y0T + 3 + (MarkerNum*10)
        Justify = 'w'
        if MarkerLoc == 'UR' or MarkerLoc == 'ur':
            x = X0L + GRW - 5
            y = Y0T + 3 + (MarkerNum*10)
            Justify = 'e'
        if MarkerLoc == 'LL' or MarkerLoc == 'll':
            x = X0L + 5
            y = Y0T + GRH + 3 - (MarkerNum*10)
            Justify = 'w'
        if MarkerLoc == 'LR' or MarkerLoc == 'lr':
            x = X0L + GRW - 5
            y = Y0T + GRH + 3 - (MarkerNum*10)
            Justify = 'e'
        ca.create_text(event.x+4, event.y, text=str(MarkerNum), fill=COLORtext, anchor=Justify, font=("arial", FontSize ))
        ca.create_text(x, y, text=V_label, fill=COLORmarker, anchor=Justify, font=("arial", FontSize ))
        PrevV = yvolts
        PrevT = Tpoint
    else:
        if MeasGateStatus.get() == 1:
            Tstep = (10.0 * TIMEdiv) / GRW # time in mS per pixel
            if MeasGateNum == 0:
                MeasGateLeft = ((event.x-X0L) * Tstep) #+ HoldOff
                MeasGateNum = 1
            else:
                MeasGateRight = ((event.x-X0L) * Tstep) #+ HoldOff
                MeasGateNum = 0
            LeftGate = X0L + MeasGateLeft / Tstep
            RightGate = X0L + MeasGateRight / Tstep
            ca.create_line(LeftGate, Y0T, LeftGate, Y0T+GRH, fill=COLORtext)
            ca.create_line(RightGate, Y0T, RightGate, Y0T+GRH, fill=COLORtext)

def onTextScroll(event):   # Use mouse wheel to scroll entry values, august 7
    button = event.widget
    cursor_position = button.index(tk.INSERT) # get current cursor position
    Pos = cursor_position
    OldVal = button.get() # get current entry string
    OldValfl = float(OldVal) # and its value
    Len = len(OldVal)
    Dot = OldVal.find (".")  # find decimal point position
    Decimals = Len - Dot - 1
    if Dot == -1 : # no point
        Decimals = 0             
        Step = 10**(Len - Pos)
    elif Pos <= Dot : # no point left of position
        Step = 10**(Dot - Pos)
    else:
        Step = 10**(Dot - Pos + 1)
    # respond to Linux or Windows wheel event
    if event.num == 5 or event.delta == -120:
        NewVal = OldValfl - Step
    if event.num == 4 or event.delta == 120:
        NewVal = OldValfl + Step
    FormatStr = "{0:." + str(Decimals) + "f}"
    NewStr = FormatStr.format(NewVal)
    NewDot = NewStr.find (".") 
    NewPos = Pos + NewDot - Dot
    if Decimals == 0 :
        NewLen = len(NewStr)
        NewPos = Pos + NewLen - Len
    button.delete(0, tk.END) # remove old entry
    button.insert(0, NewStr) # insert new entry
    button.icursor(NewPos) # resets the insertion cursor

def onAWGAkey(event):
    global AWGAShape  
    onTextKey(event)
    ReMakeAWGwaves()

def onAWGBkey(event):
    global AWGBShape    
    onTextKey(event)
    ReMakeAWGwaves()

def onTextKeyAWG(event):
    onTextKey(event)
    ReMakeAWGwaves()

# Use Arriw keys to inc dec entry values
def onTextKey(event):
    button = event.widget
    cursor_position = button.index(tk.INSERT) # get current cursor position
    Pos = cursor_position
    OldVal = button.get() # get current entry string
    OldValfl = float(OldVal) # and its value
    Len = len(OldVal)
    Dot = OldVal.find (".")  # find decimal point position
    Decimals = Len - Dot - 1
    if Dot == -1 : # no point
        Decimals = 0             
        Step = 10**(Len - Pos)
    elif Pos <= Dot : # no point left of position
        Step = 10**(Dot - Pos)
    else:
        Step = 10**(Dot - Pos + 1)
    if platform.system() == "Windows":
        if event.keycode == 38: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 40: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    elif platform.system() == "Linux":
        if event.keycode == 111: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 116: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return

    FormatStr = "{0:." + str(Decimals) + "f}"
    NewStr = FormatStr.format(NewVal)
    NewDot = NewStr.find (".") 
    NewPos = Pos + NewDot - Dot
    if Decimals == 0 :
        NewLen = len(NewStr)
        NewPos = Pos + NewLen - Len
    button.delete(0, tk.END) # remove old entry
    button.insert(0, NewStr) # insert new entry
    button.icursor(NewPos) # resets the insertion cursor

def onSpinBoxScroll(event):
    spbox = event.widget
    if sys.version_info[0] == 3: # Spin Boxes do this automatically in Python 3 apparently
        return
    if event.delta > 0: # increment digit
        spbox.invoke('buttonup')
    else: # decrement digit
        spbox.invoke('buttondown')

def onSettingsScroll(event):
    onTextScroll(event)
    UpdateSettingsMenu()

def onSettingsTextKey(event):
    onTextKey(event)
    UpdateSettingsMenu()

def onCanvasMouse_xy(event):
    global MouseX, MouseY, MouseWidget
    MouseWidget = event.widget
    MouseX, MouseY = event.x, event.y
    
def onSrateScroll(event):
    onSpinBoxScroll(event)
    SetSampleRate()

def onRetSrate(event):
    SetSampleRate()
    
def onCAresize(event):
    global ca, GRW, XOL, GRH, Y0T, CANVASwidth, CANVASheight, FontSize   
    XOL = FontSize * 7
    CANVASwidth = event.width - 4
    CANVASheight = event.height - 4
    GRW = CANVASwidth - (2 * X0L) # new grid width
    GRH = CANVASheight - (Y0T + (FontSize * 7))   # new grid height
    UpdateTimeAll()

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Utilities
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Load configuration from a file, im Config File stehen zeilenwese Befehle
# welche ausgeführt werden
def BLoadConfig(filename):
    # Read configuration values from file
    try:
        ConfgFile = open(filename)
        for line in ConfgFile:
            try:
                exec(line.rstrip())
            except:
                print( "Skipping " + line.rstrip())
        ConfgFile.close()
        UpdateAWGMenu()
        time.sleep(0.05)
        ReMakeAWGwaves()
        session.tk.END() # Add this to turn off outputs after first tiem loading a config? 
        BTime()
    except:
        print( "Config File Not Found.")
    UpdateTimeTrace()

# Function to close and exit ALICE
def Bcloseexit():
    global RUNstatus, session, CHA, CHB, devx, AWG_2X 
    RUNstatus.set(0)
    # BSaveConfig("alice-last-config.cfg")
    try:
        # Put channels in Hi-Z and exit
        CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
        devx.set_adc_mux(0) # set ADC mux conf to default
        AWG_2X.set(0)
        BAWG2X()
        CHA.constant(0.0)
        CHB.constant(0.0)
        devx.set_led(0b001) # Set LED.red on the way out
        if session.continuous:
            session.tk.END()
    except:
        pass
    root.destroy()
    exit()

def donothing():
    pass

#==============================================================================
#==============================================================================
#Eigentliches Hauptprogramm, das das Scopefenster aufbaut.
#==============================================================================
#==============================================================================
frame2r = tk.Frame(root, borderwidth=5, relief=tk.RIDGE)
frame2r.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.NO)
frame1 = tk.Frame(root, borderwidth=5, relief=tk.RIDGE)
frame1.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.NO)
frame2 = tk.Frame(root, borderwidth=5, relief=tk.RIDGE)
frame2.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
frame3 = tk.Frame(root, borderwidth=5, relief=tk.RIDGE)
frame3.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.NO)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Trigger Menü
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Triggermenu = tk.Menubutton(frame1, text="Trigger", style="W7.TButton")
Triggermenu.menu = tk.Menu(Triggermenu, tearoff = 0 )
Triggermenu["menu"]  = Triggermenu.menu
Triggermenu.menu.add_radiobutton(label='None', variable=TgInput, value=0)
Triggermenu.menu.add_radiobutton(label='CA-V', variable=TgInput, value=1)
Triggermenu.menu.add_radiobutton(label='CA-I', variable=TgInput, value=2)
Triggermenu.menu.add_radiobutton(label='CB-V', variable=TgInput, value=3)
Triggermenu.menu.add_radiobutton(label='CB-I', variable=TgInput, value=4)
Triggermenu.menu.add_checkbutton(label='Auto Level', variable=AutoLevel)
Triggermenu.menu.add_checkbutton(label='Low Pass Filter', variable=LPFTrigger)
Triggermenu.menu.add_checkbutton(label='Manual Trgger', variable=ManualTrigger)
Triggermenu.menu.add_checkbutton(label='SingleShot', variable=SingleShot)
Triggermenu.pack(side=tk.LEFT)

Edgemenu = tk.Menubutton(frame1, text="Edge", style="W5.TButton")
Edgemenu.menu = tk.Menu(Edgemenu, tearoff = 0 )
Edgemenu["menu"]  = Edgemenu.menu
Edgemenu.menu.add_radiobutton(label='Rising [+]', variable=TgEdge, value=0)
Edgemenu.menu.add_radiobutton(label='Falling [-]', variable=TgEdge, value=1)
Edgemenu.pack(side=tk.LEFT)

tlab = tk.Label(frame1, text="Trig Level")
tlab.pack(side=tk.LEFT)
TRIGGERentry = tk.Entry(frame1, width=5)
TRIGGERentry.bind('<MouseWheel>', onTextScroll)
TRIGGERentry.bind("<Button-4>", onTextScroll)# with Linux OS
TRIGGERentry.bind("<Button-5>", onTextScroll)
TRIGGERentry.bind("<Return>", BTriglevel)
TRIGGERentry.bind('<Key>', onTextKey)
TRIGGERentry.pack(side=tk.LEFT)
TRIGGERentry.delete(0,"tk.END")
TRIGGERentry.insert(0,0.0)

tgb = tk.Button(frame1, text="50%", style="W4.TButton", command=BTrigger50p)
tgb.pack(side=tk.LEFT)

hldlab = tk.Button(frame1, text="Hold Off", style="W8.TButton", command=IncHoldOff)
hldlab.pack(side=tk.LEFT)
HoldOffentry = tk.Entry(frame1, width=4)
HoldOffentry.bind('<MouseWheel>', onTextScroll)
HoldOffentry.bind("<Button-4>", onTextScroll)# with Linux OS
HoldOffentry.bind("<Button-5>", onTextScroll)
HoldOffentry.bind("<Return>", BHoldOff)
HoldOffentry.bind('<Key>', onTextKey)
HoldOffentry.pack(side=tk.LEFT)
HoldOffentry.delete(0,"tk.END")
HoldOffentry.insert(0,0.0)

hozlab = tk.Button(frame1, text="Horz Pos", style="W8.TButton", command=SetTriggerPoss)
hozlab.pack(side=tk.LEFT)
HozPossentry = tk.Entry(frame1, width=4)
HozPossentry.bind('<MouseWheel>', onTextScroll)
HozPossentry.bind("<Button-4>", onTextScroll)# with Linux OS
HozPossentry.bind("<Button-5>", onTextScroll)
HozPossentry.bind("<Return>", BHozPoss)
HozPossentry.bind('<Key>', onTextKey)
HozPossentry.pack(side=tk.LEFT)
HozPossentry.delete(0,"tk.END")
HozPossentry.insert(0,0.0)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Run, Stop, Exit Buttons
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
bexit = tk.Button(frame1, text="Exit", style="W4.TButton", command=Bcloseexit)
bexit.pack(side=tk.RIGHT)
bstop = tk.Button(frame1, text="Stop", style="Stop.TButton", command=BStop)
bstop.pack(side=tk.RIGHT)
brun = tk.Button(frame1, text="Run", style="Run.TButton", command=BStart)
brun.pack(side=tk.RIGHT)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Curves Menu , background="#A0A0A0"
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Showmenu = tk.Menubutton(frame1, text="Curves", style="W7.TButton")
Showmenu.menu = tk.Menu(Showmenu, tearoff = 0 )
Showmenu["menu"] = Showmenu.menu
Showmenu.menu.add_command(label="-Show-", foreground="blue", command=donothing)
Showmenu.menu.add_command(label="All", command=BShowCurvesAll)
Showmenu.menu.add_command(label="None", command=BShowCurvesNone)
Showmenu.menu.add_checkbutton(label='CA-V [1]', background=COLORtrace1, variable=ShowC1_V, command=TraceSelectADC_Mux)
Showmenu.menu.add_checkbutton(label='CA-I [3]', background=COLORtrace3, variable=ShowC1_I, command=TraceSelectADC_Mux)
Showmenu.menu.add_checkbutton(label='CB-V [2]', background=COLORtrace2, variable=ShowC2_V, command=TraceSelectADC_Mux)
Showmenu.menu.add_checkbutton(label='CB-I [4]', background=COLORtrace4,variable=ShowC2_I, command=TraceSelectADC_Mux)
Showmenu.menu.add_command(label="-Auto Vert Center-", foreground="blue", command=donothing)
Showmenu.menu.add_checkbutton(label='Center CA-V', variable=AutoCenterA)
Showmenu.menu.add_checkbutton(label='Center CB-V', variable=AutoCenterB)
Showmenu.menu.add_separator()  
Showmenu.menu.add_checkbutton(label='T Cursor [t]', variable=ShowTCur, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='V Cursor [v]', variable=ShowVCur, command=UpdateTimeTrace)
Showmenu.pack(side=tk.RIGHT)

Triggermenu_tip = CreateToolTip(Triggermenu, 'Select trigger signal')
Edgemenu_tip = CreateToolTip(Edgemenu, 'Select trigger edge')
tgb_tip = CreateToolTip(tgb, 'Set trigger level to waveform mid point')
hldlab_tip = CreateToolTip(hldlab, 'Increment Hold Off setting by one time division')
hozlab_tip = CreateToolTip(hozlab, 'When triggering, set trigger point to center of screen')
bexit_tip = CreateToolTip(bexit, 'Exit ALICE Desktop')
bstop_tip = CreateToolTip(bstop, 'Stop acquiring data')
brun_tip = CreateToolTip(brun, 'Start acquiring data')
pwrbt_tip = CreateToolTip(PwrBt, 'Toggle ext power supply')
Showmenu_tip = CreateToolTip(Showmenu, 'Select which traces to display')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Horizontal Menü: Time per Div
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
TMsb = tk.Spinbox(frame1, width=5, values= TMpdiv, command=BTime)
TMsb.bind('<MouseWheel>', onSpinBoxScroll)
TMsb.pack(side=tk.RIGHT)
TMsb.delete(0,"tk.END")
TMsb.insert(0,0.5)
TMlab = tk.Label(frame1, text="Time mS/Div")
TMlab.pack(side=tk.RIGHT)

# Canvas (gesamter Bildschirmbereich)
ca = tk.Canvas(frame2, width=CANVASwidth, height=CANVASheight, background=COLORcanvas, cursor='cross')
# add mouse left and right button click to canvas
ca.bind('<Configure>', onCAresize)
ca.bind('<1>', onCanvasClickLeft)
ca.bind('<3>', onCanvasClickRight)
ca.bind("<Motion>",onCanvasMouse_xy)
ca.bind("<Up>", onCanvasUpArrow)
ca.bind("<Down>", onCanvasDownArrow)
ca.bind("<Left>", onCanvasLeftArrow)
ca.bind("<Right>", onCanvasRightArrow)
ca.bind('<MouseWheel>', onCanvasClickScroll)
ca.bind("<Button-4>", onCanvasClickScroll)# with Linux OS
ca.bind("<Button-5>", onCanvasClickScroll)
ca.pack(side=tk.TOP, fill=tk.tk.BOTH, expand=tk.YES)
MouseWidget = ca

# right side menu buttons
dropmenu = tk.Frame( frame2r )
dropmenu.pack(side=tk.TOP)

# Connect Button (nötig?)
bcon = tk.Button(dropmenu, text="Recon", style="RConn.TButton", command=ConSingDev)
bcon.pack(side=tk.LEFT, anchor=tk.W)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# File menu
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Filemenu = tk.Menubutton(dropmenu, text="File", style="W4.TButton")
Filemenu.menu = tk.Menu(Filemenu, tearoff = 0 )
Filemenu["menu"] = Filemenu.menu
Filemenu.menu.add_command(label="Load Config", command=BLoadConfig)
Filemenu.menu.add_command(label="Save Screen", command=BSaveScreen)
Filemenu.menu.add_command(label="Save To CSV", command=BSaveData)
Filemenu.pack(side=tk.LEFT, anchor=tk.W)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Options Menu
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Optionmenu = tk.Menubutton(dropmenu, text="Options", style="W7.TButton")
Optionmenu.menu = tk.Menu(Optionmenu, tearoff = 0 )
Optionmenu["menu"]  = Optionmenu.menu
Optionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
Optionmenu.menu.add_command(label='Set Sample Rate', command=MakeSampleRateMenu) # SetSampleRate)
Optionmenu.menu.add_checkbutton(label='Smooth', variable=SmoothCurves, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Z-O-Hold', variable=ZOHold, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Trace Avg [a]', variable=TRACEmodeTime)
Optionmenu.menu.add_checkbutton(label='Persistance', variable=ScreenTrefresh)
Optionmenu.menu.add_command(label='Set Marker Location', command=BSetMarkerLocation)
Optionmenu.menu.add_radiobutton(label='Black BG', variable=ColorMode, value=0, command=BgColor)
Optionmenu.menu.add_radiobutton(label='White BG', variable=ColorMode, value=1, command=BgColor)
Optionmenu.pack(side=tk.LEFT, anchor=tk.W)
dropmenu2 = tk.Frame( frame2r )
dropmenu2.pack(side=tk.TOP)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Measurments und Math menu
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
measlab = tk.Label(dropmenu2, text="Meas")
measlab.pack(side=tk.LEFT, anchor=tk.W)
MeasmenuA = tk.Menubutton(dropmenu2, text="CA", style="W3.TButton")
MeasmenuA.menu = tk.Menu(MeasmenuA, tearoff = 0 )
MeasmenuA["menu"]  = MeasmenuA.menu
MeasmenuA.menu.add_command(label="-CA-V-Verical-", foreground="blue", command=donothing)
MeasmenuA.menu.add_checkbutton(label='Avg', variable=MeasDCV1)
MeasmenuA.menu.add_checkbutton(label='Min', variable=MeasMinV1)
MeasmenuA.menu.add_checkbutton(label='Max', variable=MeasMaxV1)
MeasmenuA.menu.add_checkbutton(label='Base', variable=MeasBaseV1)
MeasmenuA.menu.add_checkbutton(label='Top', variable=MeasTopV1)
MeasmenuA.menu.add_checkbutton(label='Mid', variable=MeasMidV1)
MeasmenuA.menu.add_checkbutton(label='P-P', variable=MeasPPV1)
MeasmenuA.menu.add_checkbutton(label='RMS', variable=MeasRMSV1)
MeasmenuA.menu.add_checkbutton(label='CA-CB', variable=MeasDiffAB)
MeasmenuA.menu.add_checkbutton(label='CA-CB RMS', variable=MeasRMSVA_B)
MeasmenuA.menu.add_separator()
MeasmenuA.menu.add_command(label="-CA-I-Vertical", foreground="blue", command=donothing)
MeasmenuA.menu.add_checkbutton(label='Avg', variable=MeasDCI1)
MeasmenuA.menu.add_checkbutton(label='Min', variable=MeasMinI1)
MeasmenuA.menu.add_checkbutton(label='Max', variable=MeasMaxI1)
MeasmenuA.menu.add_checkbutton(label='Mid', variable=MeasMidI1)
MeasmenuA.menu.add_checkbutton(label='P-P', variable=MeasPPI1)
MeasmenuA.menu.add_checkbutton(label='RMS', variable=MeasRMSI1)
MeasmenuA.menu.add_separator()
MeasmenuA.menu.add_command(label="-CA-Horizontal-", foreground="blue", command=donothing)
MeasmenuA.menu.add_checkbutton(label='H-Width', variable=MeasAHW)
MeasmenuA.menu.add_checkbutton(label='L-Width', variable=MeasALW)
MeasmenuA.menu.add_checkbutton(label='DutyCyle', variable=MeasADCy)
MeasmenuA.menu.add_checkbutton(label='Period', variable=MeasAPER)
MeasmenuA.menu.add_checkbutton(label='Freq', variable=MeasAFREQ)
MeasmenuA.menu.add_checkbutton(label='A-B Phase', variable=MeasPhase)
MeasmenuA.pack(side=tk.LEFT)

MeasmenuB = tk.Menubutton(dropmenu2, text="CB", style="W3.TButton")
MeasmenuB.menu = tk.Menu(MeasmenuB, tearoff = 0 )
MeasmenuB["menu"]  = MeasmenuB.menu
MeasmenuB.menu.add_command(label="-CB-V-Vertical-", foreground="blue", command=donothing)
MeasmenuB.menu.add_checkbutton(label='Avg', variable=MeasDCV2)
MeasmenuB.menu.add_checkbutton(label='Min', variable=MeasMinV2)
MeasmenuB.menu.add_checkbutton(label='Max', variable=MeasMaxV2)
MeasmenuB.menu.add_checkbutton(label='Base', variable=MeasBaseV2)
MeasmenuB.menu.add_checkbutton(label='Top', variable=MeasTopV2)
MeasmenuB.menu.add_checkbutton(label='Mid', variable=MeasMidV2)
MeasmenuB.menu.add_checkbutton(label='P-P', variable=MeasPPV2)
MeasmenuB.menu.add_checkbutton(label='RMS', variable=MeasRMSV2)
MeasmenuB.menu.add_checkbutton(label='CB-CA', variable=MeasDiffBA)
MeasmenuB.menu.add_separator()
MeasmenuB.menu.add_command(label="-CB-I-Vertical-", foreground="blue", command=donothing)
MeasmenuB.menu.add_checkbutton(label='Avg', variable=MeasDCI2)
MeasmenuB.menu.add_checkbutton(label='Min', variable=MeasMinI2)
MeasmenuB.menu.add_checkbutton(label='Max', variable=MeasMaxI2)
MeasmenuB.menu.add_checkbutton(label='Mid', variable=MeasMidI2)
MeasmenuB.menu.add_checkbutton(label='P-P', variable=MeasPPI2)
MeasmenuB.menu.add_checkbutton(label='RMS', variable=MeasRMSI2)
MeasmenuB.menu.add_separator()
MeasmenuB.menu.add_command(label="-CB-Horizontal-", foreground="blue", command=donothing)
MeasmenuB.menu.add_checkbutton(label='H-Width', variable=MeasBHW)
MeasmenuB.menu.add_checkbutton(label='L-Width', variable=MeasBLW)
MeasmenuB.menu.add_checkbutton(label='DutyCyle', variable=MeasBDCy)
MeasmenuB.menu.add_checkbutton(label='Period', variable=MeasBPER)
MeasmenuB.menu.add_checkbutton(label='Freq', variable=MeasBFREQ)
MeasmenuB.menu.add_checkbutton(label='B-A Delay', variable=MeasDelay)
MeasmenuB.pack(side=tk.LEFT)

mathbt = tk.Button(dropmenu2, text="Math", style="W4.TButton", command = MakeMathMenu)
mathbt.pack(side=tk.RIGHT, anchor=tk.W)

math_tip = CreateToolTip(mathbt, 'Open Math window')
BuildAWGScreen_tip = CreateToolTip(BuildAWGScreen, 'Surface AWG Controls window')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# AWG Menü
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
BuildAWGScreen = tk.Button(frame2r, text="AWG Window", style="W16.TButton", command=MakeAWGMenu)
BuildAWGScreen.pack(side=tk.TOP)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Menü zur Anzeige der Traces
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
ckbt1 = tk.Checkbutton(frame2r, text='CA-V [1]', style="Strace1.TCheckbutton", variable=ShowC1_V, command=TraceSelectADC_Mux)
ckbt1.pack(side=tk.TOP)
ckbt2 = tk.Checkbutton(frame2r, text='CA-I [3]', style="Strace3.TCheckbutton", variable=ShowC1_I, command=TraceSelectADC_Mux)
ckbt2.pack(side=tk.TOP)
ckbt3 = tk.Checkbutton(frame2r, text='CB-V [2]', style="Strace2.TCheckbutton", variable=ShowC2_V, command=TraceSelectADC_Mux)
ckbt3.pack(side=tk.TOP)
ckbt4 = tk.Checkbutton(frame2r, text='CB-I [4]', style="Strace4.TCheckbutton", variable=ShowC2_I, command=TraceSelectADC_Mux)
ckbt4.pack(side=tk.TOP)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Gain-/Offsetkorrektur für V und I der beiden Kanäle (Fenster rechts)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
prlab = tk.Label(frame2r, text="Adjust Gain / Offset")
prlab.pack(side=tk.TOP)
ProbeA = tk.Frame(frame2r)
ProbeA.pack(side=tk.TOP)
gain1lab = tk.Label(ProbeA, text="CA-V")
gain1lab.pack(side=tk.LEFT)

CHAVGainEntry = tk.Entry(ProbeA, width=5)
CHAVGainEntry.bind('<Return>', onTextKey)
CHAVGainEntry.bind('<MouseWheel>', onTextScroll)
CHAVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAVGainEntry.bind("<Button-5>", onTextScroll)
CHAVGainEntry.bind('<Key>', onTextKey)
CHAVGainEntry.pack(side=tk.LEFT)
CHAVGainEntry.delete(0,"tk.END")
CHAVGainEntry.insert(0,1.0)

CHAVOffsetEntry = tk.Entry(ProbeA, width=5)
CHAVOffsetEntry.bind('<Return>', onTextKey)
CHAVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHAVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAVOffsetEntry.bind("<Button-5>", onTextScroll)
CHAVOffsetEntry.bind('<Key>', onTextKey)
CHAVOffsetEntry.pack(side=tk.LEFT)
CHAVOffsetEntry.delete(0,"tk.END")
CHAVOffsetEntry.insert(0,0.0)

ProbeB = tk.Frame( frame2r )
ProbeB.pack(side=tk.TOP)
gain2lab = tk.Label(ProbeB, text="CB-V")
gain2lab.pack(side=tk.LEFT)

CHBVGainEntry = tk.Entry(ProbeB, width=5)
CHBVGainEntry.bind('<Return>', onTextKey)
CHBVGainEntry.bind('<MouseWheel>', onTextScroll)
CHBVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBVGainEntry.bind("<Button-5>", onTextScroll)
CHBVGainEntry.bind('<Key>', onTextKey)
CHBVGainEntry.pack(side=tk.LEFT)
CHBVGainEntry.delete(0,"tk.END")
CHBVGainEntry.insert(0,1.0)

CHBVOffsetEntry = tk.Entry(ProbeB, width=5)
CHBVOffsetEntry.bind('<Return>', onTextKey)
CHBVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHBVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBVOffsetEntry.bind("<Button-5>", onTextScroll)
CHBVOffsetEntry.bind('<Key>', onTextKey)
CHBVOffsetEntry.pack(side=tk.LEFT)
CHBVOffsetEntry.delete(0,"tk.END")
CHBVOffsetEntry.insert(0,0.0)

ProbeAI = tk.Frame( frame2r )
ProbeAI.pack(side=tk.TOP)
gainailab = tk.Label(ProbeAI, text="CA-I")
gainailab.pack(side=tk.LEFT)

CHAIGainEntry = tk.Entry(ProbeAI, width=5)
CHAIGainEntry.bind('<Return>', onTextKey)
CHAIGainEntry.bind('<MouseWheel>', onTextScroll)
CHAIGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAIGainEntry.bind("<Button-5>", onTextScroll)
CHAIGainEntry.bind('<Key>', onTextKey)
CHAIGainEntry.pack(side=tk.LEFT)
CHAIGainEntry.delete(0,"tk.END")
CHAIGainEntry.insert(0,1.0)

CHAIOffsetEntry = tk.Entry(ProbeAI, width=5)
CHAIOffsetEntry.bind('<Return>', onTextKey)
CHAIOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHAIOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAIOffsetEntry.bind("<Button-5>", onTextScroll)
CHAIOffsetEntry.bind('<Key>', onTextKey)
CHAIOffsetEntry.pack(side=tk.LEFT)
CHAIOffsetEntry.delete(0,"tk.END")
CHAIOffsetEntry.insert(0,0.0)

ProbeBI = tk.Frame( frame2r )
ProbeBI.pack(side=tk.TOP)
gainbilab = tk.Label(ProbeBI, text="CB-I")
gainbilab.pack(side=tk.LEFT)

CHBIGainEntry = tk.Entry(ProbeBI, width=5)
CHBIGainEntry.bind('<Return>', onTextKey)
CHBIGainEntry.bind('<MouseWheel>', onTextScroll)
CHBIGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBIGainEntry.bind("<Button-5>", onTextScroll)
CHBIGainEntry.bind('<Key>', onTextKey)
CHBIGainEntry.pack(side=tk.LEFT)
CHBIGainEntry.delete(0,"tk.END")
CHBIGainEntry.insert(0,1.0)

CHBIOffsetEntry = tk.Entry(ProbeBI, width=5)
CHBIOffsetEntry.bind('<Return>', onTextKey)
CHBIOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHBIOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBIOffsetEntry.bind("<Button-5>", onTextScroll)
CHBIOffsetEntry.bind('<Key>', onTextKey)
CHBIOffsetEntry.pack(side=tk.LEFT)
CHBIOffsetEntry.delete(0,"tk.END")
CHBIOffsetEntry.insert(0,0.0)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Vertikaleinstellungen Gain und Offset für V und I der beiden Kanäle
# Boxen unterhalb Oszibild
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Voltage channel A: Verschiedene V/Div - Werte (siehe CHvpdiv)
CHAsb = tk.Spinbox(frame3, width=4, values=CHvpdiv, command=BCHAlevel)
CHAsb.bind('<MouseWheel>', onSpinBoxScroll)
CHAsb.pack(side=tk.LEFT)
CHAsb.delete(0,"tk.END")
CHAsb.insert(0,0.5)
CHAlab = tk.Button(frame3, text="CA V/Div", style="Rtrace1.TButton", command=SetScaleA)
CHAlab.pack(side=tk.LEFT)
CHAVPosEntry = tk.Entry(frame3, width=5)
CHAVPosEntry.bind("<Return>", BOffsetA)
CHAVPosEntry.bind('<MouseWheel>', onTextScroll)# with Windows OS
CHAVPosEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAVPosEntry.bind("<Button-5>", onTextScroll)
CHAVPosEntry.bind('<Key>', onTextKey)
CHAVPosEntry.pack(side=tk.LEFT)
CHAVPosEntry.delete(0,"tk.END")
CHAVPosEntry.insert(0,2.5)
CHAofflab = tk.Button(frame3, text="CA V Pos", style="Rtrace1.TButton", command=SetVAPoss)
CHAofflab.pack(side=tk.LEFT)
# Current channel A: Verschiedene A/Div - Werte (siehe CHipdiv)
CHAIsb = tk.Spinbox(frame3, width=4, values=CHipdiv, command=BCHAIlevel)
CHAIsb.bind('<MouseWheel>', onSpinBoxScroll)
CHAIsb.pack(side=tk.LEFT)
CHAIsb.delete(0,"tk.END")
CHAIsb.insert(0,50.0)
CHAIlab = tk.Button(frame3, text="CA mA/Div", style="Strace3.TButton", command=SetScaleIA)
CHAIlab.pack(side=tk.LEFT)
CHAIPosEntry = tk.Entry(frame3, width=5)
CHAIPosEntry.bind("<Return>", BIOffsetA)
CHAIPosEntry.bind('<MouseWheel>', onTextScroll)# with Windows OS
CHAIPosEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAIPosEntry.bind("<Button-5>", onTextScroll)
CHAIPosEntry.bind('<Key>', onTextKey)
CHAIPosEntry.pack(side=tk.LEFT)
CHAIPosEntry.delete(0,"tk.END")
CHAIPosEntry.insert(0,0.0)
CHAIofflab = tk.Button(frame3, text="CA I Pos", style="Rtrace3.TButton", command=SetIAPoss)
CHAIofflab.pack(side=tk.LEFT)
# Voltage channel B, wie oben
CHBsb = tk.Spinbox(frame3, width=4, values=CHvpdiv, command=BCHBlevel)
CHBsb.bind('<MouseWheel>', onSpinBoxScroll)
CHBsb.pack(side=tk.LEFT)
CHBsb.delete(0,"tk.END")
CHBsb.insert(0,0.5)
CHBlab = tk.Button(frame3, text="CB V/Div", style="Strace2.TButton", command=SetScaleB)
CHBlab.pack(side=tk.LEFT)
CHBVPosEntry = tk.Entry(frame3, width=5)
CHBVPosEntry.bind("<Return>", BOffsetB)
CHBVPosEntry.bind('<MouseWheel>', onTextScroll)# with Windows OS
CHBVPosEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBVPosEntry.bind("<Button-5>", onTextScroll)
CHBVPosEntry.bind('<Key>', onTextKey)
CHBVPosEntry.pack(side=tk.LEFT)
CHBVPosEntry.delete(0,"tk.END")
CHBVPosEntry.insert(0,2.5)
CHBofflab = tk.Button(frame3, text="CB V Pos", style="Rtrace2.TButton", command=SetVBPoss)
CHBofflab.pack(side=tk.LEFT)
# Current channel B, wie oben
CHBIsb = tk.Spinbox(frame3, width=4, values=CHipdiv, command=BCHBIlevel)
CHBIsb.bind('<MouseWheel>', onSpinBoxScroll)
CHBIsb.pack(side=tk.LEFT)
CHBIsb.delete(0,"tk.END")
CHBIsb.insert(0,50.0)
CHBIlab = tk.Button(frame3, text="CB mA/Div", style="Strace4.TButton", command=SetScaleIB)
CHBIlab.pack(side=tk.LEFT)
CHBIPosEntry = tk.Entry(frame3, width=5)
CHBIPosEntry.bind("<Return>", BIOffsetB)
CHBIPosEntry.bind('<MouseWheel>', onTextScroll)# with Windows OS
CHBIPosEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBIPosEntry.bind("<Button-5>", onTextScroll)
CHBIPosEntry.bind('<Key>', onTextKey)
CHBIPosEntry.pack(side=tk.LEFT)
CHBIPosEntry.delete(0,"tk.END")
CHBIPosEntry.insert(0,0.0)
CHBIofflab = tk.Button(frame3, text="CB I Pos", style="Rtrace4.TButton", command=SetIBPoss)
CHBIofflab.pack(side=tk.LEFT)
# Tooltips für die Vertikaleinstellungen zu Channel A und B
CHAlab_tip = CreateToolTip(CHAlab, 'Select CHA-V vertical range/position axis to be used for markers and drawn color')
CHBlab_tip = CreateToolTip(CHBlab, 'Select CHB-V vertical range/position axis to be used for markers and drawn color')
CHAIlab_tip = CreateToolTip(CHAIlab, 'Select CHA-I vertical range/position axis to be used for markers and drawn color')
CHBIlab_tip = CreateToolTip(CHBIlab, 'Select CHB-I vertical range/position axis to be used for markers and drawn color')
CHAofflab_tip = CreateToolTip(CHAofflab, 'Set CHA-V position to DC average of signal')
CHBofflab_tip = CreateToolTip(CHBofflab, 'Set CHB-V position to DC average of signal')
CHAIofflab_tip = CreateToolTip(CHAIofflab, 'Set CHA-I position to DC average of signal')
CHBIofflab_tip = CreateToolTip(CHBIofflab, 'Set CHB-I position to DC average of signal')

root.geometry('+300+root')
root.protocol("WM_DELETE_WINDOW", Bcloseexit)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Hauptroutine
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
ConSingDev() # Connect a single (only one connected) M1K device
MakeAWGMenu() # always build AWG window
MakeMeasureMenu()
BLoadConfig("default-config.cfg") # load default configuration
root.update() # Activate updated screens  
Analog_In() # Start sampling