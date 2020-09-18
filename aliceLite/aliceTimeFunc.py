#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gehört zu aliceLite
S. Mack, 15.9.20
"""
import tkinter as tk
import config as cf
import logging

## Trace line Array Variables used
T1Vline = []                # Voltage Trace line channel A
T2Vline = []                # Voltage Trace line channel B
T1Iline = []                # Current Trace line channel A
T2Iline = []                # Current Trace line channel B
Tmathline = []              # Math trace line
Triggerline = []            # Triggerline
Triggersymbol = []          # Trigger symbol
MathAxis = "V-A"
MouseCAV = MouseCAI = MouseCBV = MouseCBI = -10
DISsamples = cf.GRW # Number of samples to display

## Make the scope time traces
def MakeTimeTrace():
    logging.warning('MakeTimeTrace()')
    global T1Vline, T2Vline, T1Iline, T2Iline
    global TMAVline, TMBVline, TMCVline, TMDVline
    global Tmathline, TMXline, TMYline
    global MathAxis
    global Triggerline, Triggersymbol
    global MouseCAV, MouseCAI, MouseCBV, MouseCBI    
    global SCstart, DISsamples
    global CurOffA, CurOffB, CurGainA, CurGainB

    if len(cf.VBuffA) < 100:
        return

    SCstart = 0 # Index für Zeitpunkt 0
    ylo = 0.0
    Ymin = cf.Y0T # Minimum position of time grid (top)
    Ymax = cf.Y0T + cf.GRH # Maximum position of time grid (bottom)
    # prevent divide by zero error
    if cf.TIMEdiv < 0.0002:
        cf.TIMEdiv = 0.01
    try:
        cf.CHAVScale = float(eval(cf.CHAsb.get()))
    except:
        cf.CHAsb.delete(0,tk.END)
        cf.CHAsb.insert(0, cf.CHAVScale)
    try:
        cf.CHBVScale = float(eval(cf.CHBsb.get()))
    except:
        cf.CHBsb.delete(0,tk.END)
        cf.CHBsb.insert(0, cf.CHBVScale)
    try:
        cf.CHAIScale = float(eval(cf.CHAIsb.get()))
    except:
        cf.CHAIsb.delete(0,tk.END)
        cf.CHAIsb.insert(0, cf.CHAIScale)
    try:
        cf.CHBIScale = float(eval(cf.CHBIsb.get()))
    except:
        cf.CHBIsb.delete(0,tk.END)
        cf.CHBIsb.insert(0, cf.CHBIScale)
    # get the vertical offsets
    try:
        cf.CHAVOffset = float(eval(cf.CHAVPosEntry.get()))
    except:
        cf.CHAVPosEntry.delete(0,tk.END)
        cf.CHAVPosEntry.insert(0, cf.CHAVOffset)
    try:
        cf.CHAIOffset = float(eval(cf.CHAIPosEntry.get()))
    except:
        cf.CHAIPosEntry.delete(0,tk.END)
        cf.CHAIPosEntry.insert(0, cf.CHAIOffset)
    try:
        cf.CHBVOffset = float(eval(cf.CHBVPosEntry.get()))
    except:
        cf.CHBVPosEntry.delete(0,tk.END)
        cf.CHBVPosEntry.insert(0, cf.CHBVOffset)
    try:
        cf.CHBIOffset = float(eval(cf.CHBIPosEntry.get()))
    except:
        cf.CHBIPosEntry.delete(0,tk.END)
        cf.CHBIPosEntry.insert(0, cf.CHBIOffset)
    # prevent divide by zero error
    if cf.CHAVScale < 0.001:
        cf.CHAVScale = 0.001
    if cf.CHBVScale < 0.001:
        cf.CHBVScale = 0.001
    if cf.CHAIScale < 0.1:
        cf.CHAIScale = 0.1
    if cf.CHBIScale < 0.1:
        cf.CHBIScale = 0.1
          
    #  drawing the traces 
    if cf.NTrace == 0: # If no trace, skip rest of this routine
        T1Vline = []   # Trace line channel A V
        T2Vline = []   # Trace line channel B V
        T1Iline = []
        T2Iline = []
        Tmathline = [] # math trce line
        return() 
    # set and/or corrected for in range
    if cf.TgInput.get() > 0: # Trigger auf Signal aktiv (nicht None)
        SCmin = int(-1 * cf.TRIGGERsample) # erster Index für Darstellung # Wieso negativ?
        SCmax = int(cf.NTrace - cf.TRIGGERsample - 0) # letzter Index für Darstellung
    else:
        SCmin = 0 
        SCmax = cf.NTrace - 1
    if SCstart < SCmin:             # Index für Zeitpunkt 0 kann nicht kleiner sein als Anfang Sample-Trace
        SCstart = SCmin
    if SCstart  > SCmax:            # Index für Zeitpunkt 0 kann nicht größer sein als Ende Sample-Trace
        SCstart = SCmax
    # Make Trace lines etc.
    Yconv1 = float(cf.GRH/10.0) / cf.CHAVScale    # Vertical Conversion factors from samples to screen points
    Yconv2 = float(cf.GRH/10.0) / cf.CHBVScale
    YIconv1 = float(cf.GRH/10.0) / cf.CHAIScale
    YIconv2 = float(cf.GRH/10.0) / cf.CHBIScale
     
    c1 = cf.GRH / 2.0 + cf.Y0T    # fixed correction channel A
    c2 = cf.GRH / 2.0 + cf.Y0T    # fixed correction channel B
 
    DISsamples = cf.SampRate * 10.0 * cf.TIMEdiv / 1000.0 # number of samples to display
    # Wie kriegt man es hin, dass die Traces nur aktualisiert werden bei Trigger>None oder Triggerereignis?
    T1Vline = []                    # V Trace line channel A
    T2Vline = []                    # V Trace line channel B
    T1Iline = []                    # I Trace line channel A
    T2Iline = []                    # I Trace line channel B
    Tmathline = []                  # math trce line
    
    if len(cf.VBuffA) < 4 and len(cf.VBuffB) < 4 and len(cf.IBuffA) < 4 and len(cf.IBuffB) < 4:
        return
    t = int(SCstart + cf.TRIGGERsample) # Start Index im Sample Trace für Darstellung # Hier = Triggerzeitpunkt
    logging.warning('MakeTimeTrace(): Start Index t={}, SCstart={}, cf.TRIGGERsample={}'.format(t,SCstart,cf.TRIGGERsample))
    if t < 0:
        t = 0
    x = 0                           # Horizontal screen pixel

    ypv1 = int(c1 - Yconv1 * (cf.VBuffA[t] - cf.CHAVOffset))
    ypi1 = int(c1 - YIconv1 * (cf.IBuffA[t] - cf.CHAIOffset))
    ypv2 = int(c2 - Yconv2 * (cf.VBuffB[t] - cf.CHBVOffset))
    ypi2 = int(c1 - YIconv2 * (cf.IBuffB[t] - cf.CHBIOffset))
    DvY1 = DvY2 = DiY1 = DiY2 = 0 

    if (DISsamples <= cf.GRW): # Weniger Abtastpunkte als die Breite des Grids (in Pixel)
        logging.warning('MakeTimeTrace(): Weniger Abtastpunkte als Breite Grid')
        Xstep = cf.GRW / DISsamples
        if cf.AWGBMode.get() == 2 and cf.Two_X_Sample == 0:
            xa = int((Xstep/-2.5) - (Xstep*cf.trgIpol))
        else:
            xa = 0 - int(Xstep*cf.trgIpol) # adjust start pixel for interpolated trigger point
        x = 0 - int(Xstep*cf.trgIpol)
        x1 = 0 # x position of trace line
        xa1 = 0
        y1 = 0.0 # y position of trace line
        ypv1 = int(c1 - Yconv1 * (cf.VBuffA[t] - cf.CHAVOffset))
        ytemp = cf.IBuffA[t]
        ypi1 = int(c1 - YIconv1 * (ytemp - cf.CHAIOffset))
        ypv2 = int(c2 - Yconv2 * (cf.VBuffB[t] - cf.CHBVOffset))
        ytemp = cf.IBuffB[t]
        ypi2 = int(c1 - YIconv2 * (ytemp - cf.CHBIOffset))
        ypm = cf.GRH / 2.0 + cf.Y0T
        if cf.TgInput.get() == 0:
            Xlimit = cf.GRW
        else:
            Xlimit = cf.GRW+Xstep
        while x <= Xlimit:
            if t < cf.NTrace:
                xa1 = xa + cf.X0L
                x1 = x + cf.X0L
                y1 = int(c1 - Yconv1 * (cf.VBuffA[t] - cf.CHAVOffset))
                ytemp = cf.IBuffA[t]
                yi1 = int(c1 - YIconv1 * (ytemp - cf.CHAIOffset))
                
                if y1 < Ymin: # clip waveform if going off grid
                    y1 = Ymin
                if y1 > Ymax:
                    y1 = Ymax
                if yi1 < Ymin:
                    yi1 = Ymin
                if yi1 > Ymax:
                    yi1 = Ymax
                if cf.ShowC1_V.get() == 1 :
                    if cf.ZOHold.get() == 1:
                        T1Vline.append(int(xa1))
                        T1Vline.append(int(ypv1))
                        T1Vline.append(int(xa1))
                        T1Vline.append(int(y1))
                    else:    
                        T1Vline.append(int(xa1))
                        T1Vline.append(int(y1))
                    DvY1 = ypv1 - y1
                    ypv1 = y1
                if cf.ShowC1_I.get() == 1:
                    if cf.ZOHold.get() == 1:
                        T1Iline.append(int(xa1))
                        T1Iline.append(int(ypi1))
                        T1Iline.append(int(xa1))
                        T1Iline.append(int(yi1))
                    else:
                        T1Iline.append(int(xa1))
                        T1Iline.append(int(yi1))
                    DiY1 = ypi1 - yi1
                    ypi1 = yi1
                if cf.ShowC2_V.get() == 1:
                    y1 = int(c2 - Yconv2 * (cf.VBuffB[t] - cf.CHBVOffset))
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if cf.ZOHold.get() == 1:
                        T2Vline.append(int(x1))
                        T2Vline.append(int(ypv2))
                        T2Vline.append(int(x1))
                        T2Vline.append(int(y1))
                    else:
                        T2Vline.append(int(x1))
                        T2Vline.append(int(y1))
                    DvY2 = ypv2 - y1
                    ypv2 = y1
                if cf.ShowC2_I.get() == 1:
                    ytemp = cf.IBuffB[t]
                    yi1 = int(c1 - YIconv2 * (ytemp - cf.CHBIOffset))
                    if yi1 < Ymin:
                        yi1 = Ymin
                    if yi1 > Ymax:
                        yi1 = Ymax
                    if (cf.ZOHold.get() == 1):
                        T2Iline.append(int(x1))
                        T2Iline.append(int(ypi2))
                        T2Iline.append(int(x1))
                        T2Iline.append(int(yi1))
                    else:
                        T2Iline.append(int(x1))
                        T2Iline.append(int(yi1))
                    DiY2 = ypi2 - yi1
                    ypi2 = yi1
                if cf.MathTrace.get() > 0:
                    if cf.MathTrace.get() == 1: # plot sum of CA-V and CB-V
                        y1 = int(c1 - Yconv1 * (cf.VBuffA[t] + cf.VBuffB[t] - cf.CHAVOffset))
                    elif cf.MathTrace.get() == 2: # plot difference of CA-V and CB-V 
                        y1 = int(c1 - Yconv1 * (cf.VBuffA[t] - cf.VBuffB[t] - cf.CHAVOffset))
                    elif cf.MathTrace.get() == 3: # plot difference of CB-V and CA-V 
                        y1 = int(c2 - Yconv2 * (cf.VBuffB[t] - cf.VBuffA[t] - cf.CHBVOffset))
                    elif cf.MathTrace.get() == 4: # plot product of CA-V and CA-I
                        Ypower = cf.VBuffA[t] * cf.IBuffA[t] # mAmps * Volts = mWatts
                        ytemp = YIconv1 * (Ypower - cf.CHAIOffset)
                        y1 = int(c1 - ytemp)
                    elif cf.MathTrace.get() == 5: # plot product of CB-V and CB-I
                        Ypower = cf.VBuffB[t] * cf.IBuffB[t] # mAmps * Volts = mWatts
                        ytemp = YIconv2 * (Ypower - cf.CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif cf.MathTrace.get() == 6: # plot ratio of CA-V and CA-I
                        Yohms = cf.VBuffA[t] / (cf.IBuffA[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv1 * (Yohms - cf.CHAIOffset)
                        y1 = int(c1 - ytemp)
                    elif cf.MathTrace.get() == 7: # plot ratio of CB-V and CB-I
                        Yohms = cf.cf.VBuffB[t] / (cf.IBuffB[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv2 * (Yohms - cf.CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif cf.MathTrace.get() == 8: # plot difference of CA-I and CB-I
                        Ydif = (cf.IBuffA[t] - cf.IBuffB[t])#  in mA
                        ytemp = YIconv1 * (Ydif - cf.CHAIOffset)
                        y1 = int(c2 - ytemp)
                    elif cf.MathTrace.get() == 9: # plot difference of CB-I and CA-I
                        Ydif =  (cf.IBuffB[t] - cf.IBuffA[t]) #  in mA
                        ytemp = YIconv2 * (Ydif - cf.CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif cf.MathTrace.get() == 10: # plot ratio of CB-V and CA-V
                        try:
                            y1 = int(c1 - Yconv2 * ((cf.VBuffB[t] / cf.VBuffA[t]) - cf.CHBVOffset)) #  voltage gain A to B
                        except:
                            y1 = int(c1 - Yconv2 * ((cf.VBuffB[t] / 0.000001) - cf.CHBVOffset))
                    elif cf.MathTrace.get() == 11: # plot ratio of CB-I and CA-I
                        try:
                            Y1 = (cf.IBuffB[t] / cf.IBuffA[t])  # current gain A to B
                        except:
                            Y1 = (cf.IBuffB[t] / 0.000001)
                        ytemp = YIconv2 * (Y1 - cf.CHBIOffset)
                        y1 = int(c2 - ytemp)                                         
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if cf.ZOHold.get() == 1: # connet the dots with stair step
                        Tmathline.append(int(x1))
                        Tmathline.append(int(ypm))
                        Tmathline.append(int(x1))
                        Tmathline.append(int(y1))
                    else:    # connet the dots with single line
                        Tmathline.append(int(x1))
                        Tmathline.append(int(y1))
                    ypm = y1
                
            # remember trace verticle pixel at X mouse location
            if cf.MouseX - cf.X0L >= x and cf.MouseX - cf.X0L < (x + Xstep): # - Xstep
                Xfine = cf.MouseX - cf.X0L - x
                MouseCAV = ypv1 - (DvY1 * (Xfine/Xstep)) # interpolate along yaxis 
                MouseCAI = ypi1 - (DiY1 * (Xfine/Xstep))
                MouseCBV = ypv2 - (DvY2 * (Xfine/Xstep))
                MouseCBI = ypi2 - (DiY2 * (Xfine/Xstep))
            t = int(t + 1)
            x = x + Xstep
            xa = xa + Xstep           
    else: # Mehr Abtastpunkte als die Breite des Grids (in Pixel)
        logging.warning('MakeTimeTrace():Mehr Abtastpunkte als Breite Grid')
        Xstep = 1
        Tstep = DISsamples / cf.GRW      # number of samples to skip per grid pixel
        x1 = 0.0                          # x position of trace line
        ylo = 0.0                       # ymin position of trace 1 line
        yhi = 0.0                       # ymax position of trace 1 line
        t = int(SCstart + cf.TRIGGERsample)  # Startindex des Sample Trace für Darstellung
        if t > len(cf.VBuffA)-1:
            t = 0
        if t < 0:
            t = 0
        x = 0               # Horizontal screen pixel
        ft = t              # time point with fractions
        while (x <= cf.GRW):
            if (t < cf.NTrace):
                if (t >= len(cf.VBuffA)):
                    t = len(cf.VBuffA)-2
                    x = cf.GRW
                x1 = x + cf.X0L
                ylo = cf.VBuffA[t] - cf.CHAVOffset
                ilo = cf.IBuffA[t] - cf.CHAIOffset
                yhi = ylo
                ihi = ilo
                n = t
                while n < (t + Tstep) and n < cf.NTrace:
                    if ( cf.ShowC1_V.get() == 1 ):
                        v = cf.VBuffA[t] - cf.CHAVOffset
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v
                    if ( cf.ShowC1_I.get() == 1 ):
                        i = cf.IBuffA[t] - cf.CHAIOffset
                        if i < ilo:
                            ilo = i
                        if i > ihi:
                            ihi = i
                    n = n + 1
                if ( cf.ShowC1_V.get() == 1 ):
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
                    T1Vline.append(int(x1))
                    T1Vline.append(int(ylo))        
                    T1Vline.append(int(x1))
                    T1Vline.append(int(yhi))
                    ypv1 = ylo
                if ( cf.ShowC1_I.get() == 1 ):    
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
                    T1Iline.append(int(x1))
                    T1Iline.append(int(ilo))        
                    T1Iline.append(int(x1))
                    T1Iline.append(int(ihi))
                    ypi1 = ilo
                ylo = cf.VBuffB[t] - cf.CHBVOffset
                ilo = cf.IBuffB[t] - cf.CHBIOffset
                yhi = ylo
                ihi = ilo
                n = t          
                while n < (t + Tstep) and n < cf.NTrace:
                    if ( cf.ShowC2_V.get() == 1 ):
                        v = cf.VBuffB[t] - cf.CHBVOffset
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v
                    if ( cf.ShowC2_I.get() == 1 ):
                        i = cf.IBuffB[t] - cf.CHBIOffset
                        if i < ilo:
                            ilo = i
                        if i > ihi:
                            ihi = i
                    n = n + 1
                if ( cf.ShowC2_V.get() == 1 ):
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
                    T2Vline.append(int(x1))
                    T2Vline.append(int(ylo))        
                    T2Vline.append(int(x1))
                    T2Vline.append(int(yhi))
                    ypv2 = ylo
                if ( cf.ShowC2_I.get() == 1 ):
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
                    T2Iline.append(int(x1))
                    T2Iline.append(int(ilo))        
                    T2Iline.append(int(x1))
                    T2Iline.append(int(ihi))
                    ypi2 = ilo
                
                if cf.MathTrace.get() > 0:
                    if cf.MathTrace.get() == 1: # plot sum of CA-V and CB-V
                        y1 = int(c1 - Yconv1 * (cf.VBuffA[t] + cf.VBuffB[t] - cf.CHAVOffset))
                    elif cf.MathTrace.get() == 2: # plot difference of CA-V and CB-V 
                        y1 = int(c1 - Yconv1 * (cf.VBuffA[t] - cf.VBuffB[t] - cf.CHAVOffset))
                    elif cf.MathTrace.get() == 3: # plot difference of CB-V and CA-V 
                        y1 = int(c2 - Yconv2 * (cf.VBuffB[t] - cf.VBuffA[t] - cf.CHBVOffset))
                    elif cf.MathTrace.get() == 4: # plot product of CA-V and CA-I
                        Ypower = cf.VBuffA[t] * cf.IBuffA[t] # mAmps * Volts = mWatts
                        ytemp = YIconv1 * (Ypower - cf.CHAIOffset)
                        y1 = int(c1 - ytemp)                                            
                    elif cf.MathTrace.get() == 5: # plot product of CB-V and CB-I
                        Ypower = cf.VBuffB[t] * cf.IBuffB[t] # mAmps * Volts = mWatts
                        ytemp = YIconv2 * (Ypower - cf.CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif cf.MathTrace.get() == 6: # plot ratio of CA-V and CA-I
                        Yohms = cf.VBuffA[t] / (cf.IBuffA[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv1 * (Yohms- cf.CHAIOffset)
                        y1 = int(c1 - ytemp)
                    elif cf.MathTrace.get() == 7: # plot ratio of CB-V and CB-I
                        Yohms = cf.VBuffB[t] / (cf.IBuffB[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv2 * (Yohms - cf.CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif cf.MathTrace.get() == 8: # plot difference of CA-I and CB-I
                        Ydif = (cf.IBuffA[t] - cf.IBuffB[t]) #  in mA
                        ytemp = YIconv1 * (Ydif - cf.CHAIOffset)
                        y1 = int(c2 - ytemp)
                    elif cf.MathTrace.get() == 9: # plot difference of CB-I and CA-I
                        Ydif = (cf.IBuffB[t] - cf.IBuffA[t])  # in mA
                        ytemp = YIconv2 * (Ydif - cf.CHBIOffset)
                        y1 = int(c2 - ytemp)
                    elif cf.MathTrace.get() == 10: # plot ratio of CB-V and CA-V
                        try:
                            y1 = int(c1 - Yconv2 * ((cf.VBuffB[t] / cf.VBuffA[t]) - cf.CHBVOffset)) #  voltage gain A to B
                        except:
                            y1 = int(c1 - Yconv2 * ((cf.VBuffB[t] / 0.000001) - cf.CHBVOffset))
                    elif cf.MathTrace.get() == 11: # plot ratio of CB-I and CA-I
                        try:
                            Y1 = (cf.IBuffB[t] / cf.IBuffA[t]) # current gain A to B
                        except:
                            Y1 = (cf.IBuffB[t] / 0.000001)
                        ytemp = YIconv2 * (Y1 - cf.CHBIOffset)
                        y1 = int(c2 - ytemp)
                      
                    if (y1 < Ymin):
                        y1 = Ymin
                    if (y1 > Ymax):
                        y1 = Ymax
                    if (cf.ZOHold.get() == 1):
                        Tmathline.append(int(x1))
                        Tmathline.append(int(ypm))
                        Tmathline.append(int(x1))
                        Tmathline.append(int(y1))
                    else:    
                        Tmathline.append(int(x1))
                        Tmathline.append(int(y1))
                    ypm = y1
                
            ft = ft + Tstep
            if (cf.MouseX - cf.X0L) == x: # > (x - 1) and (cf.MouseX - cf.X0L) < (x + 1):
                MouseCAV = ypv1
                MouseCAI = ypi1
                MouseCBV = ypv2
                MouseCBI = ypi2
            t = int(ft)
            if (t > len(cf.VBuffA)):
                t = len(cf.VBuffA)-2
                x = cf.GRW
            x = x + Xstep
    # Make trigger triangle pointer
    logging.warning('MakeTimeTrace(): Make trigger triangle pointer')
    Triggerline = []                # Trigger pointer
    Triggersymbol = []                # Trigger symbol
    if cf.TgInput.get() > 0:
        if cf.TgInput.get() == 1 : # triggering on CA-V
            x1 = cf.X0L
            ytemp = Yconv1 * (float(cf.TRIGGERlevel)-cf.CHAVOffset) 
            y1 = int(c1 - ytemp)
        elif cf.TgInput.get() == 2:  # triggering on CA-I
            x1 = cf.X0L+cf.GRW
            y1 = int(c1 - YIconv1 * (float(cf.TRIGGERlevel) - cf.CHAIOffset))
        elif cf.TgInput.get() == 3:  # triggering on CB-V
            x1 = cf.X0L
            ytemp = Yconv2 * (float(cf.TRIGGERlevel)-cf.CHBVOffset)          
            y1 = int(c2 - ytemp)
        elif cf.TgInput.get() == 4: # triggering on CB-I
            x1 = cf.X0L+cf.GRW
            y1 = int(c2 - YIconv2 * (float(cf.TRIGGERlevel) - cf.CHBIOffset))
            
        if (y1 < Ymin):
            y1 = Ymin
        if (y1 > Ymax):
            y1 = Ymax
        Triggerline.append(int(x1-5))
        Triggerline.append(int(y1+5))
        Triggerline.append(int(x1+5))
        Triggerline.append(int(y1))
        Triggerline.append(int(x1-5))
        Triggerline.append(int(y1-5))
        Triggerline.append(int(x1-5))
        Triggerline.append(int(y1+5))
        x1 = cf.X0L + (cf.GRW/2)
        if cf.TgEdge.get() == 0: # draw rising edge symbol
            y1 = -3
            y2 = -13
        else:
            y1 = -13
            y2 = -3
        Triggersymbol.append(int(x1-10))
        Triggersymbol.append(int(Ymin+y1))
        Triggersymbol.append(int(x1))
        Triggersymbol.append(int(Ymin+y1))
        Triggersymbol.append(int(x1))
        Triggersymbol.append(int(Ymin+y2))
        Triggersymbol.append(int(x1+10))
        Triggersymbol.append(int(Ymin+y2))

## Update the time screen with traces and text   
def MakeTimeScreen():
    logging.debug('MakeTimeScreen()')    
    global T1Vline, T2Vline, T1Iline, T2Iline # active trave lines
    global Triggerline, Triggersymbol, Tmathline
    global Ymin, Ymax
    global MouseCAV, MouseCAI, MouseCBV, MouseCBI
    global ShowXCur, ShowYCur
    global ShowMath       
    global DISsamples      # current spin box value
    global HtMulEntry
    global TRACErefresh, TRACEmode
    global DCV1, DCV2, CHAHW, CHALW, CHADCy, CHAperiod, CHAfreq
    global DCI1, DCI2, CHBHW, CHBLW, CHBDCy, CHBperiod, CHBfreq
    global CurOffA, CurOffB, CurGainA, CurGainB
    global CHABphase 
    
    
    COLORgrid = "#808080"     # 50% Gray
    COLORzeroline = "#0000ff" # 100% blue
      
    Ymin = cf.Y0T                  # Minimum position of time grid (top)
    Ymax = cf.Y0T + cf.GRH            # Maximum position of time grid (bottom)
    Tstep = (10.0 * cf.TIMEdiv) / cf.GRW # time in mS per pixel
    # get the vertical ranges
    try:
        cf.CHAVScale = float(eval(cf.CHAsb.get()))
    except:
        cf.CHAsb.delete(0,tk.END)
        cf.CHAsb.insert(0, cf.CHAVScale)
    try:
        cf.CHBVScale = float(eval(cf.CHBsb.get()))
    except:
        cf.CHBsb.delete(0,tk.END)
        cf.CHBsb.insert(0, cf.CHBVScale)
    try:
        cf.CHAIScale = float(eval(cf.CHAIsb.get()))
    except:
        cf.CHAIsb.delete(0,tk.END)
        cf.CHAIsb.insert(0, cf.CHAIScale)
    try:
        cf.CHBIScale = float(eval(cf.CHBIsb.get()))
    except:
        cf.CHBIsb.delete(0,tk.END)
        cf.CHBIsb.insert(0, cf.CHBIScale)
    # get the vertical offsets
    try:
        cf.CHAVOffset = float(eval(cf.CHAVPosEntry.get()))
    except:
        cf.CHAVPosEntry.delete(0,tk.END)
        cf.CHAVPosEntry.insert(0, cf.CHAVOffset)
    try:
        cf.CHAIOffset = float(eval(cf.CHAIPosEntry.get()))
    except:
        cf.CHAIPosEntry.delete(0,tk.END)
        cf.CHAIPosEntry.insert(0, cf.CHAIOffset)
    try:
        cf.CHBVOffset = float(eval(cf.CHBVPosEntry.get()))
    except:
        cf.CHBVPosEntry.delete(0,tk.END)
        cf.CHBVPosEntry.insert(0, cf.CHBVOffset)
    try:
        cf.CHBIOffset = float(eval(cf.CHBIPosEntry.get()))
    except:
        cf.CHBIPosEntry.delete(0,tk.END)
        cf.CHBIPosEntry.insert(0, cf.CHBIOffset)
    # slide trace left right by cf.HozPos
#    try:
#        cf.HozPos = float(eval(cf.HozPosentry.get()))
#    except:
#        cf.HozPosentry.delete(0,tk.END)
#        cf.HozPosentry.insert(0, cf.HozPos)      
    # prevent divide by zero error
    if cf.CHAVScale < 0.001:
        cf.CHAVScale = 0.001
    if cf.CHBVScale < 0.001:
        cf.CHBVScale = 0.001
    if cf.CHAIScale < 0.1:
        cf.CHAIScale = 0.1
    if cf.CHBIScale < 0.1:
        cf.CHBIScale = 0.1
    vt = cf.HozPos
    # Delete all items on the screen
    cf.ca.delete(tk.ALL) # remove all items
    # Draw horizontal grid lines
    i = 0
    x1 = cf.X0L
    x2 = cf.X0L + cf.GRW
    mg_siz = cf.GRW/10.0
    mg_inc = mg_siz/5.0
    MathFlag1 = (MathAxis == "V-A" and cf.MathTrace.get() == 12)
    MathFlag2 = (MathAxis == "V-B" and cf.MathTrace.get() == 12)
    MathFlag3 = (MathAxis == "I-A" and cf.MathTrace.get() == 12)
    MathFlag4 = (MathAxis == "I-B" and cf.MathTrace.get() == 12)
    # vertical scale text labels
    RightOffset = cf.FontSize * 3
    LeftOffset = int(cf.FontSize/2)
    if (cf.ShowC1_V.get() == 1 or cf.MathTrace.get() == 1 or cf.MathTrace.get() == 2 or MathFlag1):
        cf.ca.create_text(x1-LeftOffset, 12, text="CA-V", fill=cf.COLORtrace1, anchor="e", font=("arial", cf.FontSize-1 ))
    if (cf.ShowC1_I.get() == 1 or cf.MathTrace.get() == 4 or cf.MathTrace.get() == 6 or cf.MathTrace.get() == 8 or MathFlag3):
        cf.ca.create_text(x2+LeftOffset, 12, text="CA-I", fill=cf.COLORtrace3, anchor="w", font=("arial", cf.FontSize-1 ))
    if (cf.ShowC2_V.get() == 1 or cf.MathTrace.get() == 3 or cf.MathTrace.get() == 10 or MathFlag2):
        cf.ca.create_text(x1-RightOffset+2, 12, text="CB-V", fill=cf.COLORtrace2, anchor="e", font=("arial", cf.FontSize-1 )) #26
    if (cf.ShowC2_I.get() == 1 or cf.MathTrace.get() == 5 or cf.MathTrace.get() == 7 or cf.MathTrace.get() == 9 or cf.MathTrace.get() == 11 or MathFlag4):
        cf.ca.create_text(x2+RightOffset+4, 12, text="CB-I", fill=cf.COLORtrace4, anchor="w", font=("arial", cf.FontSize-1 )) #28
    
    while (i < 11):
        y = cf.Y0T + i * cf.GRH/10.0
        Dline = [x1,y,x2,y]
        if i == 5:
            cf.ca.create_line(Dline, fill=COLORzeroline, width=cf.GridWidth.get())   # Blue line at center of grid
            k = 0
            while (k < 10):
                l = 1
                while (l < 5):
                    Dline = [x1+k*mg_siz+l*mg_inc,y-5,x1+k*mg_siz+l*mg_inc,y+5]
                    cf.ca.create_line(Dline, fill=COLORgrid, width=cf.GridWidth.get())
                    l = l + 1
                k = k + 1
        else:
            cf.ca.create_line(Dline, fill=COLORgrid, width=cf.GridWidth.get())

        if (cf.ShowC1_V.get() == 1 or cf.MathTrace.get() == 1 or cf.MathTrace.get() == 2 or MathFlag1):
            Vaxis_value = (((5-i) * cf.CHAVScale ) + cf.CHAVOffset)
            Vaxis_label = str(round(Vaxis_value,3 ))
            cf.ca.create_text(x1-LeftOffset, y, text=Vaxis_label, fill=cf.COLORtrace1, anchor="e", font=("arial", cf.FontSize ))
            
        if (cf.ShowC1_I.get() == 1 or cf.MathTrace.get() == 4 or cf.MathTrace.get() == 6 or cf.MathTrace.get() == 8 or MathFlag3):
            Iaxis_value = 1.0 * (((5-i) * cf.CHAIScale ) + cf.CHAIOffset)
            Iaxis_label = str(round(Iaxis_value, 3))
            cf.ca.create_text(x2+LeftOffset, y, text=Iaxis_label, fill=cf.COLORtrace3, anchor="w", font=("arial", cf.FontSize ))
            
        if (cf.ShowC2_V.get() == 1 or cf.MathTrace.get() == 3 or cf.MathTrace.get() == 10 or MathFlag2):
            Vaxis_value = (((5-i) * cf.CHBVScale ) + cf.CHBVOffset)
            Vaxis_label = str(round(Vaxis_value, 3))
            cf.ca.create_text(x1-RightOffset+2, y, text=Vaxis_label, fill=cf.COLORtrace2, anchor="e", font=("arial", cf.FontSize )) # 26
            
        if (cf.ShowC2_I.get() == 1 or cf.MathTrace.get() == 5 or cf.MathTrace.get() == 7 or cf.MathTrace.get() == 9 or cf.MathTrace.get() == 11 or MathFlag4):
            Iaxis_value = 1.0 * (((5-i) * cf.CHBIScale ) + cf.CHBIOffset)
            Iaxis_label = str(round(Iaxis_value, 3))
            cf.ca.create_text(x2+RightOffset+4, y, text=Iaxis_label, fill=cf.COLORtrace4, anchor="w", font=("arial", cf.FontSize )) # 28
        i = i + 1
    # Draw vertical grid lines
    i = 0
    y1 = cf.Y0T
    y2 = cf.Y0T + cf.GRH
    mg_siz = cf.GRH/10.0
    mg_inc = mg_siz/5.0
    vx = cf.TIMEdiv # Spaltenbreite des Oszigrids
    vt = cf.HozPos # Offset der Zeitachsenbeschriftung infolge HorzPos-Einstellung in UI (war cf.HoldOff)

    while (i < 11):
        x = cf.X0L + i * cf.GRW/10.0
        Dline = [x,y1,x,y2]
        if (i == 5):
            cf.ca.create_line(Dline, fill=COLORzeroline, width=cf.GridWidth.get())   # Blue vertical line at center of grid
            k = 0
            while (k < 10):
                l = 1
                while (l < 5):
                    Dline = [x-5,y1+k*mg_siz+l*mg_inc,x+5,y1+k*mg_siz+l*mg_inc]
                    cf.ca.create_line(Dline, fill=COLORgrid, width=cf.GridWidth.get())
                    l = l + 1
                k = k + 1

            if vx >= 1000:
                axis_value = ((i * vx)+ vt) / 1000.0
                axis_label = ' {0:.1f} '.format(axis_value) + " s"
            if vx < 1000 and vx >= 1:
                axis_value = (i * vx) + vt
                axis_label = ' {0:.1f} '.format(axis_value) + " ms"
            if vx < 1:
                axis_value = ((i * vx) + vt) * 1000.0
                axis_label = ' {0:.1f} '.format(axis_value) + " us"
            cf.ca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", cf.FontSize ))
        else:
            cf.ca.create_line(Dline, fill=COLORgrid, width=cf.GridWidth.get())
            if vx >= 1000:
                axis_value = ((i * vx)+ vt) / 1000.0
                axis_label = ' {0:.1f} '.format(axis_value) + " s"
            if vx < 1000 and vx >= 1:
                axis_value = (i * vx) + vt
                axis_label = ' {0:.1f} '.format(axis_value) + " ms"
            if vx < 1:
                axis_value = ((i * vx) + vt) * 1000.0
                axis_label = ' {0:.1f} '.format(axis_value) + " us"
            cf.ca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", cf.FontSize ))
                    
        i = i + 1
    # Write the trigger line if available
    if len(Triggerline) > 2:                    # Avoid writing lines with 1 coordinate
        cf.ca.create_polygon(Triggerline, outline=cf.COLORtrigger, fill=cf.COLORtrigger, width=1)
        cf.ca.create_line(Triggersymbol, fill=cf.COLORtrigger, width=cf.GridWidth.get())
        TgLabel = ""
        if cf.TgInput.get() == 1:
            TgLabel = "CA-V"
        if cf.TgInput.get() == 2:
            TgLabel = "CA-I"
        if cf.TgInput.get() == 3:
            TgLabel = "CB-V"
        if cf.TgInput.get() == 4:
            TgLabel = "CB-I"
        if cf.Is_Triggered == 1:
            TgLabel = TgLabel + " Triggered"
        else:
            TgLabel = TgLabel + " Not Triggered"
            if cf.SingleShot.get() > 0:
                TgLabel = TgLabel + " Armed"
        x = cf.X0L + (cf.GRW/2) + 12
        cf.ca.create_text(x, Ymin-cf.FontSize, text=TgLabel, fill=cf.COLORtrigger, anchor="w", font=("arial", cf.FontSize ))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Setzen der Zeit-/Signalcursor bei Rechtsklick auf Oszibild
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++   
    #--- Zeit-/Signalcursor falls in UI für den ausgewählten Trace zeichnen

    if cf.ShowCur.get() == 1:
        cf.MouseY = MouseCAV
        Yconv1 = float(cf.GRH/10.0) / cf.CHAVScale
        Yoffset1 = cf.CHAVOffset
        COLORmarker = cf.COLORtrace1
        Units = " V"
    if cf.ShowCur.get() == 2:
        cf.MouseY = MouseCBV
        Yconv1 = float(cf.GRH/10.0) / cf.CHBVScale
        Yoffset1 = cf.CHBVOffset
        COLORmarker = cf.COLORtrace2
        Units = " V"
    if cf.ShowCur.get() == 3:
        cf.MouseY = MouseCAI
        Yconv1 = float(cf.GRH/10.0) / cf.CHAIScale
        Yoffset1 = cf.CHAIOffset
        COLORmarker = cf.COLORtrace3
        Units = " mA"
    if cf.ShowCur.get() == 4:
        cf.MouseY = MouseCBI
        Yconv1 = float(cf.GRH/10.0) / cf.CHBIScale
        Yoffset1 = cf.CHBIOffset
        COLORmarker = cf.COLORtrace4
        Units = " mA"
    if cf.ShowCur.get() > 0: # Falls nicht "None" in UI ausgewählt
        Dline = [cf.TCursor, cf.Y0T, cf.TCursor, cf.Y0T+cf.GRH]
        cf.ca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=cf.GridWidth.get())
        Tpoint = ((cf.TCursor-cf.X0L) * Tstep) + vt
        Tpoint = Tpoint
        if Tpoint >= 1000:
            axis_value = Tpoint / 1000.0
            V_label = ' {0:.2f} '.format(axis_value) + " s"
        if Tpoint < 1000 and Tpoint >= 1:
            axis_value = Tpoint
            V_label = ' {0:.2f} '.format(axis_value) + " ms"
        if Tpoint < 1:
            axis_value = Tpoint * 1000.0
            V_label = ' {0:.2f} '.format(axis_value) + " us"
        cf.ca.create_text(cf.TCursor+2, cf.VCursor-10, text=V_label, fill=cf.COLORtext, anchor="w", font=("arial", cf.FontSize )) # Angabe Zeitwert Cursor Maus Rechtsklick
        Dline = [cf.X0L, cf.VCursor, cf.X0L+cf.GRW, cf.VCursor]
        cf.ca.create_line(Dline, dash=(4,3), fill=COLORmarker, width=cf.GridWidth.get())
        c1 = cf.GRH / 2 + cf.Y0T    # fixed Y correction 
        yvolts = ((cf.VCursor-c1)/Yconv1) - Yoffset1
        V1String = ' {0:.3f} '.format(-yvolts)
        V_label = V1String + Units
        cf.ca.create_text(cf.TCursor+2, cf.VCursor+10, text=V_label, fill=COLORmarker, anchor="w", font=("arial", cf.FontSize )) # Angabe Signalwert Cursor Maus Rechtsklick
 
    SmoothBool = cf.SmoothCurves.get()
    # Write the traces if available
    if len(T1Vline) > 4: # Avoid writing lines with 1 coordinate    
        cf.ca.create_line(T1Vline, fill=cf.COLORtrace1, smooth=SmoothBool, splinestep=5, width=cf.TRACEwidth.get())   # Write the voltage trace 1
    if len(T1Iline) > 4: # Avoid writing lines with 1 coordinate
        cf.ca.create_line(T1Iline, fill=cf.COLORtrace3, smooth=SmoothBool, splinestep=5, width=cf.TRACEwidth.get())   # Write the current trace 1
    if len(T2Vline) > 4: # Write the trace 2 if active
        cf.ca.create_line(T2Vline, fill=cf.COLORtrace2, smooth=SmoothBool, splinestep=5, width=cf.TRACEwidth.get())
    if len(T2Iline) > 4:
        cf.ca.create_line(T2Iline, fill=cf.COLORtrace4, smooth=SmoothBool, splinestep=5, width=cf.TRACEwidth.get())
    if len(Tmathline) > 4 and cf.MathTrace.get() > 0: # Write Math tace if active
        cf.ca.create_line(Tmathline, fill=cf.COLORtrace5, smooth=SmoothBool, splinestep=5, width=cf.TRACEwidth.get())
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Textinformationen wie Messwerte, Samplingrate ober und unterhalb Oszibild
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #--- oberhalb Oszibild
    # Info Triggermodus und Abtastrate
    txt = "Acquisition Mode: "
    if cf.TRACEmodeTime.get() == 1:
        txt = "Averaging "
#    if cf.ManualTrigger.get() == 1:
#        txt = "Manual Trigger "
    if (cf.RUNstatus.get() == 0) or (cf.RUNstatus.get() == 3):
        txt = "Stopped "
    # Info Samplingrate
    x = cf.X0L+2
    y = 12
    txt = txt + "   Sample Rate: " + str(cf.SampRate) + " S/s"
    # Info Horizontalskalierung
    txt = txt + "   Horizontal Scale/Pos: "
    vx = cf.TIMEdiv
    if vx >= 1000:
        txt = txt + ' {0:.2f} '.format(vx / 1000.0) + " s/div"
    if vx < 1000 and vx >= 1:
        txt = txt + ' {0:.2f} '.format(vx) + " ms/div"
    if vx < 1:
        txt = txt + ' {0:.2f} '.format(vx * 1000.0) + " us/div"
    # Info Horizontalposition
    txt = txt + " / "
    if abs(cf.HozPos) >= 1000:
        txt = txt + str(int(cf.HozPos / 1000.0)) + " s "
    if abs(cf.HozPos) < 1000 and abs(cf.HozPos) >= 1:
        txt = txt + str(int(cf.HozPos)) + " ms "
    if abs(cf.HozPos) < 1:
        txt = txt + str(int(cf.HozPos * 1000.0)) + " us "
    # Darstellung Werte oberhalb Oszibild
    cf.ca.create_text(x, y, text=txt, anchor=tk.W, fill=cf.COLORtext)
    x2 = cf.X0L + cf.GRW
    #--- Unterhalb des Oszibildes
    # Ausgewählte Messwerte für CA in erster Zeile
    txt = " "
    if cf.ShowC1_V.get() == 1:
        txt = "CA-V: "
        txt = txt + str(cf.CHAVScale) + " V/div"
        if cf.MeasDCV1.get() == 1: 
            txt = txt + " AvgV=" + '{0:.4f} '.format(cf.DCV1)
        if cf.MeasMaxV1.get() == 1:
            txt = txt +  " MaxV=" + '{0:.4f} '.format(cf.MaxV1)
        if cf.MeasMinV1.get() == 1:
            txt = txt +  " MinV=" + '{0:.4f} '.format(cf.MinV1)
        if cf.MeasPPV1.get() == 1:
            cf.PPV1 = cf.MaxV1-cf.MinV1
            txt = txt +  " P-PV=" + '{0:.4f} '.format(cf.PPV1)
        if cf.MeasRMSV1.get() == 1:
            txt = txt +  " RMSV=" + '{0:.4f} '.format(cf.SV1)
    if (cf.ShowC1_I.get() == 1 and cf.ShowC1_V.get() == 0):
        txt = "CA-I: "
        txt = txt + str(cf.CHAIScale) + "mA/div"
    elif (cf.ShowC1_I.get() == 1 and cf.ShowC1_V.get() == 1):
        txt = txt + "CA-I: "
        txt = txt + str(cf.CHAIScale) + "mA/div"
    if cf.ShowC1_I.get() == 1:
        if cf.MeasDCI1.get() == 1:
            V1String = '{0:.2f} '.format(DCI1)
            txt = txt + " AvgI=" + V1String
        if cf.MeasMaxI1.get() == 1:
            txt = txt +  " MaxI=" + '{0:.2f} '.format(cf.MaxI1)
        if cf.MeasMinI1.get() == 1:
            txt = txt +  " MinI=" + '{0:.2f} '.format(cf.MinI1)
        if cf.MeasPPI1.get() == 1:
            cf.PPI1 = cf.MaxI1-cf.MinI1 
            txt = txt +  " P-PI =" + '{0:.2f} '.format(cf.PPI1)
        if cf.MeasRMSI1.get() == 1:
            txt = txt +  " RMSI=" + '{0:.4f} '.format(cf.SI1)
    x = cf.X0L
    y = cf.Y0T+cf.GRH+(4*cf.FontSize) # 32
    txt = txt + "   Units: V/mA"
    cf.ca.create_text(x, y, text=txt, anchor=tk.W, fill=cf.COLORtext)
    txt= " "
    # Ausgewählte Messwerte für CA in erster Zeile
    if cf.ShowC2_V.get() == 1:
        txt = "CB-V: "
        txt = txt + str(cf.CHBVScale) + " V/div"
        if cf.MeasDCV2.get() == 1:
            txt = txt + " AvgV=" + '{0:.4f} '.format(cf.DCV2)
        if cf.MeasMaxV2.get() == 1:
            txt = txt +  " MaxV=" + '{0:.4f} '.format(cf.MaxV2)
        if cf.MeasMinV2.get() == 1:
            txt = txt +  " MinV=" + '{0:.4f} '.format(cf.MinV2)
        if cf.MeasPPV2.get() == 1:
            cf.PPV2 = cf.MaxV2-cf.MinV2
            txt = txt +  " P-PV=" + '{0:.4f} '.format(cf.PPV2)
        if cf.MeasRMSV2.get() == 1:
            txt = txt +  " RMSV=" + '{0:.4f} '.format(cf.SV2)
    if (cf.ShowC2_I.get() == 1 and cf.ShowC2_V.get() == 0):
        txt = "CB-I: "
        txt = txt + str(cf.CHBIScale) + " mA/div"
    elif (cf.ShowC2_I.get() == 1 and cf.ShowC2_V.get() == 1):
        txt = txt + "CB-I: "
        txt = txt + str(cf.CHBIScale) + " mA/div"
    if cf.ShowC2_I.get() == 1:
        if cf.MeasDCI2.get() == 1:
            V1String = '{0:.2f} '.format(cf.DCI2)
            txt = txt + " AvgI=" + V1String
        if cf.MeasMaxI2.get() == 1:
            txt = txt +  " MaxI=" + '{0:.2f} '.format(cf.MaxI2)
        if cf.MeasMinI2.get() == 1:
            txt = txt +  " MinI=" + '{0:.2f} '.format(cf.MinI2)
        if cf.MeasPPI2.get() == 1:
            cf.PPI2 = cf.MaxI2-cf.MinI2
            txt = txt +  " P-PI=" + '{0:.2f} '.format(cf.PPI2)
        if cf.MeasRMSI2.get() == 1:
            txt = txt +  " RMSI=" + '{0:.4f} '.format(cf.SI2)
    # Darstellung Werte unter Oszibild        
    x = cf.X0L
    y = cf.Y0T+cf.GRH+int(6*cf.FontSize) # 44
    txt = txt + "   Units: V/mA"
    cf.ca.create_text(x, y, text=txt, anchor=tk.W, fill=cf.COLORtext)