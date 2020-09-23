#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 22.9.20
"""

import tkinter as tk
import tkinter.ttk as ttk # nötig für Widget Styles
#import platform
from aliceAwgFunc import UpdateAwgCont
from aliceAwgFunc import UpdateAWGA
from aliceAwgFunc import UpdateAWGB
import config as cf
import logging

## Tool Tip Ballon help stuff
class CreateToolTip(object):
    ## create a tooltip for a given widget
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 100   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
    ## Action when mouse enters
    def enter(self, event=None):
        self.schedule()
    ## Action when mouse leaves
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
    ## Sehedule Action
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)
    ## Un-schedule Action
    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
    ## Display Tip Text
    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx()  # x-Position Tooltip war + 25
        y += self.widget.winfo_rooty() + 20 # war 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = ttk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)
    ## Hide Tip Action
    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()


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

MathScreenStatus = tk.IntVar(0)
SampleRateStatus = tk.IntVar(0)
SampleRatewindow = None


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Tkinter Callback-Funktionen
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def onSettingsTextKey(event):
    logging.debug('onSettingsTextKey()')
    UpdateSettingsMenu()        

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter UI Menüs aufbauen
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#--- AWG Menü im Hauptfenster
def MakeAWGMenu():
    logging.debug('MakeAWGMenu()')
    global amp1lab, amp2lab, off1lab, off2lab
    # AWGA: Menü
    ModeAMenu = ttk.Menubutton(cf.AWGAMenus, text="Mode", style="W5.TButton")
    ModeAMenu.menu = tk.Menu(ModeAMenu, tearoff = 0 )
    ModeAMenu["menu"] = ModeAMenu.menu
    # 0 muss übergeben werden, da UpdateAwgCont() unten für Entrys benutzt wird, die Event übergeben
    ModeAMenu.menu.add_radiobutton(label="SVMI", variable=cf.AWGAMode, value=0, command=UpdateAwgCont) 
    ModeAMenu.menu.add_radiobutton(label="SIMV", variable=cf.AWGAMode, value=1, command=UpdateAwgCont) 
    ModeAMenu.menu.add_radiobutton(label="Hi-Z", variable=cf.AWGAMode, value=2, command=UpdateAwgCont) 
    ModeAMenu.pack(side=tk.LEFT, anchor=tk.W)
    ShapeAMenu = ttk.Menubutton(cf.AWGAMenus, text="Shape", style="W6.TButton")
    ShapeAMenu.menu = tk.Menu(ShapeAMenu, tearoff = 0 )
    ShapeAMenu["menu"] = ShapeAMenu.menu
    ShapeAMenu.menu.add_radiobutton(label="DC", variable=cf.AWGAShape, value=0, command=UpdateAwgCont)
    ShapeAMenu.menu.add_radiobutton(label="Sine", variable=cf.AWGAShape, value=1, command=UpdateAwgCont)
    ShapeAMenu.menu.add_radiobutton(label="Triangle", variable=cf.AWGAShape, value=2, command=UpdateAwgCont)
    ShapeAMenu.menu.add_radiobutton(label="Sawtooth", variable=cf.AWGAShape, value=3, command=UpdateAwgCont)
    ShapeAMenu.menu.add_radiobutton(label="Square", variable=cf.AWGAShape, value=4, command=UpdateAwgCont)
    ShapeAMenu.menu.add_radiobutton(label="StairStep", variable=cf.AWGAShape, value=5, command=UpdateAwgCont)
    ShapeAMenu.pack(side=tk.LEFT, anchor=tk.W)
    # AWGA: Einstellung Min-/Maxwerte
    awg1ampl = ttk.Frame(cf.AWGASet)
    awg1ampl.pack(side=tk.TOP)
    cf.AWGAMinEntry = tk.Entry(awg1ampl, width=5)
    cf.AWGAMinEntry.bind("<Return>", UpdateAwgCont) # Update nur bei Return
    cf.AWGAMinEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGAMinEntry.delete(0,tk.END)
    cf.AWGAMinEntry.insert(0,0.0)
    amp1lab = ttk.Label(awg1ampl, text = "Min (V)" ) 
    amp1lab.pack(side=tk.LEFT, anchor=tk.W)
    awg1off = ttk.Frame(cf.AWGASet)
    awg1off.pack(side=tk.TOP)
    cf.AWGAMaxEntry = tk.Entry(awg1off, width=5)
    cf.AWGAMaxEntry.bind("<Return>", UpdateAwgCont)
    cf.AWGAMaxEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGAMaxEntry.delete(0,tk.END)
    cf.AWGAMaxEntry.insert(0,0.0)
    off1lab = ttk.Label(awg1off, text = "Max (V)")
    off1lab.pack(side=tk.LEFT, anchor=tk.W)
    # AWGA: Einstellung Frequenz
    awg1freq = ttk.Frame(cf.AWGASet)
    awg1freq.pack(side=tk.TOP)
    cf.AWGAFreqEntry = tk.Entry(awg1freq, width=7)
    cf.AWGAFreqEntry.bind("<Return>", UpdateAwgCont)
    cf.AWGAFreqEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGAFreqEntry.delete(0,tk.END)
    cf.AWGAFreqEntry.insert(0,100.0)
    freq1lab = ttk.Label(awg1freq, text="Freq (Hz)")
    freq1lab.pack(side=tk.LEFT, anchor=tk.W)   
    # AWGA: Einstellung Duty Cycle für Rechtecksignal
    awg1dc = ttk.Frame(cf.AWGASet)
    awg1dc.pack(side=tk.TOP)
    cf.AWGADutyCycleEntry = tk.Entry(awg1dc, width=5)
    cf.AWGADutyCycleEntry.bind("<Return>", UpdateAwgCont)
    cf.AWGADutyCycleEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGADutyCycleEntry.delete(0,tk.END)
    cf.AWGADutyCycleEntry.insert(0,50)
    duty1lab = ttk.Label(awg1dc, text="Duty Cycle (%)")
    duty1lab.pack(side=tk.LEFT, anchor=tk.W)
    # AWGB: Menü
    ModeBMenu = ttk.Menubutton(cf.AWGBMenus, text="Mode", style="W5.TButton")
    ModeBMenu.menu = tk.Menu(ModeBMenu, tearoff = 0 )
    ModeBMenu["menu"] = ModeBMenu.menu
    ModeBMenu.menu.add_radiobutton(label="SVMI", variable=cf.AWGBMode, value=0, command=UpdateAwgCont)
    ModeBMenu.menu.add_radiobutton(label="SIMV", variable=cf.AWGBMode, value=1, command=UpdateAwgCont)
    ModeBMenu.menu.add_radiobutton(label="Hi-Z", variable=cf.AWGBMode, value=2, command=UpdateAwgCont)
    ModeBMenu.pack(side=tk.LEFT, anchor=tk.W)
    ShapeBMenu = ttk.Menubutton(cf.AWGBMenus, text="Shape", style="W6.TButton")
    ShapeBMenu.menu = tk.Menu(ShapeBMenu, tearoff = 0 )
    ShapeBMenu["menu"] = ShapeBMenu.menu
    ShapeBMenu.menu.add_radiobutton(label="DC", variable=cf.AWGBShape, value=0, command=UpdateAwgCont)
    ShapeBMenu.menu.add_radiobutton(label="Sine", variable=cf.AWGBShape, value=1, command=UpdateAwgCont)
    ShapeBMenu.menu.add_radiobutton(label="Triangle", variable=cf.AWGBShape, value=2, command=UpdateAwgCont)
    ShapeBMenu.menu.add_radiobutton(label="Sawtooth", variable=cf.AWGBShape, value=3, command=UpdateAwgCont)
    ShapeBMenu.menu.add_radiobutton(label="Square", variable=cf.AWGBShape, value=4, command=UpdateAwgCont)
    ShapeBMenu.menu.add_radiobutton(label="StairStep", variable=cf.AWGBShape, value=5, command=UpdateAwgCont)
    ShapeBMenu.pack(side=tk.LEFT, anchor=tk.W)
    # AWGB: Einstellung Min-/Maxwerte
    awg2ampl = ttk.Frame(cf.AWGBSet)
    awg2ampl.pack(side=tk.TOP)
    cf.AWGBMinEntry = tk.Entry(awg2ampl, width=5)
    cf.AWGBMinEntry.bind("<Return>", UpdateAwgCont)
    cf.AWGBMinEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGBMinEntry.delete(0,tk.END)
    cf.AWGBMinEntry.insert(0,0.0)
    amp2lab = ttk.Label(awg2ampl, text = "Min (V)")
    amp2lab.pack(side=tk.LEFT, anchor=tk.W)
    awg2off = ttk.Frame(cf.AWGBSet)
    awg2off.pack(side=tk.TOP)
    cf.AWGBMaxEntry = tk.Entry(awg2off, width=5)
    cf.AWGBMaxEntry.bind("<Return>", UpdateAwgCont)
    cf.AWGBMaxEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGBMaxEntry.delete(0,tk.END)
    cf.AWGBMaxEntry.insert(0,0.0)
    off2lab = ttk.Label(awg2off, text = "Max (V)")
    off2lab.pack(side=tk.LEFT, anchor=tk.W)
    # AWGB: Einstellung Frequenz
    awg2freq = ttk.Frame(cf.AWGBSet)
    awg2freq.pack(side=tk.TOP)
    cf.AWGBFreqEntry = tk.Entry(awg2freq, width=7)
    cf.AWGBFreqEntry.bind("<Return>", UpdateAwgCont)
    cf.AWGBFreqEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGBFreqEntry.delete(0,tk.END)
    cf.AWGBFreqEntry.insert(0,100.0)
    freq2lab = ttk.Label(awg2freq, text="Freq (Hz)")
    freq2lab.pack(side=tk.LEFT, anchor=tk.W)    
    # AWGB: Einstellung Duty Cycle für Rechtecksignal
    awg2dc = ttk.Frame(cf.AWGBSet)
    awg2dc.pack(side=tk.TOP)
    cf.AWGBDutyCycleEntry = tk.Entry(awg2dc, width=5)
    cf.AWGBDutyCycleEntry.bind("<Return>", UpdateAwgCont)
    cf.AWGBDutyCycleEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGBDutyCycleEntry.delete(0,tk.END)
    cf.AWGBDutyCycleEntry.insert(0,50)
    duty2lab = ttk.Label(awg2dc, text="Duty Cycle (%)")
    duty2lab.pack(side=tk.LEFT, anchor=tk.W)
    awg2hint = ttk.Label(cf.AWGBSet, text="press <Return> to confirm" )
    awg2hint.pack(side=tk.TOP, pady = (10,0))  
    # Tooltips für die AWGs
    CreateToolTip(ModeAMenu, 'Funktion des Kanals A: Nur Sampeln (Hi-Z), AWG als Spannungsquelle (SVMI) oder Stromquelle (SIMV)')
    CreateToolTip(ShapeAMenu, 'Kurvenform des vom AWG Kanal A zu erzeugenden Signals (nur bei SVMI oder SIMV)')
    CreateToolTip(ModeBMenu, 'Funktion des Kanals B: Nur Sampeln (Hi-Z), AWG als Spannungsquelle (SVMI) oder Stromquelle (SIMV)')
    CreateToolTip(ShapeBMenu, 'Kurvenform des vom AWG Kanal B zu erzeugenden Signals (nur bei SVMI oder SIMV)')
    CreateToolTip(cf.AWGADutyCycleEntry, 'Tastverhälnis bei Auswahl Square (Rechtecksignal)')
    CreateToolTip(cf.AWGBDutyCycleEntry, 'Tastverhälnis bei Auswahl Square (Rechtecksignal)')
    
def UpdateAWGMenu():
    logging.debug('UpdateAWGMenu()')
    UpdateAWGA()
    UpdateAWGB()
    UpdateAwgCont()
#--- Ende AWG Menü im Hauptfenster


#--- Settings Menü im Unterfenster
def MakeSettingsMenu():
    logging.debug('MakeSettingsMenu()')
    global Settingswindow, TAvg, TwdthE, GwdthE
    global TrgLPFEntry
    if cf.SettingsStatus.get() == 0:
        cf.SettingsStatus.set(1)
        Settingswindow = tk.Toplevel()
        Settingswindow.title("Settings ")
        Settingswindow.resizable(False,False)
        Settingswindow.protocol("WM_DELETE_WINDOW", DestroySettingsMenu)
        frame1 = ttk.Frame(Settingswindow, borderwidth=5, relief=tk.RIDGE)
        frame1.grid(row=0, column=0, sticky=tk.W)
      
        Avglab = ttk.Label(frame1, text="Number Traces to Average", style= "A10B.TLabel")
        Avglab.grid(row=1, column=0, sticky=tk.W)
        AvgMode = ttk.Frame( frame1 )
        AvgMode.grid(row=1, column=1, sticky=tk.W)
        TAvg = tk.Entry(AvgMode, width=4)
        TAvg.bind("<Return>", onSettingsTextKey)
        #TAvg.bind('<Key>', onSettingsTextKey)
        TAvg.pack(side=tk.RIGHT)
        TAvg.delete(0,tk.END)
        TAvg.insert(0,cf.NAveTrace.get())
      
        Twdthlab = ttk.Label(frame1, text="Trace Width in Pixels", style= "A10B.TLabel")
        Twdthlab.grid(row=4, column=0, sticky=tk.W)
        TwdthMode = ttk.Frame( frame1 )
        TwdthMode.grid(row=4, column=1, sticky=tk.W)
        TwdthE = tk.Entry(TwdthMode, width=4)
        TwdthE.bind("<Return>", onSettingsTextKey)
        #TwdthE.bind('<Key>', onSettingsTextKey)
        TwdthE.pack(side=tk.RIGHT)
        TwdthE.delete(0,tk.END)
        TwdthE.insert(0,cf.TRACEwidth.get())
        
        Gwdthlab = ttk.Label(frame1, text="Grid Width in Pixels", style= "A10B.TLabel")
        Gwdthlab.grid(row=5, column=0, sticky=tk.W)
        GwdthMode = ttk.Frame( frame1 )
        GwdthMode.grid(row=5, column=1, sticky=tk.W)
        GwdthE = tk.Entry(GwdthMode, width=4)
        GwdthE.bind("<Return>", onSettingsTextKey)
        #GwdthE.bind('<Key>', onSettingsTextKey)
        GwdthE.pack(side=tk.RIGHT)
        GwdthE.delete(0,tk.END)
        GwdthE.insert(0,cf.GridWidth.get())
     
        trglpflab = ttk.Label(frame1, text="Trigger LPF Length", style= "A10B.TLabel")
        trglpflab.grid(row=6, column=0, sticky=tk.W)
        TrgLPFMode = ttk.Frame( frame1 )
        TrgLPFMode.grid(row=6, column=1, sticky=tk.W)
        TrgLPFEntry = tk.Entry(TrgLPFMode, width=4)
        TrgLPFEntry.bind("<Return>", onSettingsTextKey)
        #TrgLPFEntry.bind('<Key>', onSettingsTextKey)
        TrgLPFEntry.pack(side=tk.RIGHT)
        TrgLPFEntry.delete(0,tk.END)
        TrgLPFEntry.insert(0,cf.Trigger_LPF_length.get())
        
        hint = ttk.Label(frame1, text="press <Return> to confirm")
        hint.grid(row=7, column=0, sticky=tk.W)
       
        Settingsdismissbutton = ttk.Button(frame1, text="Close Window", style= "W12.TButton", command=DestroySettingsMenu)
        Settingsdismissbutton.grid(row=12, column=0, sticky=tk.W, pady=7)
        
        CreateToolTip(TrgLPFEntry, 'Tiefpassfilter für das Triggereingangssignal: Anzahl Samples über die gemittelt wird (2..8).')
        CreateToolTip(TAvg, 'Mittelung über mehrere Abtastperioden: Anzahl Perioden über die gemittelt wird (2...16).')
        
        
def UpdateSettingsMenu():
    logging.debug('UpdateSettingsMenu()')
    global Settingswindow, TAvg, TwdthE, GwdthE
    global TrgLPFEntry
    
    try:
        GW = int(eval(GwdthE.get()))
        if GW < 1:
            GW = 1
            GwdthE.delete(0,tk.END)
            GwdthE.insert(0, int(GW))
        if GW > 5:
            GW = 5
            GwdthE.delete(0,tk.END)
            GwdthE.insert(0, int(GW))
    except:
        GW = 1
        GwdthE.delete(0,tk.END)
        GwdthE.insert(0, GW)    
    cf.GridWidth.set(GW)

    try:
        T_length = int(eval(TrgLPFEntry.get()))
        if T_length < 2:
            T_length = 2
            TrgLPFEntry.delete(0,tk.END)
            TrgLPFEntry.insert(0, int(T_length))
        if T_length > 8:
            T_length = 8
            TrgLPFEntry.delete(0,tk.END)
            TrgLPFEntry.insert(0, int(T_length))
    except:
        T_length = 2
        TrgLPFEntry.delete(0,tk.END)
        TrgLPFEntry.insert(0, T_length)
    cf.Trigger_LPF_length.set(T_length)

    try:
        TW = int(eval(TwdthE.get()))
        if TW < 1:
            TW = 1
            TwdthE.delete(0,tk.END)
            TwdthE.insert(0, int(TW))
        if TW > 5:
            TW = 5
            TwdthE.delete(0,tk.END)
            TwdthE.insert(0, int(TW))
    except:
        TW = 1
        TwdthE.delete(0,tk.END)
        TwdthE.insert(0, TW)
    cf.TRACEwidth.set(TW)

    try:
        TA = int(eval(TAvg.get()))
        if TA < 2:
            TA = 2
            TAvg.delete(0,tk.END)
            TAvg.insert(0, int(TA))
        if TA > 16:
            TA = 16
            TAvg.delete(0,tk.END)
            TAvg.insert(0, int(TA))
    except:
        TA = 2
        TAvg.delete(0,tk.END)
        TAvg.insert(0, TA)
    cf.NAveTrace.set(TA)

def DestroySettingsMenu():
    logging.debug('DestroySettingsMenu()')
    global Settingswindow   
    cf.SettingsStatus.set(0)
    UpdateSettingsMenu()
    Settingswindow.destroy()
#--- Ende Settings Menü im Unterfenster 