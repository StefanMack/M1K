#!/usr/bin/python3
# -*- coding: utf-8 -*-
# With external module pysmu (libsmu >= 1.0.2 for ADALM1000)
# Uses new firmware (2.17 or >) that support control of ADC mux configure
# Based on Code wirtten by D Mercer ()
# https://github.com/analogdevicesinc/alice/tree/Version-1.3
#
# Version 0.6, sixth release version: Last Version named "AliceLite"
# --> Future versions will be named "smuc" due to ADI copy right issues.
'''
Bugs:
- derzeit keine :-))
'''

# *****************************************************************************
# smuc Version 0.6, S. Mack, 2.1.2021
# *****************************************************************************

import time
import logging
import tkinter as tk
import tkinter.font as tkf
import tkinter.messagebox as tkm
import tkinter.ttk as ttk # nötig für Widget Styles
from tkinter.filedialog import asksaveasfilename
import pysmu as smu # auskommentiert, wenn kein M1K angeschlossen
import config as cf # hier stehen alle ehemaligen globalen Variablen drin
from aliceIcons import hipulse, lowpulse # Bilddateien der Icons
# Thinter UI Menüs
from aliceMenus import MakeSettingsMenu, CreateToolTip, MakeAWGMenu
# Samplingfunktionen des M1K
import aliceM1kSamp as m1k
# Oszillsokopfunktionen
from aliceOsciFunc import (stop_samp, set_hscale, set_hpos,
start_samp, UpdateTimeAll, UpdateTimeTrace, UpdateTimeScreen,
BTrigger50p, BTriglevel)

# Nachfolgende Zeile für Debugmeldungen ausschalten (level=0 bedeutet alle Meldungen)
# DEBUG 10, INFO 20, WARNING 30
logging.basicConfig(level=30)
logging.basicConfig(filename='logDatei.log', level=40)


# Vertical Sensitivity list in v/div "Channel Voltage Per Division"
v_scale_vals = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)
# Vertical Sensitivity list in mA/div und Defaultwert "Channel I(Current) Per Division"
i_scale_vals = (0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter UI Initialisierungen und Styles (Instanzierung root in config.py)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
logging.debug("Windowing System is " + str(cf.root.tk.call('tk', 'windowingsystem')))
cf.root.style = ttk.Style()
# siehe wiki.tcl-lang.org/page/List+of+ttk+Themes
if (cf.root.tk.call('tk', 'windowingsystem')=='aqua'):
    Style_String = 'aqua' # vermutlich Apple
else:
    Style_String = 'alt' # built-in: 'aqua', 'step', 'clam', 'alt', 'default', 'classic'
try:
    cf.root.style.theme_use(Style_String) 
except:
    cf.root.style.theme_use('default')
    logging.debug("ttk.Style default is used")

default_font = tkf.nametofont("TkDefaultFont")
default_font.configure(size=cf.FontSize)

cf.root.title("smuc v0.6 (3.1.2021)")

img = tk.PhotoImage(file='IconOszi_80x80.png') # Programm Icon
hipulseimg = tk.PhotoImage(data=hipulse) # Icon für Trigger Rising Edge
lowpulseimg = tk.PhotoImage(data=lowpulse) # Icon für Trigger Falling Edge
cf.root.call('wm', 'iconphoto', cf.root._w, '-default', img)

#FRAME_COLOR = "#000080" 
CANVAS_COLOR = "#000000" # "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
 
#SCstart = 0 # Start sample of the trace

#--- Eigene Styles für Buttons verschiedener Breite
cf.root.style.configure("W3.TButton", width=3, relief=tk.RAISED) # "W" steht für width
cf.root.style.configure("W4.TButton", width=4, relief=tk.RAISED)
cf.root.style.configure("W5.TButton", width=5, relief=tk.RAISED)
cf.root.style.configure("W6.TButton", width=6, relief=tk.RAISED)
cf.root.style.configure("W7.TButton", width=7, relief=tk.RAISED)
cf.root.style.configure("W8.TButton", width=8, relief=tk.RAISED)
cf.root.style.configure("W12.TButton", width=12, relief=tk.RAISED)
cf.root.style.configure("W16.TButton", width=16, relief=tk.RAISED)
# Run/Stop-Button
cf.root.style.configure("Stop.TButton", background=cf.ButtonRed, width=4, relief=tk.RAISED)
cf.root.style.configure("Run.TButton", background=cf.ButtonGreen, width=4, relief=tk.RAISED)
# Button zum Verbindungsaufbau/-trennen mit dem M1K (ändert Farbe je nach Zustand)
cf.root.style.configure("RConn.TButton", background=cf.ButtonRed, width=5, relief=tk.RAISED)
cf.root.style.configure("GConn.TButton", background=cf.ButtonGreen, width=5, relief=tk.RAISED)
# Buttons für vier Traces und Math-Trace, "R" = raised, "S" = sunken
cf.root.style.configure("Rtrace1.TButton", background=cf.COLORtrace1, width=9, relief=tk.RAISED)
cf.root.style.configure("Strace1.TButton", background=cf.COLORtrace1, width=9, relief=tk.SUNKEN)
cf.root.style.configure("Rtrace2.TButton", background=cf.COLORtrace2, width=9, relief=tk.RAISED)
cf.root.style.configure("Strace2.TButton", background=cf.COLORtrace2, width=9, relief=tk.SUNKEN)
cf.root.style.configure("Rtrace3.TButton", background=cf.COLORtrace3, width=9, relief=tk.RAISED)
cf.root.style.configure("Strace3.TButton", background=cf.COLORtrace3, width=9, relief=tk.SUNKEN)
cf.root.style.configure("Rtrace4.TButton", background=cf.COLORtrace4, width=9, relief=tk.RAISED)
cf.root.style.configure("Strace4.TButton", background=cf.COLORtrace4, width=9, relief=tk.SUNKEN)
cf.root.style.configure("Math.TButton", background=cf.COLORtrace5, width=4, relief=tk.RAISED)
# Labels
cf.root.style.configure("A10R1.TLabelframe.Label", foreground=cf.COLORtrace5, font=('Arial', 10, 'bold'))
cf.root.style.configure("A10R1.TLabelframe", borderwidth=5, relief=tk.RIDGE)
cf.root.style.configure("A10R2.TLabelframe.Label", foreground=cf.COLORtraceR2, font=('Arial', 10, 'bold'))
cf.root.style.configure("A10R2.TLabelframe", borderwidth=5, relief=tk.RIDGE)
cf.root.style.configure("A10B.TLabel", foreground=CANVAS_COLOR, font="Arial 10 bold") # Black text
cf.root.style.configure("A10R.TLabel", foreground=cf.ButtonRed, font="Arial 10 bold") # Red text
cf.root.style.configure("A12B.TLabel", foreground=CANVAS_COLOR, font="Arial 12 bold") # Black text
# Checkbuttons zum Ein-/Ausschalten der vier Traces rechts neben Oszibild
cf.root.style.configure("Strace1.TCheckbutton", background=cf.COLORtrace1)
cf.root.style.configure("Strace2.TCheckbutton", background=cf.COLORtrace2)
cf.root.style.configure("Strace3.TCheckbutton", background=cf.COLORtrace3)
cf.root.style.configure("Strace4.TCheckbutton", background=cf.COLORtrace4)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Tkinter Callback-Funktionen
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#--- Cursorpostion setzen mit Maus-Klick bzw. ändern mit Maus-Scroll oder Pfeiltasten
def onCanvasClickRight(event): # Cursorkreuz setzen
    logging.debug("onCanvasClickRight() x={0} y={1}".format(event.x, event.y))
    cf.TCursor = event.x # Cursor Horizontal
    cf.VCursor = event.y # Cursor Vertikal ( V oder mA)
    if cf.RUNstatus.get() == 0: # Testweise
        UpdateTimeScreen()


#--- Setzen kleiner Cursor-Kreuze (Markern) via Maus-Linksklick (nur stop), 
#---  deren xy-Koordinaten grün im Scanbild erscheinen
#--- !!funktioniert nur im Stopp-Modus!!
def onCanvasClickLeft(event):
    logging.debug("onCanvasClickLeft() x={0} y={1}".format(event.x, event.y))
    global PrevV, PrevT
    # get time scale
    try:
        cf.TIMEdiv = float(eval(cf.TMsb.get()))
    except:
        cf.TIMEdiv = 0.5
        cf.TMsb.delete(0,tk.END)
        cf.TMsb.insert(0,cf.TIMEdiv)
    # prevent divide by zero error
    if cf.TIMEdiv < 0.0002:
        cf.TIMEdiv = 0.01
    # add markers only if stopped
    if cf.RUNstatus.get() == 0 and cf.ShowCur.get() > 0:
        cf.MarkerNum = cf.MarkerNum + 1  
        if cf.CHAVScale < 0.001: # prevent divide by zero error
            cf.CHAVScale = 0.001
        if cf.CHBVScale < 0.001:
            cf.CHBVScale = 0.001
        if cf.CHAIScale < 1.0:
            cf.CHAIScale = 1.0
        if cf.CHBIScale < 1.0:
            cf.CHBIScale = 1.0
        #YSignOff = cf.CHAVOffset # Wieso nicht 0?
        YSignOff = 0.0
        if cf.ShowCur.get() == 1:
            Yconv = float(cf.GRH/10.0) / cf.CHAVScale
            #YSignOff = cf.CHAVOffset
            YSignOff = cf.CHAVPos
            COLORmarker = cf.COLORtrace1
            Units = " V   "
        elif cf.ShowCur.get() == 2:
            Yconv = float(cf.GRH/10.0) / cf.CHBVScale
            YSignOff = cf.CHBVPos
            COLORmarker = cf.COLORtrace2
            Units = " V   "
        elif cf.ShowCur.get() == 3:
            Yconv = float(cf.GRH/10.0) / cf.CHAIScale
            YSignOff = cf.CHAIPos
            COLORmarker = cf.COLORtrace3
            Units = " mA   "
        elif cf.ShowCur.get() == 4:
            Yconv = float(cf.GRH/10.0) / cf.CHBIScale
            YSignOff = cf.CHAIPos
            COLORmarker = cf.COLORtrace4
            Units = " mA   "
            
        yMid = cf.GRH / 2.0 + cf.Y0T # absolute Y-Pixelposition Mittellinie Grid
        # draw X at marker point and number
        cf.ca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=cf.COLORtext)
        cf.ca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=cf.COLORtext)
        Tstep = (10.0 * cf.TIMEdiv) / cf.GRW # time in mS per pixel
        Tpoint = ((event.x-cf.X0L) * Tstep)
        # Angabe Zeit und Spannungswert sowie Differenzen davon
        Tpoint = Tpoint
        if Tpoint >= 1000:
            axis_value = Tpoint / 1000.0
            TString = ' {0:.2f} '.format(axis_value) + " s, "
        if Tpoint < 1000 and Tpoint >= 1:
            axis_value = Tpoint
            TString = ' {0:.2f} '.format(axis_value) + " ms, "
        if Tpoint < 1:
            axis_value = Tpoint * 1000.0
            TString = ' {0:.2f} '.format(axis_value) + " us, "
        
        ySign = ((yMid - event.y)/Yconv + YSignOff) # Mausposition in V/mA umrechnen
        logging.debug("Marker y-Value  event.y={0} ySign={1} Yconv={2} YSignOff={3} cf.GRH={4}".format(event.y, ySign, Yconv, YSignOff, cf.GRH))
        V1String = ' {0:.3f} '.format(ySign)

        V_label = str(cf.MarkerNum) + ":  Pos: " + TString + V1String
        V_label = V_label + Units
        if cf.MarkerNum > 1: # ab dem zweiten Marker
            DeltaV = ' {0:.3f} '.format(PrevV-ySign)

            DT = (Tpoint-PrevT)
            if Tpoint >= 1000:
                axis_value = DT / 1000.0
                DeltaT = ' {0:.2f} '.format(axis_value) + " s, "
            if Tpoint < 1000 and Tpoint >= 1:
                axis_value = DT
                DeltaT = ' {0:.2f} '.format(axis_value) + " ms, "
            if Tpoint < 1:
                axis_value = DT * 1000.0
                DeltaT = ' {0:.2f} '.format(axis_value) + " us, "
            if((Tpoint-PrevT) != 0):
                DFreq = ' {0:.3f} '.format(1.0/(Tpoint-PrevT))
            else: DFreq = ' inf '
            V_label = V_label + " Delta: " + DeltaT + DeltaV
            V_label = V_label + Units
            V_label = V_label + "  Freq: " + DFreq + " KHz"
        # place in upper left unless specified otherwise
        x = cf.X0L + 5
        y = cf.Y0T + 3 + (cf.MarkerNum*12)
        Justify = 'w'
        cf.ca.create_text(event.x+4, event.y, text=str(cf.MarkerNum), fill=cf.COLORtext, anchor=Justify, font=("arial", cf.FontSize, tk.font.BOLD ))
        cf.ca.create_text(x, y, text=V_label, fill=COLORmarker, anchor=Justify, font=("arial", cf.FontSize, tk.font.BOLD ))
        PrevV = ySign
        PrevT = Tpoint
        
    
def onCAresize(event):
    logging.debug("onCAresize()")
    event.widget
    cf.XOL = cf.FontSize * 7
    cf.CANVASwidth = event.width - 4
    cf.CANVASheight = event.height - 4
    cf.GRW = cf.CANVASwidth - (2 * cf.X0L) # new grid width
    cf.GRH = cf.CANVASheight - (cf.Y0T + (cf.FontSize * 10))   # new grid height, 10 Fontgrößen Raum für Darstellungen Messwerte u.A.
    UpdateTimeAll()

def onSpinBoxScroll(event): # Spin Boxes do this automatically in Python 3 apparently
    logging.debug('onSpinBoxScroll()')
    spbox = event.widget
    if event.delta > 0: # increment digit
        spbox.invoke('buttonup')
    else: # decrement digit
        spbox.invoke('buttondown')

def onSrateScroll(event): # Samplingrateeinstellung
    logging.debug('onSrateScroll()')
    onSpinBoxScroll(event)
    m1k.SetSampleRate()
    
#def onRetSrate(event): # <return> bei Samplingrateeinstellung
#    logging.debug('onRetSrate()')
#    m1k.SetSampleRate()
    

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Setterfunktionen für UI-Eingaben
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
#--- Vertikalskalierung
def SetCHAVScale():
    cf.CHAVScale = float(eval(cf.CHAVsb.get()))
    logging.debug('SetCHAVScale() with CHAVScale={}'.format(cf.CHAVScale))
    UpdateTimeTrace() # Aenderung im Scopebild aktivieren

def SetCHAIScale():
    cf.CHAIScale = float(eval(cf.CHAIsb.get()))
    logging.debug('SetCHAIScale() with CHAIScale={}'.format(cf.CHAIScale))
    UpdateTimeTrace() # Aenderung im Scopebild aktivieren

def SetCHBVScale():
    cf.CHBVScale = float(eval(cf.CHBVsb.get()))
    logging.debug('SetCHBVScale() with CHBVScale={}'.format(cf.CHBVScale))
    UpdateTimeTrace() # Aenderung im Scopebild aktivieren

def SetCHBIScale():
    cf.CHBIScale = float(eval(cf.CHBIsb.get()))
    logging.debug('SetCHBIScale() with CHBIScale={}'.format(cf.CHBIScale))
    UpdateTimeTrace() # Aenderung im Scopebild aktivieren
    
#--- Vertikalposition
def SetCHAVPos(event):
    logging.debug('SetCHBVPos()')
    try:
        cf.CHAVPos = float(eval(cf.CHAVPosEntry.get()))
    except:
        cf.CHAVPosEntry.delete(0,tk.END)
        cf.CHAVPosEntry.insert(0, cf.CHAVPos)
    logging.debug('SetCHAVPos() with CHAVPos={}'.format(cf.CHAVPos))
    UpdateTimeTrace()           # Always Update

def SetCHAIPos(event):
    logging.debug('SetCHBIPos()')
    try:
        cf.CHAIPos = float(eval(cf.CHAIPosEntry.get()))
    except:
        cf.CHAIPosEntry.delete(0,tk.END)
        cf.CHAIPosEntry.insert(0, cf.CHAIPos)
    UpdateTimeTrace()           # Always Update

def SetCHBVPos(event):
    logging.debug('SetCHBVOffset()')
    try:
        cf.CHBVPos = float(eval(cf.CHBVPosEntry.get()))
    except:
        cf.CHBVPosEntry.delete(0,tk.END)
        cf.CHBVPosEntry.insert(0, cf.CHBVPos)
    UpdateTimeTrace()           # Always Update

def SetCHBIPos(event):
    logging.debug('SetCHBIOffset()')
    try:
        cf.CHBIPos = float(eval(cf.CHBIPosEntry.get()))
    except:
        cf.CHBIPosEntry.delete(0,tk.END)
        cf.CHBIPosEntry.insert(0, cf.CHBIPos)
    UpdateTimeTrace()           # Always Update

#--- Kalibrierwerte (rechts neben Oszibild)   
def setCalValues(event):
    logging.debug('setCalValues()')
    try:
        cf.CHAVOffset = float(eval(cf.CHAVOffsetEntry.get())) # UI-Input lesen und prüfen ob Float-Wert
    except: # Falls kein Floatwert, UI-Input auf Standardwert setzen
        cf.CHAVOffset = 0.0
        cf.CHAVOffsetEntry.delete(0,tk.END)
        cf.CHAVOffsetEntry.insert(0, cf.CHAVOffset)
    try:
        cf.CHAVGain = float(eval(cf.CHAVGainEntry.get()))
    except:
        cf.CHAVGain = 1.0
        cf.CHAVGainEntry.delete(0,tk.END)
        cf.CHAVGainEntry.insert(0, cf.CHAVGain)
    try:
        cf.CHBVOffset = float(eval(cf.CHBVOffsetEntry.get()))
    except:
        cf.CHBVOffset = 0.0
        cf.CHBVOffsetEntry.delete(0,tk.END)
        cf.CHBVOffsetEntry.insert(0, cf.CHBVOffset)
    try:
        cf.CHBVGain = float(eval(cf.CHBVGainEntry.get()))
    except:
        cf.CHBVGain = 1.0
        cf.CHBVGainEntry.delete(0,tk.END)
        cf.CHBVGainEntry.insert(0, cf.CHBVGain)
    try:
        cf.CHAIOffset = float(cf.CHAIOffsetEntry.get())
    except:
        cf.CHAIOffset = 0.0
        cf.CHAIOffsetEntry.delete(0,tk.END)
        cf.CHAIOffsetEntry.insert(0, cf.CHAIOffset)
    try:
        cf.CHBIOffset = float(cf.CHBIOffsetEntry.get())
    except:
        cf.CHBIOffset = 0.0
        cf.CHBIOffsetEntry.delete(0,tk.END)
        cf.CHBIOffsetEntry.insert(0, cf.CHBIOffset)
    try:
        cf.CHAIGain = float(cf.CHAIGainEntry.get())
    except:
        cf.CHAIGain = 1.0
        cf.CHAIGainEntry.delete(0,tk.END)
        cf.CHAIGainEntry.insert(0, cf.CHAIGain)
    try:
        cf.CHBIGain = float(cf.CHBIGainEntry.get())
    except:
        cf.CHBIGain = 1.0
        cf.CHBIGainEntry.delete(0,tk.END)
        cf.CHBIGainEntry.insert(0, cf.CHBIGain)
    

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# M1K Spezifisches
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def ConSingDev():
    logging.debug('ConSingDev()')
    global PIO_0, PIO_1, PIO_2, PIO_3, PIO_4, PIO_5, PIO_6, PIO_7
    if cf.DevID == "No Device":
        try:
            cf.session = smu.Session(ignore_dataflow=True, sample_rate=cf.SampRate, queue_size=cf.MaxSamples)
        except:
            tkm.showwarning("WARNING", "M1K buisy - please reconnect USB and press the red M1K-Connect Button.")
            return
        if not cf.session.devices:
            tkm.showwarning("WARNING","No Device Plugged In!")
            cf.DevID = "No Device"
            FWRevOne = 0.0
            m1kcon.configure(text="M1K", style="RConn.TButton")
            return
        cf.session.configure(sample_rate=cf.SampRate)
        logging.debug("Session sample rate: {}".format(cf.session.sample_rate))      
        cf.devx = cf.session.devices[0] 
        cf.DevID = cf.devx.serial
        print("Device ID:" + str(cf.DevID))
        FWRevOne = float(cf.devx.fwver)
        HWRevOne = str(cf.devx.hwver)
        print('Firmware Revision: {}, Hardware Revision: {}'.format(FWRevOne, HWRevOne))   
        if FWRevOne < 2.17:
            tkm.showwarning("WARNING","This ALICE version Requires Firmware version > 2.16")
        cf.CHA = cf.devx.channels['A']    # Open CHA
        cf.CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        cf.CHB = cf.devx.channels['B']    # Open CHB
        cf.CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode  
        # Hier unterscheiden sich die beiden Hardware-Revisions
        cf.devx.set_adc_mux(0)
        if cf.devx.hwver == "F":
            logging.debug( "Rev F Board I/O ports set")
            PIO_0 = 28
            PIO_1 = 29
            PIO_2 = 47
            PIO_3 = 3
            PIO_4 = 4
            PIO_5 = 5
            PIO_6 = 6
            PIO_7 = 7
        else:
            logging.debug( "Rev D Board I/O ports set")
            PIO_0 = 0
            PIO_1 = 1
            PIO_2 = 2
            PIO_3 = 3
            PIO_4 = 4
            PIO_5 = 5
            PIO_6 = 6
            PIO_7 = 7           
        cf.devx.set_adc_mux(0)
        cf.devx.ctrl_transfer(0x40, 0x24, 0x0, 0, 0, 0, 100) # set to addr DAC A 
        cf.devx.ctrl_transfer(0x40, 0x25, 0x1, 0, 0, 0, 100) # set not addr DAC B
        try:
            cf.session.start(0) # Start kontinuierlicher Modus des M1K
            cf.devx.set_led(0b010) # set LED.green ToDo: Unterscheidung Rev D/F
            m1kcon.configure(text="M1K", style="GConn.TButton")
        except:
            tkm.showwarning("WARNING", "M1K could not be connected.")
        

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen UI
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
# Toggle the Background and text colors based on ColorMode
def BgColor():
    global CANVAS_COLOR
    if cf.ColorMode.get() > 0:
        cf.COLORtext = "#000000"   # 100% black
        cf.COLORtrace4 = "#a0a000" # 50% yellow
        cf.COLORtraceR4 = "#606000"   # 25% yellow
        CANVAS_COLOR = "#ffffff"     # 100% white
    else:
        cf.COLORtext = "#ffffff"     # 100% white
        cf.COLORtrace4 = "#ffff00" # 100% yellow
        cf.COLORtraceR4 = "#808000"   # 50% yellow        
        CANVAS_COLOR = "#000000"   # 100% black
    cf.ca.config(background=CANVAS_COLOR)
    UpdateTimeScreen()

# Screenshot des Oszibilds als eps-Grafik speichern (Konvertierung via PIL in PNG ergibt eine
# zu grobe Auflösung, besser extern konvertieren). Weiße Links-Klick-Marker verschwinden bei ColorMode 0
def BSaveScreen():
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")])
    logging.debug('BSaveScreen() with filename={}, ColorMode={}'.format(filename,cf.ColorMode.get()))
    if cf.ColorMode.get() > 0: # falls weißer Hintergrund Oszibild gewählt 
        logging.debug('no color change')
        cf.ca.postscript(file=filename, height=cf.CANVASheight, width=cf.CANVASwidth, colormode='color', rotate=1)
    else: # falls schwarzer Hintegrund, zum Speichern temporär auf Weiß wechseln, Marker gehen verloren
        logging.debug('intermediate color change to white background')
        cf.ColorMode.set(1)
        BgColor()
        UpdateTimeScreen()
        cf.ca.postscript(file=filename, height=cf.CANVASheight, width=cf.CANVASwidth, colormode='color', rotate=1)
        cf.ColorMode.set(0)
        BgColor()


# Die vier Signalverläufe sowie die Samplinzeiten dazu in eine CSV-Datei schreiben
def BSaveData():
    filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
    DataFile = open(filename, 'w')
    DataFile.write( 'Time (s), CA-V (V), CA-I (mA), CB-V (V), CB-I (mA) \n' )
    for index in range(len(cf.VBuffA)):
        TimePnt = float((index+0.0)/cf.SampRate)
        DataFile.write( str(TimePnt) + ', ' + str(cf.VBuffA[index]) + ', ' + str(cf.IBuffA[index]) + ', '
                        + str(cf.VBuffB[index]) + ', ' + str(cf.IBuffB[index]) + '\n')
    DataFile.close()


# Function to close and exit ALICE
def Bcloseexit():
    logging.debug('Bcloseexit()')
    stop_samp()
    time.sleep(0.2)
    cf.RUNstatus.set(0)
    cf.running = 0 # stop Analog_in() while loop
    time.sleep(0.2)
    try:
        cf.devx.set_led(0b100) # LED auf Blau setzen
        # Put channels in Hi-Z and exit
        cf.CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        cf.CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
        cf.devx.set_adc_mux(0) # set ADC mux conf to default
        cf.CHA.constant(0.0)
        cf.CHB.constant(0.0)
    except:
        pass
    cf.root.destroy()


def donothing(): # Workaround für blaue Überschriften im Measure-Menü
    pass

#==============================================================================
#==============================================================================
#Eigentliches Hauptprogramm, das das Scopefenster aufbaut.
#==============================================================================
#==============================================================================
cf.root.geometry('1400x800+0+0') # Größe und xy-Position Fenster beim Start
cf.root.protocol("WM_DELETE_WINDOW", Bcloseexit) # wenn Oszifenster geschlossen wird > Bcloseexit
#--- Festlegung der Teilfenster
frame1 = ttk.Frame(cf.root, borderwidth=5, relief=tk.RIDGE) # oberhalb Anzeigebereich
frame1.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.NO)
frame2r = ttk.Frame(cf.root, borderwidth=5, relief=tk.RIDGE) # rechts neben Anzeigebereich
frame2r.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.NO)
frame2 = ttk.Frame(cf.root, borderwidth=5, relief=tk.RIDGE) # Anzeigebereich Signale
frame2.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
frame3 = ttk.Frame(cf.root, borderwidth=5, relief=tk.RIDGE) # unterhalb Anzeigebereich
frame3.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.NO)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Trigger Menü
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Triggermenu = ttk.Menubutton(frame1, text="Trigger", style="W7.TButton")
Triggermenu.menu = tk.Menu(Triggermenu, tearoff = 0 )
Triggermenu["menu"]  = Triggermenu.menu
Triggermenu.menu.add_radiobutton(label='None', variable=cf.TgInput, value=0)
Triggermenu.menu.add_radiobutton(label='CA-V', variable=cf.TgInput, value=1)
Triggermenu.menu.add_radiobutton(label='CA-I', variable=cf.TgInput, value=2)
Triggermenu.menu.add_radiobutton(label='CB-V', variable=cf.TgInput, value=3)
Triggermenu.menu.add_radiobutton(label='CB-I', variable=cf.TgInput, value=4)
Triggermenu.menu.add_checkbutton(label='Low Pass Filter', variable=cf.LPFTrigger)
Triggermenu.menu.add_checkbutton(label='SingleShot', variable=cf.SingleShot)
Triggermenu.pack(side=tk.LEFT)

Edgemenu = ttk.Menubutton(frame1, text="Edge", style="W5.TButton")
Edgemenu.menu = tk.Menu(Edgemenu, tearoff = 0 )
Edgemenu["menu"]  = Edgemenu.menu
Edgemenu.menu.add_radiobutton(label='Rising [+]', variable=cf.TgEdge, value=0)
Edgemenu.menu.add_radiobutton(label='Falling [-]', variable=cf.TgEdge, value=1)
Edgemenu.pack(side=tk.LEFT)

tlab = ttk.Label(frame1, text="Trig Level (V/mA):")
tlab.pack(side=tk.LEFT)
cf.TRIGGERentry = tk.Entry(frame1, width=5)
cf.TRIGGERentry.bind("<Return>", BTriglevel)
cf.TRIGGERentry.pack(side=tk.LEFT)
cf.TRIGGERentry.delete(0,tk.END)
cf.TRIGGERentry.insert(0,2.5)

tgb = ttk.Button(frame1, text="50%", style="W4.TButton", command=BTrigger50p)
tgb.pack(side=tk.LEFT)

hint = ttk.Label(frame1, text="press <Return> to confirm")
hint.pack(side=tk.LEFT, padx=(20,0))
# Tooltips
Triggermenu_tip = CreateToolTip(Triggermenu, 'Trigger aktivieren, Triggerquelle und Triggermodus')
Edgemenu_tip = CreateToolTip(Edgemenu, 'Triggern auf steigende oder fallende Flanke')
Triglevel_tip = CreateToolTip(cf.TRIGGERentry, 'Triggerschwelle in V bzw. mA')
tgb_tip = CreateToolTip(tgb, 'Triggerschwelle in die Mitte zwischen Signalminimum und -maximum setzen')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Oszistatus Menü
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
bexit = ttk.Button(frame1, text="Exit", style="W4.TButton", command=Bcloseexit)
bexit.pack(side=tk.RIGHT)
stop_btn = ttk.Button(frame1, text="Stop", style="Stop.TButton", command=stop_samp)
stop_btn.pack(side=tk.RIGHT)
run_btn = ttk.Button(frame1, text="Run", style="Run.TButton", command=start_samp)
run_btn.pack(side=tk.RIGHT)
# M1K Connect action and status
m1kcon = ttk.Button(frame1, text="M1K", style="RConn.TButton", command=ConSingDev)
m1kcon.pack(side=tk.RIGHT)

bexit_tip = CreateToolTip(bexit, 'Anwendung schließen')
stop_btn_tip = CreateToolTip(stop_btn, 'Stop Datenaufnahme, Signalerzeugung und Aktualisierung Darstellung')
run_btn_tip = CreateToolTip(run_btn, 'Start Datenaufnahme, Signalerzeugung und Aktualisierung Darstellung')
m1kcon_tip = CreateToolTip(m1kcon, 'M1K verbinden oder trennen, Grün = M1K verbunden')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Cursor Menü: Auswahl für welchen Trace Cursor (T-Cursor immer mit dabei)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Cursormenu = ttk.Menubutton(frame1, text="Cursor", style="W7.TButton")
Cursormenu.menu = tk.Menu(Cursormenu, tearoff = 0 )
Cursormenu["menu"] = Cursormenu.menu
Cursormenu.menu.add_radiobutton(label='None', value = 0, variable=cf.ShowCur, command=UpdateTimeTrace)
Cursormenu.menu.add_radiobutton(label='CA-V Cursor', background=cf.COLORtrace1, value = 1, variable=cf.ShowCur, command=UpdateTimeTrace)
Cursormenu.menu.add_radiobutton(label='CA-I Cursor', background=cf.COLORtrace3, value = 3, variable=cf.ShowCur, command=UpdateTimeTrace)
Cursormenu.menu.add_radiobutton(label='CB-V Cursor', background=cf.COLORtrace2, value = 2, variable=cf.ShowCur, command=UpdateTimeTrace)
Cursormenu.menu.add_radiobutton(label='CB-I Cursor', background=cf.COLORtrace4, value = 4, variable=cf.ShowCur, command=UpdateTimeTrace)
Cursormenu.pack(side=tk.RIGHT, padx=(0,16))
cursor_tip = CreateToolTip(Cursormenu, 'xy-Cursor einschalten und auswählen welcher dargestellter Signalverlauf damit vermessen wird'
                           'Rechter Mausklick für Cursorkreuz, linker Mausklick (nur nach Stop) zum Setzen mehrerer xy-Punkte im Oszibild.')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Horizontal Menü: Time per Div
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
cf.TMsb = tk.Spinbox(frame1, width=5, values= cf.TMpdiv, command=set_hscale)
cf.TMsb.bind('<MouseWheel>', onSpinBoxScroll)
cf.TMsb.bind("<Return>", set_hscale)
cf.TMsb.pack(side=tk.RIGHT, padx=(0,16))
cf.TMsb.delete(0,tk.END)
cf.TMsb.insert(0,0.5)
cf.TMsb['state'] = ('readonly') # keine Texteingabe eigener Werte
cf.TMlab = ttk.Label(frame1, text="Horz Scale ms/Div:")
cf.TMlab.pack(side=tk.RIGHT)

cf.HozPosentry = tk.Entry(frame1, width=4)
cf.HozPosentry.bind("<Return>", set_hpos)
cf.HozPosentry.pack(side=tk.RIGHT)
cf.HozPosentry.delete(0,tk.END)
cf.HozPosentry.insert(0,0.0)
hozlab = ttk.Label(frame1, text="Horz Pos (ms):")
hozlab.pack(side=tk.RIGHT)
# Tooltips
hozlab_tip = CreateToolTip(cf.HozPosentry, 'Horizontale Position des Triggerzeitpunkts in der Darstellung: 0 ms = Mitte.'
                           'Für negative Werte zuerst Zahl und dann Minuszeichen eingeben. Maximal +/- 5x Zeitbasis)')
time_tip = CreateToolTip(cf.TMsb, 'Horizontale Skalierung = Zeitbasis: Zeitabstand zwischen Gitterlinien (Div)')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Anzeigebereich für Traces
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Canvas (Anzeigebereich der Signale in frame2)
cf.ca = tk.Canvas(frame2, width=cf.CANVASwidth, height=cf.CANVASheight, background=CANVAS_COLOR, cursor='cross')
# add mouse left and right button click to cf.canvas
cf.ca.bind('<Configure>', onCAresize)
cf.ca.bind('<1>', onCanvasClickLeft)
cf.ca.bind('<3>', onCanvasClickRight)
cf.ca.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
# right side menu buttons
dropmenu1 = ttk.Frame(frame2r)
dropmenu1.pack(side=tk.TOP)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# File menu
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Filemenu = ttk.Menubutton(dropmenu1, text="File", style="W4.TButton")
Filemenu.menu = tk.Menu(Filemenu, tearoff = 0 )
Filemenu["menu"] = Filemenu.menu
Filemenu.menu.add_command(label="Save Screen To EPS", command=BSaveScreen)
Filemenu.menu.add_command(label="Save Traces To CSV", command=BSaveData)
Filemenu.pack(side=tk.LEFT, anchor=tk.W)
# Tooltips
file_tip = CreateToolTip(Filemenu, 'Speichern des Oszillkopbilds als EPS-Datei oder der Signalverläufe als CSV-Datei')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Options Menu
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Optionmenu = ttk.Menubutton(dropmenu1, text="Options", style="W7.TButton")
Optionmenu.menu = tk.Menu(Optionmenu, tearoff = 0 )
Optionmenu["menu"]  = Optionmenu.menu
Optionmenu.menu.add_command(label='Settings', command=MakeSettingsMenu)
Optionmenu.menu.add_checkbutton(label='Smooth', variable=cf.SmoothCurves, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Z-O-Hold', variable=cf.ZOHold, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Trace Avg', variable=cf.TraceAvgMode)
Optionmenu.menu.add_radiobutton(label='Black BG', variable=cf.ColorMode, value=0, command=BgColor)
Optionmenu.menu.add_radiobutton(label='White BG', variable=cf.ColorMode, value=1, command=BgColor)
Optionmenu.pack(side=tk.LEFT, anchor=tk.W)
# Tooltip für Options Button (leider keine getrennten Tooltips für Menüpunkte machbar)
opt_tip=CreateToolTip(Optionmenu, 'Einstellungen, Abtastrate, Darstellungsformen, Mittelung')


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Measurments und Math menu
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
dropmenu2 = ttk.Frame(frame2r)
dropmenu2.pack(side=tk.TOP, pady=(0,8))
#--- Drop Down Menü zur Auswahl der Mathematikfunktionen
mathmenu = ttk.Menubutton(dropmenu2, text="Math", style="Math.TButton")
mathmenu.menu = tk.Menu(mathmenu, tearoff = 0 )
mathmenu["menu"]  = mathmenu.menu
mathmenu.menu.add_radiobutton(label='none', variable=cf.MathTrace, value=0, command=UpdateTimeTrace)
mathmenu.menu.add_radiobutton(label='CA-V+CB-V', variable=cf.MathTrace, value=1, command=UpdateTimeTrace)
mathmenu.menu.add_radiobutton(label='CA-V-CB-V', variable=cf.MathTrace, value=2, command=UpdateTimeTrace)
mathmenu.menu.add_radiobutton(label='CB-V-CA-V', variable=cf.MathTrace, value=3, command=UpdateTimeTrace)
mathmenu.menu.add_radiobutton(label='CA-I-CB-I', variable=cf.MathTrace, value=8, command=UpdateTimeTrace)
mathmenu.menu.add_radiobutton(label='CB-I-CA-I', variable=cf.MathTrace, value=9, command=UpdateTimeTrace)
mathmenu.menu.add_radiobutton(label='CA-I*CA-V [mW]', variable=cf.MathTrace, value=4, command=UpdateTimeTrace)
mathmenu.menu.add_radiobutton(label='CB-I*CB-V [mW]', variable=cf.MathTrace, value=5, command=UpdateTimeTrace)
mathmenu.menu.add_radiobutton(label='CA-V/CA-I [kOhm]', variable=cf.MathTrace, value=6, command=UpdateTimeTrace)
mathmenu.menu.add_radiobutton(label='CB-V/CB-I [kOhm]', variable=cf.MathTrace, value=7, command=UpdateTimeTrace)
mathmenu.menu.add_radiobutton(label='CB-V/CA-V', variable=cf.MathTrace, value=10, command=UpdateTimeTrace)
mathmenu.menu.add_radiobutton(label='CB-I/CA-I', variable=cf.MathTrace, value=11, command=UpdateTimeTrace)
mathmenu.pack(side=tk.LEFT)
#--- Drop Down Menü zur Auswahl der Messfunktionen CHA
MeasmenuA = ttk.Menubutton(dropmenu2, text="CA", style="W3.TButton")
MeasmenuA.menu = tk.Menu(MeasmenuA, tearoff = 0 )
MeasmenuA["menu"]  = MeasmenuA.menu
MeasmenuA.menu.add_command(label="-CA-V-", foreground="blue", command=donothing)
MeasmenuA.menu.add_checkbutton(label='Avg', variable=cf.MeasDCV1)
MeasmenuA.menu.add_checkbutton(label='Min', variable=cf.MeasMinV1)
MeasmenuA.menu.add_checkbutton(label='Max', variable=cf.MeasMaxV1)
MeasmenuA.menu.add_checkbutton(label='P-P', variable=cf.MeasPPV1)
MeasmenuA.menu.add_checkbutton(label='RMS', variable=cf.MeasRMSV1)
MeasmenuA.menu.add_separator()
MeasmenuA.menu.add_command(label="-CA-I-", foreground="blue", command=donothing)
MeasmenuA.menu.add_checkbutton(label='Avg', variable=cf.MeasDCI1)
MeasmenuA.menu.add_checkbutton(label='Min', variable=cf.MeasMinI1)
MeasmenuA.menu.add_checkbutton(label='Max', variable=cf.MeasMaxI1)
MeasmenuA.menu.add_checkbutton(label='P-P', variable=cf.MeasPPI1)
MeasmenuA.menu.add_checkbutton(label='RMS', variable=cf.MeasRMSI1)
MeasmenuA.pack(side=tk.LEFT)
#--- Drop Down Menü zur Auswahl der Messfunktionen CHB
MeasmenuB = ttk.Menubutton(dropmenu2, text="CB", style="W3.TButton")
MeasmenuB.menu = tk.Menu(MeasmenuB, tearoff = 0 )
MeasmenuB["menu"]  = MeasmenuB.menu
MeasmenuB.menu.add_command(label="-CB-V-", foreground="blue", command=donothing)
MeasmenuB.menu.add_checkbutton(label='Avg', variable=cf.MeasDCV2)
MeasmenuB.menu.add_checkbutton(label='Min', variable=cf.MeasMinV2)
MeasmenuB.menu.add_checkbutton(label='Max', variable=cf.MeasMaxV2)
MeasmenuB.menu.add_checkbutton(label='P-P', variable=cf.MeasPPV2)
MeasmenuB.menu.add_checkbutton(label='RMS', variable=cf.MeasRMSV2)
MeasmenuB.menu.add_separator()
MeasmenuB.menu.add_command(label="-CB-I-", foreground="blue", command=donothing)
MeasmenuB.menu.add_checkbutton(label='Avg', variable=cf.MeasDCI2)
MeasmenuB.menu.add_checkbutton(label='Min', variable=cf.MeasMinI2)
MeasmenuB.menu.add_checkbutton(label='Max', variable=cf.MeasMaxI2)
MeasmenuB.menu.add_checkbutton(label='P-P', variable=cf.MeasPPI2)
MeasmenuB.menu.add_checkbutton(label='RMS', variable=cf.MeasRMSI2)
MeasmenuB.pack(side=tk.LEFT)
measlab = ttk.Label(dropmenu2, text="Meas\n CA/CB")
measlab.pack(side=tk.LEFT)

# Tooltips
measA_tip=CreateToolTip(MeasmenuA, 'Messfunktionen wie Mittelwert, RMS für Kanal A')
measB_tip=CreateToolTip(MeasmenuB, 'Messfunktionen wie Mittelwert, RMS für Kanal B')
math_tip = CreateToolTip(mathmenu, 'Mathematikfunktionen auf Signalverläufe')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Menü zur Anzeige der Traces
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
curvelab = ttk.Label(frame2r, text="Active Channel")
curvelab.pack(side=tk.TOP, pady=(8,0))
curvecheckb = ttk.Frame(frame2r)
curvecheckb.pack(side=tk.TOP)
ckbt1 = ttk.Checkbutton(curvecheckb, text='CA-V', style="Strace1.TCheckbutton", variable=cf.ShowC1_V, command=m1k.TraceSelectADC_Mux)
ckbt1.grid(row=0, column=0)
ckbt2 = ttk.Checkbutton(curvecheckb, text='CA-I', style="Strace3.TCheckbutton", variable=cf.ShowC1_I, command=m1k.TraceSelectADC_Mux)
ckbt2.grid(row=0, column=1)
ckbt3 = ttk.Checkbutton(curvecheckb, text='CB-V', style="Strace2.TCheckbutton", variable=cf.ShowC2_V, command=m1k.TraceSelectADC_Mux)
ckbt3.grid(row=1, column=0)
ckbt4 = ttk.Checkbutton(curvecheckb, text='CB-I', style="Strace4.TCheckbutton", variable=cf.ShowC2_I, command=m1k.TraceSelectADC_Mux)
ckbt4.grid(row=1, column=1)
# Tooltips
CreateToolTip(curvelab, 'Auswahl der dargestellten Signalverläufe. Für 200 kS/s maximal 2 Kanäle auswählen.')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Menü zur Auswahl der Samplingrate
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
SampMenu= ttk.Frame(frame2r)
SampMenu.pack(side=tk.TOP, pady=(8,0))
cf.SampRatesb = tk.Spinbox(SampMenu, width=6, values=cf.SampRateList, command=m1k.SetSampleRate)
#cf.SampRatesb.bind("<Return>", onRetSrate)
cf.SampRatesb.pack(side=tk.LEFT)
cf.SampRatesb.delete(0,tk.END)
cf.SampRatesb.insert(0,cf.SampRate) # mit 100 kS/s initialisieren
cf.SampRatesb['state'] = ('readonly') # keine Texteingabe eigener Werte
Samplab = ttk.Label(SampMenu, text="Sample Rate \n (S/s)")
Samplab.pack(side=tk.LEFT)

# Tooltips
SampRate_tip = CreateToolTip(cf.SampRatesb, 'Abtastrate für ADC (Oszi) und DAC-Abtastrate (AWG). 200 kS/s nur bei ADC falls 2 oder weniger Kanäle aktiv.')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Gain-/Offsetkorrektur (Kalibrierung) für V und I der beiden Kanäle (Fenster rechts)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
prlab = ttk.Label(frame2r, text="Calibrate Gain / Offset")
prlab.pack(side=tk.TOP, pady=(8,0))
ProbeA = ttk.Frame(frame2r)
ProbeA.pack(side=tk.TOP)
gain1lab = ttk.Label(ProbeA, text="CA-V (V)")
gain1lab.pack(side=tk.LEFT)

cf.CHAVGainEntry = tk.Entry(ProbeA, width=6)
cf.CHAVGainEntry.bind('<Return>', setCalValues)
cf.CHAVGainEntry.pack(side=tk.LEFT)
cf.CHAVGainEntry.delete(0,tk.END)
cf.CHAVGainEntry.insert(0,1.0)

cf.CHAVOffsetEntry = tk.Entry(ProbeA, width=6)
cf.CHAVOffsetEntry.bind('<Return>', setCalValues)
cf.CHAVOffsetEntry.pack(side=tk.LEFT)
cf.CHAVOffsetEntry.delete(0,tk.END)
cf.CHAVOffsetEntry.insert(0,0.0)

ProbeB = ttk.Frame( frame2r )
ProbeB.pack(side=tk.TOP)
gain2lab = ttk.Label(ProbeB, text="CB-V (V)")
gain2lab.pack(side=tk.LEFT)

cf.CHBVGainEntry = tk.Entry(ProbeB, width=6)
cf.CHBVGainEntry.bind('<Return>', setCalValues)
cf.CHBVGainEntry.pack(side=tk.LEFT)
cf.CHBVGainEntry.delete(0,tk.END)
cf.CHBVGainEntry.insert(0,1.0)

cf.CHBVOffsetEntry = tk.Entry(ProbeB, width=6)
cf.CHBVOffsetEntry.bind('<Return>', setCalValues)
cf.CHBVOffsetEntry.pack(side=tk.LEFT)
cf.CHBVOffsetEntry.delete(0,tk.END)
cf.CHBVOffsetEntry.insert(0,0.0)

ProbeAI = ttk.Frame( frame2r )
ProbeAI.pack(side=tk.TOP)
gainailab = ttk.Label(ProbeAI, text="CA-I (mA)")
gainailab.pack(side=tk.LEFT)

cf.CHAIGainEntry = tk.Entry(ProbeAI, width=6)
cf.CHAIGainEntry.bind('<Return>', setCalValues)
cf.CHAIGainEntry.pack(side=tk.LEFT)
cf.CHAIGainEntry.delete(0,tk.END)
cf.CHAIGainEntry.insert(0,1.0)

cf.CHAIOffsetEntry = tk.Entry(ProbeAI, width=6)
cf.CHAIOffsetEntry.bind('<Return>', setCalValues)
cf.CHAIOffsetEntry.pack(side=tk.LEFT)
cf.CHAIOffsetEntry.delete(0,tk.END)
cf.CHAIOffsetEntry.insert(0,0.0)

ProbeBI = ttk.Frame( frame2r )
ProbeBI.pack(side=tk.TOP)
gainbilab = ttk.Label(ProbeBI, text="CB-I (mA)")
gainbilab.pack(side=tk.LEFT)

cf.CHBIGainEntry = tk.Entry(ProbeBI, width=6)
cf.CHBIGainEntry.bind('<Return>', setCalValues)
cf.CHBIGainEntry.pack(side=tk.LEFT)
cf.CHBIGainEntry.delete(0,tk.END)
cf.CHBIGainEntry.insert(0,1.0)

cf.CHBIOffsetEntry = tk.Entry(ProbeBI, width=6)
cf.CHBIOffsetEntry.bind('<Return>', setCalValues)
cf.CHBIOffsetEntry.pack(side=tk.LEFT)
cf.CHBIOffsetEntry.delete(0,tk.END)
cf.CHBIOffsetEntry.insert(0,0.0)
# Tooltips
probe_tip = CreateToolTip(prlab, 'Korrektur von Gain- und Offsetfehler der vier Messkanäle zum Kalibrieren')
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# AWG Menü
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
AWGAlab = ttk.Label(frame2r, text="AWG Channel A")
AWGAlab.pack(side=tk.TOP, pady=(8,0))
cf.AWGAMenus= ttk.Frame(frame2r)
cf.AWGAMenus.pack(side=tk.TOP)
cf.AWGASet= ttk.Frame(frame2r)
cf.AWGASet.pack(side=tk.TOP)

AWGBlab = ttk.Label(frame2r, text="AWG Channel B")
AWGBlab.pack(side=tk.TOP, pady=(8,0))
cf.AWGBMenus= ttk.Frame(frame2r)
cf.AWGBMenus.pack(side=tk.TOP)
cf.AWGBSet= ttk.Frame(frame2r)
cf.AWGBSet.pack(side=tk.TOP)

MakeAWGMenu()

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Vertikaleinstellungen Gain und Offset für V und I der beiden Kanäle
# Boxen unterhalb Oszibild
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Voltage channel A: Verschiedene V/Div - Werte siehe v_scale_vals
CHAlab = ttk.Label(frame3, text="CA V/Div:", background=cf.COLORtrace1)
CHAlab.pack(side=tk.LEFT)
cf.CHAVsb = tk.Spinbox(frame3, width=5, values=v_scale_vals, command=SetCHAVScale)
cf.CHAVsb.bind('<MouseWheel>', onSpinBoxScroll)
cf.CHAVsb.pack(side=tk.LEFT)
cf.CHAVsb.delete(0,tk.END)
cf.CHAVsb.insert(0,0.5) # 0,5 als Anfangswert setzen
cf.CHAVsb['state'] = ('readonly') # keine Texteingabe eigener Werte
CHAofflab = ttk.Label(frame3, text="CA-V Pos:", background=cf.COLORtrace1)
CHAofflab.pack(side=tk.LEFT) # rechts neben Widget 6 Pixel Abstand
cf.CHAVPosEntry = tk.Entry(frame3, width=5)
cf.CHAVPosEntry.bind("<Return>", SetCHAVPos)
cf.CHAVPosEntry.pack(side=tk.LEFT, padx=(0,8))
cf.CHAVPosEntry.delete(0,tk.END)
cf.CHAVPosEntry.insert(0,2.5)

# Current channel A: Verschiedene A/Div - Werte siehe i_scale_vals
CHAIlab = ttk.Label(frame3, text="CA mA/Div:", background=cf.COLORtrace3)
CHAIlab.pack(side=tk.LEFT)
cf.CHAIsb = tk.Spinbox(frame3, width=5, values=i_scale_vals, command=SetCHAIScale)
cf.CHAIsb.bind('<MouseWheel>', onSpinBoxScroll)
cf.CHAIsb.pack(side=tk.LEFT)
cf.CHAIsb.delete(0,tk.END)
cf.CHAIsb.insert(0,50.0)
cf.CHAIsb['state'] = ('readonly') # keine Texteingabe eigener Werte
CHAIofflab = ttk.Label(frame3, text="CA-I Pos:", background=cf.COLORtrace3)
CHAIofflab.pack(side=tk.LEFT)
cf.CHAIPosEntry = tk.Entry(frame3, width=5)
cf.CHAIPosEntry.bind("<Return>", SetCHAIPos)
cf.CHAIPosEntry.pack(side=tk.LEFT, padx=(0,8))
cf.CHAIPosEntry.delete(0,tk.END)
cf.CHAIPosEntry.insert(0,0.0)

# Voltage channel B:
CHBlab = ttk.Label(frame3, text="CB V/Div:", background=cf.COLORtrace2)
CHBlab.pack(side=tk.LEFT)
cf.CHBVsb = tk.Spinbox(frame3, width=5, values=v_scale_vals, command=SetCHBVScale)
cf.CHBVsb.bind('<MouseWheel>', onSpinBoxScroll)
cf.CHBVsb.pack(side=tk.LEFT)
cf.CHBVsb.delete(0,tk.END)
cf.CHBVsb.insert(0,0.5)
cf.CHBVsb['state'] = ('readonly') # keine Texteingabe eigener Werte
CHBofflab = ttk.Label(frame3, text="CB-V Pos:", background=cf.COLORtrace2)
CHBofflab.pack(side=tk.LEFT)
cf.CHBVPosEntry = tk.Entry(frame3, width=5)
cf.CHBVPosEntry.bind("<Return>", SetCHBVPos)
cf.CHBVPosEntry.pack(side=tk.LEFT, padx=(0,8))
cf.CHBVPosEntry.delete(0,tk.END)
cf.CHBVPosEntry.insert(0,2.5)


# Current channel B:
CHBIlab = ttk.Label(frame3, text="CB mA/Div:", background=cf.COLORtrace4)
CHBIlab.pack(side=tk.LEFT)
cf.CHBIsb = tk.Spinbox(frame3, width=5, values=i_scale_vals, command=SetCHBIScale)
cf.CHBIsb.bind('<MouseWheel>', onSpinBoxScroll)
cf.CHBIsb.pack(side=tk.LEFT)
cf.CHBIsb.delete(0,tk.END)
cf.CHBIsb.insert(0,50.0)
cf.CHBIsb['state'] = ('readonly') # keine Texteingabe eigener Werte
CHBIofflab = ttk.Label(frame3, text="CB-I Pos:", background=cf.COLORtrace4)
CHBIofflab.pack(side=tk.LEFT)
cf.CHBIPosEntry = tk.Entry(frame3, width=5)
cf.CHBIPosEntry.bind("<Return>", SetCHBIPos)
cf.CHBIPosEntry.pack(side=tk.LEFT)
cf.CHBIPosEntry.delete(0,tk.END)
cf.CHBIPosEntry.insert(0,0.0)


mathInfolab = ttk.Label(frame3, text="Math traces refer to first operand scale")
mathInfolab.pack(side=tk.LEFT, padx=(8,0))

# Tooltips für die Vertikaleinstellungen zu Channel A und B
CHAlab_tip = CreateToolTip(cf.CHAVsb, 'Vertikalskalierung Kanal A Spannung (CA-V) (und Math) in V/Div')
CHBlab_tip = CreateToolTip(cf.CHBVsb, 'Vertikalskalierung Kanal B Spannung (CB-V) in V/Div')
CHAIlab_tip = CreateToolTip(cf.CHAIsb, 'Vertikalskalierung Kanal A Strom (CA-I) (und Math) in mA/Div')
CHBIlab_tip = CreateToolTip(cf.CHBIsb, 'Vertikalskalierung in mA/Div Kanal B Strom (CA-I)')
CHAofflab_tip = CreateToolTip(cf.CHAVPosEntry, 'Höhe der Nulllinie Kanal A Spannung (CA-V) (und Math) in V ')
CHBofflab_tip = CreateToolTip(cf.CHBVPosEntry, 'Höhe der Nulllinie Kanal B Spannung (CB-V) in V')
CHAIofflab_tip = CreateToolTip(cf.CHAIPosEntry, 'Höhe der Nulllinie Kanal A Strom (CA-I) (und Math) in mA')
CHBIofflab_tip = CreateToolTip(cf.CHBIPosEntry, 'Höhe der Nulllinie Kanal B Strom (CB-I) in mA')


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Hauptroutine
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# =============================================================================
# Esgibt keinen mainloop() Befehl. Statdessen wird mit dem Aufruf von AnalogIn()
# eine While-Schleife gestartet, in der zyklisch root.update() aufgerufen wird.
# =============================================================================
ConSingDev() # Connect a single (only one connected) M1K device
logging.debug('Vor root.update() in der Hauptroutine')
cf.root.update() # Activate updated screens  
m1k.ScopeGo() # Start sampling
