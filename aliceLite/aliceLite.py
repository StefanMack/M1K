#!/usr/bin/python3
# -*- coding: utf-8 -*-
# With external module pysmu ( libsmu >= 1.0.2 for ADALM1000 )
# Uses new firmware (2.17 or >) that support control of ADC mux configure
# Based on Code wirtten by D Mercer ()
# https://github.com/analogdevicesinc/alice/tree/Version-1.3
#
# Version 4:
# AWG nur noch mit Basis-Signalformen und ohne doppelte Samplingrate.
# AWG-Terminierung fest auf "open"
# Math-Funktionen verifiziert
# M1K Samplingfunktionen verifiziert
# Ungenutzte globale Variable entfernt
# *****************************************************************************
# Light Version alice-desctop 1.38, S. Mack, 5.9.2020
# *****************************************************************************

import time
#import numpy as np
import tkinter as tk
import tkinter.font as tkf
import tkinter.messagebox as tkm
import tkinter.ttk as ttk # nötig für Widget Styles
from tkinter.filedialog import asksaveasfilename
#root=tk.Tk() # steht jetzt in config.py da sonst dort nicht Instanziert werden kann
import pysmu as smu # auskommentiert, wenn kein M1K angeschlossen
import config as cf # hier stehen alle ehemaligen globalen Variablen drin
from aliceIcons import hipulse, lowpulse, TBicon # Bilddateien der Icons
# AWG Funktionen
from aliceAwgFunc import ReMakeAWGwaves
# Thinter UI Menüs
from aliceMenus import (UpdateAWGMenu, MakeSampleRateMenu, onSpinBoxScroll,
MakeSettingsMenu, MakeMathMenu, CreateToolTip, onTextKey, MakeAWGMenuInside)
# Samplingfunktionen des M1K
from aliceM1kSamp import TraceSelectADC_Mux, Analog_In
# Oszillsokopfunktionen
from aliceOsciFunc import (BStop, BTime, BHozPoss, BCHAlevel,
BCHAIlevel, BCHBlevel, BCHBIlevel, BOffsetA, BIOffsetA, BOffsetB, BIOffsetB,
BStart, UpdateTimeAll, UpdateTimeTrace, UpdateTimeScreen, BHoldOff,
BTrigger50p, BTriglevel)

import logging

# Nachfolgende Zeile für Debugmeldungen ausschalten (level=10 bedeutet alle Meldungen)
logging.basicConfig(level=10)
logging.basicConfig(filename='logDatei.log', level=10)

RevDate = "(5 Sep 2020)"
SWRev = "1.38litev3 "



# Vertical Sensitivity list in v/div "Channel Voltage Per Division"
CHvpdiv = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)
# Vertical Sensitivity list in mA/div und Defaultwert "Channel I(Current) Per Division"
CHipdiv = (0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)
# Time list in ms/div
TMpdiv = (0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter UI Initialisierungen und Styles (Instanzierung root in config.py)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
print("Windowing System is " + str(cf.root.tk.call('tk', 'windowingsystem')))
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
    print("ttk.Style default is used")

default_font = tkf.nametofont("TkDefaultFont")
default_font.configure(size=cf.FontSize)

cf.root.title("ALICE DeskTop Lite " + SWRev + RevDate + ": ALM1000 Oscilloscope")

img = tk.PhotoImage(data=TBicon) # Programm Icon
hipulseimg = tk.PhotoImage(data=hipulse) # Icon für Trigger Rising Edge
lowpulseimg = tk.PhotoImage(data=lowpulse) # Icon für Trigger Falling Edge
cf.root.call('wm', 'iconphoto', cf.root._w, '-default', img)

COLORframes = "#000080" # Color = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
COLORcanvas = "#000000" # 100% black
 
SCstart = 0 # Start sample of the trace

#--- Eigene Styles für Buttons verschiedener Breite
cf.root.style.configure("W3.TButton", width=3, relief=tk.RAISED) # "W" steht für width
cf.root.style.configure("W4.TButton", width=4, relief=tk.RAISED)
cf.root.style.configure("W5.TButton", width=5, relief=tk.RAISED)
cf.root.style.configure("W6.TButton", width=6, relief=tk.RAISED)
cf.root.style.configure("W7.TButton", width=7, relief=tk.RAISED)
cf.root.style.configure("W8.TButton", width=8, relief=tk.RAISED)
cf.root.style.configure("W12.TButton", width=12, relief=tk.RAISED)
cf.root.style.configure("W16.TButton", width=16, relief=tk.RAISED)

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

cf.root.style.configure("A10R1.TLabelframe.Label", foreground=cf.COLORtrace5, font=('Arial', 10, 'bold')) # Math Trace Purpur
cf.root.style.configure("A10R1.TLabelframe", borderwidth=5, relief=tk.RIDGE)
cf.root.style.configure("A10R2.TLabelframe.Label", foreground=cf.COLORtraceR2, font=('Arial', 10, 'bold'))
cf.root.style.configure("A10R2.TLabelframe", borderwidth=5, relief=tk.RIDGE)
cf.root.style.configure("A10B.TLabel", foreground=COLORcanvas, font="Arial 10 bold") # Black text
cf.root.style.configure("A10R.TLabel", foreground=cf.ButtonRed, font="Arial 10 bold") # Red text
cf.root.style.configure("A12B.TLabel", foreground=COLORcanvas, font="Arial 12 bold") # Black text
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
    cf.TCursor = event.x # Cursor Horizontal
    cf.VCursor = event.y # Cursor Vertikal ( V oder mA)
    if cf.RUNstatus.get() == 0: # Testweise
        UpdateTimeScreen()


#--- Setzen von Markern via Maus-Linksklick, deren xy-Koordinaten grün im Scanbild erscheinen
#--- funktioniert nur im Stopp-Modus
def onCanvasClickLeft(event):
    global PrevV, PrevT
    try:
        cf.HoldOff = float(eval(cf.HoldOffentry.get()))
        if cf.HoldOff < 0:
            cf.HoldOff = 0
    except:
        cf.HoldOffentry.delete(0,tk.END)
        cf.HoldOffentry.insert(0, cf.HoldOff)
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
        # aktuelle Vertikalskalierungen und -offsets auslesen !! Ohne try/excpet wie in aliceTimeFunc
        CHAVScale = float(eval(cf.CHAsb.get()))
        CHBVScale = float(eval(cf.CHBsb.get()))
        CHAIScale = float(eval(cf.CHAIsb.get()))
        CHBIScale = float(eval(cf.CHBIsb.get()))
        CHAVOffset = float(eval(cf.CHAVPosEntry.get()))           
        CHAIOffset = float(eval(cf.CHAIPosEntry.get()))
        CHBVOffset = float(eval(cf.CHBVPosEntry.get()))
        CHAIOffset = float(eval(cf.CHBIPosEntry.get()))

        # prevent divide by zero error
        if CHAVScale < 0.001:
            CHAVScale = 0.001
        if CHBVScale < 0.001:
            CHBVScale = 0.001
        if CHAIScale < 1.0:
            CHAIScale = 1.0
        if CHBIScale < 1.0:
            CHBIScale = 1.0
        Yoffset1 = CHAVOffset
        if cf.ShowCur.get() == 1:
            Yconv1 = float(cf.GRH/10.0) / CHAVScale
            Yoffset1 = CHAVOffset
            COLORmarker = cf.COLORtrace1
            Units = " V"
        elif cf.ShowCur.get() == 2:
            Yconv1 = float(cf.GRH/10.0) / CHBVScale
            Yoffset1 = CHBVOffset
            COLORmarker = cf.COLORtrace2
            Units = " V"
        elif cf.ShowCur.get() == 3:
            Yconv1 = float(cf.GRH/10.0) / CHAIScale
            Yoffset1 = CHAIOffset
            COLORmarker = cf.COLORtrace3
            Units = " mA"
        elif cf.ShowCur.get() == 4:
            Yconv1 = float(cf.GRH/10.0) / CHBIScale
            Yoffset1 = CHAIOffset
            COLORmarker = cf.COLORtrace4
            Units = " mA"
            
        c1 = cf.GRH / 2.0 + cf.Y0T    # fixed correction channel A
        # draw X at marker point and number
        cf.ca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=cf.COLORtext)
        cf.ca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=cf.COLORtext)
        Tstep = (10.0 * cf.TIMEdiv) / cf.GRW # time in mS per pixel
        Tpoint = ((event.x-cf.X0L) * Tstep) + cf.HoldOff

        Tpoint = Tpoint
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
        if cf.MarkerScale.get() == 1 or cf.MarkerScale.get() == 2:
            V1String = ' {0:.3f} '.format(-yvolts)
        else:
            V1String = ' {0:.1f} '.format(-yvolts)
        V_label = str(cf.MarkerNum) + " " + TString + V1String
        V_label = V_label + Units
        if cf.MarkerNum > 1:
            if cf.MarkerScale.get() == 1 or cf.MarkerScale.get() == 2:
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
            DFreq = ' {0:.3f} '.format(1.0/(Tpoint-PrevT))
            V_label = V_label + " Delta " + DeltaT + DeltaV
            V_label = V_label + Units
            V_label = V_label + ", Freq " + DFreq + " KHz"
        # place in upper left unless specified otherwise
        x = cf.X0L + 5
        y = cf.Y0T + 3 + (cf.MarkerNum*12)
        Justify = 'w'
        cf.ca.create_text(event.x+4, event.y, text=str(cf.MarkerNum), fill=cf.COLORtext, anchor=Justify, font=("arial", cf.FontSize ))
        cf.ca.create_text(x, y, text=V_label, fill=COLORmarker, anchor=Justify, font=("arial", cf.FontSize ))
        PrevV = yvolts
        PrevT = Tpoint

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


def onCanvasMouse_xy(event):
    cf.MouseWidget = event.widget
    cf.MouseX, cf.MouseY = event.x, event.y
    
def onCAresize(event):
    cf.XOL = cf.FontSize * 7
    cf.CANVASwidth = event.width - 4
    cf.CANVASheight = event.height - 4
    cf.GRW = cf.CANVASwidth - (2 * cf.X0L) # new grid width
    cf.GRH = cf.CANVASheight - (cf.Y0T + (cf.FontSize * 10))   # new grid height, 10 Fontgrößen Raum für Darstellungen Messwerte u.A.
    UpdateTimeAll()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# M1K Spezifisches
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#DevID = "No Device" # Initialisierung

def ConSingDev():
    logging.info('ConSingDev()')
    global PIO_0, PIO_1, PIO_2, PIO_3, PIO_4, PIO_5, PIO_6, PIO_7
    if cf.DevID == "No Device":
        cf.session = smu.Session(ignore_dataflow=True, sample_rate=cf.SAMPLErate, queue_size=cf.MaxSamples)
        if not cf.session.devices:
            tkm.showwarning("WARNING","No Device Plugged In!")
            cf.DevID = "No Device"
            FWRevOne = 0.0
            m1kcon.configure(text="M1K", style="RConn.TButton")
            return
        cf.session.configure(sample_rate=cf.SAMPLErate)
        print("Session sample rate: " + str(cf.session.sample_rate))      
        cf.devx = cf.session.devices[0] 
        cf.DevID = cf.devx.serial
        print("Device ID:" + str(cf.DevID))
        FWRevOne = float(cf.devx.fwver)

        HWRevOne = str(cf.devx.hwver)
        print( FWRevOne, HWRevOne)   
        if FWRevOne < 2.17:
            tkm.showwarning("WARNING","This ALICE version Requires Firmware version > 2.16")
        cf.CHA = cf.devx.channels['A']    # Open CHA
        cf.CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        cf.CHB = cf.devx.channels['B']    # Open CHB
        cf.CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode  
        # Hier unterscheiden sich die beiden Hardware-Revisions
        cf.devx.set_adc_mux(0)
        if cf.devx.hwver == "F":
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
        cf.devx.set_adc_mux(0)
        cf.devx.ctrl_transfer(0x40, 0x24, 0x0, 0, 0, 0, 100) # set to addr DAC A 
        cf.devx.ctrl_transfer(0x40, 0x25, 0x1, 0, 0, 0, 100) # set not addr DAC B
        try:
            cf.session.start(0) # Start kontinuierlicher Modus des M1K
            cf.devx.set_led(0b010) # set LED.green
            m1kcon.configure(text="M1K", style="GConn.TButton")
        except:
            tkm.showwarning("M1K could not be connected.")
        

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funktionen UI
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
# Toggle the Background and text colors based on ColorMode
def BgColor():
    global COLORcanvas
    if cf.ColorMode.get() > 0:
        cf.COLORtext = "#000000"   # 100% black
        cf.COLORtrace4 = "#a0a000" # 50% yellow
        cf.COLORtraceR4 = "#606000"   # 25% yellow
        COLORcanvas = "#ffffff"     # 100% white
    else:
        COLORcanvas = "#000000"   # 100% black
        cf.COLORtrace4 = "#ffff00" # 100% yellow
        cf.COLORtraceR4 = "#808000"   # 50% yellow
        cf.COLORtext = "#ffffff"     # 100% white
    cf.ca.config(background=COLORcanvas)
    UpdateTimeScreen()

# Save scope cf.canvas as encapsulated postscript file
# To do: in PNG ändern
def BSaveScreen():
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")])
    Orient = tkm.askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n")
    if cf.MarkerNum > 0 or cf.ColorMode.get() > 0:
        cf.ca.postscript(file=filename, height=cf.CANVASheight, width=cf.CANVASwidth, colormode='color', rotate=Orient)
    else:    # temp chnage text corlor to black
        cf.COLORtext = "#000000"
        UpdateTimeScreen()
        # first save postscript file
        cf.ca.postscript(file=filename, height=cf.CANVASheight, width=cf.CANVASwidth, colormode='color', rotate=Orient)
        # now convert to bit map
        #img = Image.open("screen_shot.eps")
        #img.save("screen_shot.gif", "gif")
        cf.COLORtext = "#ffffff"
        UpdateTimeScreen()

## Save scope all time array data to file
def BSaveData():
    # open file to save data
    filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
    DataFile = open(filename, 'w')
    DataFile.write( 'Sample-#, CA-V, CA-I, CB-V, CB-I \n' )
    for index in range(len(cf.VBuffA)):
        TimePnt = float((index+0.0)/cf.SAMPLErate)
        DataFile.write( str(TimePnt) + ', ' + str(cf.VBuffA[index]) + ', ' + str(cf.IBuffA[index]) + ', '
                        + str(cf.VBuffB[index]) + ', ' + str(cf.IBuffB[index]) + '\n')
    DataFile.close()
 
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
        cf.session.tk.END() # Add this to turn off outputs after first tiem loading a config? 
        BTime()
    except:
        print( "Config File Not Found.")
    UpdateTimeTrace()

# Function to close and exit ALICE
def Bcloseexit():
    cf.RUNstatus.set(0)
    # BSaveConfig("alice-last-config.cfg")
    try:
        cf.devx.set_led(0b100) # LED auf Blau setzen
        # Put channels in Hi-Z and exit
        cf.CHA.mode = smu.Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        cf.CHB.mode = smu.Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
        cf.devx.set_adc_mux(0) # set ADC mux conf to default
        cf.AWG_2X(0)
        #BAWG2X()
        cf.CHA.constant(0.0)
        cf.CHB.constant(0.0)
    except:
        pass
    cf.root.destroy()
    exit()

def donothing():
    pass

#==============================================================================
#==============================================================================
#Eigentliches Hauptprogramm, das das Scopefenster aufbaut.
#==============================================================================
#==============================================================================
cf.root.geometry('1400x800+0+0') # Größe und xy-Position Fenster beim Start
cf.root.protocol("WM_DELETE_WINDOW", Bcloseexit)
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
Triggermenu.menu.add_checkbutton(label='Manual Trgger', variable=cf.ManualTrigger)
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

hldlab = ttk.Label(frame1, text="Hold Off (ms):")
hldlab.pack(side=tk.LEFT)
cf.HoldOffentry = tk.Entry(frame1, width=4)
cf.HoldOffentry.bind("<Return>", BHoldOff)
cf.HoldOffentry.pack(side=tk.LEFT)
cf.HoldOffentry.delete(0,tk.END)
cf.HoldOffentry.insert(0,0.0)

hint = ttk.Label(frame1, text=" at numeric inputs \n press <Return> to confirm")
hint.pack(side=tk.LEFT, padx=(20,0))

Triggermenu_tip = CreateToolTip(Triggermenu, 'Triggerquelle')
Edgemenu_tip = CreateToolTip(Edgemenu, 'Triggerflanke')
Triglevel_tip = CreateToolTip(cf.TRIGGERentry, 'Triggerschwelle')
tgb_tip = CreateToolTip(tgb, 'Triggerschwelle auf 50 % setzen')
hldlab_tip = CreateToolTip(hldlab, 'Increment Hold Off setting by one time division')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Oszistatus Menü
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
bexit = ttk.Button(frame1, text="Exit", style="W4.TButton", command=Bcloseexit)
bexit.pack(side=tk.RIGHT)
bstop = ttk.Button(frame1, text="Stop", style="Stop.TButton", command=BStop)
bstop.pack(side=tk.RIGHT)
brun = ttk.Button(frame1, text="Run", style="Run.TButton", command=BStart)
brun.pack(side=tk.RIGHT)
# M1K Connect action and status
m1kcon = ttk.Button(frame1, text="M1K", style="RConn.TButton", command=ConSingDev)
m1kcon.pack(side=tk.RIGHT)

bexit_tip = CreateToolTip(bexit, 'Anwendung schließen')
bstop_tip = CreateToolTip(bstop, 'Stop Datenaufnahme')
brun_tip = CreateToolTip(brun, 'Start Datenaufnahme')
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

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Horizontal Menü: Time per Div
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
cf.TMsb = tk.Spinbox(frame1, width=5, values= TMpdiv, command=BTime)
cf.TMsb.bind('<MouseWheel>', onSpinBoxScroll)
cf.TMsb.pack(side=tk.RIGHT, padx=(0,16))
cf.TMsb.delete(0,tk.END)
cf.TMsb.insert(0,0.5)
cf.TMlab = ttk.Label(frame1, text="Time ms/Div:")
cf.TMlab.pack(side=tk.RIGHT)

cf.HozPossentry = tk.Entry(frame1, width=4)
cf.HozPossentry.bind("<Return>", BHozPoss)
cf.HozPossentry.pack(side=tk.RIGHT)
cf.HozPossentry.delete(0,tk.END)
cf.HozPossentry.insert(0,0.0)
hozlab = ttk.Label(frame1, text="Horz Pos (ms):")
hozlab.pack(side=tk.RIGHT)

hozlab_tip = CreateToolTip(hozlab, 'When triggering, set trigger point to center of screen')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Anzeigebereich für Traces
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Canvas (Anzeigebereich der Signale in frame2)
cf.ca = tk.Canvas(frame2, width=cf.CANVASwidth, height=cf.CANVASheight, background=COLORcanvas, cursor='cross')
# add mouse left and right button click to cf.canvas
cf.ca.bind('<Configure>', onCAresize)
cf.ca.bind('<1>', onCanvasClickLeft)
cf.ca.bind('<3>', onCanvasClickRight)
cf.ca.bind("<Motion>",onCanvasMouse_xy)
cf.ca.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
cf.MouseWidget = cf.ca


# right side menu buttons
dropmenu1 = ttk.Frame(frame2r)
dropmenu1.pack(side=tk.TOP)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# File menu
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Filemenu = ttk.Menubutton(dropmenu1, text="File", style="W4.TButton")
Filemenu.menu = tk.Menu(Filemenu, tearoff = 0 )
Filemenu["menu"] = Filemenu.menu
Filemenu.menu.add_command(label="Load Config", command=BLoadConfig)
Filemenu.menu.add_command(label="Save Screen", command=BSaveScreen)
Filemenu.menu.add_command(label="Save To CSV", command=BSaveData)
Filemenu.pack(side=tk.LEFT, anchor=tk.W)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Options Menu
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Optionmenu = ttk.Menubutton(dropmenu1, text="Options", style="W7.TButton")
Optionmenu.menu = tk.Menu(Optionmenu, tearoff = 0 )
Optionmenu["menu"]  = Optionmenu.menu
Optionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
Optionmenu.menu.add_command(label='Set Sample Rate', command=MakeSampleRateMenu)
Optionmenu.menu.add_checkbutton(label='Smooth', variable=cf.SmoothCurves, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Z-O-Hold', variable=cf.ZOHold, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Trace Avg [a]', variable=cf.TRACEmodeTime)
Optionmenu.menu.add_radiobutton(label='Black BG', variable=cf.ColorMode, value=0, command=BgColor)
Optionmenu.menu.add_radiobutton(label='White BG', variable=cf.ColorMode, value=1, command=BgColor)
Optionmenu.pack(side=tk.LEFT, anchor=tk.W)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Measurments und Math menu
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#--- Drop Down Menü zur Auswahl der Messungen CHA
dropmenu2 = ttk.Frame(frame2r)
dropmenu2.pack(side=tk.TOP, pady=(0,8))
measlab = ttk.Label(dropmenu2, text="Meas")
measlab.pack(side=tk.LEFT, anchor=tk.W)
MeasmenuA = ttk.Menubutton(dropmenu2, text="CA", style="W3.TButton")
MeasmenuA.menu = tk.Menu(MeasmenuA, tearoff = 0 )
MeasmenuA["menu"]  = MeasmenuA.menu
MeasmenuA.menu.add_command(label="-CA-V-Verical-", foreground="blue", command=donothing)
MeasmenuA.menu.add_checkbutton(label='Avg', variable=cf.MeasDCV1)
MeasmenuA.menu.add_checkbutton(label='Min', variable=cf.MeasMinV1)
MeasmenuA.menu.add_checkbutton(label='Max', variable=cf.MeasMaxV1)
MeasmenuA.menu.add_checkbutton(label='P-P', variable=cf.MeasPPV1)
MeasmenuA.menu.add_checkbutton(label='RMS', variable=cf.MeasRMSV1)
MeasmenuA.menu.add_separator()
MeasmenuA.menu.add_command(label="-CA-I-Vertical", foreground="blue", command=donothing)
MeasmenuA.menu.add_checkbutton(label='Avg', variable=cf.MeasDCI1)
MeasmenuA.menu.add_checkbutton(label='Min', variable=cf.MeasMinI1)
MeasmenuA.menu.add_checkbutton(label='Max', variable=cf.MeasMaxI1)
MeasmenuA.menu.add_checkbutton(label='P-P', variable=cf.MeasPPI1)
MeasmenuA.menu.add_checkbutton(label='RMS', variable=cf.MeasRMSI1)
MeasmenuA.menu.add_separator()
MeasmenuA.menu.add_command(label="-CA-Horizontal-", foreground="blue", command=donothing)
MeasmenuA.menu.add_checkbutton(label='Period', variable=cf.MeasAPER)
MeasmenuA.menu.add_checkbutton(label='Freq', variable=cf.MeasAFREQ)
MeasmenuA.pack(side=tk.LEFT)
#--- Drop Down Menü zur Auswahl der Messungen CHB
MeasmenuB = ttk.Menubutton(dropmenu2, text="CB", style="W3.TButton")
MeasmenuB.menu = tk.Menu(MeasmenuB, tearoff = 0 )
MeasmenuB["menu"]  = MeasmenuB.menu
MeasmenuB.menu.add_command(label="-CB-V-Vertical-", foreground="blue", command=donothing)
MeasmenuB.menu.add_checkbutton(label='Avg', variable=cf.MeasDCV2)
MeasmenuB.menu.add_checkbutton(label='Min', variable=cf.MeasMinV2)
MeasmenuB.menu.add_checkbutton(label='Max', variable=cf.MeasMaxV2)
MeasmenuB.menu.add_checkbutton(label='P-P', variable=cf.MeasPPV2)
MeasmenuB.menu.add_checkbutton(label='RMS', variable=cf.MeasRMSV2)
MeasmenuB.menu.add_separator()
MeasmenuB.menu.add_command(label="-CB-I-Vertical-", foreground="blue", command=donothing)
MeasmenuB.menu.add_checkbutton(label='Avg', variable=cf.MeasDCI2)
MeasmenuB.menu.add_checkbutton(label='Min', variable=cf.MeasMinI2)
MeasmenuB.menu.add_checkbutton(label='Max', variable=cf.MeasMaxI2)
MeasmenuB.menu.add_checkbutton(label='P-P', variable=cf.MeasPPI2)
MeasmenuB.menu.add_checkbutton(label='RMS', variable=cf.MeasRMSI2)
MeasmenuB.menu.add_separator()
MeasmenuB.menu.add_command(label="-CB-Horizontal-", foreground="blue", command=donothing)
MeasmenuB.menu.add_checkbutton(label='Period', variable=cf.MeasBPER)
MeasmenuB.menu.add_checkbutton(label='Freq', variable=cf.MeasBFREQ)
MeasmenuB.pack(side=tk.LEFT)

mathbt = ttk.Button(dropmenu2, text="Math", style="Math.TButton", command = MakeMathMenu)
mathbt.pack(side=tk.RIGHT, anchor=tk.W)

math_tip = CreateToolTip(mathbt, 'Open Math window')

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Menü zur Anzeige der Traces
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
curvelab = ttk.Label(frame2r, text="Active Channel")
curvelab.pack(side=tk.TOP, pady=(8,0))
curvecheckb = ttk.Frame(frame2r)
curvecheckb.pack(side=tk.TOP)
ckbt1 = ttk.Checkbutton(curvecheckb, text='CA-V', style="Strace1.TCheckbutton", variable=cf.ShowC1_V, command=TraceSelectADC_Mux)
ckbt1.grid(row=0, column=0)
ckbt2 = ttk.Checkbutton(curvecheckb, text='CA-I', style="Strace3.TCheckbutton", variable=cf.ShowC1_I, command=TraceSelectADC_Mux)
ckbt2.grid(row=0, column=1)
ckbt3 = ttk.Checkbutton(curvecheckb, text='CB-V', style="Strace2.TCheckbutton", variable=cf.ShowC2_V, command=TraceSelectADC_Mux)
ckbt3.grid(row=1, column=0)
ckbt4 = ttk.Checkbutton(curvecheckb, text='CB-I', style="Strace4.TCheckbutton", variable=cf.ShowC2_I, command=TraceSelectADC_Mux)
ckbt4.grid(row=1, column=1)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Gain-/Offsetkorrektur für V und I der beiden Kanäle (Fenster rechts)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
prlab = ttk.Label(frame2r, text="Adjust Gain / Offset")
prlab.pack(side=tk.TOP, pady=(8,0))
ProbeA = ttk.Frame(frame2r)
ProbeA.pack(side=tk.TOP)
gain1lab = ttk.Label(ProbeA, text="CA-V")
gain1lab.pack(side=tk.LEFT)

cf.CHAVGainEntry = tk.Entry(ProbeA, width=5)
cf.CHAVGainEntry.bind('<Return>', onTextKey)
cf.CHAVGainEntry.pack(side=tk.LEFT)
cf.CHAVGainEntry.delete(0,tk.END)
cf.CHAVGainEntry.insert(0,1.0)

cf.CHAVOffsetEntry = tk.Entry(ProbeA, width=5)
cf.CHAVOffsetEntry.bind('<Return>', onTextKey)
cf.CHAVOffsetEntry.pack(side=tk.LEFT)
cf.CHAVOffsetEntry.delete(0,tk.END)
cf.CHAVOffsetEntry.insert(0,0.0)

ProbeB = ttk.Frame( frame2r )
ProbeB.pack(side=tk.TOP)
gain2lab = ttk.Label(ProbeB, text="CB-V")
gain2lab.pack(side=tk.LEFT)

cf.CHBVGainEntry = tk.Entry(ProbeB, width=5)
cf.CHBVGainEntry.bind('<Return>', onTextKey)
cf.CHBVGainEntry.pack(side=tk.LEFT)
cf.CHBVGainEntry.delete(0,tk.END)
cf.CHBVGainEntry.insert(0,1.0)

cf.CHBVOffsetEntry = tk.Entry(ProbeB, width=5)
cf.CHBVOffsetEntry.bind('<Return>', onTextKey)
cf.CHBVOffsetEntry.pack(side=tk.LEFT)
cf.CHBVOffsetEntry.delete(0,tk.END)
cf.CHBVOffsetEntry.insert(0,0.0)

ProbeAI = ttk.Frame( frame2r )
ProbeAI.pack(side=tk.TOP)
gainailab = ttk.Label(ProbeAI, text="CA-I")
gainailab.pack(side=tk.LEFT)

cf.CHAIGainEntry = tk.Entry(ProbeAI, width=5)
cf.CHAIGainEntry.bind('<Return>', onTextKey)
cf.CHAIGainEntry.pack(side=tk.LEFT)
cf.CHAIGainEntry.delete(0,tk.END)
cf.CHAIGainEntry.insert(0,1.0)

cf.CHAIOffsetEntry = tk.Entry(ProbeAI, width=5)
cf.CHAIOffsetEntry.bind('<Return>', onTextKey)
cf.CHAIOffsetEntry.pack(side=tk.LEFT)
cf.CHAIOffsetEntry.delete(0,tk.END)
cf.CHAIOffsetEntry.insert(0,0.0)

ProbeBI = ttk.Frame( frame2r )
ProbeBI.pack(side=tk.TOP)
gainbilab = ttk.Label(ProbeBI, text="CB-I")
gainbilab.pack(side=tk.LEFT)

cf.CHBIGainEntry = tk.Entry(ProbeBI, width=5)
cf.CHBIGainEntry.bind('<Return>', onTextKey)
cf.CHBIGainEntry.pack(side=tk.LEFT)
cf.CHBIGainEntry.delete(0,tk.END)
cf.CHBIGainEntry.insert(0,1.0)

cf.CHBIOffsetEntry = tk.Entry(ProbeBI, width=5)
cf.CHBIOffsetEntry.bind('<Return>', onTextKey)
cf.CHBIOffsetEntry.pack(side=tk.LEFT)
cf.CHBIOffsetEntry.delete(0,tk.END)
cf.CHBIOffsetEntry.insert(0,0.0)

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

MakeAWGMenuInside()

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Vertikaleinstellungen Gain und Offset für V und I der beiden Kanäle
# Boxen unterhalb Oszibild
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Voltage channel A: Verschiedene V/Div - Werte siehe CHvpdiv
CHAlab = ttk.Label(frame3, text="CA V/Div:", background=cf.COLORtrace1)
CHAlab.pack(side=tk.LEFT)
cf.CHAsb = tk.Spinbox(frame3, width=4, values=CHvpdiv, command=BCHAlevel)
cf.CHAsb.bind('<MouseWheel>', onSpinBoxScroll)
cf.CHAsb.pack(side=tk.LEFT)
cf.CHAsb.delete(0,tk.END)
cf.CHAsb.insert(0,0.5)
CHAofflab = ttk.Label(frame3, text="CA-V Pos:", background=cf.COLORtrace1)
CHAofflab.pack(side=tk.LEFT) # rechts neben Widget 6 Pixel Abstand
cf.CHAVPosEntry = tk.Entry(frame3, width=5)
cf.CHAVPosEntry.bind("<Return>", BOffsetA)
cf.CHAVPosEntry.pack(side=tk.LEFT, padx=(0,8))
cf.CHAVPosEntry.delete(0,tk.END)
cf.CHAVPosEntry.insert(0,2.5)

# Current channel A: Verschiedene A/Div - Werte siehe CHipdiv
cf.CHAIsb = tk.Spinbox(frame3, width=4, values=CHipdiv, command=BCHAIlevel)
cf.CHAIsb.bind('<MouseWheel>', onSpinBoxScroll)
cf.CHAIsb.pack(side=tk.LEFT)
cf.CHAIsb.delete(0,tk.END)
cf.CHAIsb.insert(0,50.0)
CHAIlab = ttk.Label(frame3, text="CA mA/Div", background=cf.COLORtrace3)
CHAIlab.pack(side=tk.LEFT)
cf.CHAIPosEntry = tk.Entry(frame3, width=5)
cf.CHAIPosEntry.bind("<Return>", BIOffsetA)
cf.CHAIPosEntry.pack(side=tk.LEFT)
cf.CHAIPosEntry.delete(0,tk.END)
cf.CHAIPosEntry.insert(0,0.0)
CHAIofflab = ttk.Label(frame3, text="CA-I Pos", background=cf.COLORtrace3)
CHAIofflab.pack(side=tk.LEFT, padx=(0,8))

# Voltage channel B:
cf.CHBsb = tk.Spinbox(frame3, width=4, values=CHvpdiv, command=BCHBlevel)
cf.CHBsb.bind('<MouseWheel>', onSpinBoxScroll)
cf.CHBsb.pack(side=tk.LEFT)
cf.CHBsb.delete(0,tk.END)
cf.CHBsb.insert(0,0.5)
CHBlab = ttk.Label(frame3, text="CB V/Div", background=cf.COLORtrace2)
CHBlab.pack(side=tk.LEFT)
cf.CHBVPosEntry = tk.Entry(frame3, width=5)
cf.CHBVPosEntry.bind("<Return>", BOffsetB)
cf.CHBVPosEntry.pack(side=tk.LEFT)
cf.CHBVPosEntry.delete(0,tk.END)
cf.CHBVPosEntry.insert(0,2.5)
CHBofflab = ttk.Label(frame3, text="CB-V Pos", background=cf.COLORtrace2)
CHBofflab.pack(side=tk.LEFT, padx=(0,8))

# Current channel B:
cf.CHBIsb = tk.Spinbox(frame3, width=4, values=CHipdiv, command=BCHBIlevel)
cf.CHBIsb.bind('<MouseWheel>', onSpinBoxScroll)
cf.CHBIsb.pack(side=tk.LEFT)
cf.CHBIsb.delete(0,tk.END)
cf.CHBIsb.insert(0,50.0)
CHBIlab = ttk.Label(frame3, text="CB mA/Div", background=cf.COLORtrace4)
CHBIlab.pack(side=tk.LEFT)
cf.CHBIPosEntry = tk.Entry(frame3, width=5)
cf.CHBIPosEntry.bind("<Return>", BIOffsetB)
cf.CHBIPosEntry.pack(side=tk.LEFT)
cf.CHBIPosEntry.delete(0,tk.END)
cf.CHBIPosEntry.insert(0,0.0)
CHBIofflab = ttk.Label(frame3, text="CB-I Pos", background=cf.COLORtrace4)
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


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Hauptroutine
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
ConSingDev() # Connect a single (only one connected) M1K device
#BLoadConfig("default-config.cfg") # load default configuration
cf.root.update() # Activate updated screens  
Analog_In() # Start sampling