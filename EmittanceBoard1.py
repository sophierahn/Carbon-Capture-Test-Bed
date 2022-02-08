#!/usr/bin/env python3
#Enable I2C and SPI in the RPi
#Check directory with files /usr/local/lib/python3.7/dist-packages
import queue
import RPi.GPIO as GPIO
import board
import busio
#import digitalio
import smbus #SetVolts DAC5691
from tkinter import *
import tkinter as tk #tkinter (no capital T) in case of Python 3
from tkinter import messagebox
from tkinter import Canvas
import re
import time
from time import sleep
from datetime import datetime
import math
import sys
import os #interact with the OS (mkdir, files etc)
from os import path
import platform
import numpy as np
from threading import Thread as th
from threading import Lock
from multiprocessing import Process, Queue
import subprocess
from subprocess import Popen
import asyncio
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
matplotlib.use('TkAgg')
import pandas as pd
import func
#from Adafruit.ADS1x15 import Adafruit_ADS1x15
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import warnings
warnings.filterwarnings("ignore",category=FutureWarning)#Avoid warnings of future updates


##############################################################
##########GLOBALS - Motor and DRIVER CONFIGURATION############
##############################################################
MinStep = 0.01#mm #Theory: 4mm/200Steps = 0.02mm/step ||| 4mm/400Steps = 0.01mm/step
StepRev = 4/MinStep #335.43 steps/rev #In theory 400steps/rev but is 335 according first set of tests. Driver configured with 400 steps/360deg 4mm in 400 steps (In case of 200Steps = 1.8deg/step --> 4mm in 200steps)
thresSignal = 0.5#To Be Updated
############################################################################

#root = Tk()
EnergySet=0#keV
Angle=0
PosMaxSet=True #*****FALSE
PosMinSet=True
PosADCMax=13325 #Bit number TBUpdated
PosMax=105.5 #mm
PosADCMin=1490 #Bit number TBUpdated
PosMin= 0.0 #mm
pos=0#PosMax/2.#Initial
maxQSX = 0.0
maxQPos = 0.0

voltDisplay = 0

f1 = None
stopm=True
TxtM = [None]*3
TxtV = [None]*3
TxtT = [None]*1
TxtDT = [None]*1
TxtE = [None]*1
TxtThr = [None]*1
comment = [None]*1


###########################################################
######################GLOBALS Striptool####################
###########################################################
PauseStriptool=False
Running=False
EnableUpdatePlotNotRunning=False
outputfile = None

ChangeColorRunning = False
ChangeFreqRunning = False
LW=np.array
NDevices = 4
ExtFile = [None]*NDevices
Colores = np.array
updatecolor = False

class Feature:
    def __init__(self,Name,Label,Limits,VALUE,lblUnits,Color):
        #Name="TC1" Label="Temperatura[C]" Limits=MinMaxinPlot, Name="Vacuum" TextLabel="%.4E psi"
        self.Name = Name
        self.Label = Label
        self.Limits = [Limits[i] for i in range(2)]
        self.VALUE = VALUE
        self.lblUnits = lblUnits
        self.Color = [Color[i] for i in range(2)]#Color and activecolor

Var = [Feature([None],[None],[[None],[None]],[None],[None],[[None],[None]])]*6
Colores = [['#000000','#C0C0C0'],['#FF0000','#DD0000'],['#00FF00','#00DD00'],['#0000FF','#0000DD'],['#FFFF00','#DDDD00'],['#00FFFF','#00DDDD']]

###########################################################
###########################################################
###########################################################

status = Tk()
status.geometry('50x60+1150+0') #Size and Position of GUI
#status.attributes('-topmost',False
status.title('Motor Status')
Moving = Label(status, text="Motor Moving", font=("Calibri",10),bg='#FFFFFF', wraplength=50)
Moving.grid(column=1, row = 1, padx=10, pady=10)

class TFL(tk.Frame):
    def __init__(self,master):
        super(TFL,self).__init__()
        global Angle,EnergySet,PosMin,PosMax,f1,stopm
#        global StopMot
        global TxtM,TxtV,TxtT,TxtE, TxtThr, comment
        self.master = master
        master.title("Emittance meter control system")
        master.geometry('1130x630') #Set Size of GUI window (WxH)
        master.lift()
        master.attributes('-topmost',True)
        #master.focus_set()
        MVP = 400 #Motor Variables Position in the GUI

        text = 10

        self.canvas = Canvas(master)
        self.canvas.place(x=MVP+10, y=50)
        self.canvas.create_line(1,1,1,255, width = 3, fill="#666666")
#        self.canvas.create_line(20,280,MVP-10,280, width = 3, fill="#666666")

        self.canvas1 = Canvas(master)
        self.canvas1.place(x=MVP+10, y=260)
        self.canvas1.create_line(1,1,1,350, width = 3, fill="#666666")

        self.canvas2 = Canvas(master)
        self.canvas2.place(x=20, y=280)
        self.canvas2.create_line(1,1,MVP,1, width = 3, fill="#666666")

        self.lblTop = Label(master, text="Emittance meter", font=("Calibri",text+14))
        self.lblTop.place(x=285, y=5)

        ###############################################
        ###############Measurement cycle##############
        ###############################################
        self.lblTit = Label(master, text="Measurement settings", font=("Calibri",text+8))
        self.lblRg = Label(master, text="Ranges", font=("Calibri",text+4))
        self.lblStp = Label(master, text="Steps", font=("Calibri",text+4))
        self.lblTit.place(x=100,y=45)
        self.lblRg.place(x=200,y=75)
        self.lblStp.place(x=310,y=75)

        yposM=100
        self.lblM = [None]*4
        self.lblM[0] = Label(master, text="Motor position:", font=("Calibri",text+4))
        self.lblM[1] = Label(master, text="to", font=("Calibri",text))
        self.lblM[2] = Label(master, text="mm", font=("Calibri",text))#Units Range
        self.lblM[3] = Label(master, text="steps", font=("Calibri",text))#Units Step
        TxtM[0] = Entry(master, width=5, justify=RIGHT)
        TxtM[1] = Entry(master, width=5, justify=RIGHT)
        TxtM[2] = Entry(master, width=5, justify=RIGHT)
        self.lblM[0].place(x=40,y=yposM)
        TxtM[0].place(x=170,y=yposM)
        self.lblM[1].place(x=220,y=yposM+5)
        TxtM[1].place(x=235,y=yposM)
        self.lblM[2].place(x=280,y=yposM+5)
        TxtM[2].place(x=310,y=yposM)
        self.lblM[3].place(x=356,y=yposM+5)
        TxtM[0].insert(0,"0") #Motor Position Range and Steps
        TxtM[1].insert(0,PosMax)
        TxtM[2].insert(0,"%.0d"%StepRev)#Default steps = 360deg

        self.lblV = [None]*4
        self.lblV[0] = Label(master, text="Voltage:", font=("Calibri",text+4))
        self.lblV[1] = Label(master, text="to", font=("Calibri",text))
        self.lblV[2] = Label(master, text="V", font=("Calibri",text))#Units Range
        self.lblV[3] = Label(master, text="V", font=("Calibri",text))#Units Step
        TxtV[0] = Entry(master, width=5, justify=RIGHT)
        TxtV[1] = Entry(master, width=5, justify=RIGHT)
        TxtV[2] = Entry(master, width=5, justify=RIGHT)
        self.lblV[0].place(x=40,y=yposM+30)
        TxtV[0].place(x=170,y=yposM+30)#Range min
        self.lblV[1].place(x=220,y=yposM+35)
        TxtV[1].place(x=235,y=yposM+30)#Range max
        self.lblV[2].place(x=283,y=yposM+35)
        TxtV[2].place(x=310,y=yposM+30)#Step
        self.lblV[3].place(x=358,y=yposM+35)
        TxtV[0].insert(0,"0")#Set Default
        TxtV[1].insert(0,"500")#Set Default
        TxtV[2].insert(0,"50")#Set Default

        self.lblT = [None]*2
        self.lblT[0] = Label(master, text="Integration time:", font=("Calibri",text+4))
        self.lblT[1] = Label(master, text="s", font=("Calibri",text))
        TxtT[0] = Entry(master, width=4, justify=RIGHT)
        self.lblT[0].place(x=40,y=yposM+60)
        TxtT[0].place(x=170,y=yposM+60)
        self.lblT[1].place(x=210,y=yposM+65)
        TxtT[0].insert(0,"5") #Integration Time

        self.lblDT = [None]*2
        self.lblDT[0] = Label(master, text="Delay btw readings:", font=("Calibri",text),wraplength=80)
        self.lblDT[1] = Label(master, text="s", font=("Calibri",text))
        TxtDT[0] = Entry(master, width=4, justify=RIGHT)
        self.lblDT[0].place(x=245,y=yposM+58)
        TxtDT[0].place(x=310,y=yposM+60)
        self.lblDT[1].place(x=358,y=yposM+65)
        TxtDT[0].insert(0,"2") #Delay Time

        self.lblE = [None]*2
        self.lblE[0] = Label(master, text="Energy:", font=("Calibri",text+4))
        self.lblE[1] = Label(master, text="keV", font=("Calibri",text))
        TxtE[0] = Entry(master, width=4, justify=RIGHT)
        self.lblE[0].place(x=40,y=yposM+90)
        TxtE[0].place(x=170,y=yposM+90)
        self.lblE[1].place(x=210,y=yposM+95)
        TxtE[0].insert(0,"0") #Energy

        self.lblThr = [None]*2
        self.lblThr[0] = Label(master, text="Beam Threshold:", font=("Calibri",text), wraplength=80)
        self.lblThr[1] = Label(master, text="V", font=("Calibri",text))
        TxtThr[0] = Entry(master, width=4, justify=RIGHT)
        self.lblThr[0].place(x=245,y=yposM+90)
        TxtThr[0].place(x=310,y=yposM+90)
        self.lblThr[1].place(x=358,y=yposM+95)
        TxtThr[0].insert(0,"0") #Threshold Signal

        self.TFLBtn = Button(master, text="Start Measurement", command=lambda: self.startA(), width=10, height=2, bg='#DDDDDD', activebackground='#32CD32', wraplength=100)
        self.TFLBtn.place(x=70,y=yposM+125)
        self.StopBtn = Button(master, text="Stop Measurement", command=lambda: self.stopmeasurement(False), width=10, height=2, bg='#DDDDDD', activebackground='#32CD32', wraplength=100)
        self.StopBtn.place(x=200,y=yposM+125)

        ###############################################
        ################# Manual settings ############# GUI Layout settings
        ###############################################

        self.lbl1 = Label(master, text="Manual settings:", font=("Calibri",text+8))
        self.lbl1.place(x=MVP+120, y=45)
        self.lbl2 = Label(master, text="Set reference position:", font=("Calibri",text+6))
        self.lbl2.place(x=MVP+95, y=75)

#       self.MUBtn = Button(master, text="Set Motor Top", command=lambda: self.movemotlimit(1,0,0.0015,stopm), width=12)
        self.MUBtn = Button(master, text="Set Motor Top", command=lambda: self.premovemotlimit(1), width=12)
        self.MUBtn.place(x=MVP+125,y=105)
        #self.MDBtn = Button(master, text="Set Motor Bottom", command=lambda: self.movemotlimit(0,0,0.0015,stopm), width=12)
        self.MDBtn = Button(master, text="Set Motor Bottom", command=lambda:  self.premovemotlimit(0), width=12)
        self.MDBtn.place(x=MVP+125,y=145)

        #Manual Positioning
        ylblpos = 175
        ylblvolt = ylblpos+225
        self.lblpos = [None]*4
        self.lblpos[0] = Label(master, text="Position:", font=("Calibri",text+6))
        self.lblpos[0].place(x=MVP+140,y=ylblpos)
        self.lblStep = Label(master, text="(Step = %.3f mm)"%MinStep, font=("Calibri",text))#Units Step
        self.lblStep.place(x=MVP+240,y=ylblpos)
        self.lblRev = Label(master, text="(1 rev = %.0d steps)"%StepRev, font=("Calibri",text))#Units Step
        self.lblRev.place(x=MVP+240,y=ylblpos+15)

        self.TxtUp = Entry(master, width=6, justify=RIGHT)
        self.TxtUp.place(x=MVP+130,y=ylblpos+30)
        self.TxtUp.insert(0,"%.0d"%StepRev)
        self.SUBtn = Button(master, text="Move Up", command=lambda: self.movemot(1,self.TxtUp.get(),0.001,stopm), width=8)
        self.SUBtn.place(x=MVP+25,y=ylblpos+25)
        self.lblpos[2] = Label(master, text="steps", font=("Calibri",text+2))
        self.lblpos[2].place(x=MVP+182, y=ylblpos+33)

        self.TxtDown = Entry(master, width=6, justify=RIGHT)
        self.TxtDown.place(x=MVP+130,y=ylblpos+70)
        self.TxtDown.insert(0,"%.0d"%StepRev)
        self.SDBtn = Button(master, text="Move Down", command=lambda: self.movemot(0,self.TxtDown.get(),0.001,stopm), width=8)
        self.SDBtn.place(x=MVP+25,y=ylblpos+65)
        self.lblpos[3] = Label(master, text="steps", font=("Calibri",text+2))
        self.lblpos[3].place(x=MVP+182, y=ylblpos+73)


        initpos = GetPos(False)
        self.GetPosBtn = Button(master, text="Get Position", command=lambda: self.UpdatePosLabel(), width=8)
        self.GetPosBtn.place(x=MVP+25,y=ylblpos+105)
        self.lblpos[1] = Label(master, text=str(initpos)+" mm", font=("Calibri",text+2))#Updated label
        self.lblpos[1].place(x=MVP+132,y=ylblpos+115)

        self.Posicio_scale = Scale(master, orient = VERTICAL,from_ = float(PosMax),to =float(PosMin), resolution = float(MinStep), variable = initpos, fg = '#000000', activebackground = '#FF0000',label = "",troughcolor = "#00FF00")
        self.Posicio_scale.place(x=MVP+235, y=ylblpos+35)
        self.Posicio_scale.set(initpos)
#       self.Posicio_scale.pack(anchor=CENTER)#, side = RIGHT)
        self.GoBtn = Button(master, text="Go", command=lambda: self.gogo(stopm))
        self.GoBtn.place(x=MVP+305,y=ylblpos+105)

        #Manual Measurement display and buttons
        self.Measure = Label(master, text="QSX: "+str(voltDisplay), font=("Calibri",text+2))#Updated label
        self.Measure.place(x=MVP+280,y=ylblpos+145)
        self.MeasureBtn = Button(master, text="Measure", command=lambda: self.GetMeasurement())
        self.MeasureBtn.place(x=MVP+280,y=ylblpos+165)
        self.highestQSX = Label(master, text = "Highest QSX: {:.5} at {:.4}mm".format(maxQSX, maxQPos), font=("Calibri",text+1))
        self.highestQSX.place(x=MVP+50,y=ylblpos+165)

        #Information Lights
        self.MeasurementProgress = Label(master, text="Measurement in Progress", font=("Calibri",text+2), bg='#FFFFFF', wraplength=100)
        self.MeasurementProgress.place(x=950,y=ylblvolt+30)
        self.MeasurementComplete = Label(master, text="Measurement Complete", font=("Calibri",text+2), bg='#FFFFFF', wraplength=100)
        self.MeasurementComplete.place(x=950,y=ylblvolt-10)
        self.TopLimit = Label(master, text="Top Limit", font=("Calibri",text+2), bg='#FFFFFF', wraplength=50)
        self.TopLimit.place(x=945,y=ylblvolt+80)
        self.BottomLimit = Label(master, text="Bottom Limit", font=("Calibri",text+2), bg='#FFFFFF', wraplength=50)
        self.BottomLimit.place(x=1000,y=ylblvolt+80)

        self.CommentLab = Label(master, text="Comment:", font=("Calibri",text+2))
        self.CommentLab.place(x=MVP+25,y=ylblvolt+180)
        comment = Entry(master, width=40, justify=LEFT)
        comment.place(x=MVP+100,y=ylblvolt+180)
        
        
        initvolts = GetADC1()
        if(float(initvolts)>1000):
            bglblV='#FF0000'
        else:
            bglblV='#00FF00'
        
        #Manual Voltage setting
        self.lblV = [None]*3
        self.lblV[0] = Label(master, text="Plate Voltage:", font=("Calibri",text+6))
        self.lblV[0].place(x=MVP+140,y=ylblvolt)
        self.GetVBtn = Button(master, text="Get Volts", command=lambda: self.UpdateVoltLabel(), width=8)
        self.GetVBtn.place(x=MVP+25,y=ylblvolt+25)
        self.lblV[1] = Label(master, text=str(initvolts)+"V", font=("Calibri",text+2),bg=bglblV)#Updated label
        self.lblV[1].place(x=MVP+132,y=ylblvolt+35)

        TxtsetV = Entry(master, width=5, justify=RIGHT)
        TxtsetV.place(x=MVP+120,y=ylblvolt+70)#Range min
        TxtsetV.insert(0,"10")#Set Default
        self.SetVBtn = Button(master, text="Set Volts", command=lambda: self.SetGetVolts(TxtsetV.get()), width=8)
        self.SetVBtn.place(x=MVP+25,y=ylblvolt+65)
        self.lblV[2] = Label(master, text="V", font=("Calibri",text+2))
        self.lblV[2].place(x=MVP+167,y=ylblvolt+75)

        #Start new file button
        self.StartFileBtn = Button(master, text="Start New Log File", command=lambda: StartNewFile(), width=10, height=2, bg='#DDDDDD', activebackground='#32CD32', wraplength=100)
        self.StartFileBtn.place(x=MVP+25,y=ylblvolt+115)

        #Close Button
        self.close_button = Button(master, text="Close", command=lambda: self.close())#command=master.quit)
        self.close_button.place(x=1035,y=ylblvolt+180)#y=size-40

        #Estop and Home buttons
        self.EStopBtn = Button(master, text="ESTOP", command=lambda: self.Estop(), width=9, height=2, bg='#FF0000',activebackground = '#a60000')
        self.EStopBtn.place(x=900,y=ylblvolt+150)
        self.homeBtn = Button(master, text="Home", command=lambda: self.home(), width=8)
        self.homeBtn.place(x=1020,y=ylblvolt+140)

        textPos = 770
        #####################
        ### Instructions ####
        self.Instruct = Label(master, text='Instructions', font=("Calibri",text+4), wraplength=200)
        self.Instruct.place(x=textPos+130, y=10)
        self.measureInst = Label(master, text='Measurement Cycle:\n\
            - Enter Positon and Voltage Ranges and Steps\n\
            - Enter Beam Energy: Set by user only, no readback\n\
            - Enter Threshold Signal: Eliminate noise from data\n\
            - Add Comment, Saved to Data file\n', font=("Calibri",text), anchor="e", justify=LEFT)
        self.measureInst.place(x=textPos, y=30)
        self.StripInst = Label(master, text='Striptool:\n\
            - Adjust Max and Min ranges for all values\n\
            - Select value for second axis\n\
            - Adjust Axis and frequency if desired\n', font=("Calibri",text), anchor="e", justify=LEFT)
        self.StripInst.place(x=textPos, y=110)
        self.ManualInst = Label(master, text='Manual Options:\n\
            - Must set Top and Bottom limit first\n\
            - Move # of Steps or select position on scale\n\
            - Measurement button: Capture a single signal reading\n\
            - Voltage: Manually set, readback from power supply\n', font=("Calibri",text), anchor="e", justify=LEFT)
        self.ManualInst.place(x=textPos, y=180)
        self.ButtonInst = Label(master, text='Buttons:\n\
            - Split Data file: Start new file\n\
            - Home: Returns Meter to top position\n\
            - Estop: Stops all motor motion, set voltage to zero\n', font=("Calibri",text), anchor="e", justify=LEFT)
        self.ButtonInst.place(x=textPos, y=260)
        

        ##############################################################
        ########################## Striptool #########################
        ##############################################################
        global outputfile
        global Colores
        global Var
        global LW
        global NDevices
        yposST = yposM+195
        #Feature[Unit],Label[Units],Min,Max,?,lblUnits,RNGTestMin/addr,RngTestMax/ch
        Var[0] = (Feature("Position [mm]","Motor Position [mm]",[0.00-1,PosMax+10],-1,"%.2f mm",[Colores[0][0],Colores[0][1]]))#POS
        Var[1] = (Feature("Energy [keV]","Energy  [keV]",[0,5000],-1,"%.0f keV",[Colores[1][0],Colores[1][1]]))
        Var[2] = (Feature("Voltage Set [V]","Voltage Set [V]",[0.00-1,1010],-1,"%.3f V",[Colores[2][0],Colores[2][1]]))#VOLTS SET
        Var[3] = (Feature("Voltage RDBK [V]","Voltage Readback [V]",[0.00,1010],-1,"%.3f V",[Colores[3][0],Colores[3][1]]))#AIN2
        Var[4] = (Feature("Initial angle [mrad]","Initial angle x' [mrad]",[0,150],-1,"%.1f mrad",[Colores[4][0],Colores[4][1]]))#AIN2
        Var[5] = (Feature("QSX [V]","QSX [V]",[0.00,1010],-1,"%.3f V",[Colores[5][0],Colores[5][1]]))#AIN3

        self.lblTitStriptool = Label(master, text="Striptool settings", font=("Calibri",text+6))
        self.lblTitStriptool.place(x=120,y=yposST)

        self.lmin = Label(master, text="Min", font=("Calibri",text))
        self.lmin.place(x=30+180,y=yposST+30)
        self.lmax = Label(master, text="Max", font=("Calibri",text))
        self.lmax.place(x=30+240,y=yposST+30)
        self.lAx2 = Label(master, text="Axis R", font=("Calibri",text))
        self.lAx2.place(x=30+300,y=yposST+30)
        self.lLog = Label(master, text="Log", font=("Calibri",text))
        self.lLog.place(x=30+345,y=yposST+30)

        self.ticks = []#np.zeros(len(Var), dtype=bool)
        self.ticksLog = []#np.zeros(len(Var), dtype=bool)
        self.chk = []
        self.chkLog = []
        self.opt1 = []
        self.opt2 = []
        self.Ax2 = IntVar()
        self.ColorBtn = [None]*len(Var)
        self.TxtStUp = [None]*len(Var)
        self.TxtStDw = [None]*len(Var)
        LW = [None]*len(Var)
       # LW = [None]*len(Var)
        for i in range(0,len(Var)):#Change to number of positions in the line array
            tick = IntVar()
            tickLog = IntVar()
            self.chk=Checkbutton(master, text=Var[i].Name, onvalue=1,offvalue=0,variable=tick)
            self.chk.place(x=30+30,y=yposST+50+i*30)
            self.chk.select()
            self.ticks.append(tick)
            if(i>0):
                self.opt2=Radiobutton(master,text="",variable=self.Ax2,value=i)
                self.opt2.place(x=30+300,y=yposST+50+i*30)
            self.chkLog=Checkbutton(master, text="", onvalue=1,offvalue=0,variable=tickLog)
            self.chkLog.place(x=30+340,y=yposST+50+i*30)
            self.ticksLog.append(tickLog)
            self.ColorBtn[i]=Button(master,bd=0, activebackground = Var[i].Color[1], bg=Var[i].Color[0],command=lambda a1=i,a2=self.ColorBtn: self.ChangeColorPreface(a1,a2), text="", width=1, height=1, font=("Calibri",8))
            self.ColorBtn[i].place(x=30,y=yposST+50+i*30)
            self.TxtStDw[i]=Entry(master, width=6, justify=RIGHT)
            self.TxtStUp[i]=Entry(master, width=6, justify=RIGHT)
            self.TxtStDw[i].place(x=30+180,y=yposST+50+i*30)
            self.TxtStUp[i].place(x=30+240,y=yposST+50+i*30)
            self.TxtStUp[i].insert(0,Var[i].Limits[1])#limits[i][1])
            self.TxtStDw[i].insert(0,Var[i].Limits[0])#limits[i][0])
            LW[i]=1.5

        yposSTBtn = yposST+250
        self.lTxtXt1 = Label(master, text="    Set X axis (s)", font=("Calibri",text+2))
        self.lTxtXt2 = Label(master, text="Span time:", font=("Calibri",text))
        self.lTxtXt3 = Label(master, text="Right ref.:", font=("Calibri",text))
        self.TxtX1=Entry(master, width=6, justify=RIGHT)
        self.TxtX2=Entry(master, width=6, justify=RIGHT)
        self.lTxtXt1.place(x=270,y=yposSTBtn)
        self.lTxtXt2.place(x=270,y=yposSTBtn+25)
        self.lTxtXt3.place(x=270,y=yposSTBtn+45)
        self.TxtX1.place(x=330,y=yposSTBtn+20)
        self.TxtX1.insert(0,60)
        self.TxtX2.place(x=330,y=yposSTBtn+40)
        self.TxtX2.insert(0,0)

        self.FreqValue = 1
        self.BtnFreq = Button(master)
        self.BtnFreq = Button(master, text="Set register frequency Current: %d s"%self.FreqValue, wraplength=90, command=lambda a1=self.BtnFreq: self.RegFreq(a1), font=("Calibri",text+2), width=8, height=3)
        self.BtnFreq.place(x=170,y=yposSTBtn)

        self.StartBtn = Button(master, text="Start Striptool", wraplength=70, command=lambda: self.Striptool(), width=5, height=3, bg='#DDDDDD', activebackground='#32CD32')
        self.StartBtn.place(x=20,y=yposSTBtn)
        self.PauseBtn = Button(master, text="Pause Log File", wraplength=50, command=lambda: self.PauseAction(), width=5, height=3, bg='#DDDDDD')
        self.PauseBtn.place(x=95,y=yposSTBtn)

    #Update GUI Functions
    def UpdatePosLabel(self):
        pos=GetPos(True)
        self.lblpos[1].config(text=str(pos)+" mm")
        pos="%.2f"%float(GetPos(True))
        self.Posicio_scale.set(float(pos))
        self.lblpos[1].config(text=str(pos)+" mm")
        self.UpdateMovementLabel()
    
    def UpdateMovementLabel(self):
        if GPIO.input(17)==GPIO.LOW:
            bkgdTop = '#FFD700'
        else:
            bkgdTop = '#FFFFFF'

        if GPIO.input(4)==GPIO.LOW:
            bkgdBottom = '#FFD700'
        else:
            bkgdBottom = '#FFFFFF'
        self.TopLimit.config(bg = bkgdTop)
        self.BottomLimit.config(bg = bkgdBottom)

    def UpdateVoltLabel(self):
        voltage=GetADC1()
        if(float(voltage)>1000):
            lblVColor='#FF0000'
        else:
            lblVColor='#00FF00'
        self.lblV[1].config(text=str(voltage)+" V",bg=lblVColor)

    def SetGetVolts(self,v2set):
        SetVolts(v2set,stopm)
        self.UpdateVoltLabel()

    def home(self):
        self.movemotlimit(1,0,0.001,True)
       

    #Safe Shutdown Function
    def close(self):
        stopm = True
        global f1, p2, p1
        global outputfile
        global Running
        global EnableUpdatePlotNotRunning
        if(outputfile!=None):#STOP Striptool if file exists
            Running = False
            EnableUpdatePlotNotRunning = True
            outputfile.close()
            outputfile=None #Enables Start
        if(f1 is not None):
            #f1.flush()
            time.sleep(0.1)
            f1.close()
        #self.home() #Move meter to top postion, out of beam line ***Uncomment****
        if 'p1' in globals():
            p1.terminate()
        if 'p2' in globals():
            p2.terminate()
        GPIO.output(21,GPIO.HIGH) #disable motor controller (Board 1: Active Low, Board 2: Active High)
        GPIO.setup(27,GPIO.OUT)
        GPIO.output(27, GPIO.HIGH) #disable Voltage Control
        GPIO.cleanup()
        sys.exit(0)

    #Manuel Beam Checking function, saves highest recorded signal
    def GetMeasurement(self):
        global maxQSX, maxQPos
        voltDisplay=float(GetADC3())
        self.Measure.config(text = "QSX: "+str(voltDisplay))
        if float(voltDisplay) > float(maxQSX):
            maxQSX = voltDisplay
            maxQPos = float(GetPos(False))
        self.highestQSX.configure(text="Highest QSX: {:.5} at {:.4}mm".format(maxQSX, maxQPos))
        
    #Stop all movement
    def Estop(self):
        global stopm, StopMot, p1, p2
        StopMot = True
        stopm = True
        if 'p1' in globals():
            p1.terminate()
        if 'p2' in globals():
            p2.terminate()
        SetVolts(0,True)
        pos="%.2f"%float(GetPos(True))
        self.Posicio_scale.set(float(pos))
        self.lblpos[1].config(text=str(pos)+" mm")
        self.MeasurementProgress.config(bg = '#FFFFFF')
        self.MeasurementComplete.config(bg = '#FFFFFF')
        print("All opperation stopped")
        func.Missatge("Warning","ESTOP Performed, All operations ceased")

    #Motor Moving Function: Opens subprocess
    def movemot(self,sentit,stp,delay,moveallowed):#Sentit 0Down, 1Up
        checkMoving = isMoving()
        if(moveallowed and not checkMoving):
            global PosMaxSet,PosMinSet,PosMax,f1,StopMot, p2
            if(not (bool(PosMaxSet) and bool(PosMinSet))):
                if((not bool(PosMaxSet)) and (not bool(PosMinSet))):
                    func.Missatge("Warning","The reference position of the motor has to be set to start. Use Motor Top and Motor Bottom buttons to set it.")
                elif((not bool(PosMaxSet)) and bool(PosMinSet)):
                    func.Missatge("Warning","The reference position of the motor has to be set to start. Use Motor Top to finish the reference setting.")
                elif(bool(PosMaxSet) and (not bool(PosMinSet))):
                    func.Missatge("Warning","The reference position of the motor has to be set to start. Use Motor Down to finish the reference setting.")
            else:
                pos="%.2f"%float(GetPos(False))
                if ((not func.isint(stp)) or int(stp)<=0 or int(stp)>int(float(PosMax)/float(MinStep))):
                    func.Missatge("Warning","The motor step entry box must contain a positive integer")
                    if int(stp)>int(float(PosMax)/float(MinStep)):
                        stp = 0
                elif(not func.isfloat(delay) or float(delay)<0.001):#0.0005 is the minimum working
                    func.Missatge("Warning","The delay set for the motor driver has to be a float number greater or equal to 0.001.")
                elif(not func.isint(sentit) or (int(sentit)<0 or int(sentit)>1)):
                    func.Missatge("Warning","Direction has to be 0 or 1.")
                else:
                    if (int(sentit)==1 and (int(stp)>int((float(PosMax)-float(pos))/float(MinStep)))):
                        func.Missatge("Error","The position of the plates is too high to move %d steps up." %int(stp))
                    elif (int(sentit)==0 and (int(stp)>int((float(pos)-float(PosMin))/float(MinStep)))):
                        func.Missatge("Error","The position of the plates is too low to move %d steps down." %int(stp))
                    else:
                        pos="%.2f"%float(GetPos(False))
                        if(int(stp)>0):# and (not stopm):
                            p2 = Popen(['python3','MotorMove.py', str(sentit),str(stp),str(delay)])
                            finestra.attributes('-topmost',True)
                            finestra.focus_force()
                            self.UpdateMovementLabel()
        else:#not moveallowed
            func.Missatge("Not Allowed","A measurement or movement is ongoing, this action is not allowed.")

    #Setting top and bottom with limit switches
    def premovemotlimit(self,a):
        global StopMot, PosMinSet, PosMaxSet
        self.movemotlimit(a,0,0.001,stopm)

    def movemotlimit(self,sentit,stp,delay,moveallowed):#stp==0
        global PosMinSet,PosMaxSet,PosMin,PosMax,f1,StopMot, PosVoltMin, PosVoltMax, p1, stopm
        #print ("Max and Min POS:", PosMin, PosMax)
        checkMoving = isMoving()
        if(moveallowed and not checkMoving):
            pos="%.2f"%float(GetPos(False))
            if(PosMaxSet and self.Posicio_scale.get()>=PosMax and sentit==1):
                func.Missatge("Info","The device is already at its highest position.")
            elif(PosMinSet and self.Posicio_scale.get()<=PosMin and sentit==0):
                func.Missatge("Info","The device is already at its lowest position.")
            else:#Not PosSet or PosMin<Pos<PosMax
                if(not func.isfloat(delay) or float(delay)<0.001):#0.0005 is the minimum working
                    func.Missatge("The delay set for the motor driver has to be a float number greater or equal to 0.001.")
                elif(not func.isint(sentit) or (int(sentit)<0 or int(sentit)>1)):
                    func.Missatge("Direction has to be 0 or 1.")
                else:#All errors clear, Open Subprocess for motor moving
                    p1 = Popen(['python3','MotorMove.py', str(sentit),str(stp),str(delay)])
                    self.UpdateMovementLabel()
                    #self.lift()
                    finestra.attributes('-topmost',True)
                    finestra.focus_force()
                    #setting Top and Bottom Limits Flags
                    if(int(sentit)==0):
                        PosMinSet=True
                    else:#if(int(sentit)==1):
                        PosMaxSet=True
        else:#not moveallowed
            func.Missatge("Not Allowed","A measurement or movement is ongoing, this action is not allowed.")

    #Manual Scale Moving Function
    def gogo(self,moveallowed):
        global PosMaxSet,PosMinSet,PosMin,PosMax,StopMot
        if(not (bool(PosMaxSet) and bool(PosMinSet))):
            func.Missatge("Warning","The position reference has to be set before moving the motor. Use Motor Top and Motor Bottom buttons.")
            pos = "%.2f"%float(GetPos(False))
            self.Posicio_scale.set(float(pos))
            self.lblpos[1].config(text=str(pos)+" mm")
        else:
            pos = float(GetPos(False))
            newpos = float(self.Posicio_scale.get())
            if(float(newpos) > float(pos)):
                sentit = 1
            else:#elif(float(newpos) <= float(pos)):
                sentit = 0
            stepstomove = round((abs(float(newpos) - float(pos)))/(float(MinStep)))
            if (stepstomove<1 and stopm):
                func.Missatge("Info","The position required is already the current position.")
            self.movemot(sentit,int(stepstomove),0.0015,bool(moveallowed))

    #Auto Set upper and lower limit, at start of measurement cycle
    def SetRefPosition(self):
        global PauseStriptool
        PauseStriptool = True
        if(float(GetPos(False))<float(65.0)):
            if(not bool(PosMinSet)):
                self.movemotlimit(0,0,0.0015,True)
            if(not bool(PosMaxSet)):
                self.movemotlimit(1,0,0.0015,True)
        else:#if(float(GetPos(False))>=float(65.0)):
            if(not bool(PosMaxSet)):
                self.movemotlimit(1,0,0.0015,True)
            if(not bool(PosMinSet)):
                self.movemotlimit(0,0,0.0015,True)
        PauseStriptool = False

    #Start of Main Measurement Loop: Error Checking
    def startA(self):
        global PauseStriptool,Running #Striptool control
        global stopm, PosMin, PosMax
        global TxtM,TxtV,TxtT,TxtE,TxtDT,Angle,EnergySet, TxtThr, t
        checkMoving = isMoving()
        if(not stopm and not checkMoving):
            func.Missatge("Info","Measurement is ongoing.")
        else:
            if(not(func.isint(TxtV[0].get()) and func.isint(TxtV[1].get()) and func.isint(TxtV[2].get()))):
                func.Missatge("Warning","Voltage values are not correct. Only integers are allowed. Measurement aborted.")
            elif(int(TxtV[0].get())>1000 or int(TxtV[1].get())>1000):
                func.Missatge("Warning","Maximum voltage to operate is 1000V. Measurement aborted.")
            elif(int(TxtV[2].get())<0):
                func.Missatge("Warning","Step voltage can't be a negative value. Measurement aborted.")
            elif(int(TxtV[2].get())>abs(int(TxtV[1].get())-int(TxtV[0].get()))):
                func.Missatge("Warning","Voltage step is larger than the range. Measurement aborted.")
            elif(int(TxtV[2].get())==0 and abs(int(TxtV[1].get())-int(TxtV[0].get()))>0):
                func.Missatge("Warning","Voltage step can only be 0V in the case of min and max voltages in the measurement are the same value. Measurement aborted.")
            elif(not(func.isfloat(TxtM[0].get()) and func.isfloat(TxtM[1].get()) and func.isint(TxtM[2].get()))):
                func.Missatge("Warning","Motor position values are not correct. Ranges must be float numbers and the steps entry box requires a positive integer. Measurement aborted.")
            elif(int(TxtM[2].get())<1):
                func.Missatge("Warning","The number of steps has to be an integer positive number. Measurement aborted.")
            elif((int(TxtM[2].get())*float(MinStep))>abs(float(TxtM[1].get())-float(TxtM[0].get()))):
                func.Missatge("Warning","Motor step is larger than the set range. Measurement aborted.")
            elif(float(TxtM[0].get())>PosMax or float(TxtM[1].get())>PosMax):
                func.Missatge("Warning","Maximum motor position allowed is %f. Measurement aborted."%(PosMax))
            elif(float(TxtM[0].get())<PosMin or float(TxtM[1].get())<PosMin):
                func.Missatge("Warning","Minimum motor position allowed is %f. Measurement aborted."%(PosMin))
            elif(float(TxtM[0].get())==float(TxtM[1].get()) and (int(TxtM[2].get())>0)):
                func.Missatge("Warning","Positions are not possible to achieve with the set steps distance. Measurement aborted.")
            elif(not (func.isint(TxtDT[0].get())) or int(TxtDT[0].get())<1):
                func.Missatge("Warning","The delay time between measurements has to be an integer positive number. Measurement aborted.")
            elif(not (func.isint(TxtT[0].get())) or int(TxtT[0].get())<1):
                func.Missatge("Warning","The integration time of the measurements has to be an integer positive number. Measurement aborted.")
            elif(not (func.isint(TxtE[0].get())) or int(TxtE[0].get())<8 or int(TxtE[0].get())>60):
                func.Missatge("Warning","The energy value has to be an integer and in the range of 8keV to 60keV. Measurement aborted.")
            else:
                stopm = False
                StopMot = False
                self.MeasurementProgress.config(bg = '#FFD700')
                self.MeasurementComplete.config(bg = '#FFFFFF')
                if(not (bool(PosMaxSet) and bool(PosMinSet))):
                    messagebox.showinfo("Info","The reference position is not set yet. The system is setting the position before starting the measurement now.")
                    sleep(0.1)
                    self.SetRefPosition()
                t = th(target = self.startB)
                t.start()
                
    #Actual Main Measurement Loop
    #Run in a new Thread
    def startB(self):
        global EnergySet, PosMaxSet, PosMinSet
        global stopm,StopMot
        global TxtM,TxtV,TxtT,TxtE,TxtDT,thresSignal, maxQSX, maxQPos, p2
        #Read and Arrange all inputs from user
        while True:
            if(not stopm):
                EnergySet=TxtE[0].get()
                PosInit = float(TxtM[0].get())
                PosEnd = float(TxtM[1].get())
                Steps = int(TxtM[2].get())
                thresSignal = float(TxtThr[0].get())
                if(float(TxtM[1].get())>float(TxtM[0].get())):
                    sentit = 1
                else:
                    sentit = 0
                if(int(TxtV[0].get())<int(TxtV[1].get())):
                    StepV = int(TxtV[2].get())
                    VoltInit = int(TxtV[0].get())
                    VoltEnd = int(TxtV[1].get())
                else:
                    StepV = -1*int(TxtV[2].get())
                    VoltInit = int(TxtV[0].get())
                    VoltEnd = int(TxtV[1].get())
                StartNewFile() #Start emittance data file
                
                #Send to Starting position
                pos = "%.2f"%float(GetPos(False))
                self.lblpos[1].config(text=str(pos)+" mm")
                self.Posicio_scale.set(float(PosInit))
                self.gogo(True)
                sleep(0.5)
                pos = "%.2f"%float(GetPos(False))
                self.Posicio_scale.set(pos)#Read first position set
                self.lblpos[1].config(text=str(pos)+" mm")
                it=0 #Loop Counter
                MoveIt = float(int(Steps)*float(MinStep)) #Distance moved each loop
                self.UpdatePosLabel()

                #Main Measurement Loop
                while((sentit == 1 and float(PosEnd)>(float(pos)+float(MoveIt))) or (sentit == 0 and float(PosEnd)<(float(pos)-float(MoveIt)))):
                    if stopm:
                        break
                    #Move sensor set amount of steps, every loop but the first
                    if(it>0):
                        self.movemot(int(sentit),int(Steps),0.001,True)
                        sleep(0.5)
                    it=it+1
                    pos = "%.2f"%float(GetPos(False))
                    self.UpdatePosLabel()

                    #Voltage Measurments, one voltage only
                    if(StepV==0):#VoltInit == VoltEnd (Only Measuring one voltage)
                        if stopm:
                            break
                        else:
                            readbackvolt=SetVolts(int(VoltEnd),True)
                            self.UpdateVoltLabel()
                            sleep(int(TxtDT[0].get()))#Delay
                            #Signal integration
                            tin=datetime.now()
                            counts=0 #Integration Counter
                            #Integration Loop
                            while(datetime.now()-tin).seconds<int(TxtT[0].get()) and (not stopm):#sleep(int(TxtT[0].get()))
                                signal = float(GetADC3())
                                if(signal>float(thresSignal)):#checking if signal is higher than threshold signal
                                    if float(signal) > float(maxQSX): #keeping track of max recorded signal
                                        maxQSX = signal
                                        maxQPos = pos
                                    self.highestQSX.configure(text="Highest QSX: {:.5} at {:.4}mm".format(maxQSX, maxQPos))
                                    counts=counts+1
                            SaveLine(counts)
                            self.UpdatePosLabel()

                    #Measuring a Voltage Range
                    else:
                        for j in range (int(VoltInit),int(VoltEnd),int(StepV)):#j=volts
                            if stopm:
                                break
                            else:
                                readbackvolt=SetVolts(j,True)
                                self.UpdateVoltLabel()
                                sleep(int(TxtDT[0].get()))#Delay
                                
                                #Signal integration: calaculating counts and storing highest observed signal
                                tin=datetime.now()
                                counts=0
                                while(datetime.now()-tin).seconds<int(TxtT[0].get()) and (not stopm):#sleep(int(TxtT[0].get()))
                                    signal = float(GetADC3())
                                    if(signal>float(thresSignal)):#SetThershold
                                        if float(signal) > float(maxQSX): #keeping track of max recorded signal
                                            maxQSX = signal
                                            maxQPos = pos
                                        self.highestQSX.configure(text="Highest QSX: {:.5} at {:.4}mm".format(maxQSX, maxQPos))
                                        counts=counts+1
                                SaveLine(counts)
                                self.UpdatePosLabel()
                if(not stopm): #if measurement not stopped early by user, run Stop Measurement 
                    print("Measurement completed")
                    isAuto = True
                    self.MeasurementComplete.config(bg = '#00FF00', height=3, font=("Calibri",8+4), wraplength=150)
                    self.MeasurementComplete.place(x=940, y=360)
                    self.MeasurementProgress.config(bg = '#FFFFFF')
                    sleep(5)
                    self.MeasurementComplete.config(font=("Calibri",8+2), height=2)
                    self.MeasurementComplete.place(x=950,y=390)
                    self.stopmeasurement(isAuto)
                break

    #Safely exits measurement cycle, Initiated by user or run at end of measurement loop
    def stopmeasurement(self,isAuto):
        global stopm,StopMot, p2, p1
        if(stopm==True):
            func.Missatge("Info","No measurement was running.")
        if (not isAuto and not stopm):
            func.Missatge("Info","Measurement Ended by User")
        stopm = True
        StopMot = True
        if 'p1' in globals():
            p1.terminate()
        if 'p2' in globals():
            p2.terminate()
        self.MeasurementProgress.config(bg = '#FFFFFF')
        self.UpdatePosLabel()
        SetVolts(0,True)
        self.UpdateVoltLabel()
        SaveLine("end")



#############################################################################################
################################# STRIPTOOL functions #######################################
#############################################################################################
    def PauseAction(self): #Pause function, consider using ! operator
        global PauseStriptool
        if (not PauseStriptool):
            PauseStriptool = True
            EnableUpdatePlotNotRunning = True
        else:# (PauseStriptool):
            PauseStriptool = False
            EnableUpdatePlotNotRunning = False

    #Intial Striptool Startihng function, check if file already exsits
    def Striptool(self):
        global outputfile
        global Running
        global EnableUpdatePlotNotRunning
        if(outputfile!=None):#STOP Striptool if file exists
            Running = False
            EnableUpdatePlotNotRunning = True
            outputfile.close()
            outputfile=None #Enables Start
            self.StartBtn.config(text="Start Striptool", bg='#DDDDDD', activebackground='#32CD32')
        else:#Outputfile=None
#            th (target = self.startB).start()#stopm in startB prevents running when not allowed
            Running=True
            EnableUpdatePlotNotRunning = False
            p0 = Process(target=self.StriptoolStart(),)
            p0.start()
            while(Running):
                a=True
            p0.terminate()

    #Main Striptool Function: Data Write
    def StriptoolStart(self):
        global PauseStriptool
        global Running
        global outputfile
        global updatecolor
        global LW
        global EnableUpdatePlotNotRunning
        self.line = np.zeros(len(Var)+2)
        self.linestr = [None]*(len(Var)+2)
        plt.style.use('ggplot')#set ggplot style
        fig, self.axL = plt.subplots()
        fig.subplots_adjust(right=0.88)
        self.ax = [None]*len(Var)
        #self.ax = np.empty(len(Var))

        fig.canvas.draw()
        self.axL.set_xlim(float(self.TxtX2.get())-float(self.TxtX1.get()),float(self.TxtX2.get()))
        self.axL.set_title('Emittance Striptool')
        self.axL.set_xlabel('Time (s)')
        if(self.ticksLog[0].get()==True):
            self.axL.set_yscale('log')
        for i in range(0,len(Var)):
            self.ax[i] = self.axL.twinx()
            self.ax[i].tick_params(axis='y', labelcolor=Var[i].Color[0])
            self.ax[i].yaxis.label.set_color(Var[i].Color[0])
        self.StartBtn.config(text="Stop Striptool", bg='#DDDDDD', activebackground='#AA0000')
        #Open and Write Data File
        tfile = time.strftime("%Y%m%d-%H%M%S")
        NameFile = "data/" + tfile + "_StriptoolData.csv" #Writing Strip Tool File
        PauseStriptool=False
        Running = True
        outputfile = open(NameFile,"w")#Not Append because is always a new measurment.
        capsal = [None]*(len(Var)+2)
        capsal[0]="Date-hour"
        capsal[1]="Elapsed time"
        for i in range (0,len(Var)):
            capsal[i+2]= str(Var[i].Name)
        data = pd.DataFrame(columns=list(capsal))
        outputfile.write(', '.join(map(str,capsal))+"\n")#Every second
        initime=time.time()
        #Writing File while active:
        while(Running):
            self.linestr[0] = str(time.strftime("%Y%m%d-%H:%M:%S",time.localtime(time.time())))
            self.line[0] = time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()))
            self.linestr[1] = self.line[1] = "%.4f"%float(time.time()-initime)#dt
            self.setplot()
            self.lineIn=pd.DataFrame([self.line],columns=list(capsal))
            data = pd.concat([self.lineIn,data],ignore_index=True)
            sys.stdout.write(', '.join(map(str,self.linestr))+'\r')#View last line only
            sys.stdout.flush()
            if(not PauseStriptool):
                outputfile.write(', '.join(map(str,self.linestr))+"\n")#Every second
                for i in range(0,len(Var)):
                    if (self.ticks[i].get()==True):#Si no n' hi ha cap no plotejar!
                        if(self.ax[i].get_visible()==False or updatecolor):
                            self.ax[i].clear()
                            self.ax[i].tick_params(axis='y', labelcolor=Var[i].Color[0])
                            self.ax[i].yaxis.label.set_color(Var[i].Color[0])
                            self.ax[i].plot(data[capsal[1]],data[capsal[i+2]], marker='',color=Var[i].Color[0], linewidth=LW[i], label=Var[i].Label)
                        else:
                            self.ax[i].plot(data[capsal[1]].loc[0:1],data[capsal[i+2]].loc[0:1], marker='',color=Var[i].Color[0], linewidth=LW[i], label=Var[i].Label)
                        self.ax[i].set_visible(True)
                    else:
                         self.ax[i].set_visible(False)
                updatecolor = False
            plt.draw()#show()
            plt.pause(0.01)
            pt=time.time()-(initime+float(self.line[1]))
            if(float(self.FreqValue)>(float(pt)+0.0009)):
                sleep(float(self.FreqValue)-float(pt)-0.0009)

    #Update Plot Settings Function
    def UpdatePlot(self):
        global EnableUpdatePlotNotRunning
        global Var
        if(not EnableUpdatePlotNotRunning):
            func.Missatge("Error","Striptool running. Update when measurement stopped.")
        else: #(EnableUpdateNotRunning):
           self.setplot()
           for i in range(0,len(Var)):
               if (self.ticks[i].get()==True):
                   self.ax[i].tick_params(axis='y', labelcolor=Var[i].Color[0])
                   self.ax[i].yaxis.label.set_color(Var[i].Color[0])
                   self.ax[i].set_visible(True)
               else:
                    self.ax[i].set_visible(False)
           plt.draw()#show()

    #Plot Settings Function
    def setplot(self):
        if(func.isfloat(self.TxtX1.get()) and func.isfloat(self.TxtX2.get())):
            if(float(self.TxtX1.get()) > 0):
               self.axL.set_xlim(float(self.line[1])+(float(self.TxtX2.get())-float(self.TxtX1.get())),float(self.line[1])+float(self.TxtX2.get()))
            else:
                self.axL.set_xlim(float(self.line[1])-1,float(self.line[1]))
        for i in range (0,len(Var)):
            if(func.isfloat(self.TxtStDw[i].get()) and func.isfloat(self.TxtStUp[i].get())):
                if(float(self.TxtStDw[i].get()) != float(self.TxtStUp[i].get())):
                    if(i==0):
                        self.axL.set_ylim(float(self.TxtStDw[0].get()),float(self.TxtStUp[0].get()))
                    self.ax[i].set_ylim(float(self.TxtStDw[i].get()),float(self.TxtStUp[i].get()))
            if(self.ticksLog[i].get()==True):
                if func.isfloat(self.TxtStDw[i].get()):
                    if(float(self.TxtStDw[i].get())<=0):
                        self.TxtStDw[i].delete(0,"end")
                        self.TxtStDw[i].insert(0,'1e-7')
                    if(i==0):
                        self.axL.set_yscale('log')
                    self.ax[i].set_yscale('log')
            else:
                if(i==0):
                    self.axL.set_yscale('linear')
                self.ax[i].set_yscale('linear')
            self.axL.set_ylabel(Var[0].Label)
            if i==self.Ax2.get():
                self.ax[i].axes.get_yaxis().set_visible(True)
                self.ax[i].set_ylabel(Var[i].Label)
            else:
                 self.ax[i].axes.get_yaxis().set_visible(False)
            if(i==0):
                Var[i].VALUE = str(GetPos(False))
            elif(i==1):
                Var[i].VALUE = str(GetEnergy())
            elif(i==2):
                Var[i].VALUE = str(GetADC1())
            elif(i==3):
                Var[i].VALUE = str(GetADC2())
            elif(i==4):
                Var[i].VALUE = str(GetAngle())
            elif(i==5):
                Var[i].VALUE = str(GetADC3())
            else:
                Var[i].VALUE = str(-1)
            self.linestr[i+2] = self.line[i+2] = float(Var[i].VALUE)

############################################################################
###################COLOR CHANGE TOOL #######################################
############################################################################
    def ChangeColorPreface(self,colorrow,btn):
        global ChangeColorRunning
        if(ChangeColorRunning):
            func.Missatge("Action not possible","Please change properties for only one feature at a time.")
        else:
            ChangeColorRunning = True
            self.ColorProc(colorrow,btn)

    #Color Select
    def ColorProc(self,colorrow,btn):
        tk2 = tk.Toplevel(self)
        tk2.wm_title("Change properties feature %s"%str(colorrow+1))
        tk2.geometry('250x170')
        self.l1 = Canvas(tk2,width=50, height=20)
        self.l1.place(x=150, y=50)
        it = self.l1.create_line(0,10,50,10, fill=Colores[colorrow%len(Colores)][0],width=float(LW[colorrow])*1.5)
        self.LTit=Label(tk2,text="Modify the HEX color code in \"#RRGGBB\" format:", wraplength = 220)
        self.LTit.place(x=25,y=10)
        self.TxtRGB=Entry(tk2, width=8, justify=LEFT)
        self.TxtRGB.place(x=35,y=50)
        self.TxtRGB.insert(0,Colores[colorrow%len(Colores)][0])
        self.LW=Label(tk2,text="Set line width:")
        self.LW.place(x=25,y=90)
        self.TxtLWSet=Entry(tk2, width=3, justify=RIGHT)
        self.TxtLWSet.place(x=150,y=90)
        self.TxtLWSet.insert(0,LW[colorrow])
        self.BLoad=Button(tk2,bg='#DDDDDD', command=lambda a1=self.TxtRGB, a2 = colorrow, a3=btn, a4=self.TxtLWSet, a5=self.l1, a6=it: self.AssignColor(a1,a2,a3,a4,a5,a6), text="LOAD", width=6, height=1)
        self.BLoad.place(x=35,y=130)
        self.BClose=Button(tk2,bg='#DDDDDD', command=lambda a1=tk2: self.CloseAssignColor(a1), text="Close", width=6, height=1)#bg='#aaaaaa'
        self.BClose.place(x=150,y=130)

    #Apply Color
    def AssignColor(self,TxtRGB,colorrow,btn,TxtLWSet,l1,it):
        global Var
        global LW
        global Colores
        global updatecolor
        if(len(self.TxtRGB.get())==7 and bool(re.match(r"#[0-9,A-F,a-f][0-9,A-F,a-f][0-9,A-F,a-f][0-9,A-F,a-f][0-9,A-F,a-f][0-9,A-F,a-f]",self.TxtRGB.get())) and func.isfloat(TxtLWSet.get())):
            if(float(TxtLWSet.get())>0.0):
                Colores[colorrow][0] = self.TxtRGB.get()
                Colores[colorrow][1] = self.TxtRGB.get()
                Var[colorrow].Color[0]=Colores[colorrow%len(Colores)][0]
                Var[colorrow].Color[1]=Colores[colorrow%len(Colores)][1]
                btn[colorrow].config(activebackground = Var[colorrow].Color[1], bg=Var[colorrow].Color[0])
                LW[colorrow]=TxtLWSet.get()
                l1.itemconfig(it, fill=TxtRGB.get(), width=float(LW[colorrow])*1.5)
                updatecolor = True
            else:
                func.Missatge("Error","The width has to be a positive number.")
        else:
            func.Missatge("Error","The color code or the line width is not accepted.")

    def CloseAssignColor(self,tk2):
        global ChangeColorRunning
        ChangeColorRunning = False
        tk2.destroy()

############################################################################
###################Set Register Frequency ##################################
############################################################################
    def RegFreq(self,btnfreq):
        global ChangeFreqRunning
        if(ChangeFreqRunning):
            func.Missatge("Action not possible","Changing frequency action is already running.")
        else:
            ChangeFreqRunning = True
            self.FreqProc(btnfreq)

    def FreqProc(self,btnfreq):
        tkFreq = tk.Toplevel(self)
        tkFreq.wm_title("Change register frequency")
        tkFreq.geometry('200x130')
        self.LTit=Label(tkFreq,text="Introduce the register frequency to set (s):", wraplength = 150)
        self.LTit.place(x=25,y=10)
        self.TxtRF=Entry(tkFreq, width=4, justify=RIGHT)
        self.TxtRF.place(x=80,y=50)
        self.TxtRF.insert(0,self.FreqValue)
        self.BLoad=Button(tkFreq,bg='#DDDDDD', command=lambda a1=self.TxtRF, a2=btnfreq: self.AssignFreq(a1,a2), text="LOAD", width=6, height=1)
        self.BLoad.place(x=15,y=90)
        self.BClose=Button(tkFreq,bg='#DDDDDD', command=lambda a1=tkFreq: self.CloseAssignFreq(a1), text="Close", width=6, height=1)
        self.BClose.place(x=105,y=90)

    def AssignFreq(self,TxtRF,btnfreq):
        if(func.isfloat(TxtRF.get())):
            if(float(TxtRF.get())>=0.5):
                self.FreqValue = TxtRF.get()
                self.BtnFreq.config(text="Set register frequency Current: %s s"%str(self.FreqValue))
            else:
                func.Missatge("Error","The register frequency has to be a positive number greater or equal to 0.5s.")
        else:
            func.Missatge("Error","The register frequency has to be a positive number greater or equal to 0.5s.")

    def CloseAssignFreq(self,tkFreq):
        global ChangeFreqRunning
        ChangeFreqRunning = False
        tkFreq.destroy()

############################################################################
#         Additional Helper Functions
############################################################################

def GetEnergy():
    global EnergySet#keV
    return("%.0f"%float(EnergySet))

def GetAngle():
    global Angle,EnergySet#keV
    #Specifications
    D=53#mm
    L=1.5#mm
    g=2#mm
    s=0.07#mm
    V=GetADC1()#ADC1 is Volts Set not readback in this case should be ADC2
    if(float(EnergySet)==0):
        Angle = "-nan"
    else:
        Angle=float((float(V)/(float(EnergySet)*1000))*((float(D)-(2*float(L)))/(4*float(g))))*1000#mrad
    return("%.3f"%float(Angle))

#Setting voltage across plates
def SetVolts(valor,SetVAllowed):#AD5691RBRMZ ADDR 4C
    global stopm
    maxvolt = 1000
    if(SetVAllowed):
        #print("Volts to set: " + str(valor))
        if(not func.isfloat(valor) or float(valor)<0):
            func.Missatge("Wrong input","The set voltage must be a positive number between 0 and %d. Now is set at 0V, and the measurement is stopped." %maxvolt)
            stopm = True
            return(SetVolts(0,True))
        elif(float(valor)>maxvolt):
            func.Missatge("Wrong input","Voltage requested is above the limit of %dV. Now is set at 0V, and any measurement is stopped." %maxvolt)
            stopm = True
            return(SetVolts(0,True))
        else:
            voltdig = int(4096*float(valor)/maxvolt)#direct bit format
            channel = 1
            addr = 0x4c #shifted left from 0x98
            bus = smbus.SMBus(channel)
            voltage = voltdig & 0xfff
            HB = (voltage & 0xff0) >> 4 #Bit And with 4080, Shift Right by 4
            LB = (voltage & 0xf) << 4 #Bit And with 15, shift Left by 4
            val = [HB, LB]
            GPIO.setup(27,GPIO.OUT)
            GPIO.output(27, GPIO.HIGH)
            bus.write_i2c_block_data(addr,0x1d,val) # 76,29,
            sleep(0.001)
            #print("Voltages: Set, RDBK, QSX: ", GetADC1(), GetADC2(), GetADC3())
            #voltDAC = (voltdig/4095)* 3.3 #4096=2^12 If Limit were 3.3V directly from RPi
            voltDAC = (voltdig/4096)* 2.5 #4096=2^12 Limit DAC 2.5V
            return(voltDAC)
    else:#SetVAllowed = False
        func.Missatge("Not Allowed","A measurement or movement is ongoing, this action is not allowed.")

#Checking if Motor is Moving
#looking to see if subprocesses are active, blocks GUI actions except ESTOP
def isMoving():
    global p1, p2
    if 'p1' in globals():
        poll1 = p1.poll()
    else:
        poll1 = 0
    if 'p2' in globals():
        poll2 = p2.poll()
    else:
        poll2 = 0
    if poll2 is None or poll1 is None:
        return True
    else:
        return False

#Getting current position 
def GetPos(warnmsg):#ADC0
    warn = bool(warnmsg)
    global PosADCMax,PosADCMin,PosMax,PosMaxSet,PosMinSet,PosMin
    ads = ADS.ADS1115(busio.I2C(board.SCL,board.SDA))
    pos = AnalogIn(ads,ADS.P0)
    func.configpi()
    if(GPIO.input(17)==GPIO.LOW):#Top apretat
        PosADCMax = pos.value
    elif(GPIO.input(4)==GPIO.LOW):#Bottom apretat
        PosADCMin = pos.value
    if(not (bool(PosMaxSet) and bool(PosMinSet))):
        if(warnmsg):
            func.Missatge("Warning","The position reference has not been completely set. The given position is based on previous default references.")
    gotpos = (int(pos.value)-int(PosADCMin)) * float(PosMax)/(int(PosADCMax)-int(PosADCMin))
    return("%0.2f"%gotpos)

#Set voltage sent to power supply
def GetADC1():#AIN1 - Volts set, Desired voltage
    ads = ADS.ADS1115(busio.I2C(board.SCL,board.SDA))
    adc1 = AnalogIn(ads,ADS.P1)
    return("%0.1f"%float(float(adc1.voltage)*400))#4 is the multipying factor from DAC to PS 0-10V signal W/B cables. Check drawings if need of change.

#Readback voltage from power supply
def GetADC2():#AIN2 - Vols Readback, Actual voltage
    ads = ADS.ADS1115(busio.I2C(board.SCL,board.SDA))
    adc2 = AnalogIn(ads,ADS.P2)
    return("%0.5f"%adc2.voltage)

#Signal voltage
def GetADC3():#AIN2 - QSX
    ads = ADS.ADS1115(busio.I2C(board.SCL,board.SDA))
    adc3 = AnalogIn(ads,ADS.P3)
    return("%0.5f"%adc3.voltage)# current

#initallize file
def StartNewFile():
    global f1
    if(not path.exists("data")):
        os.mkdir("data")
    if(f1 is not None):
        f1.close()

    if float(TxtM[2].get()) != 0:
        posBins = round((float(TxtM[1].get())-float(TxtM[0].get()))/(MinStep*float(TxtM[2].get())))  
    else:
        posBins = 0  

    if float(TxtV[2].get()) != 0:
        angBins = round((float(TxtV[1].get())-float(TxtV[0].get()))/float(TxtV[2].get()))
    else:
        angBins = 0

    datavui = datetime.now().strftime("%Y%m%d-%H%M%S")
    NameFile = "./data/%s_EmittanceData.csv"%(datavui)
    f1 = open(NameFile,"a")
    if os.stat(NameFile).st_size == 0:
        f1.write("Comment: " + comment.get() + "\n")
        f1.write("Start time: " + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "\nBeam energy [keV]: " + str(GetEnergy()) + "\n")
        f1.write("Position range [mm]: " + TxtM[0].get() + " - " + TxtM[1].get() + " Steps: " + TxtM[2].get() + "\n")
        f1.write("Voltage range [V]: " + TxtV[0].get() + " - " + TxtV[1].get() + " Steps[V]: " + TxtV[2].get() + "\n")
        f1.write("Integration time: " + TxtT[0].get() + "\n")
        f1.write("Position Bins: "+ str(abs(posBins))+"\n")
        f1.write("Angle Bins: "+ str(abs(angBins)) + "\n")
        f1.write("Date,Time,Position[mm],Voltage Set[V],Volts Readback[V],Initial angle [mrad], Signal counts\n")#Voltages info need to be updated when testind
    f1.flush()

#Save measurement Data, Position and Voltage
def SaveLine(counts):
    global f1,stopm
    if (stopm):
        if (f1 is not None):
            f1.close()
    else:
        if (f1 is None or (not path.exists(f1.name))):#Check File Exists if doesn't create another one with the header.
            StartNewFile()
        if(f1 is not None):
            f1.write(str(datetime.now().strftime("%Y/%m/%d,%H:%M:%S.%f")[:-5]) + "," + str(GetPos(False)) + "," + str(GetADC1()) + "," + str(GetADC2()) + "," + str(GetAngle()) + "," + str(counts) + "\n")#Voltages need to be updated when testing
            f1.flush()

#initating GUI elements 
finestra = tk.Tk()
my_gui = TFL(finestra)
my_gui.UpdatePosLabel()
finestra.update_idletasks()
finestra.attributes('-topmost', True)
finestra.focus_force()
finestra.mainloop()
