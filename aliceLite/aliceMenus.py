#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 29.8.20
"""

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
# check which operating system
import platform

from aliceIcons import hipulse, lowpulse, TBicon # Bilddateien der Icons
from aliceTimeFunc import MakeTimeTrace, MakeTimeScreen
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

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Tkinter UI Menüs aufbauen
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# AWG Unterfenster
def MakeAWGMenu():
    global AWGAMode, AWGATerm, AWGAShape, AWGSync, awgwindow, AWGAPhaseDelay, AWGBPhaseDelay
    global AWGBMode, AWGBTerm, AWGBShape, AWGScreenStatus, AWGARepeatFlag, AWGBRepeatFlag
    global AWGAShapeLabel, AWGBShapeLabel, AWGShowAdvanced
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGAPhaseEntry, AWGADutyCycleEntry
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBPhaseEntry, AWGBDutyCycleEntry
    global AWGALength, AWGBLength, RevDate, phasealab, phaseblab, AWGAModeLabel, AWGBModeLabel
    global duty1lab, duty2lab, awgaph, awgadel, awgbph, awgbdel
    global AwgLayout, AWG_Amp_Mode, awgsync, SWRev # 0 = Min/Max mode, 1 = Amp/Offset
    global amp1lab, amp2lab, off1lab, off2lab, AWG_2X
    
    if AWGScreenStatus.get() == 0:
        AWGScreenStatus.set(1)
        
        awgwindow = tk.Toplevel()
        awgwindow.title("AWG Controls " + SWRev + RevDate)
        awgwindow.resizable(False,False)
        awgwindow.geometry('+0+100')
        awgwindow.protocol("WM_DELETE_WINDOW", DestroyAWGMenu)

        frame2 = tk.LabelFrame(awgwindow, text="AWG CH A", style="A10R1.TLabelframe")
        frame3 = tk.LabelFrame(awgwindow, text="AWG CH B", style="A10R2.TLabelframe")
        frame2.pack(side=tk.LEFT, expand=1, fill=tk.X)
        frame3.pack(side=tk.LEFT, expand=1, fill=tk.X)
 
        # now AWG A
        # AWG enable sub frame
        AWGAMode = tk.IntVar(0)   # AWG A mode variable
        AWGATerm = tk.IntVar(0)   # AWG A termination variable
        AWGAShape = tk.IntVar(0)  # AWG A Wave shape variable
        AWGARepeatFlag = tk.IntVar(0) # AWG A Arb shape repeat flag
        AWGAMode.set(2)
        AWGSync = tk.IntVar(0) # Sync start both AWG channels
        AWGSync.set(1)
        awg1eb = tk.Frame( frame2 )
        awg1eb.pack(side=tk.TOP)
        ModeAMenu = tk.Menubutton(awg1eb, text="Mode", style="W5.TButton")
        ModeAMenu.menu = tk.Menu(ModeAMenu, tearoff = 0 )
        ModeAMenu["menu"] = ModeAMenu.menu
        ModeAMenu.menu.add_command(label="-Mode-", foreground="blue", command=donothing)
        ModeAMenu.menu.add_radiobutton(label="SVMI", variable=AWGAMode, value=0, command=BAWGAModeLabel)
        ModeAMenu.menu.add_radiobutton(label="SIMV", variable=AWGAMode, value=1, command=BAWGAModeLabel)
        ModeAMenu.menu.add_radiobutton(label="Hi-Z", variable=AWGAMode, value=2, command=BAWGAModeLabel)
        ModeAMenu.menu.add_separator()
        ModeAMenu.menu.add_command(label="-Term-", foreground="blue", command=donothing)
        ModeAMenu.menu.add_radiobutton(label="Open", variable=AWGATerm, value=0, command=UpdateAwgCont)
        ModeAMenu.menu.add_radiobutton(label="To GND", variable=AWGATerm, value=1, command=UpdateAwgCont)
        ModeAMenu.menu.add_radiobutton(label="To 2.5V", variable=AWGATerm, value=2, command=UpdateAwgCont)
        ModeAMenu.pack(side=tk.LEFT, anchor=tk.W)
        ShapeAMenu = tk.tk.Menubutton(awg1eb, text="Shape", style="W6.TButton")
        ShapeAMenu.menu = tk.Menu(ShapeAMenu, tearoff = 0 )
        ShapeAMenu["menu"] = ShapeAMenu.menu
        ShapeAMenu.menu.add_command(label="-Basic-", foreground="blue", command=donothing)
        ShapeAMenu.menu.add_radiobutton(label="DC", variable=AWGAShape, value=0, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="Sine", variable=AWGAShape, value=18, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="Triangle", variable=AWGAShape, value=2, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="Sawtooth", variable=AWGAShape, value=3, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="Square", variable=AWGAShape, value=4, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="StairStep", variable=AWGAShape, value=5, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_command(label="-Advanced-", foreground="blue", command=donothing)
        ShapeAMenu.menu.add_radiobutton(label="Impulse", variable=AWGAShape, value=9, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="Trapezoid", variable=AWGAShape, value=11, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="Pulse", variable=AWGAShape, value=20, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="Ramp", variable=AWGAShape, value=16, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="SSQ Pulse", variable=AWGAShape, value=15, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="U-D Ramp", variable=AWGAShape, value=12, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="Sin X/X", variable=AWGAShape, value=19, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="PWM Sine", variable=AWGAShape, value=17, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="FM Sine", variable=AWGAShape, value=21, command=AWGAMakeFMSine)
        ShapeAMenu.menu.add_radiobutton(label="AM Sine", variable=AWGAShape, value=22, command=AWGAMakeAMSine)
        ShapeAMenu.menu.add_radiobutton(label="UU Noise", variable=AWGAShape, value=7, command=ReMakeAWGwaves)
        ShapeAMenu.menu.add_radiobutton(label="UG Noise", variable=AWGAShape, value=8, command=ReMakeAWGwaves)
        else:
            ShapeAMenu.menu.add_separator()
        ShapeAMenu.menu.add_checkbutton(label='Repeat', variable=AWGARepeatFlag)
        ShapeAMenu.pack(side=tk.LEFT, anchor=tk.W)
        #
        AWGAModeLabel = tk.Label(frame2, text="AWG A Mode")
        AWGAModeLabel.pack(side=tk.TOP)
        AWGAShapeLabel = tk.Label(frame2, text="AWG A Shape")
        AWGAShapeLabel.pack(side=tk.TOP)
        #
        awg1ampl = tk.Frame( frame2 )
        awg1ampl.pack(side=tk.TOP)
        AWGAAmplEntry = tk.Entry(awg1ampl, width=5)
        AWGAAmplEntry.bind("<Return>", UpdateAwgContRet)

        AWGAAmplEntry.bind('<Key>', onTextKeyAWG)
        AWGAAmplEntry.pack(side=tk.LEFT, anchor=tk.W)
        AWGAAmplEntry.delete(0,"tk.END")
        AWGAAmplEntry.insert(0,0.0)
        amp1lab = tk.Label(awg1ampl) #, text="Min Ch A")
        amp1lab.pack(side=tk.LEFT, anchor=tk.W)
        #
        awg1off = tk.Frame( frame2 )
        awg1off.pack(side=tk.TOP)
        AWGAOffsetEntry = tk.Entry(awg1off, width=5)
        AWGAOffsetEntry.bind("<Return>", UpdateAwgContRet)
        AWGAOffsetEntry.bind('<Key>', onTextKeyAWG)
        AWGAOffsetEntry.pack(side=tk.LEFT, anchor=tk.W)
        AWGAOffsetEntry.delete(0,"tk.END")
        AWGAOffsetEntry.insert(0,0.0)
        off1lab = tk.Label(awg1off) #, text="Max Ch A")
        off1lab.pack(side=tk.LEFT, anchor=tk.W)
        if AWG_Amp_Mode.get() == 0:
            amp1lab.config(text = "Min Ch A" ) # change displayed value
            off1lab.config(text = "Max Ch A" ) # change displayed value
        else:
            amp1lab.config(text = "Amp Ch A" )
            off1lab.config(text = "Off Ch A" )
        # AWG Frequency sub frame
        awg1freq = tk.Frame( frame2 )
        awg1freq.pack(side=tk.TOP)
        AWGAFreqEntry = tk.Entry(awg1freq, width=7)
        AWGAFreqEntry.bind("<Return>", UpdateAwgContRet)
        AWGAFreqEntry.bind('<Key>', onTextKeyAWG)
        AWGAFreqEntry.pack(side=tk.LEFT, anchor=tk.W)
        AWGAFreqEntry.delete(0,"tk.END")
        AWGAFreqEntry.insert(0,100.0)
        freq1lab = tk.Label(awg1freq, text="Freq Ch A")
        freq1lab.pack(side=tk.LEFT, anchor=tk.W)
        # AWG Phase or delay select sub frame
        AWGAPhaseDelay = tk.IntVar(0) # 
        awgadelay = tk.Frame( frame2 )
        awgadelay.pack(side=tk.TOP)
        awgaph = tk.Radiobutton(awgadelay, text="Phase", style="WPhase.TRadiobutton", variable=AWGAPhaseDelay, value=0, command=BAWGAPhaseDelay)
        awgaph.pack(side=tk.LEFT, anchor=tk.W)
        awgadel = tk.Radiobutton(awgadelay, text="Delay", style="GPhase.TRadiobutton", variable=AWGAPhaseDelay, value=1, command=BAWGAPhaseDelay)
        awgadel.pack(side=tk.LEFT, anchor=tk.W)
        # AWG Phase entry sub frame
        awg1phase = tk.Frame( frame2 )
        awg1phase.pack(side=tk.TOP)
        AWGAPhaseEntry = tk.Entry(awg1phase, width=5)
        AWGAPhaseEntry.bind("<Return>", UpdateAwgContRet)
        AWGAPhaseEntry.bind('<Key>', onTextKeyAWG)
        AWGAPhaseEntry.pack(side=tk.LEFT, anchor=tk.W)
        AWGAPhaseEntry.delete(0,"tk.END")
        AWGAPhaseEntry.insert(0,0)
        phasealab = tk.Label(awg1phase, text="Deg")
        phasealab.pack(side=tk.LEFT, anchor=tk.W)
        # AWG duty cycle frame
        awg1dc = tk.Frame( frame2 )
        awg1dc.pack(side=tk.TOP)
        AWGADutyCycleEntry = tk.Entry(awg1dc, width=5)
        AWGADutyCycleEntry.bind("<Return>", UpdateAwgContRet)
        AWGADutyCycleEntry.bind('<Key>', onTextKeyAWG)
        AWGADutyCycleEntry.pack(side=tk.LEFT, anchor=tk.W)
        AWGADutyCycleEntry.delete(0,"tk.END")
        AWGADutyCycleEntry.insert(0,50)
        duty1lab = tk.Label(awg1dc, text="%")
        duty1lab.pack(side=tk.LEFT, anchor=tk.W)
        #
        AWGALength = tk.Label(frame2, text="Length")
        AWGALength.pack(side=tk.TOP)
        #
        ## Hier fehlt noch Kombination VA und VB mit 200.000 S/s
        awg2x1 = tk.Radiobutton(frame2, text="Both CH 1X", variable=AWG_2X, value=0, command=BAWG2X)
        awg2x1.pack(side=tk.TOP)
        awg2x2 = tk.Radiobutton(frame2, text="CH A 2X", variable=AWG_2X, value=1, command=BAWG2X)
        awg2x2.pack(side=tk.TOP)
        awg2x3 = tk.Radiobutton(frame2, text="CH B 2X", variable=AWG_2X, value=2, command=BAWG2X)
        awg2x3.pack(side=tk.TOP)

        # now AWG B
        # AWG enable sub frame
        AWGBMode = tk.IntVar(0)   # AWG B mode variable
        AWGBTerm = tk.IntVar(0)   # AWG B termination variable
        AWGBShape = tk.IntVar(0)  # AWG B Wave shape variable
        AWGBRepeatFlag = tk.IntVar(0) # AWG B Arb shape repeat flag
        AWGBMode.set(2)
        awg2eb = tk.Frame( frame3 )
        awg2eb.pack(side=tk.TOP)
        ModeBMenu = tk.Menubutton(awg2eb, text="Mode", style="W5.TButton")
        ModeBMenu.menu = tk.Menu(ModeBMenu, tearoff = 0 )
        ModeBMenu["menu"] = ModeBMenu.menu
        ModeBMenu.menu.add_command(label="-Mode-", foreground="blue", command=donothing)
        ModeBMenu.menu.add_radiobutton(label="SVMI", variable=AWGBMode, value=0, command=BAWGBModeLabel)
        ModeBMenu.menu.add_radiobutton(label="SIMV", variable=AWGBMode, value=1, command=BAWGBModeLabel)
        ModeBMenu.menu.add_radiobutton(label="Hi-Z", variable=AWGBMode, value=2, command=BAWGBModeLabel)
        ModeBMenu.menu.add_separator()
        ModeBMenu.menu.add_command(label="-Term-", foreground="blue", command=donothing)
        ModeBMenu.menu.add_radiobutton(label="Open", variable=AWGBTerm, value=0, command=UpdateAwgCont)
        ModeBMenu.menu.add_radiobutton(label="To GND", variable=AWGBTerm, value=1, command=UpdateAwgCont)
        ModeBMenu.menu.add_radiobutton(label="To 2.5V", variable=AWGBTerm, value=2, command=UpdateAwgCont)
        ModeBMenu.pack(side=tk.LEFT, anchor=tk.W)
        ShapeBMenu = tk.Menubutton(awg2eb, text="Shape", style="W6.TButton")
        ShapeBMenu.menu = tk.Menu(ShapeBMenu, tearoff = 0 )
        ShapeBMenu["menu"] = ShapeBMenu.menu
        ShapeBMenu.menu.add_command(label="-Basic-", foreground="blue", command=donothing)
        ShapeBMenu.menu.add_radiobutton(label="DC", variable=AWGBShape, value=0, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="Sine", variable=AWGBShape, value=18, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="Triangle", variable=AWGBShape, value=2, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="Sawtooth", variable=AWGBShape, value=3, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="Square", variable=AWGBShape, value=4, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="StairStep", variable=AWGBShape, value=5, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_command(label="-Advanced-", foreground="blue", command=donothing)
        ShapeBMenu.menu.add_radiobutton(label="Impulse", variable=AWGBShape, value=9, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="Trapezoid", variable=AWGBShape, value=11, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="Pulse", variable=AWGBShape, value=20, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="Ramp", variable=AWGBShape, value=16, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="SSQ Pulse", variable=AWGBShape, value=15, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="U-D Ramp", variable=AWGBShape, value=12, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="Sin X/X", variable=AWGBShape, value=19, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="PWM Sine", variable=AWGBShape, value=17, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="UU Noise", variable=AWGBShape, value=7, command=ReMakeAWGwaves)
        ShapeBMenu.menu.add_radiobutton(label="UG Noise", variable=AWGBShape, value=8, command=ReMakeAWGwaves)
        else:
            ShapeBMenu.menu.add_separator()
        ShapeBMenu.menu.add_checkbutton(label='Repeat', variable=AWGBRepeatFlag)
        ShapeBMenu.pack(side=tk.LEFT, anchor=tk.W)
        #
        AWGBModeLabel = tk.Label(frame3, text="AWG B Mode")
        AWGBModeLabel.pack(side=tk.TOP)
        AWGBShapeLabel = tk.Label(frame3, text="AWG B Shape")
        AWGBShapeLabel.pack(side=tk.TOP)
        #
        awg2ampl = tk.Frame( frame3 )
        awg2ampl.pack(side=tk.TOP)
        AWGBAmplEntry = tk.Entry(awg2ampl, width=5)
        AWGBAmplEntry.bind("<Return>", UpdateAwgContRet)
        AWGBAmplEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBAmplEntry.bind("<Button-4>", onAWGBscroll)# with Linux OS
        AWGBAmplEntry.bind("<Button-5>", onAWGBscroll)
        AWGBAmplEntry.bind('<Key>', onTextKeyAWG)
        AWGBAmplEntry.pack(side=tk.LEFT, anchor=tk.W)
        AWGBAmplEntry.delete(0,"tk.END")
        AWGBAmplEntry.insert(0,0.0)
        amp2lab = tk.Label(awg2ampl) #, text="Min Ch B")
        amp2lab.pack(side=tk.LEFT, anchor=tk.W)
        #
        awg2off = tk.Frame( frame3 )
        awg2off.pack(side=tk.TOP)
        AWGBOffsetEntry = tk.Entry(awg2off, width=5)
        AWGBOffsetEntry.bind("<Return>", UpdateAwgContRet)
        AWGBOffsetEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBOffsetEntry.bind("<Button-4>", onAWGBscroll)# with Linux OS
        AWGBOffsetEntry.bind("<Button-5>", onAWGBscroll)
        AWGBOffsetEntry.bind('<Key>', onTextKeyAWG)
        AWGBOffsetEntry.pack(side=tk.LEFT, anchor=tk.W)
        AWGBOffsetEntry.delete(0,"tk.END")
        AWGBOffsetEntry.insert(0,0.0)
        off2lab = tk.Label(awg2off) #, text="Max Ch B")
        off2lab.pack(side=tk.LEFT, anchor=tk.W)
        if AWG_Amp_Mode.get() == 0:
            amp2lab.config(text = "Min Ch B" ) # change displayed value
            off2lab.config(text = "Max Ch B" ) # change displayed value
        else:
            amp2lab.config(text = "Amp Ch B" )
            off2lab.config(text = "Off Ch B" )
        # AWG Frequency sub frame
        awg2freq = tk.Frame( frame3 )
        awg2freq.pack(side=tk.TOP)
        AWGBFreqEntry = tk.Entry(awg2freq, width=7)
        AWGBFreqEntry.bind("<Return>", UpdateAwgContRet)
        AWGBFreqEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBFreqEntry.bind("<Button-4>", onAWGBscroll)# with Linux OS
        AWGBFreqEntry.bind("<Button-5>", onAWGBscroll)
        AWGBFreqEntry.bind('<Key>', onTextKeyAWG)
        AWGBFreqEntry.pack(side=tk.LEFT, anchor=tk.W)
        AWGBFreqEntry.delete(0,"tk.END")
        AWGBFreqEntry.insert(0,100.0)
        freq2lab = tk.Label(awg2freq, text="Freq Ch B")
        freq2lab.pack(side=tk.LEFT, anchor=tk.W)
        # AWG Phase or delay select sub frame
        AWGBPhaseDelay = tk.IntVar(0) # 
        awgbdelay = tk.Frame( frame3 )
        awgbdelay.pack(side=tk.TOP)
        awgbph = tk.Radiobutton(awgbdelay, text="Phase", style="WPhase.TRadiobutton", variable=AWGBPhaseDelay, value=0, command=BAWGBPhaseDelay)
        awgbph.pack(side=tk.LEFT, anchor=tk.W)
        awgbdel = tk.Radiobutton(awgbdelay, text="Delay", style="GPhase.TRadiobutton", variable=AWGBPhaseDelay, value=1, command=BAWGBPhaseDelay)
        awgbdel.pack(side=tk.LEFT, anchor=tk.W)
        # AWG Phase sub frame
        awg2phase = tk.Frame( frame3 )
        awg2phase.pack(side=tk.TOP)
        AWGBPhaseEntry = tk.Entry(awg2phase, width=5)
        AWGBPhaseEntry.bind("<Return>", UpdateAwgContRet)
        AWGBPhaseEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBPhaseEntry.bind("<Button-4>", onAWGBscroll)# with Linux OS
        AWGBPhaseEntry.bind("<Button-5>", onAWGBscroll)
        AWGBPhaseEntry.bind('<Key>', onTextKeyAWG)
        AWGBPhaseEntry.pack(side=tk.LEFT, anchor=tk.W)
        AWGBPhaseEntry.delete(0,"tk.END")
        AWGBPhaseEntry.insert(0,0)
        phaseblab = tk.Label(awg2phase, text="Deg")
        phaseblab.pack(side=tk.LEFT, anchor=tk.W)
        # AWG duty cycle frame
        awg2dc = tk.Frame( frame3 )
        awg2dc.pack(side=tk.TOP)
        AWGBDutyCycleEntry = tk.Entry(awg2dc, width=5)
        AWGBDutyCycleEntry.bind("<Return>", UpdateAwgContRet)
        AWGBDutyCycleEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBDutyCycleEntry.bind("<Button-4>", onAWGBscroll)# with Linux OS
        AWGBDutyCycleEntry.bind("<Button-5>", onAWGBscroll)
        AWGBDutyCycleEntry.bind('<Key>', onTextKeyAWG)
        AWGBDutyCycleEntry.pack(side=tk.LEFT, anchor=tk.W)
        AWGBDutyCycleEntry.delete(0,"tk.END")
        AWGBDutyCycleEntry.insert(0,50)
        duty2lab = tk.Label(awg2dc, text="%")
        duty2lab.pack(side=tk.LEFT, anchor=tk.W)
        #
        AWGBLength = tk.Label(frame3, text="Length")
        AWGBLength.pack(side=tk.TOP)

        dismissbutton = tk.Button(frame3, text="Minimize", style="W8.TButton", command=DestroyAWGMenu)
        dismissbutton.pack(side=tk.TOP)
    else:
        awgwindow.deiconify()

def UpdateAWGMenu():
    UpdateAWGA()
    UpdateAWGB()
    ReMakeAWGwaves()

def DestroyAWGMenu():
    global awgwindow, AWGScreenStatus   
    awgwindow.iconify()

# Samplingrate Unterfenster
# Die 2x Einstellung für die Samplingrate beißt sich wohl mit der 2x Option im AWG-Fenster    
def MakeSampleRateMenu():
    global SAMPLErate, AWGSAMPLErate, BaseSampleRate, session, etssrlab, RevDate
    global Two_X_Sample, ADC_Mux_Mode, SampleRatewindow, SampleRateStatus, BaseRatesb
    global Alternate_Sweep_Mode, DeBugMode, SWRev, SampRateList

    if SampleRateStatus.get() == 0:
        SampleRateStatus.set(1)
        SampleRatewindow = tk.tk.Toplevel()
        SampleRatewindow.title("Set Sample Rate " + SWRev + RevDate)
        SampleRatewindow.resizable(False,False)
        SampleRatewindow.protocol("WM_DELETE_WINDOW", DestroySampleRateMenu)
        frame1 = tk.Frame(SampleRatewindow, borderwidth=5, relief=tk.RIDGE)
        frame1.grid(row=0, column=0, sticky=tk.W)
        #
        BaseRATE = tk.Frame( frame1 )
        BaseRATE.grid(row=0, column=0, sticky=tk.W)
        baseratelab = tk.Label(BaseRATE, text="Base Sample Rate", style="A10B.TLabel") #, font = "Arial 10 bold")
        baseratelab.pack(side=tk.LEFT)
        BaseRatesb = tk.Spinbox(BaseRATE, width=6, values=SampRateList, command=SetSampleRate)
        BaseRatesb.bind('<MouseWheel>', onSrateScroll)
        BaseRatesb.bind("<Button-4>", onSrateScroll)# with Linux OS
        BaseRatesb.bind("<Button-5>", onSrateScroll)
        BaseRatesb.bind("<Return>", onRetSrate)
        BaseRatesb.pack(side=tk.LEFT)
        BaseRatesb.delete(0,"tk.END")
        BaseRatesb.insert(0,BaseSampleRate)
        
        nextrow = 2        
        twoX = tk.Checkbutton(frame1, text="Double Sample Rate", variable=Two_X_Sample, command=SetADC_Mux )
        twoX.grid(row=1, column=0, sticky=tk.W)
        muxlab1 = tk.Label(frame1, text="ADC MUX Modes", style="A10B.TLabel") #, font = "Arial 10 bold")
        muxlab1.grid(row=2, column=0, sticky=tk.W)
        AltSweep = tk.Checkbutton(frame1, text="Alternate Sweep Mode", variable=Alternate_Sweep_Mode ) #, command=SetADC_Mux )
        AltSweep.grid(row=3, column=0, sticky=tk.W)
        chabuttons = tk.Frame( frame1 )
        chabuttons.grid(row=4, column=0, sticky=tk.W)
        ## Mux Modus 0 ist nötig für VA und VB mit 200.000 S/s
        ## Hier wird der ADC_Mux_Mode eingestellt, je nachdem welche Knöpfe (VA, VB, IA, IB) vom Benutzer aktiviert sind.
        muxrb1 = tk.Radiobutton(chabuttons, text="VA and VB", variable=ADC_Mux_Mode, value=0, command=SetADC_Mux ) #style="W8.TButton",
        muxrb1.pack(side=tk.LEFT)
        muxrb2 = tk.Radiobutton(chabuttons, text="IA and IB", variable=ADC_Mux_Mode, value=1, command=SetADC_Mux ) #style="W8.TButton",
        muxrb2.pack(side=tk.LEFT)
        chcbuttons = tk.Frame( frame1 )
        chcbuttons.grid(row=5, column=0, sticky=tk.W)
        muxrb5 = tk.Radiobutton(chcbuttons, text="VA and IA", variable=ADC_Mux_Mode, value=4, command=SetADC_Mux ) # style="W8.TButton",
        muxrb5.pack(side=tk.LEFT)
        muxrb6 = tk.Radiobutton(chcbuttons, text="VB and IB", variable=ADC_Mux_Mode, value=5, command=SetADC_Mux ) # style="W8.TButton",
        muxrb6.pack(side=tk.LEFT)
        nextrow = 6
        if DeBugMode == 1:
            chbbuttons = tk.Frame( frame1 )
            chbbuttons.grid(row=nextrow, column=0, sticky=tk.W)
            muxrb3 = tk.Radiobutton(chbbuttons, text="VA and IB", variable=ADC_Mux_Mode, value=2, command=SetADC_Mux ) # style="W8.TButton",
            muxrb3.pack(side=tk.LEFT)
            muxrb4 = tk.Radiobutton(chbbuttons, text="VB and IA", variable=ADC_Mux_Mode, value=3, command=SetADC_Mux ) # style="W8.TButton",
            muxrb4.pack(side=tk.LEFT)
            nextrow = nextrow + 1
        
        sratedismissclbutton = tk.Button(frame1, text="Dismiss", style="W8.TButton", command=DestroySampleRateMenu)
        sratedismissclbutton.grid(row=nextrow, column=0, sticky=tk.W, pady=7)

def DestroySampleRateMenu():
    global SampleRatewindow, SampleRateStatus
    
    SampleRateStatus.set(0)
    SampleRatewindow.destroy()

def MakeSettingsMenu():
    global GridWidth, TRACEwidth, TRACEaverage, Vdiv, HarmonicMarkers, ZEROstuffing, RevDate
    global Settingswindow, SettingsStatus, ZSTuff, TAvg, VDivE, TwdthE, GwdthE, HarMon
    global AWG_Amp_Mode, SWRev, EnableHSsampling
    global TrgLPFEntry, Trigger_LPF_length
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry

    if SettingsStatus.get() == 0:
        SettingsStatus.set(1)
        Settingswindow = tk.tk.Toplevel()
        Settingswindow.title("Settings " + SWRev + RevDate)
        Settingswindow.resizable(False,False)
        Settingswindow.protocol("WM_DELETE_WINDOW", DestroySettingsMenu)
        frame1 = tk.Frame(Settingswindow, borderwidth=5, relief=tk.RIDGE)
        frame1.grid(row=0, column=0, sticky=tk.W)
        #
        zstlab = tk.Label(frame1, text="FFT Zero Stuffing", style= "A10B.TLabel")
        zstlab.grid(row=0, column=0, sticky=tk.W)
        zstMode = tk.Frame( frame1 )
        zstMode.grid(row=0, column=1, sticky=tk.W)
        ZSTuff = tk.Entry(zstMode, width=4)
        ZSTuff.bind("<Return>", onSettingsTextKey)
        ZSTuff.bind('<MouseWheel>', onSettingsScroll)
        ZSTuff.bind("<Button-4>", onSettingsScroll)# with Linux OS
        ZSTuff.bind("<Button-5>", onSettingsScroll)
        ZSTuff.bind('<Key>', onSettingsTextKey)
        ZSTuff.pack(side=tk.RIGHT)
        ZSTuff.delete(0,"tk.END")
        ZSTuff.insert(0,ZEROstuffing.get())
        #
        Avglab = tk.Label(frame1, text="Number Traces to Average", style= "A10B.TLabel")
        Avglab.grid(row=1, column=0, sticky=tk.W)
        AvgMode = tk.Frame( frame1 )
        AvgMode.grid(row=1, column=1, sticky=tk.W)
        TAvg = tk.Entry(AvgMode, width=4)
        TAvg.bind("<Return>", onSettingsTextKey)
        TAvg.bind('<MouseWheel>', onSettingsScroll)
        TAvg.bind("<Button-4>", onSettingsScroll)# with Linux OS
        TAvg.bind("<Button-5>", onSettingsScroll)
        TAvg.bind('<Key>', onSettingsTextKey)
        TAvg.pack(side=tk.RIGHT)
        TAvg.delete(0,"tk.END")
        TAvg.insert(0,TRACEaverage.get())
        #
        HarMlab = tk.Label(frame1, text="Number of Harmonic Markers", style= "A10B.TLabel")
        HarMlab.grid(row=2, column=0, sticky=tk.W)
        HarMMode = tk.Frame( frame1 )
        HarMMode.grid(row=2, column=1, sticky=tk.W)
        HarMon = tk.Entry(HarMMode, width=4)
        HarMon.bind("<Return>", onSettingsTextKey)
        HarMon.bind('<MouseWheel>', onSettingsScroll)
        HarMon.bind("<Button-4>", onSettingsScroll)# with Linux OS
        HarMon.bind("<Button-5>", onSettingsScroll)
        HarMon.bind('<Key>', onSettingsTextKey)
        HarMon.pack(side=tk.RIGHT)
        HarMon.delete(0,"tk.END")
        HarMon.insert(0,HarmonicMarkers.get())
        #
        Vdivlab = tk.Label(frame1, text="Number Vertical Div (SA, Bode)", style= "A10B.TLabel")
        Vdivlab.grid(row=3, column=0, sticky=tk.W)
        VdivMode = tk.Frame( frame1 )
        VdivMode.grid(row=3, column=1, sticky=tk.W)
        VDivE = tk.Entry(VdivMode, width=4)
        VDivE.bind("<Return>", onSettingsTextKey)
        VDivE.bind('<MouseWheel>', onSettingsScroll)
        VDivE.bind("<Button-4>", onSettingsScroll)# with Linux OS
        VDivE.bind("<Button-5>", onSettingsScroll)
        VDivE.bind('<Key>', onSettingsTextKey)
        VDivE.pack(side=tk.RIGHT)
        VDivE.delete(0,"tk.END")
        VDivE.insert(0,Vdiv.get())
        #
        Twdthlab = tk.Label(frame1, text="Trace Width in Pixels", style= "A10B.TLabel")
        Twdthlab.grid(row=4, column=0, sticky=tk.W)
        TwdthMode = tk.Frame( frame1 )
        TwdthMode.grid(row=4, column=1, sticky=tk.W)
        TwdthE = tk.Entry(TwdthMode, width=4)
        TwdthE.bind("<Return>", onSettingsTextKey)
        TwdthE.bind('<MouseWheel>', onSettingsScroll)
        TwdthE.bind("<Button-4>", onSettingsScroll)# with Linux OS
        TwdthE.bind("<Button-5>", onSettingsScroll)
        TwdthE.bind('<Key>', onSettingsTextKey)
        TwdthE.pack(side=tk.RIGHT)
        TwdthE.delete(0,"tk.END")
        TwdthE.insert(0,TRACEwidth.get())
        #
        Gwdthlab = tk.Label(frame1, text="Grid Width in Pixels", style= "A10B.TLabel")
        Gwdthlab.grid(row=5, column=0, sticky=tk.W)
        GwdthMode = tk.Frame( frame1 )
        GwdthMode.grid(row=5, column=1, sticky=tk.W)
        GwdthE = tk.Entry(GwdthMode, width=4)
        GwdthE.bind("<Return>", onSettingsTextKey)
        GwdthE.bind('<MouseWheel>', onSettingsScroll)
        GwdthE.bind("<Button-4>", onSettingsScroll)# with Linux OS
        GwdthE.bind("<Button-5>", onSettingsScroll)
        GwdthE.bind('<Key>', onSettingsTextKey)
        GwdthE.pack(side=tk.RIGHT)
        GwdthE.delete(0,"tk.END")
        GwdthE.insert(0,GridWidth.get())
        #
        trglpflab = tk.Label(frame1, text="Trigger LPF Length", style= "A10B.TLabel")
        trglpflab.grid(row=6, column=0, sticky=tk.W)
        TrgLPFMode = tk.Frame( frame1 )
        TrgLPFMode.grid(row=6, column=1, sticky=tk.W)
        TrgLPFEntry = tk.Entry(TrgLPFMode, width=4)
        TrgLPFEntry.bind("<Return>", onSettingsTextKey)
        TrgLPFEntry.bind('<MouseWheel>', onSettingsScroll)
        TrgLPFEntry.bind("<Button-4>", onSettingsScroll)# with Linux OS
        TrgLPFEntry.bind("<Button-5>", onSettingsScroll)
        TrgLPFEntry.bind('<Key>', onSettingsTextKey)
        TrgLPFEntry.pack(side=tk.RIGHT)
        TrgLPFEntry.delete(0,"tk.END")
        TrgLPFEntry.insert(0,Trigger_LPF_length.get())
        #
        AwgAmplrb1 = tk.Radiobutton(frame1, text="AWG Min/Max", variable=AWG_Amp_Mode, value=0, command=UpdateAWGMenu)
        AwgAmplrb1.grid(row=7, column=0, sticky=tk.W)
        AwgAmplrb2 = tk.Radiobutton(frame1, text="AWG Amp/Off ", variable=AWG_Amp_Mode, value=1, command=UpdateAWGMenu)
        AwgAmplrb2.grid(row=7, column=1, sticky=tk.W)
        
        Settingsdismissbutton = tk.Button(frame1, text="Dismiss", style= "W8.TButton", command=DestroySettingsMenu)
        Settingsdismissbutton.grid(row=12, column=0, sticky=tk.W, pady=7)
    
def UpdateSettingsMenu():
    global GridWidth, TRACEwidth, TRACEaverage, Vdiv, HarmonicMarkers, ZEROstuffing, RevDate
    global Settingswindow, SettingsStatus, ZSTuff, TAvg, VDivE, TwdthE, GwdthE, HarMon
    global CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2, TrgLPFEntry, Trigger_LPF_length
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    
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
        GwdthE.insert(0, GridWidth.get())
    GridWidth.set(GW)
    #
    try:
        T_length = int(eval(TrgLPFEntry.get()))
        if T_length < 1:
            T_length = 1
            TrgLPFEntry.delete(0,tk.tk.END)
            TrgLPFEntry.insert(0, int(GW))
        if T_length > 100:
            T_length = 100
            TrgLPFEntry.delete(0,tk.tk.END)
            TrgLPFEntry.insert(0, int(GW))
    except:
        TrgLPFEntry.delete(0,tk.END)
        TrgLPFEntry.insert(0, Trigger_LPF_length.get())
    Trigger_LPF_length.set(T_length)
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
        TwdthE.insert(0, TRACEwidth.get())
    TRACEwidth.set(TW)
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
        TAvg.insert(0, TRACEaverage.get())
    TRACEaverage.set(TA)
    # Number of vertical divisions for spectrum / Bode
    try:
        VDv = int(eval(VDivE.get()))
        if VDv < 1:
            VDv = 1
            VDivE.delete(0,tk.END)
            VDivE.insert(0, int(VDv))
        if VDv > 16:
            VDv = 16
            VDivE.delete(0,tk.END)
            VDivE.insert(0, int(VDv))
    except:
        VDivE.delete(0,tk.END)
        VDivE.insert(0, Vdiv.get())
    Vdiv.set(VDv)
    # number of Harmonic Markers in SA
    try:
        HM = int(eval(HarMon.get()))
        if HM < 1:
            HM = 1
            HarMon.delete(0,tk.END)
            HarMon.insert(0, int(HM))
        if HM > 9:
            HM =9
            HarMon.delete(0,tk.END)
            HarMon.insert(0, int(HM))
    except:
        HarMon.delete(0,tk.END)
        HarMon.insert(0, HarmonicMarkers.get())
    HarmonicMarkers.set(HM)
 # The zero stuffing value is 2 ** ZERO stuffing, calculated on initialize
    try:
        ZST = int(eval(ZSTuff.get()))
        if ZST < 1:
            ZST = 1
            ZSTuff.delete(0,tk.END)
            ZSTuff.insert(0, int(ZST))
        if ZST > 5:
            ZST = 5
            ZSTuff.delete(0,tk.END)
            ZSTuff.insert(0, int(ZST))
    except:
        ZSTuff.delete(0,tk.END)
        ZSTuff.insert(0, ZEROstuffing.get())
    ZEROstuffing.set(ZST)

#
def DestroySettingsMenu():
    global Settingswindow, SettingsStatus   
    SettingsStatus.set(0)
    UpdateSettingsMenu()
    Settingswindow.destroy()
    
#--- Messfunktionen
def MakeMeasureMenu():
    global measurewindow, MeasureStatus, RevDate, SWRev
    global ChaLab1, ChaLab12, ChaLab3, ChaLab4, ChaLab5, ChaLab6
    global ChaValue1, ChaValue2, ChaValue3, ChaValue4, ChaValue5, ChaValue6
    global ChbLab1, ChbLab12, ChbLab3, ChbLab4, ChbLab5, ChbLab6
    global ChbValue1, ChbValue2, ChbValue3, ChbValue4, ChbValue5, ChbValue6
    global ChaLableSrring1, ChaLableSrring2, ChaLableSrring3, ChaLableSrring4, ChaLableSrring5, ChaLableSrring6
    global ChbLableSrring1, ChbLableSrring2, ChbLableSrring3, ChbLableSrring4, ChbLableSrring5, ChbLableSrring6
    
    if MeasureStatus.get() == 0:
        MeasureStatus.set(1)
        measurewindow = tk.Toplevel()
        measurewindow.title("Measurements " + SWRev + RevDate)
        measurewindow.resizable(False,False)
        measurewindow.protocol("WM_DELETE_WINDOW", DestroyMeasureMenu)
        toplab = tk.Label(measurewindow,text="Measurements ", style="A12B.TLabel")
        toplab.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        ChaLab1 = tk.Label(measurewindow,text=ChaLableSrring1, style="A10B.TLabel")
        ChaLab1.grid(row=1, column=0, columnspan=1, sticky=tk.W)
        ChaValue1 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue1.grid(row=1, column=1, columnspan=1, sticky=tk.W)
        ChaLab2 = tk.Label(measurewindow,text=ChaLableSrring2, style="A10B.TLabel")
        ChaLab2.grid(row=1, column=2, columnspan=1, sticky=tk.W)
        ChaValue2 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue2.grid(row=1, column=3, columnspan=1, sticky=tk.W)
        ChaLab3 = tk.Label(measurewindow,text=ChaLableSrring3, style="A10B.TLabel")
        ChaLab3.grid(row=2, column=0, columnspan=1, sticky=tk.W)
        ChaValue3 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue3.grid(row=2, column=1, columnspan=1, sticky=tk.W)
        ChaLab4 = tk.Label(measurewindow,text=ChaLableSrring4, style="A10B.TLabel")
        ChaLab4.grid(row=2, column=2, columnspan=1, sticky=tk.W)
        ChaValue4 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue4.grid(row=2, column=3, columnspan=1, sticky=tk.W)
        ChaLab5 = tk.Label(measurewindow,text=ChaLableSrring5, style="A10B.TLabel")
        ChaLab5.grid(row=3, column=0, columnspan=1, sticky=tk.W)
        ChaValue5 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue5.grid(row=3, column=1, columnspan=1, sticky=tk.W)
        ChaLab6 = tk.Label(measurewindow,text=ChaLableSrring6, style="A10B.TLabel")
        ChaLab6.grid(row=3, column=2, columnspan=1, sticky=tk.W)
        ChaValue6 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue6.grid(row=3, column=3, columnspan=1, sticky=tk.W)
        #
        ChbLab1 = tk.Label(measurewindow,text=ChbLableSrring1, style="A10B.TLabel")
        ChbLab1.grid(row=4, column=0, columnspan=1, sticky=tk.W)
        ChbValue1 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue1.grid(row=4, column=1, columnspan=1, sticky=tk.W)
        ChbLab2 = tk.Label(measurewindow,text=ChbLableSrring2, style="A10B.TLabel")
        ChbLab2.grid(row=4, column=2, columnspan=1, sticky=tk.W)
        ChbValue2 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue2.grid(row=4, column=3, columnspan=1, sticky=tk.W)
        ChbLab3 = tk.Label(measurewindow,text=ChbLableSrring3, style="A10B.TLabel")
        ChbLab3.grid(row=5, column=0, columnspan=1, sticky=tk.W)
        ChbValue3 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue3.grid(row=5, column=1, columnspan=1, sticky=tk.W)
        ChbLab4 = tk.Label(measurewindow,text=ChbLableSrring4, style="A10B.TLabel")
        ChbLab4.grid(row=5, column=2, columnspan=1, sticky=tk.W)
        ChbValue4 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue4.grid(row=5, column=3, columnspan=1, sticky=tk.W)
        ChbLab5 = tk.Label(measurewindow,text=ChbLableSrring5, style="A10B.TLabel")
        ChbLab5.grid(row=6, column=0, columnspan=1, sticky=tk.W)
        ChbValue5 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue5.grid(row=6, column=1, columnspan=1, sticky=tk.W)
        ChbLab6 = tk.Label(measurewindow,text=ChbLableSrring6, style="A10B.TLabel")
        ChbLab6.grid(row=6, column=2, columnspan=1, sticky=tk.W)
        ChbValue6 = tk.Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue6.grid(row=6, column=3, columnspan=1, sticky=tk.W)  

def UpdateMeasureMenu():
    global ChaLab1, ChaLab12, ChaLab3, ChaLab4, ChaLab5, ChaLab6
    global ChaValue1, ChaValue2, ChaValue3, ChaValue4, ChaValue5, ChaValue6
    global ChbLab1, ChbLab12, ChbLab3, ChbLab4, ChbLab5, ChbLab6
    global ChbValue1, ChbValue2, ChbValue3, ChbValue4, ChbValue5, ChbValue6
    global ChaMeasString1, ChaMeasString2, ChaMeasString3, ChaMeasString4, ChaMeasString5, ChaMeasString6
    global ChbMeasString1, ChbMeasString2, ChbMeasString3, ChbMeasString4, ChbMeasString5, ChbMeasString6
    
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString1))
    ChaValue1.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString2))
    ChaValue2.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString3))
    ChaValue3.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString4))
    ChaValue4.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString5))
    ChaValue5.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString6))
    ChaValue6.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString1))
    ChbValue1.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString2))
    ChbValue2.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString3))
    ChbValue3.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString4))
    ChbValue4.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString5))
    ChbValue5.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString6))
    ChbValue6.config(text = ValueText)

def DestroyMeasureMenu():
    global measurewindow, MeasureStatus
    MeasureStatus.set(0)
    measurewindow.destroy()  
    
#--- Mathematikfunktionen
# Make New Math waveform controls menu window
def MakeMathMenu():
    global RUNstatus, MathScreenStatus, MathWindow, SWRev, RevDate
    global MathAxis, MathTrace
    global formentry, unitsentry, axisentry, xformentry, xunitsentry, xaxisentry, yformentry, yunitsentry, yaxisentry
    global formlab, xformlab, yformlab
    
    if MathScreenStatus.get() == 0:
        MathScreenStatus.set(1)
        MathWindow = tk.tk.Toplevel()
        MathWindow.title("Math Formula " + SWRev + RevDate)
        MathWindow.resizable(False,False)
        MathWindow.protocol("WM_DELETE_WINDOW", DestroyMathMenu)
        frame1 = tk.LabelFrame(MathWindow, text="Built-in Exp", style="A10R1.TLabelframe")
        # Wozu frame2-3?
        frame2 = tk.LabelFrame(MathWindow, text="Math Trace", style="A10R1.TLabelframe")
        frame3 = tk.LabelFrame(MathWindow, text="X Math Trace", style="A10R1.TLabelframe")
        frame4 = tk.LabelFrame(MathWindow, text="Y Math Trace", style="A10R1.TLabelframe")
        frame1.grid(row = 0, column=0, rowspan=3, sticky=tk.W)
        frame2.grid(row = 0, column=1, sticky=tk.W)
        frame3.grid(row = 1, column=1, sticky=tk.W)
        frame4.grid(row = 2, column=1, sticky=tk.W)
        # Built in functions
        rb1 = tk.Radiobutton(frame1, text='none', variable=MathTrace, value=0, command=UpdateTimeTrace)
        rb1.grid(row=0, column=0, sticky=tk.W)
        rb2 = tk.Radiobutton(frame1, text='CAV+CBV', variable=MathTrace, value=1, command=UpdateTimeTrace)
        rb2.grid(row=1, column=0, sticky=tk.W)
        rb3 = tk.Radiobutton(frame1, text='CAV-CBV', variable=MathTrace, value=2, command=UpdateTimeTrace)
        rb3.grid(row=2, column=0, sticky=tk.W)
        rb4 = tk.Radiobutton(frame1, text='CBV-CAV', variable=MathTrace, value=3, command=UpdateTimeTrace)
        rb4.grid(row=3, column=0, sticky=tk.W)
        rb5 = tk.Radiobutton(frame1, text='CAI-CBI', variable=MathTrace, value=8, command=UpdateTimeTrace)
        rb5.grid(row=4, column=0, sticky=tk.W)
        rb6 = tk.Radiobutton(frame1, text='CBI-CAI', variable=MathTrace, value=9, command=UpdateTimeTrace)
        rb6.grid(row=5, column=0, sticky=tk.W)
        rb7 = tk.Radiobutton(frame1, text='CAV*CAI', variable=MathTrace, value=4, command=UpdateTimeTrace)
        rb7.grid(row=6, column=0, sticky=tk.W)
        rb8 = tk.Radiobutton(frame1, text='CBV*CBI', variable=MathTrace, value=5, command=UpdateTimeTrace)
        rb8.grid(row=7, column=0, sticky=tk.W)
        rb9 = tk.Radiobutton(frame1, text='CAV/CAI', variable=MathTrace, value=6, command=UpdateTimeTrace)
        rb9.grid(row=8, column=0, sticky=tk.W)
        rb10 = tk.Radiobutton(frame1, text='CBV/CBI', variable=MathTrace, value=7, command=UpdateTimeTrace)
        rb10.grid(row=9, column=0, sticky=tk.W)
        rb11 = tk.Radiobutton(frame1, text='CBV/CAV', variable=MathTrace, value=10, command=UpdateTimeTrace)
        rb11.grid(row=10, column=0, sticky=tk.W)
        rb12 = tk.Radiobutton(frame1, text='CBI/CAI', variable=MathTrace, value=11, command=UpdateTimeTrace)
        rb12.grid(row=11, column=0, sticky=tk.W)     
        dismissbutton = tk.Button(MathWindow, text="Dismiss", command=DestroyMathMenu)
        dismissbutton.grid(row=3, column=0, sticky=tk.W)      
    if RUNstatus.get() > 0:
        UpdateTimeTrace()

# Destroy New Math waveform controls menu window
def DestroyMathMenu():
    global MathScreenStatus, MathWindow 
    if MathScreenStatus.get() == 1:
        MathScreenStatus.set(0)
        MathWindow.destroy()
        
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
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)
    ## Hide Tip Action
    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()