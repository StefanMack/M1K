#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 29.8.20
"""

import tkinter as tk
import tkinter.ttk as ttk # nötig für Widget Styles
import tkinter.messagebox as tkm
import platform
import aliceM1kSamp as m1k
#from aliceM1kSamp import SetSampleRate, SetADC_Mux
from aliceAwgFunc import ReMakeAWGwaves, UpdateAwgCont
from aliceAwgFunc import UpdateAWGA
from aliceAwgFunc import UpdateAWGB
from aliceOsciFunc import UpdateTimeTrace
import config as cf

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
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
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
def onSpinBoxScroll(event): # Spin Boxes do this automatically in Python 3 apparently
    spbox = event.widget
    if event.delta > 0: # increment digit
        spbox.invoke('buttonup')
    else: # decrement digit
        spbox.invoke('buttondown')

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

def onSettingsTextKey(event):
    onTextKey(event)
    UpdateSettingsMenu()  
    
def onSrateScroll(event):
    onSpinBoxScroll(event)
    m1k.SetSampleRate()

def onRetSrate(event):
    m1k.SetSampleRate()
    
#def onTextKeyAWG(event): # Udate nur bei Return
#    onTextKey(event)
#    ReMakeAWGwaves()


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter UI Menüs aufbauen
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#--- AWG Menü im Hauptfenster
def MakeAWGMenuInside():
    global amp1lab, amp2lab, off1lab, off2lab
    # now AWG A

    ModeAMenu = ttk.Menubutton(cf.AWGAMenus, text="Mode", style="W5.TButton")
    ModeAMenu.menu = tk.Menu(ModeAMenu, tearoff = 0 )
    ModeAMenu["menu"] = ModeAMenu.menu
    ModeAMenu.menu.add_radiobutton(label="SVMI", variable=cf.AWGAMode, value=0, command=ReMakeAWGwaves)
    ModeAMenu.menu.add_radiobutton(label="SIMV", variable=cf.AWGAMode, value=1, command=ReMakeAWGwaves)
    ModeAMenu.menu.add_radiobutton(label="Hi-Z", variable=cf.AWGAMode, value=2, command=ReMakeAWGwaves)
    ModeAMenu.pack(side=tk.LEFT, anchor=tk.W)
    ShapeAMenu = ttk.Menubutton(cf.AWGAMenus, text="Shape", style="W6.TButton")
    ShapeAMenu.menu = tk.Menu(ShapeAMenu, tearoff = 0 )
    ShapeAMenu["menu"] = ShapeAMenu.menu
    ShapeAMenu.menu.add_radiobutton(label="DC", variable=cf.AWGAShape, value=0, command=ReMakeAWGwaves)
    ShapeAMenu.menu.add_radiobutton(label="Sine", variable=cf.AWGAShape, value=1, command=ReMakeAWGwaves)
    ShapeAMenu.menu.add_radiobutton(label="Triangle", variable=cf.AWGAShape, value=2, command=ReMakeAWGwaves)
    ShapeAMenu.menu.add_radiobutton(label="Sawtooth", variable=cf.AWGAShape, value=3, command=ReMakeAWGwaves)
    ShapeAMenu.menu.add_radiobutton(label="Square", variable=cf.AWGAShape, value=4, command=ReMakeAWGwaves)
    ShapeAMenu.menu.add_radiobutton(label="StairStep", variable=cf.AWGAShape, value=5, command=ReMakeAWGwaves)
    ShapeAMenu.pack(side=tk.LEFT, anchor=tk.W)

    # AWGA: Einstellung Min-/Maxwerte
    awg1ampl = ttk.Frame(cf.AWGASet)
    awg1ampl.pack(side=tk.TOP)
    cf.AWGAMinEntry = tk.Entry(awg1ampl, width=5)
    cf.AWGAMinEntry.bind("<Return>", UpdateAwgCont) # Update nur bei Return
    #cf.AWGAMinEntry.bind('<Key>', onTextKeyAWG)
    cf.AWGAMinEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGAMinEntry.delete(0,tk.END)
    cf.AWGAMinEntry.insert(0,0.0)
    amp1lab = ttk.Label(awg1ampl, text = "Min (V)" ) 
    amp1lab.pack(side=tk.LEFT, anchor=tk.W)
    awg1off = ttk.Frame(cf.AWGASet)
    awg1off.pack(side=tk.TOP)
    cf.AWGAMaxEntry = tk.Entry(awg1off, width=5)
    cf.AWGAMaxEntry.bind("<Return>", UpdateAwgCont)
    #cf.AWGAMaxEntry.bind('<Key>', onTextKeyAWG)
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
    #cf.AWGAFreqEntry.bind('<Key>', onTextKeyAWG)
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
    #cf.AWGADutyCycleEntry.bind('<Key>', onTextKeyAWG)
    cf.AWGADutyCycleEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGADutyCycleEntry.delete(0,tk.END)
    cf.AWGADutyCycleEntry.insert(0,50)
    duty1lab = ttk.Label(awg1dc, text="Duty Cycle (%)")
    duty1lab.pack(side=tk.LEFT, anchor=tk.W)

    # now AWG B
    ModeBMenu = ttk.Menubutton(cf.AWGBMenus, text="Mode", style="W5.TButton")
    ModeBMenu.menu = tk.Menu(ModeBMenu, tearoff = 0 )
    ModeBMenu["menu"] = ModeBMenu.menu
    ModeBMenu.menu.add_radiobutton(label="SVMI", variable=cf.AWGBMode, value=0, command=ReMakeAWGwaves)
    ModeBMenu.menu.add_radiobutton(label="SIMV", variable=cf.AWGBMode, value=1, command=ReMakeAWGwaves)
    ModeBMenu.menu.add_radiobutton(label="Hi-Z", variable=cf.AWGBMode, value=2, command=ReMakeAWGwaves)
    ModeBMenu.pack(side=tk.LEFT, anchor=tk.W)
    ShapeBMenu = ttk.Menubutton(cf.AWGBMenus, text="Shape", style="W6.TButton")
    ShapeBMenu.menu = tk.Menu(ShapeBMenu, tearoff = 0 )
    ShapeBMenu["menu"] = ShapeBMenu.menu
    ShapeBMenu.menu.add_radiobutton(label="DC", variable=cf.AWGBShape, value=0, command=ReMakeAWGwaves)
    ShapeBMenu.menu.add_radiobutton(label="Sine", variable=cf.AWGBShape, value=1, command=ReMakeAWGwaves)
    ShapeBMenu.menu.add_radiobutton(label="Triangle", variable=cf.AWGBShape, value=2, command=ReMakeAWGwaves)
    ShapeBMenu.menu.add_radiobutton(label="Sawtooth", variable=cf.AWGBShape, value=3, command=ReMakeAWGwaves)
    ShapeBMenu.menu.add_radiobutton(label="Square", variable=cf.AWGBShape, value=4, command=ReMakeAWGwaves)
    ShapeBMenu.menu.add_radiobutton(label="StairStep", variable=cf.AWGBShape, value=5, command=ReMakeAWGwaves)
    ShapeBMenu.pack(side=tk.LEFT, anchor=tk.W)

    # AWGB: Einstellung Min-/Maxwerte
    awg2ampl = ttk.Frame(cf.AWGBSet)
    awg2ampl.pack(side=tk.TOP)
    cf.AWGBMinEntry = tk.Entry(awg2ampl, width=5)
    cf.AWGBMinEntry.bind("<Return>", UpdateAwgCont)
    #cf.AWGBMinEntry.bind('<Key>', onTextKeyAWG)
    cf.AWGBMinEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGBMinEntry.delete(0,tk.END)
    cf.AWGBMinEntry.insert(0,0.0)
    amp2lab = ttk.Label(awg2ampl, text = "Min (V)")
    amp2lab.pack(side=tk.LEFT, anchor=tk.W)
    awg2off = ttk.Frame(cf.AWGBSet)
    awg2off.pack(side=tk.TOP)
    cf.AWGBMaxEntry = tk.Entry(awg2off, width=5)
    cf.AWGBMaxEntry.bind("<Return>", UpdateAwgCont)
    #cf.AWGBMaxEntry.bind('<Key>', onTextKeyAWG)
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
    #cf.AWGBFreqEntry.bind('<Key>', onTextKeyAWG)
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
    #cf.AWGBDutyCycleEntry.bind('<Key>', onTextKeyAWG)
    cf.AWGBDutyCycleEntry.pack(side=tk.LEFT, anchor=tk.W)
    cf.AWGBDutyCycleEntry.delete(0,tk.END)
    cf.AWGBDutyCycleEntry.insert(0,50)
    duty2lab = ttk.Label(awg2dc, text="Duty Cycle (%)")
    duty2lab.pack(side=tk.LEFT, anchor=tk.W)
    awg2hint = ttk.Label(cf.AWGBSet, text=" at numeric inputs \n press <Return> to confirm" )
    awg2hint.pack(side=tk.TOP, pady = (10,0))
    
    # Tooltips für die AWGs
    CreateToolTip(ModeAMenu, 'Hier die Fuktion des Kanals einstellen: Nur Sampeln (Hi-Z), AWG als Spannungsquelle (SVMI) oder Stromquelle (SIMV)')


def UpdateAWGMenu():
    UpdateAWGA()
    UpdateAWGB()
    ReMakeAWGwaves()
    


#--- Ende AWG Menü im Hauptfenster
    
#--- Samplingrate Menü im Unterfenster
def MakeSampleRateMenu():
    global SampleRatewindow, SampleRateStatus, BaseRatesb
    if (SampleRateStatus.get() == 0 and cf.DevID != "No Device"):
        SampleRateStatus.set(1)
        SampleRatewindow = tk.Toplevel()
        SampleRatewindow.title("Set Sample Rate ")
        SampleRatewindow.resizable(False,False)
        SampleRatewindow.protocol("WM_DELETE_WINDOW", DestroySampleRateMenu)
        frame1 = ttk.Frame(SampleRatewindow, borderwidth=5, relief=tk.RIDGE)
        frame1.grid(row=0, column=0, sticky=tk.W)
 
        BaseRATE = ttk.Frame(frame1)
        BaseRATE.grid(row=0, column=0, sticky=tk.W)
        baseratelab = ttk.Label(BaseRATE, text="Base Sample Rate", style="A10B.TLabel") #, font = "Arial 10 bold")
        baseratelab.pack(side=tk.LEFT)
        BaseRatesb = tk.Spinbox(BaseRATE, width=6, values=cf.SampRateList, command=m1k.SetSampleRate)
        BaseRatesb.bind('<MouseWheel>', onSrateScroll)
        BaseRatesb.bind("<Button-4>", onSrateScroll)# with Linux OS
        BaseRatesb.bind("<Button-5>", onSrateScroll)
        BaseRatesb.bind("<Return>", onRetSrate)
        BaseRatesb.pack(side=tk.LEFT)
        BaseRatesb.delete(0,tk.END)
        BaseRatesb.insert(0,cf.BaseSampleRate)
       
        twoX = ttk.Checkbutton(frame1, text="2x Sample Rate", variable=cf.Two_X_Sample, command=m1k.SetADC_Mux)
        twoX.grid(row=1, column=0, sticky=tk.W)

        ## Mux Modus 0 ist nötig für VA und VB mit 200.000 S/s
        ## Hier wird der ADC_Mux_Mode eingestellt, je nachdem welche Knöpfe (VA, VB, IA, IB) vom Benutzer aktiviert sind.
        muxlab1 = ttk.Label(frame1, text="Chose CHs for 2x", style="A10B.TLabel") #, font = "Arial 10 bold")
        muxlab1.grid(row=2, column=0, sticky=tk.W)
        chabuttons = ttk.Frame(frame1)
        chabuttons.grid(row=3, column=0, sticky=tk.W)
        muxrb1 = ttk.Radiobutton(chabuttons, text="VA and VB", variable=cf.ADC_Mux_Mode, value=0, command=m1k.SetADC_Mux ) #style="W8.TButton",
        muxrb1.pack(side=tk.LEFT)
        muxrb2 = ttk.Radiobutton(chabuttons, text="IA and IB", variable=cf.ADC_Mux_Mode, value=1, command=m1k.SetADC_Mux ) #style="W8.TButton",
        muxrb2.pack(side=tk.LEFT)
        chcbuttons = ttk.Frame(frame1)
        chcbuttons.grid(row=4, column=0, sticky=tk.W)
        muxrb5 = ttk.Radiobutton(chcbuttons, text="VA and IA", variable=cf.ADC_Mux_Mode, value=4, command=m1k.SetADC_Mux ) # style="W8.TButton",
        muxrb5.pack(side=tk.LEFT)
        muxrb6 = ttk.Radiobutton(chcbuttons, text="VB and IB", variable=cf.ADC_Mux_Mode, value=5, command=m1k.SetADC_Mux ) # style="W8.TButton",
        muxrb6.pack(side=tk.LEFT)
        chbbuttons = ttk.Frame(frame1)
        chbbuttons.grid(row=5, column=0, sticky=tk.W)
        muxrb3 = ttk.Radiobutton(chbbuttons, text="VA and IB", variable=cf.ADC_Mux_Mode, value=2, command=m1k.SetADC_Mux ) # style="W8.TButton",
        muxrb3.pack(side=tk.LEFT)
        muxrb4 = ttk.Radiobutton(chbbuttons, text="VB and IA", variable=cf.ADC_Mux_Mode, value=3, command=m1k.SetADC_Mux ) # style="W8.TButton",
        muxrb4.pack(side=tk.LEFT)
        
        sratedismissclbutton = ttk.Button(frame1, text="Close Window", style="W12.TButton", command=DestroySampleRateMenu)
        sratedismissclbutton.grid(row=6, column=0, sticky=tk.W, pady=7)
    else:
        tkm.showwarning("WARNING","No Device Plugged In!")
        return 

def DestroySampleRateMenu():
    global SampleRatewindow, SampleRateStatus   
    SampleRateStatus.set(0)
    SampleRatewindow.destroy()
#--- Ende Samplingrate Menü im Unterfenster

#--- Settings Menü im Unterfenster
def MakeSettingsMenu():
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
        TAvg.bind('<Key>', onSettingsTextKey)
        TAvg.pack(side=tk.RIGHT)
        TAvg.delete(0,tk.END)
        TAvg.insert(0,cf.TRACEaverage.get())
      
        Twdthlab = ttk.Label(frame1, text="Trace Width in Pixels", style= "A10B.TLabel")
        Twdthlab.grid(row=4, column=0, sticky=tk.W)
        TwdthMode = ttk.Frame( frame1 )
        TwdthMode.grid(row=4, column=1, sticky=tk.W)
        TwdthE = tk.Entry(TwdthMode, width=4)
        TwdthE.bind("<Return>", onSettingsTextKey)
        TwdthE.bind('<Key>', onSettingsTextKey)
        TwdthE.pack(side=tk.RIGHT)
        TwdthE.delete(0,tk.END)
        TwdthE.insert(0,cf.TRACEwidth.get())
        
        Gwdthlab = ttk.Label(frame1, text="Grid Width in Pixels", style= "A10B.TLabel")
        Gwdthlab.grid(row=5, column=0, sticky=tk.W)
        GwdthMode = ttk.Frame( frame1 )
        GwdthMode.grid(row=5, column=1, sticky=tk.W)
        GwdthE = tk.Entry(GwdthMode, width=4)
        GwdthE.bind("<Return>", onSettingsTextKey)
        GwdthE.bind('<Key>', onSettingsTextKey)
        GwdthE.pack(side=tk.RIGHT)
        GwdthE.delete(0,tk.END)
        GwdthE.insert(0,cf.GridWidth.get())
     
        trglpflab = ttk.Label(frame1, text="Trigger LPF Length", style= "A10B.TLabel")
        trglpflab.grid(row=6, column=0, sticky=tk.W)
        TrgLPFMode = ttk.Frame( frame1 )
        TrgLPFMode.grid(row=6, column=1, sticky=tk.W)
        TrgLPFEntry = tk.Entry(TrgLPFMode, width=4)
        TrgLPFEntry.bind("<Return>", onSettingsTextKey)
        TrgLPFEntry.bind('<Key>', onSettingsTextKey)
        TrgLPFEntry.pack(side=tk.RIGHT)
        TrgLPFEntry.delete(0,tk.END)
        TrgLPFEntry.insert(0,cf.Trigger_LPF_length.get())
       
        Settingsdismissbutton = ttk.Button(frame1, text="Close Window", style= "W12.TButton", command=DestroySettingsMenu)
        Settingsdismissbutton.grid(row=12, column=0, sticky=tk.W, pady=7)
    
def UpdateSettingsMenu():
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
        GwdthE.delete(0,tk.END)
        GwdthE.insert(0, cf.GridWidth.get())
    cf.GridWidth.set(GW)
    #
    try:
        T_length = int(eval(TrgLPFEntry.get()))
        if T_length < 1:
            T_length = 1
            TrgLPFEntry.delete(0,tk.END)
            TrgLPFEntry.insert(0, int(GW))
        if T_length > 100:
            T_length = 100
            TrgLPFEntry.delete(0,tk.END)
            TrgLPFEntry.insert(0, int(GW))
    except:
        TrgLPFEntry.delete(0,tk.END)
        TrgLPFEntry.insert(0, cf.Trigger_LPF_length.get())
    cf.Trigger_LPF_length.set(T_length)
    #
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
        TwdthE.delete(0,tk.END)
        TwdthE.insert(0, cf.TRACEwidth.get())
    cf.TRACEwidth.set(TW)
 # Number of average sweeps for average mode
    try:
        TA = int(eval(TAvg.get()))
        if TA < 1:
            TA = 1
            TAvg.delete(0,tk.END)
            TAvg.insert(0, int(TA))
        if TA > 16:
            TA = 16
            TAvg.delete(0,tk.END)
            TAvg.insert(0, int(TA))
    except:
        TAvg.delete(0,tk.END)
        TAvg.insert(0, cf.TRACEaverage.get())
    cf.TRACEaverage.set(TA)

def DestroySettingsMenu():
    global Settingswindow   
    cf.SettingsStatus.set(0)
    UpdateSettingsMenu()
    Settingswindow.destroy()
#--- Ende Settings Menü im Unterfenster 
      
#--- Menü mit Mathematikfunktionen
def MakeMathMenu():
    global MathScreenStatus, MathWindow
    
    if MathScreenStatus.get() == 0:
        MathScreenStatus.set(1)
        MathWindow = tk.Toplevel()
        MathWindow.title("Math Formula ")
        MathWindow.resizable(False,False)
        MathWindow.protocol("WM_DELETE_WINDOW", DestroyMathMenu)
        frame1 = ttk.LabelFrame(MathWindow, text="Math Trace", style="A10R1.TLabelframe")
        #frame2 = ttk.LabelFrame(MathWindow, text="Math Trace", style="A10R1.TLabelframe")
        frame1.grid(row = 0, column=0, rowspan=3, sticky=tk.W)
        #frame2.grid(row = 0, column=1, sticky=tk.W)

        # Built in functions
        rb1 = ttk.Radiobutton(frame1, text='none', variable=cf.MathTrace, value=0, command=UpdateTimeTrace)
        rb1.grid(row=0, column=0, sticky=tk.W)
        rb2 = ttk.Radiobutton(frame1, text='CAV+CBV', variable=cf.MathTrace, value=1, command=UpdateTimeTrace)
        rb2.grid(row=1, column=0, sticky=tk.W)
        rb3 = ttk.Radiobutton(frame1, text='CAV-CBV', variable=cf.MathTrace, value=2, command=UpdateTimeTrace)
        rb3.grid(row=2, column=0, sticky=tk.W)
        rb4 = ttk.Radiobutton(frame1, text='CBV-CAV', variable=cf.MathTrace, value=3, command=UpdateTimeTrace)
        rb4.grid(row=3, column=0, sticky=tk.W)
        rb5 = ttk.Radiobutton(frame1, text='CAI-CBI', variable=cf.MathTrace, value=8, command=UpdateTimeTrace)
        rb5.grid(row=4, column=0, sticky=tk.W)
        rb6 = ttk.Radiobutton(frame1, text='CBI-CAI', variable=cf.MathTrace, value=9, command=UpdateTimeTrace)
        rb6.grid(row=5, column=0, sticky=tk.W)
        rb7 = ttk.Radiobutton(frame1, text='CAV*CAI', variable=cf.MathTrace, value=4, command=UpdateTimeTrace)
        rb7.grid(row=6, column=0, sticky=tk.W)
        rb8 = ttk.Radiobutton(frame1, text='CBV*CBI', variable=cf.MathTrace, value=5, command=UpdateTimeTrace)
        rb8.grid(row=7, column=0, sticky=tk.W)
        rb9 = ttk.Radiobutton(frame1, text='CAV/CAI', variable=cf.MathTrace, value=6, command=UpdateTimeTrace)
        rb9.grid(row=8, column=0, sticky=tk.W)
        rb10 = ttk.Radiobutton(frame1, text='CBV/CBI', variable=cf.MathTrace, value=7, command=UpdateTimeTrace)
        rb10.grid(row=9, column=0, sticky=tk.W)
        rb11 = ttk.Radiobutton(frame1, text='CBV/CAV', variable=cf.MathTrace, value=10, command=UpdateTimeTrace)
        rb11.grid(row=10, column=0, sticky=tk.W)
        rb12 = ttk.Radiobutton(frame1, text='CBI/CAI', variable=cf.MathTrace, value=11, command=UpdateTimeTrace)
        rb12.grid(row=11, column=0, sticky=tk.W)     
        dismissbutton = ttk.Button(MathWindow, text="Close Window", command=DestroyMathMenu)
        dismissbutton.grid(row=3, column=0, sticky=tk.W)      
    if cf.RUNstatus.get() > 0:
        UpdateTimeTrace()

# Destroy New Math waveform controls menu window
def DestroyMathMenu():
    global MathScreenStatus, MathWindow 
    if MathScreenStatus.get() == 1:
        MathScreenStatus.set(0)
        MathWindow.destroy()
#--- Ende Menü mit Mathematikfunktionen


    