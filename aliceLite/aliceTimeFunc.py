#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 19:57:41 2020

@author: stefan
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
import platform

from aliceIcons import hipulse, lowpulse, TBicon # Bilddateien der Icons
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


## Make the scope time traces
def MakeTimeTrace():
    global VBuffA, VBuffB, IBuffA, IBuffB
    global VBuffMA, VBuffMB, VBuffMC, VBuffMD
    global VmemoryA, VmemoryB, ImemoryA, ImemoryB
    global AWGAwaveform, AWGBwaveform
    global T1Vline, T2Vline, T1Iline, T2Iline
    global TMAVline, TMBVline, TMCVline, TMDVline
    global Tmathline, TMXline, TMYline
    global MathAxis
    global Triggerline, Triggersymbol, TgInput, TgEdge, HoldOff, HoldOffentry,hldn
    global X0L, Y0T, GRW, GRH, MouseX, MouseY, MouseCAV, MouseCAI, MouseCBV, MouseCBI
    global SHOWsamples, ZOHold, AWGBMode
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I   
    global RUNstatus
    global AutoCenterA, AutoCenterB
    global CHAsb, CHBsb, CHAOffset, CHBOffset, CHAIsb, CHBIsb, CHAIOffset, CHBIOffset
    global TMsb         # Time per div spin box variable
    global TIMEdiv      # current spin box value
    global SAMPLErate, SCstart, Two_X_Sample, DISsamples
    global TRIGGERsample, TRACEsize, DX
    global TRIGGERlevel, TRIGGERentry, AutoLevel
    global InOffA, InGainA, InOffB, InGainB
    global CurOffA, CurOffB, CurGainA, CurGainB
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAIPosEntry, CHAVPosEntry, CHBIPosEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
    global HozPoss, HozPossentry

    # Set the TRACEsize variable
    if len(VBuffA) < 100:
        return
    TRACEsize = SHOWsamples               # Set the trace length
    SCstart = 0
    ylo = 0.0
    Ymin = Y0T                  # Minimum position of time grid (top)
    Ymax = Y0T + GRH            # Maximum position of time grid (bottom)


    # prevent divide by zero error
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.01
    # Check for Auto Centering
    if AutoCenterA.get() > 0:
        CHAOffset = DCV1
        CHAVPosEntry.delete(0,tk.END)
        CHAVPosEntry.insert(0, ' {0:.2f} '.format(CHAOffset))
    if AutoCenterB.get() > 0:
        CHBOffset = DCV2
        CHBVPosEntry.delete(0,tk.END)
        CHBVPosEntry.insert(0, ' {0:.2f} '.format(CHBOffset))
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
    if CH1IpdvRange < 0.1:
        CH1IpdvRange = 0.1
    if CH2IpdvRange < 0.1:
        CH2IpdvRange = 0.1

    try:
        HoldOff = float(eval(HoldOffentry.get()))
        if HoldOff < 0:
            HoldOff = 0
            HoldOffentry.delete(0,tk.END)
            HoldOffentry.insert(0, HoldOff)
    except:
        HoldOffentry.delete(0,tk.END)
        HoldOffentry.insert(0, HoldOff)

    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,tk.END)
        HozPossentry.insert(0, HozPoss)

    hldn = int(HoldOff * SAMPLErate/1000 )
    hozpos = int(HozPoss * SAMPLErate/1000 )
    if hozpos < 0:
        hozpos = 0        
    #  drawing the traces 
    if TRACEsize == 0:                          # If no trace, skip rest of this routine
        T1Vline = []                            # Trace line channel A V
        T2Vline = []                            # Trace line channel B V
        T1Iline = []
        T2Iline = []
        Tmathline = []                  # math trce line
        return() 

    # set and/or corrected for in range
    if TgInput.get() > 0:
        SCmin = int(-1 * TRIGGERsample)
        SCmax = int(TRACEsize - TRIGGERsample - 0)
    else:
        SCmin = 0 # hldn
        SCmax = TRACEsize - 1
    if SCstart < SCmin:             # No reading before start of array
        SCstart = SCmin
    if SCstart  > SCmax:            # No reading after tk.END of array
        SCstart = SCmax

    # Make Trace lines etc.
    Yconv1 = float(GRH/10.0) / CH1pdvRange    # Vertical Conversion factors from samples to screen points
    Yconv2 = float(GRH/10.0) / CH2pdvRange
    YIconv1 = float(GRH/10.0) / CH1IpdvRange
    YIconv2 = float(GRH/10.0) / CH2IpdvRange
     
    if MathAxis == "V-A":
        YconvM = Yconv1
        CHMOffset = CHAOffset
    elif MathAxis == "V-B":
        YconvM = Yconv2
        CHMOffset = CHBOffset
    elif MathAxis == "I-A":
        YconvM = YIconv1
        CHMOffset = CHAIOffset
    elif MathAxis == "I-B":
        YconvM = YIconv2
        CHMOffset = CHBIOffset
    else:
        YconvM = Yconv1
        CHMOffset = CHAOffset

    c1 = GRH / 2.0 + Y0T    # fixed correction channel A
    c2 = GRH / 2.0 + Y0T    # fixed correction channel B
 
    DISsamples = SAMPLErate * 10.0 * TIMEdiv / 1000.0 # number of samples to display
    T1Vline = []                    # V Trace line channel A
    T2Vline = []                    # V Trace line channel B
    T1Iline = []                    # I Trace line channel A
    T2Iline = []                    # I Trace line channel B

    Tmathline = []                  # math trce line
    TMXline = []                    # X math Trace line
    TMYline = []                    # Y math Trace line
    if len(VBuffA) < 4 and len(VBuffB) < 4 and len(IBuffA) < 4 and len(IBuffB) < 4:
        return
    t = int(SCstart + TRIGGERsample) # - (TriggerPos * SAMPLErate) # t = Start sample in trace
    if t < 0:
        t = 0
    x = 0                           # Horizontal screen pixel
#
    ypv1 = int(c1 - Yconv1 * (VBuffA[t] - CHAOffset))
    ypi1 = int(c1 - YIconv1 * (IBuffA[t] - CHAIOffset))
    ypv2 = int(c2 - Yconv2 * (VBuffB[t] - CHBOffset))
    ypi2 = int(c1 - YIconv2 * (IBuffB[t] - CHBIOffset))
    DvY1 = DvY2 = DiY1 = DiY2 = 0 
#
    if (DISsamples <= GRW):
        Xstep = GRW / DISsamples
        if AWGBMode.get() == 2 and Two_X_Sample.get() == 0:
            xa = int((Xstep/-2.5) - (Xstep*DX))
        else:
            xa = 0 - int(Xstep*DX)       # adjust start pixel for interpolated trigger point
        x = 0 - int(Xstep*DX)
        Tstep = 1
        x1 = 0                      # x position of trace line
        xa1 = 0
        y1 = 0.0                    # y position of trace line
        ypv1 = int(c1 - Yconv1 * (VBuffA[t] - CHAOffset))
        ytemp = IBuffA[t]
        ypi1 = int(c1 - YIconv1 * (ytemp - CHAIOffset))
        ypv2 = int(c2 - Yconv2 * (VBuffB[t] - CHBOffset))
        ytemp = IBuffB[t]
        ypi2 = int(c1 - YIconv2 * (ytemp - CHBIOffset))
        ypm = ypmx = ypmy = GRH / 2.0 + Y0T
        if TgInput.get() == 0:
            Xlimit = GRW
        else:
            Xlimit = GRW+Xstep
        while x <= Xlimit:
            if t < TRACEsize:
                xa1 = xa + X0L
                x1 = x + X0L
                y1 = int(c1 - Yconv1 * (VBuffA[t] - CHAOffset))
                ytemp = IBuffA[t]
                yi1 = int(c1 - YIconv1 * (ytemp - CHAIOffset))
                
                if y1 < Ymin: # clip waveform if going off grid
                    y1 = Ymin
                if y1 > Ymax:
                    y1 = Ymax
                if yi1 < Ymin:
                    yi1 = Ymin
                if yi1 > Ymax:
                    yi1 = Ymax
                if ShowC1_V.get() == 1 :
                    if ZOHold.get() == 1:
                        T1Vline.apptk.END(int(xa1))
                        T1Vline.apptk.END(int(ypv1))
                        T1Vline.apptk.END(int(xa1))
                        T1Vline.apptk.END(int(y1))
                    else:    
                        T1Vline.apptk.END(int(xa1))
                        T1Vline.apptk.END(int(y1))
                    DvY1 = ypv1 - y1
                    ypv1 = y1
                if ShowC1_I.get() == 1:
                    if ZOHold.get() == 1:
                        T1Iline.apptk.END(int(xa1))
                        T1Iline.apptk.END(int(ypi1))
                        T1Iline.apptk.END(int(xa1))
                        T1Iline.apptk.END(int(yi1))
                    else:
                        T1Iline.apptk.END(int(xa1))
                        T1Iline.apptk.END(int(yi1))
                    DiY1 = ypi1 - yi1
                    ypi1 = yi1
                if ShowC2_V.get() == 1:
                    y1 = int(c2 - Yconv2 * (VBuffB[t] - CHBOffset))
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1:
                        T2Vline.apptk.END(int(x1))
                        T2Vline.apptk.END(int(ypv2))
                        T2Vline.apptk.END(int(x1))
                        T2Vline.apptk.END(int(y1))
                    else:
                        T2Vline.apptk.END(int(x1))
                        T2Vline.apptk.END(int(y1))
                    DvY2 = ypv2 - y1
                    ypv2 = y1
                if ShowC2_I.get() == 1:
                    ytemp = IBuffB[t]
                    yi1 = int(c1 - YIconv2 * (ytemp - CHBIOffset))
                    if yi1 < Ymin:
                        yi1 = Ymin
                    if yi1 > Ymax:
                        yi1 = Ymax
                    if (ZOHold.get() == 1):
                        T2Iline.apptk.END(int(x1))
                        T2Iline.apptk.END(int(ypi2))
                        T2Iline.apptk.END(int(x1))
                        T2Iline.apptk.END(int(yi1))
                    else:
                        T2Iline.apptk.END(int(x1))
                        T2Iline.apptk.END(int(yi1))
                    DiY2 = ypi2 - yi1
                    ypi2 = yi1
                if MathTrace.get() > 0:
                    if MathTrace.get() == 1: # plot sum of CA-V and CB-V
                        y1 = int(c1 - Yconv1 * (VBuffA[t] + VBuffB[t] - CHAOffset))
                    elif MathTrace.get() == 2: # plot difference of CA-V and CB-V 
                        y1 = int(c1 - Yconv1 * (VBuffA[t] - VBuffB[t] - CHAOffset))
                    elif MathTrace.get() == 3: # plot difference of CB-V and CA-V 
                        y1 = int(c2 - Yconv2 * (VBuffB[t] - VBuffA[t] - CHBOffset))
                    elif MathTrace.get() == 4: # plot product of CA-V and CA-I
                        Ypower = VBuffA[t] * IBuffA[t] # mAmps * Volts = mWatts
                        ytemp = YIconv1 * (Ypower - CHAIOffset)
                        y1 = int(c1 - ytemp)
                    elif MathTrace.get() == 5: # plot product of CB-V and CB-I
                        Ypower = VBuffB[t] * IBuffB[t] # mAmps * Volts = mWatts
                        ytemp = YIconv2 * (Ypower - CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif MathTrace.get() == 6: # plot ratio of CA-V and CA-I
                        Yohms = VBuffA[t] / (IBuffA[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv1 * (Yohms - CHAIOffset)
                        y1 = int(c1 - ytemp)
                    elif MathTrace.get() == 7: # plot ratio of CB-V and CB-I
                        Yohms = VBuffB[t] / (IBuffB[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv2 * (Yohms - CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif MathTrace.get() == 8: # plot difference of CA-I and CB-I
                        Ydif = (IBuffA[t] - IBuffB[t])#  in mA
                        ytemp = YIconv1 * (Ydif - CHAIOffset)
                        y1 = int(c2 - ytemp)
                    elif MathTrace.get() == 9: # plot difference of CB-I and CA-I
                        Ydif =  (IBuffB[t] - IBuffA[t]) #  in mA
                        ytemp = YIconv2 * (Ydif - CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif MathTrace.get() == 10: # plot ratio of CB-V and CA-V
                        try:
                            y1 = int(c1 - Yconv2 * ((VBuffB[t] / VBuffA[t]) - CHBOffset)) #  voltage gain A to B
                        except:
                            y1 = int(c1 - Yconv2 * ((VBuffB[t] / 0.000001) - CHBOffset))
                    elif MathTrace.get() == 11: # plot ratio of CB-I and CA-I
                        try:
                            Y1 = (IBuffB[t] / IBuffA[t])  # current gain A to B
                        except:
                            Y1 = (IBuffB[t] / 0.000001)
                        ytemp = YIconv2 * (Y1 - CHBIOffset)
                        y1 = int(c2 - ytemp)                                         
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1: # connet the dots with stair step
                        Tmathline.apptk.END(int(x1))
                        Tmathline.apptk.END(int(ypm))
                        Tmathline.apptk.END(int(x1))
                        Tmathline.apptk.END(int(y1))
                    else:    # connet the dots with single line
                        Tmathline.apptk.END(int(x1))
                        Tmathline.apptk.END(int(y1))
                    ypm = y1
                
            # remember trace verticle pixel at X mouse location
            if MouseX - X0L >= x and MouseX - X0L < (x + Xstep): # - Xstep
                Xfine = MouseX - X0L - x
                MouseCAV = ypv1 - (DvY1 * (Xfine/Xstep)) # interpolate along yaxis 
                MouseCAI = ypi1 - (DiY1 * (Xfine/Xstep))
                MouseCBV = ypv2 - (DvY2 * (Xfine/Xstep))
                MouseCBI = ypi2 - (DiY2 * (Xfine/Xstep))
            t = int(t + Tstep)
            x = x + Xstep
            xa = xa + Xstep           
    else: #if (DISsamples > GRW): # if the number of samples is larger than the grid width need to ship over samples
        Xstep = 1
        Tstep = DISsamples / GRW      # number of samples to skip per grid pixel
        x1 = 0.0                          # x position of trace line
        ylo = 0.0                       # ymin position of trace 1 line
        yhi = 0.0                       # ymax position of trace 1 line
        t = int(SCstart + TRIGGERsample) # - (TriggerPos * SAMPLErate) # t = Start sample in trace
        if t > len(VBuffA)-1:
            t = 0
        if t < 0:
            t = 0
        x = 0               # Horizontal screen pixel
        ft = t              # time point with fractions
        while (x <= GRW):
            if (t < TRACEsize):
                if (t >= len(VBuffA)):
                    t = len(VBuffA)-2
                    x = GRW
                x1 = x + X0L
                ylo = VBuffA[t] - CHAOffset
                ilo = IBuffA[t] - CHAIOffset
                yhi = ylo
                ihi = ilo
                n = t
                while n < (t + Tstep) and n < TRACEsize:
                    if ( ShowC1_V.get() == 1 ):
                        v = VBuffA[t] - CHAOffset
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v
                    if ( ShowC1_I.get() == 1 ):
                        i = IBuffA[t] - CHAIOffset
                        if i < ilo:
                            ilo = i
                        if i > ihi:
                            ihi = i
                    n = n + 1
                if ( ShowC1_V.get() == 1 ):
                    ylo = int(c1 - Yconv1 * ylo)
                    yhi = int(c1 - Yconv1 * yhi)
                    if (ylo < Ymin):
                        ylo = Ymin
                    if (ylo > Ymax):
                        ylo = Ymax
                    if (yhi < Ymin):
                        yhi = Ymin
                    if (yhi > Ymax):
                        yhi = Ymax
                    T1Vline.apptk.END(int(x1))
                    T1Vline.apptk.END(int(ylo))        
                    T1Vline.apptk.END(int(x1))
                    T1Vline.apptk.END(int(yhi))
                    ypv1 = ylo
                if ( ShowC1_I.get() == 1 ):    
                    ilo = int(c1 - YIconv1 * ilo)
                    ihi = int(c1 - YIconv1 * ihi)
                    if (ilo < Ymin):
                        ilo = Ymin
                    if (ilo > Ymax):
                        ilo = Ymax
                    if (ihi < Ymin):
                        ihi = Ymin
                    if (ihi > Ymax):
                        ihi = Ymax
                    T1Iline.apptk.END(int(x1))
                    T1Iline.apptk.END(int(ilo))        
                    T1Iline.apptk.END(int(x1))
                    T1Iline.apptk.END(int(ihi))
                    ypi1 = ilo
                ylo = VBuffB[t] - CHBOffset
                ilo = IBuffB[t] - CHBIOffset
                yhi = ylo
                ihi = ilo
                n = t          
                while n < (t + Tstep) and n < TRACEsize:
                    if ( ShowC2_V.get() == 1 ):
                        v = VBuffB[t] - CHBOffset
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v
                    if ( ShowC2_I.get() == 1 ):
                        i = IBuffB[t] - CHBIOffset
                        if i < ilo:
                            ilo = i
                        if i > ihi:
                            ihi = i
                    n = n + 1
                if ( ShowC2_V.get() == 1 ):
                    ylo = int(c2 - Yconv2 * ylo)
                    yhi = int(c2 - Yconv2 * yhi)
                    if (ylo < Ymin):
                        ylo = Ymin
                    if (ylo > Ymax):
                        ylo = Ymax

                    if (yhi < Ymin):
                         yhi = Ymin
                    if (yhi > Ymax):
                        yhi = Ymax
                    T2Vline.apptk.END(int(x1))
                    T2Vline.apptk.END(int(ylo))        
                    T2Vline.apptk.END(int(x1))
                    T2Vline.apptk.END(int(yhi))
                    ypv2 = ylo
                if ( ShowC2_I.get() == 1 ):
                    ilo = int(c2 - YIconv2 * ilo)
                    ihi = int(c2 - YIconv2 * ihi)
                    if (ilo < Ymin):
                        ilo = Ymin
                    if (ilo > Ymax):
                        ilo = Ymax
                    if (ihi < Ymin):
                        ihi = Ymin
                    if (ihi > Ymax):
                        ihi = Ymax
                    T2Iline.apptk.END(int(x1))
                    T2Iline.apptk.END(int(ilo))        
                    T2Iline.apptk.END(int(x1))
                    T2Iline.apptk.END(int(ihi))
                    ypi2 = ilo
                
                if MathTrace.get() > 0:
                    if MathTrace.get() == 1: # plot sum of CA-V and CB-V
                        y1 = int(c1 - Yconv1 * (VBuffA[t] + VBuffB[t] - CHAOffset))
                    elif MathTrace.get() == 2: # plot difference of CA-V and CB-V 
                        y1 = int(c1 - Yconv1 * (VBuffA[t] - VBuffB[t] - CHAOffset))
                    elif MathTrace.get() == 3: # plot difference of CB-V and CA-V 
                        y1 = int(c2 - Yconv2 * (VBuffB[t] - VBuffA[t] - CHBOffset))
                    elif MathTrace.get() == 4: # plot product of CA-V and CA-I
                        Ypower = VBuffA[t] * IBuffA[t] # mAmps * Volts = mWatts
                        ytemp = YIconv1 * (Ypower - CHAIOffset)
                        y1 = int(c1 - ytemp)                                            
                    elif MathTrace.get() == 5: # plot product of CB-V and CB-I
                        Ypower = VBuffB[t] * IBuffB[t] # mAmps * Volts = mWatts
                        ytemp = YIconv2 * (Ypower - CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif MathTrace.get() == 6: # plot ratio of CA-V and CA-I
                        Yohms = VBuffA[t] / (IBuffA[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv1 * (Yohms- CHAIOffset)
                        y1 = int(c1 - ytemp)
                    elif MathTrace.get() == 7: # plot ratio of CB-V and CB-I
                        Yohms = VBuffB[t] / (IBuffB[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv2 * (Yohms - CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif MathTrace.get() == 8: # plot difference of CA-I and CB-I
                        Ydif = (IBuffA[t] - IBuffB[t]) #  in mA
                        ytemp = YIconv1 * (Ydif - CHAIOffset)
                        y1 = int(c2 - ytemp)
                    elif MathTrace.get() == 9: # plot difference of CB-I and CA-I
                        Ydif = (IBuffB[t] - IBuffA[t])  # in mA
                        ytemp = YIconv2 * (Ydif - CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif MathTrace.get() == 10: # plot ratio of CB-V and CA-V
                        try:
                            y1 = int(c1 - Yconv2 * ((VBuffB[t] / VBuffA[t]) - CHBOffset)) #  voltage gain A to B
                        except:
                            y1 = int(c1 - Yconv2 * ((VBuffB[t] / 0.000001) - CHBOffset))
                    elif MathTrace.get() == 11: # plot ratio of CB-I and CA-I
                        try:
                            Y1 = (IBuffB[t] / IBuffA[t]) # current gain A to B
                        except:
                            Y1 = (IBuffB[t] / 0.000001)
                        ytemp = YIconv2 * (Y1 - CHBIOffset)
                        y1 = int(c2 - ytemp)
                      
                    if (y1 < Ymin):
                        y1 = Ymin
                    if (y1 > Ymax):
                        y1 = Ymax
                    if (ZOHold.get() == 1):
                        Tmathline.apptk.END(int(x1))
                        Tmathline.apptk.END(int(ypm))
                        Tmathline.apptk.END(int(x1))
                        Tmathline.apptk.END(int(y1))
                    else:    
                        Tmathline.apptk.END(int(x1))
                        Tmathline.apptk.END(int(y1))
                    ypm = y1
                
            ft = ft + Tstep
            if (MouseX - X0L) == x: # > (x - 1) and (MouseX - X0L) < (x + 1):
                MouseCAV = ypv1
                MouseCAI = ypi1
                MouseCBV = ypv2
                MouseCBI = ypi2
            t = int(ft)
            if (t > len(VBuffA)):
                t = len(VBuffA)-2
                x = GRW
            x = x + Xstep

    # Make trigger triangle pointer
    Triggerline = []                # Trigger pointer
    Triggersymbol = []                # Trigger symbol
    if TgInput.get() > 0:
        if TgInput.get() == 1 : # triggering on CA-V
            x1 = X0L
            ytemp = Yconv1 * (float(TRIGGERlevel)-CHAOffset) # / InGainA
            y1 = int(c1 - ytemp)
        elif TgInput.get() == 2:  # triggering on CA-I
            x1 = X0L+GRW
            y1 = int(c1 - YIconv1 * (float(TRIGGERlevel) - CHAIOffset))
        elif TgInput.get() == 3:  # triggering on CB-V
            x1 = X0L
            ytemp = Yconv2 * (float(TRIGGERlevel)-CHBOffset) # / InGainB         
            y1 = int(c2 - ytemp)
        elif TgInput.get() == 4: # triggering on CB-I
            x1 = X0L+GRW
            y1 = int(c2 - YIconv2 * (float(TRIGGERlevel) - CHBIOffset))
            
        if (y1 < Ymin):
            y1 = Ymin
        if (y1 > Ymax):
            y1 = Ymax
        Triggerline.apptk.END(int(x1-5))
        Triggerline.apptk.END(int(y1+5))
        Triggerline.apptk.END(int(x1+5))
        Triggerline.apptk.END(int(y1))
        Triggerline.apptk.END(int(x1-5))
        Triggerline.apptk.END(int(y1-5))
        Triggerline.apptk.END(int(x1-5))
        Triggerline.apptk.END(int(y1+5))
        x1 = X0L + (GRW/2)
        if TgEdge.get() == 0: # draw rising edge symbol
            y1 = -3
            y2 = -13
        else:
            y1 = -13
            y2 = -3
        Triggersymbol.apptk.END(int(x1-10))
        Triggersymbol.apptk.END(int(Ymin+y1))
        Triggersymbol.apptk.END(int(x1))
        Triggersymbol.apptk.END(int(Ymin+y1))
        Triggersymbol.apptk.END(int(x1))
        Triggersymbol.apptk.END(int(Ymin+y2))
        Triggersymbol.apptk.END(int(x1+10))
        Triggersymbol.apptk.END(int(Ymin+y2))

## Update the time screen with traces and text   
def MakeTimeScreen():     
    global T1Vline, T2Vline, T1Iline, T2Iline # active trave lines
    global Triggerline, Triggersymbol, Tmathline
    global VBuffA, VBuffB, IBuffA, IBuffB 
    global VmemoryA, VmemoryB
    global X0L          # Left top X value
    global Y0T          # Left top Y value
    global GRW          # Screenwidth
    global GRH          # Screenheight
    global Ymin, Ymax
    global FontSize

    global MouseX, MouseY, MouseWidget, MouseCAV, MouseCAI, MouseCBV, MouseCBI
    global ShowXCur, ShowYCur, TCursor, VCursor
    global SHOWsamples  # Number of samples in data record
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I, ShowMath
    global RUNstatus, SingleShot, ManualTrigger, session    
    global CHAsb        # V range spinbox Index for channel 1
    global CHBsb        # V range spinbox Index for channel 2
    global CHAOffset    # Position value for channel 1 V
    global CHBOffset    # Position value for channel 2 V
    global CHAIsb       # I range spinbox Index for channel 1
    global CHBIsb       # I range spinbox Index for channel 2
    global CHAIOffset   # Postion value for channel 1 I
    global CHBIOffset   # position value for channel 2 I     
    global TMsb         # Time per div spin box variable
    global TIMEdiv, Mulx, DISsamples      # current spin box value
    global SAMPLErate, contloop, discontloop, HtMulEntry
    global TRIGGERsample, TRIGGERlevel, HoldOff, HoldOffentry, TgInput
    global COLORgrid, COLORzeroline, COLORtext, COLORtrigger, COLORtrace7, COLORtraceR7 # The colors
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, COLORtrace5, COLORtrace6
    global COLORtraceR1, COLORtraceR2, COLORtraceR3, COLORtraceR4, COLORtraceR5, COLORtraceR6
    global CANVASwidth
    global TRACErefresh, TRACEmode, TRACEwidth, GridWidth
    global ScreenTrefresh, SmoothCurves, Is_Triggered
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2, CHAHW, CHALW, CHADCy, CHAperiod, CHAfreq
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2, CHBHW, CHBLW, CHBDCy, CHBperiod, CHBfreq
    global InOffA, InGainA, InOffB, InGainB
    global CurOffA, CurOffB, CurGainA, CurGainB
    global SV1, SI1, SV2, SI2, CHABphase, SVA_B
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1
    global MeasDCI1, MeasMinI1, MeasMaxI1, MeasMidI1, MeasPPI1
    global MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2, MeasPPV2
    global MeasDCI2, MeasMinI2, MeasMaxI2, MeasMidI2, MeasPPI2
    global MeasRMSV1, MeasRMSI1, MeasRMSV2, MeasRMSI2, MeasPhase, MeasRMSVA_B
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global AWGAShape, AWGBShape, MeasDiffAB, MeasDiffBA 
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAIPosEntry, CHAVPosEntry, CHBIPosEntry
    global CH1pdvRange, CHAOffset, CH2pdvRange, CHBOffset
    global DevID, devx, MarkerNum, MarkerScale, MeasGateLeft, MeasGateRight, MeasGateStatus
    global HozPoss, HozPossentry
    global VABase, VATop, VBBase, VBTop
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2, MeasUserA, MeasUserB
    global CHBADelayR1, CHBADelayR2, CHBADelayF, MeasDelay
    #
    Ymin = Y0T                  # Minimum position of time grid (top)
    Ymax = Y0T + GRH            # Maximum position of time grid (bottom)
    Tstep = (10.0 * TIMEdiv) / GRW # time in mS per pixel
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
    try:
        HoldOff = float(eval(HoldOffentry.get()))
        if HoldOff < 0:
            HoldOff = 0
    except:
        HoldOffentry.delete(0,tk.END)
        HoldOffentry.insert(0, HoldOff)


    Mulx = 1
    # slide trace left right by HozPoss
    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,tk.END)
        HozPossentry.insert(0, HozPoss)
        
    # prevent divide by zero error
    if CH1pdvRange < 0.001:
        CH1pdvRange = 0.001
    if CH2pdvRange < 0.001:
        CH2pdvRange = 0.001
    if CH1IpdvRange < 0.1:
        CH1IpdvRange = 0.1
    if CH2IpdvRange < 0.1:
        CH2IpdvRange = 0.1
    vt = HoldOff + HozPoss # invert sign and scale to mSec
    if ScreenTrefresh.get() == 0:
        # Delete all items on the screen
        ca.delete(tk.ALL) # remove all items
        MarkerNum = 0
        # Draw horizontal grid lines
        i = 0
        x1 = X0L
        x2 = X0L + GRW
        mg_siz = GRW/10.0
        mg_inc = mg_siz/5.0
        MathFlag1 = (MathAxis == "V-A" and MathTrace.get() == 12)
        MathFlag2 = (MathAxis == "V-B" and MathTrace.get() == 12)
        MathFlag3 = (MathAxis == "I-A" and MathTrace.get() == 12)
        MathFlag4 = (MathAxis == "I-B" and MathTrace.get() == 12)
        # vertical scale text labels
        RightOffset = FontSize * 3
        LeftOffset = int(FontSize/2)
        if (ShowC1_V.get() == 1 or MathTrace.get() == 1 or MathTrace.get() == 2 or MathFlag1):
            ca.create_text(x1-LeftOffset, 12, text="CA-V", fill=COLORtrace1, anchor="e", font=("arial", FontSize-1 ))
        if (ShowC1_I.get() == 1 or MathTrace.get() == 4 or MathTrace.get() == 6 or MathTrace.get() == 8 or MathFlag3):
            ca.create_text(x2+LeftOffset, 12, text="CA-I", fill=COLORtrace3, anchor="w", font=("arial", FontSize-1 ))
        if (ShowC2_V.get() == 1 or MathTrace.get() == 3 or MathTrace.get() == 10 or MathFlag2):
            ca.create_text(x1-RightOffset+2, 12, text="CB-V", fill=COLORtrace2, anchor="e", font=("arial", FontSize-1 )) #26
        if (ShowC2_I.get() == 1 or MathTrace.get() == 5 or MathTrace.get() == 7 or MathTrace.get() == 9 or MathTrace.get() == 11 or MathFlag4):
            ca.create_text(x2+RightOffset+4, 12, text="CB-I", fill=COLORtrace4, anchor="w", font=("arial", FontSize-1 )) #28
        #
        while (i < 11):
            y = Y0T + i * GRH/10.0
            Dline = [x1,y,x2,y]
            if i == 5:
                ca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue line at center of grid
                k = 0
                while (k < 10):
                    l = 1
                    while (l < 5):
                        Dline = [x1+k*mg_siz+l*mg_inc,y-5,x1+k*mg_siz+l*mg_inc,y+5]
                        ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
            else:
                ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())

            if (ShowC1_V.get() == 1 or MathTrace.get() == 1 or MathTrace.get() == 2 or MathFlag1):
                Vaxis_value = (((5-i) * CH1pdvRange ) + CHAOffset)
                # Vaxis_label = ' {0:.2f} '.format(Vaxis_value)
                Vaxis_label = str(round(Vaxis_value,3 ))
                ca.create_text(x1-LeftOffset, y, text=Vaxis_label, fill=COLORtrace1, anchor="e", font=("arial", FontSize ))
                
            if (ShowC1_I.get() == 1 or MathTrace.get() == 4 or MathTrace.get() == 6 or MathTrace.get() == 8 or MathFlag3):
                Iaxis_value = 1.0 * (((5-i) * CH1IpdvRange ) + CHAIOffset)
                Iaxis_label = str(round(Iaxis_value, 3))
                ca.create_text(x2+LeftOffset, y, text=Iaxis_label, fill=COLORtrace3, anchor="w", font=("arial", FontSize ))
                
            if (ShowC2_V.get() == 1 or MathTrace.get() == 3 or MathTrace.get() == 10 or MathFlag2):
                Vaxis_value = (((5-i) * CH2pdvRange ) + CHBOffset)
                Vaxis_label = str(round(Vaxis_value, 3))
                ca.create_text(x1-RightOffset+2, y, text=Vaxis_label, fill=COLORtrace2, anchor="e", font=("arial", FontSize )) # 26
                
            if (ShowC2_I.get() == 1 or MathTrace.get() == 5 or MathTrace.get() == 7 or MathTrace.get() == 9 or MathTrace.get() == 11 or MathFlag4):
                Iaxis_value = 1.0 * (((5-i) * CH2IpdvRange ) + CHBIOffset)
                Iaxis_label = str(round(Iaxis_value, 3))
                ca.create_text(x2+RightOffset+4, y, text=Iaxis_label, fill=COLORtrace4, anchor="w", font=("arial", FontSize )) # 28
            i = i + 1
        # Draw vertical grid lines
        i = 0
        y1 = Y0T
        y2 = Y0T + GRH
        mg_siz = GRH/10.0
        mg_inc = mg_siz/5.0
        vx = TIMEdiv/Mulx
        vt = HoldOff/Mulx # invert sign and scale to mSec
        # vx = TIMEdiv
        while (i < 11):
            x = X0L + i * GRW/10.0
            Dline = [x,y1,x,y2]
            if (i == 5):
                ca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue vertical line at center of grid
                k = 0
                while (k < 10):
                    l = 1
                    while (l < 5):
                        Dline = [x-5,y1+k*mg_siz+l*mg_inc,x+5,y1+k*mg_siz+l*mg_inc]
                        ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
    #
                if vx >= 1000:
                    axis_value = ((i * vx)+ vt) / 1000.0
                    axis_label = ' {0:.1f} '.format(axis_value) + " S"
                if vx < 1000 and vx >= 1:
                    axis_value = (i * vx) + vt
                    axis_label = ' {0:.1f} '.format(axis_value) + " mS"
                if vx < 1:
                    axis_value = ((i * vx) + vt) * 1000.0
                    axis_label = ' {0:.1f} '.format(axis_value) + " uS"
                ca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", FontSize ))
            else:
                ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                if vx >= 1000:
                    axis_value = ((i * vx)+ vt) / 1000.0
                    axis_label = ' {0:.1f} '.format(axis_value) + " S"
                if vx < 1000 and vx >= 1:
                    axis_value = (i * vx) + vt
                    axis_label = ' {0:.1f} '.format(axis_value) + " mS"
                if vx < 1:
                    axis_value = ((i * vx) + vt) * 1000.0
                    axis_label = ' {0:.1f} '.format(axis_value) + " uS"
                ca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", FontSize ))
                        
            i = i + 1
    # Write the trigger line if available
    if len(Triggerline) > 2:                    # Avoid writing lines with 1 coordinate
        ca.create_polygon(Triggerline, outline=COLORtrigger, fill=COLORtrigger, width=1)
        ca.create_line(Triggersymbol, fill=COLORtrigger, width=GridWidth.get())
        if TgInput.get() == 1:
            TgLabel = "CA-V"
        if TgInput.get() == 2:
            TgLabel = "CA-I"
        if TgInput.get() == 3:
            TgLabel = "CB-V"
        if TgInput.get() == 4:
            TgLabel = "CB-I"
        if Is_Triggered == 1:
            TgLabel = TgLabel + " Triggered"
        else:
            TgLabel = TgLabel + " Not Triggered"
            if SingleShot.get() > 0:
                TgLabel = TgLabel + " Armed"
        x = X0L + (GRW/2) + 12
        ca.create_text(x, Ymin-FontSize, text=TgLabel, fill=COLORtrigger, anchor="w", font=("arial", FontSize ))
    # Draw T - V Cursor lines if required
    if MarkerScale.get() == 0:
        Yconv1 = float(GRH/10.0) / CH1pdvRange
        Yoffset1 = CHAOffset
        COLORmarker = COLORtrace1
        Units = " V"
    if MarkerScale.get() == 1:
        MouseY = MouseCAV
        Yconv1 = float(GRH/10.0) / CH1pdvRange
        Yoffset1 = CHAOffset
        COLORmarker = COLORtrace1
        Units = " V"
    if MarkerScale.get() == 2:
        MouseY = MouseCBV
        Yconv1 = float(GRH/10.0) / CH2pdvRange
        Yoffset1 = CHBOffset
        COLORmarker = COLORtrace2
        Units = " V"
    if MarkerScale.get() == 3:
        MouseY = MouseCAI
        Yconv1 = float(GRH/10.0) / CH1IpdvRange
        Yoffset1 = CHAIOffset
        COLORmarker = COLORtrace3
        Units = " mA"
    if MarkerScale.get() == 4:
        MouseY = MouseCBI
        Yconv1 = float(GRH/10.0) / CH2IpdvRange
        Yoffset1 = CHBIOffset
        COLORmarker = COLORtrace4
        Units = " mA"
    if ShowTCur.get() > 0:
        Dline = [TCursor, Y0T, TCursor, Y0T+GRH]
        ca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
        Tpoint = ((TCursor-X0L) * Tstep) + vt
        Tpoint = Tpoint/Mulx
        if Tpoint >= 1000:
            axis_value = Tpoint / 1000.0
            V_label = ' {0:.2f} '.format(axis_value) + " S"
        if Tpoint < 1000 and Tpoint >= 1:
            axis_value = Tpoint
            V_label = ' {0:.2f} '.format(axis_value) + " mS"
        if Tpoint < 1:
            axis_value = Tpoint * 1000.0
            V_label = ' {0:.2f} '.format(axis_value) + " uS"
        ca.create_text(TCursor+1, VCursor-5, text=V_label, fill=COLORtext, anchor="w", font=("arial", FontSize ))
    if ShowVCur.get() > 0:
        Dline = [X0L, VCursor, X0L+GRW, VCursor]
        ca.create_line(Dline, dash=(4,3), fill=COLORmarker, width=GridWidth.get())
        c1 = GRH / 2 + Y0T    # fixed Y correction 
        yvolts = ((VCursor-c1)/Yconv1) - Yoffset1
        V1String = ' {0:.3f} '.format(-yvolts)
        V_label = V1String + Units
        ca.create_text(TCursor+1, VCursor+5, text=V_label, fill=COLORmarker, anchor="w", font=("arial", FontSize ))
    if ShowTCur.get() == 0 and ShowVCur.get() == 0 and MouseWidget == ca:
        if MouseX > X0L and MouseX < X0L+GRW and MouseY > Y0T and MouseY < Y0T+GRH:
            Dline = [MouseX, Y0T, MouseX, Y0T+GRH]
            ca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            Tpoint = ((MouseX-X0L) * Tstep) + vt
            Tpoint = Tpoint/Mulx
            if Tpoint >= 1000:
                axis_value = Tpoint / 1000.0
                V_label = ' {0:.2f} '.format(axis_value) + " S"
            if Tpoint < 1000 and Tpoint >= 1:
                axis_value = Tpoint
                V_label = ' {0:.2f} '.format(axis_value) + " mS"
            if Tpoint < 1:
                axis_value = Tpoint * 1000.0
                V_label = ' {0:.2f} '.format(axis_value) + " uS"
            ca.create_text(MouseX+1, MouseY-5, text=V_label, fill=COLORtext, anchor="w", font=("arial", FontSize ))
            Dline = [X0L, MouseY, X0L+GRW, MouseY]
            ca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            c1 = GRH / 2 + Y0T    # fixed Y correction 
            yvolts = ((MouseY-c1)/Yconv1) - Yoffset1
            V1String = ' {0:.3f} '.format(-yvolts)
            V_label = V1String + Units
            ca.create_text(MouseX+1, MouseY+5, text=V_label, fill=COLORmarker, anchor="w", font=("arial", FontSize ))
#
    if MeasGateStatus.get() == 1:
        LeftGate = X0L + MeasGateLeft / Tstep
        RightGate = X0L + MeasGateRight / Tstep
        ca.create_line(LeftGate, Y0T, LeftGate, Y0T+GRH, dash=(5,3), width=GridWidth.get(), fill=COLORtrace5)
        ca.create_line(RightGate, Y0T, RightGate, Y0T+GRH, dash=(5,3), width=GridWidth.get(), fill=COLORtrace7)
        #
        # TString = ' {0:.2f} '.format(Tpoint)
        DT = (MeasGateRight-MeasGateLeft)/Mulx
        if DT == 0.0:
            DT = 1.0
        if DT >= 1000:
            axis_value = DT / 1000.0
            DeltaT = ' {0:.2f} '.format(axis_value) + " S "
        if DT < 1000 and DT >= 1:
            axis_value = DT
            DeltaT = ' {0:.2f} '.format(axis_value) + " mS "
        if DT < 1:
            axis_value = DT * 1000.0
            DeltaT = ' {0:.2f} '.format(axis_value) + " uS "
        # DeltaT = ' {0:.3f} '.format(Tpoint-PrevT)
        DFreq = ' {0:.3f} '.format(1.0/DT)
        V_label = " Delta T" + DeltaT
        #V_label = V_label + Units
        V_label = V_label + ", Freq " + DFreq + " KHz"
        # place in upper left unless specified otherwise
        x = X0L + 5
        y = Y0T + 7
        Justify = 'w'
        if MarkerLoc == 'UR' or MarkerLoc == 'ur':
            x = X0L + GRW - 5
            y = Y0T + 7
            Justify = 'e'
        if MarkerLoc == 'LL' or MarkerLoc == 'll':
            x = X0L + 5
            y = Y0T + GRH + 7 - (MarkerNum*10)
            Justify = 'w'
        if MarkerLoc == 'LR' or MarkerLoc == 'lr':
            x = X0L + GRW - 5
            y = Y0T + GRH + 7
            Justify = 'e'
        ca.create_text(x, y, text=V_label, fill=COLORtrace5, anchor=Justify, font=("arial", FontSize ))
        #
#
    SmoothBool = SmoothCurves.get()
    # Write the traces if available
    if len(T1Vline) > 4: # Avoid writing lines with 1 coordinate    
        ca.create_line(T1Vline, fill=COLORtrace1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())   # Write the voltage trace 1
    if len(T1Iline) > 4: # Avoid writing lines with 1 coordinate
        ca.create_line(T1Iline, fill=COLORtrace3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())   # Write the current trace 1
    if len(T2Vline) > 4: # Write the trace 2 if active
        ca.create_line(T2Vline, fill=COLORtrace2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(T2Iline) > 4:
        ca.create_line(T2Iline, fill=COLORtrace4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(Tmathline) > 4 and MathTrace.get() > 0: # Write Math tace if active
        ca.create_line(Tmathline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())

    # General information on top of the grid
    # Sweep information
    if session.continuous:
        sttxt = "Running Continuous"
    else:
        sttxt = "Running Discontinuous"
    if TRACEmodeTime.get() == 1:
        sttxt = sttxt + " Averaging"
    if ManualTrigger.get() == 1:
        sttxt = "Manual Trigger"
    if (RUNstatus.get() == 0) or (RUNstatus.get() == 3):
        sttxt = "Stopped"
    if ScreenTrefresh.get() == 1:
        sttxt = sttxt + " Persistance ON"
        # Delete text at bottom of screen
        de = ca.find_enclosed( X0L-1, Y0T+GRH+12, CANVASwidth, Y0T+GRH+100)
        for n in de: 
            ca.delete(n)
        # Delete text at top of screen
        de = ca.find_enclosed( X0L-1, -1, CANVASwidth, 20)
        for n in de: 
            ca.delete(n)
    else:
        txt = "Device ID " + DevID[17:31] + " Sample rate: " + str(SAMPLErate) + " " + sttxt
    x = X0L+2
    y = 12
    ca.create_text(x, y, text=txt, anchor=tk.W, fill=COLORtext)
    # digital I/O indicators
    x2 = X0L + GRW
    #BoxColor = "#808080"   # gray
    
    # Time sweep information and view at information
    vx = TIMEdiv/Mulx
    if vx >= 1000:
        txt = ' {0:.2f} '.format(vx / 1000.0) + " S/div"
    if vx < 1000 and vx >= 1:
        txt = ' {0:.2f} '.format(vx) + " mS/div"
    if vx < 1:
        txt = ' {0:.2f} '.format(vx * 1000.0) + " uS/div"

    txt = txt + "  "
    #
    txt = txt + "View at "
    if abs(vt) >= 1000:
        txt = txt + str(int(vt / 1000.0)) + " S "
    if abs(vt) < 1000 and abs(vt) >= 1:
        txt = txt + str(int(vt)) + " mS "
    if abs(vt) < 1:
        txt = txt + str(int(vt * 1000.0)) + " uS "
    # print period and frequency of displayed channels
    if ShowC1_V.get() == 1 or ShowC2_V.get() == 1:
        FindRisingEdge(VBuffA,VBuffB)
        if ShowC1_V.get() == 1:
            if MeasAHW.get() == 1:
                txt = txt + " CA Hi Width = " + ' {0:.3f} '.format(CHAHW/Mulx) + " mS "
            if MeasALW.get() == 1:
                txt = txt + " CA Lo Width = " + ' {0:.3f} '.format(CHALW/Mulx) + " mS "
            if MeasADCy.get() == 1:
                txt = txt + " CA DutyCycle = " + ' {0:.1f} '.format(CHADCy) + " % "
            if MeasAPER.get() == 1:
                txt = txt + " CA Period = " + ' {0:.3f} '.format(CHAperiod/Mulx) + " mS "
            if MeasAFREQ.get() == 1:
                txt = txt + " CA Freq = "
                ChaF = CHAfreq*Mulx
                if ChaF < 1000:
                    V1String = ' {0:.1f} '.format(ChaF)
                    txt = txt + str(V1String) + " Hz "
                if ChaF > 1000 and ChaF < 1000000:
                    V1String = ' {0:.1f} '.format(ChaF/1000)
                    txt = txt + str(V1String) + " KHz "
                if ChaF > 1000000:
                    V1String = ' {0:.1f} '.format(ChaF/1000000)
                    txt = txt + str(V1String) + " MHz "
                #txt = txt + " CA Freq = " + ' {0:.1f} '.format(CHAfreq) + " Hz "
        if ShowC2_V.get() == 1:
            if MeasBHW.get() == 1:
                txt = txt + " CB Hi Width = " + ' {0:.3f} '.format(CHBHW/Mulx) + " mS "
            if MeasBLW.get() == 1:
                txt = txt + " CB Lo Width = " + ' {0:.3f} '.format(CHBLW/Mulx) + " mS "
            if MeasBDCy.get() == 1:
                txt = txt + " CB DutyCycle = " + ' {0:.1f} '.format(CHBDCy) + " % "
            if MeasBPER.get() == 1:
                txt = txt + " CB Period = " + ' {0:.3f} '.format(CHBperiod/Mulx) + " mS "
            if MeasBFREQ.get() == 1:
                txt = txt + " CB Freq = "
                ChaF = CHBfreq*Mulx
                if ChaF < 1000:
                    V1String = ' {0:.1f} '.format(ChaF)
                    txt = txt + str(V1String) + " Hz "
                if ChaF > 1000 and ChaF < 1000000:
                    V1String = ' {0:.1f} '.format(ChaF/1000)
                    txt = txt + str(V1String) + " KHz "
                if ChaF > 1000000:
                    V1String = ' {0:.1f} '.format(ChaF/1000000)
                    txt = txt + str(V1String) + " MHz "
                #txt = txt + " CB Freq = " + ' {0:.1f} '.format(CHBfreq) + " Hz "
        if MeasPhase.get() == 1:
            txt = txt + " CA-B Phase = " + ' {0:.1f} '.format(CHABphase) + " deg "
        if MeasDelay.get() == 1:
            txt = txt + " CB-A Delay = " + ' {0:.3f} '.format(CHBADelayR1) + " mS "    
         
    x = X0L
    y = Y0T+GRH+int(2.5 *FontSize) # 20
    ca.create_text(x, y, text=txt, anchor=tk.W, fill=COLORtext)

    txt = " "
    if ShowC1_V.get() == 1:
    # Channel A information
        if CHA_RC_HP.get() == 1:
            txt = "CHA: HP "
        else:
            txt = "CHA: "
        txt = txt + str(CH1pdvRange) + " V/div"
        if MeasDCV1.get() == 1: 
            txt = txt + " AvgV = " + ' {0:.4f} '.format(DCV1)
        if MeasMaxV1.get() == 1:
            txt = txt +  " MaxV = " + ' {0:.4f} '.format(MaxV1)
        if MeasTopV1.get() == 1:
            txt = txt +  " Top = " + ' {0:.4f} '.format(VATop)
        if MeasMinV1.get() == 1:
            txt = txt +  " MinV = " + ' {0:.4f} '.format(MinV1)
        if MeasBaseV1.get() == 1:
            txt = txt +  " Base = " + ' {0:.4f} '.format(VABase)
        if MeasMidV1.get() == 1:
            MidV1 = (MaxV1+MinV1)/2.0
            txt = txt +  " MidV = " + ' {0:.4f} '.format(MidV1)
        if MeasPPV1.get() == 1:
            PPV1 = MaxV1-MinV1
            txt = txt +  " P-PV = " + ' {0:.4f} '.format(PPV1)
        if MeasRMSV1.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SV1)
        if MeasRMSVA_B.get() == 1:
            txt = txt +  " A-B RMS = " + ' {0:.4f} '.format(SVA_B)
        if MeasDiffAB.get() == 1:
            txt = txt +  " CA-CB = " + ' {0:.4f} '.format(DCV1-DCV2)
    if (ShowC1_I.get() == 1 and ShowC1_V.get() == 0):
        txt = "CHA: "
        txt = txt + str(CH1IpdvRange) + " mA/div"
    elif (ShowC1_I.get() == 1 and ShowC1_V.get() == 1):
        txt = txt + "CHA: "
        txt = txt + str(CH1IpdvRange) + " mA/div"
    if ShowC1_I.get() == 1:
        if MeasDCI1.get() == 1:
            V1String = ' {0:.2f} '.format(DCI1)
            txt = txt + " AvgI = " + V1String
            if AWGAShape.get() == 0: # if this is a DC measurement calc resistance
                try:
                    Resvalue = (DCV1/DCI1)*1000
                    txt = txt + " Res = " + ' {0:.1f} '.format(Resvalue)
                except:
                    txt = txt + " Res = OverRange" 
        if MeasMaxI1.get() == 1:
            txt = txt +  " MaxI = " + ' {0:.2f} '.format(MaxI1)
        if MeasMinI1.get() == 1:
            txt = txt +  " MinI = " + ' {0:.2f} '.format(MinI1)
        if MeasMidI1.get() == 1:
            MidI1 = (MaxI1+MinI1)/2.0
            txt = txt +  " MidV = " + ' {0:.2f} '.format(MidI1)
        if MeasPPI1.get() == 1:
            PPI1 = MaxI1-MinI1 
            txt = txt +  " P-PI = " + ' {0:.2f} '.format(PPI1)
        if MeasRMSI1.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SI1)
        
    x = X0L
    y = Y0T+GRH+(4*FontSize) # 32
    ca.create_text(x, y, text=txt, anchor=tk.W, fill=COLORtext)
    txt= " "
    # Channel B information
    if ShowC2_V.get() == 1:
        if CHB_RC_HP.get() == 1:
            txt = "CHB: HP "
        else:
            txt = "CHB: "
        txt = txt + str(CH2pdvRange) + " V/div"
        if MeasDCV2.get() == 1:
            txt = txt + " AvgV = " + ' {0:.4f} '.format(DCV2)
        if MeasMaxV2.get() == 1:
            txt = txt +  " MaxV = " + ' {0:.4f} '.format(MaxV2)
        if MeasTopV2.get() == 1:
            txt = txt +  " Top = " + ' {0:.4f} '.format(VBTop)
        if MeasMinV2.get() == 1:
            txt = txt +  " MinV = " + ' {0:.4f} '.format(MinV2)
        if MeasBaseV2.get() == 1:
            txt = txt +  " Base = " + ' {0:.4f} '.format(VBBase)
        if MeasMidV2.get() == 1:
            MidV2 = (MaxV2+MinV2)/2.0
            txt = txt +  " MidV = " + ' {0:.4f} '.format(MidV2)
        if MeasPPV2.get() == 1:
            PPV2 = MaxV2-MinV2
            txt = txt +  " P-PV = " + ' {0:.4f} '.format(PPV2)
        if MeasRMSV2.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SV2)
        if MeasDiffBA.get() == 1:
            txt = txt +  " CB-CA = " + ' {0:.4f} '.format(DCV2-DCV1)
    if (ShowC2_I.get() == 1 and ShowC2_V.get() == 0):
        txt = "CHB: "
        txt = txt + str(CH2IpdvRange) + " mA/div"
    elif (ShowC2_I.get() == 1 and ShowC2_V.get() == 1):
        txt = txt + "CHB: "
        txt = txt + str(CH2IpdvRange) + " mA/div"
    if ShowC2_I.get() == 1:
        if MeasDCI2.get() == 1:
            V1String = ' {0:.2f} '.format(DCI2)
            txt = txt + " AvgI = " + V1String
            if AWGBShape.get() == 0: # if this is a DC measurement calc resistance
                try:
                    Resvalue = (DCV2/DCI2)*1000
                    R1String = ' {0:.1f} '.format(Resvalue)
                    txt = txt + " Res = " + R1String
                except:
                    txt = txt + " Res = OverRange" 
        if MeasMaxI2.get() == 1:
            txt = txt +  " MaxI = " + ' {0:.2f} '.format(MaxI2)
        if MeasMinI2.get() == 1:
            txt = txt +  " MinI = " + ' {0:.2f} '.format(MinI2)
        if MeasMidI2.get() == 1:
            MidI2 = (MaxI2+MinI2)/2.0
            txt = txt +  " MidV = " + ' {0:.2f} '.format(MidI2)
        if MeasPPI2.get() == 1:
            PPI2 = MaxI2-MinI2
            txt = txt +  " P-PI = " + ' {0:.2f} '.format(PPI2)
        if MeasRMSI2.get() == 1:
            txt = txt +  " RMS = " + ' {0:.4f} '.format(SI2)
            
    x = X0L
    y = Y0T+GRH+int(5.5*FontSize) # 44
    ca.create_text(x, y, text=txt, anchor=tk.W, fill=COLORtext)