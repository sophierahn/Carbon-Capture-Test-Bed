#!/usr/bin/python3

from cgi import test
from distutils.log import error
from re import I
import sys
import time
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import Canvas
from PIL import ImageTk, Image, ImageFile
from random import randint
from numpy import False_
import os
import glob
import csv
from datetime import datetime
from datetime import timedelta
from multiprocessing import Process, Pipe, Queue
from subprocess import Popen
import func
#Using *** to indicate Changes should be made in future

#set true to view UI not on RPI
mac = True
if not mac:
    from pressure_sensor import start_psensor
    from detect_bright_spots import start_imageCapture
    from mulitplexer import muliplexer
    from power_sensor import power_log
    import RPi.GPIO as GPIO
    func.setZero()


   
# USB is automatically mounted as media/pi/Lexar no matter what plug is used
# A folder named C02_Sensor_Data has been made *** switch data to save there


ImageFile.LOAD_TRUNCATED_IMAGES = True

EntFlow = [None]*1
EntPower = [None]*1
EntTime = [None]*1
EntFlowLim = [None]*1
EntCurrentLim = [None]*1
EntVoltLim = [None]*1
EntPressureLim = [None]*1
EntImageRate = [None]*1

estop = False
graph = False
countdown = None
debug = False
testRunning = False
testDefault = []

#User Editable Settings
preTestWait = 5
preTestDelay = 120

class controls:
    global radioVar, estop, countdown, testDefault, graph, testRunning
    testDefault = func.loadTestPresets()
    def __init__(self, master):
        self.master = master
        global testDefault
        #Define Window
        master.title("Carbon Capture Control")
        master.geometry('1100x700') #Set Size of GUI window (WxH)
        master.lift()

        #RPI settings
        text = 6
        setX = 30
        setY = 130
        entX = 155

        #### Data variables ####
        self.pressure = float(0)
        self.saltArea = float(0)
        self.errorTuple = (False,0)
        
        # self.canvas.create_line(1,1,1,255, width = 3, fill="#666666")

        #Master Title
        self.lblTitle = Label(master, text="MEA Cell Controls", font=("Calibri",text+14))
        self.lblTitle.place(x=400,y=10)

    #### Settings Titles ####
        self.TitlFlow = Label(master, text="Flow Controller", font=("Calibri",text+8))
        self.TitlFlow.place(x=setX,y=setY)
        self.TitlPower = Label(master, text="Power Supply", font=("Calibri",text+8))
        self.TitlPower.place(x=setX,y=setY+70)
        
        #Countdown Timer
        self.LblTimer = Label(master, text="Remaining Time: ", font=("Calibri",text+8))
        self.LblTimer.place(x=425,y=50)
        self.LblCountdown = Label(master, text="", font=("Calibri",text+6))
        self.LblCountdown.place(x=590,y=53)

    #### Settings Controls ####
        def only_numbers(char):
            if char.isnumeric() or char == ".":
                return True
            else:
                return True
        validation = root.register(only_numbers)

        #Flow Controller controls
        self.LblFlow = Label(master, text="Flow Rate (SCCM):", font=("Calibri",text+4))
        self.LblFlow.place(x=setX,y=setY+30)
        EntFlow[0] = Entry(master, width=5, justify=RIGHT)
        EntFlow[0].place(x=entX,y=setY+30)
        EntFlow[0].insert(tk.INSERT,testDefault[0])
        EntFlow[0].config(validate="key", validatecommand=(validation, '%S'))    
        
        #Power supply controls
        self.LblPower = Label(master, text="Set Voltage (V):    ", font=("Calibri",text+4))
        self.LblPower.place(x=setX,y=setY+150)#Power Entry Lable
        EntPower[0] = Entry(master, width=5, justify=RIGHT)
        EntPower[0].place(x=entX,y=setY+150)#Power Entry Box
        EntPower[0].insert(tk.INSERT,testDefault[2])#Set Default
        EntPower[0].config(validate="key", validatecommand=(validation, '%S'))
        
        global var1, var2, logScale #global UI varibles
        var1 = IntVar()
        var2 = IntVar()
        self.radPowerV = Radiobutton(master, text="Voltage Control", variable=var1, value=1, command=lambda: self.lblChange())
        self.radPowerC = Radiobutton(master, text="Current Control", variable=var1, value=2, command=lambda: self.lblChange())
        self.radPowerV.place(x=setX,y=setY+100)#Voltage select 
        self.radPowerC.place(x=setX,y=setY+120)#Current Select
        var1.set(int(testDefault[1]))
        self.lblChange()

        #Test Duration
        EntTime[0] = Entry(master, width=5, justify=RIGHT)
        EntTime[0].place(x=entX,y=setY+190)
        EntTime[0].insert(0,testDefault[3])#Set Default
        EntTime[0].config(validate="key", validatecommand=(validation, '%S'))
        self.LblTime = Label(master, text="Test Duration (min):", font=("Calibri",text+4))
        self.LblTime.place(x=setX-25,y=setY+190)

    ### Shutoff Limits ###
        limX = setX+200
        limY = setY-30
        self.TitlLimits = Label(master, text="Shutoff Limits", font=("Calibri",text+8))
        self.TitlLimits.place(x=limX,y=limY)

        self.lblFlowLim = Label(master, text="Flow Rate Cut Off (SCCM):", font=("Calibri",text+4))
        self.lblFlowLim.place(x=limX,y=limY+30)
        EntFlowLim[0] = Entry(master, width=7, justify=RIGHT)
        EntFlowLim[0].place(x=limX+200,y=limY+30)
        EntFlowLim[0].insert(tk.INSERT,testDefault[6])
        EntFlowLim[0].config(validate="key", validatecommand=(validation, '%S')) 

        self.lblCurrentLim = Label(master, text="Current Cut Off (A):", font=("Calibri",text+4))
        self.lblCurrentLim.place(x=limX,y=limY+60)
        EntCurrentLim[0] = Entry(master, width=7, justify=RIGHT)
        EntCurrentLim[0].place(x=limX+200,y=limY+60)
        EntCurrentLim[0].insert(tk.INSERT,testDefault[7])
        EntCurrentLim[0].config(validate="key", validatecommand=(validation, '%S')) 

        self.lblVoltLim = Label(master, text="Voltage Cut Off (V):", font=("Calibri",text+4))
        self.lblVoltLim.place(x=limX,y=limY+90)
        EntVoltLim[0] = Entry(master, width=7, justify=RIGHT)
        EntVoltLim[0].place(x=limX+200,y=limY+90)
        EntVoltLim[0].insert(tk.INSERT,testDefault[8])
        EntVoltLim[0].config(validate="key", validatecommand=(validation, '%S')) 
         
        self.lblPressureLim = Label(master, text="Pressure Flux Limit (kpa):", font=("Calibri",text+4))
        self.lblPressureLim.place(x=limX,y=limY+120)
        EntPressureLim[0] = Entry(master, width=7, justify=RIGHT)
        EntPressureLim[0].place(x=limX+200,y=limY+120)
        EntPressureLim[0].insert(tk.INSERT,testDefault[9])
        EntPressureLim[0].config(validate="key", validatecommand=(validation, '%S')) 

    ### Data Settings ###
        dataX = limX+30
        dataY = limY+170
        self.TitlData = Label(master, text="Logging Settings", font=("Calibri",text+8))
        self.TitlData.place(x=dataX,y=dataY)
        #Image Frequancy 
        self.lblImage = Label(master, text="Image Capture Rate (s):", font=("Calibri",text+4))
        self.lblImage.place(x=dataX,y=dataY+30)
        EntImageRate[0] = Entry(master, width=7, justify=RIGHT)
        EntImageRate[0].place(x=limX+200,y=dataY+30)
        EntImageRate[0].insert(tk.INSERT,testDefault[10])
        #Data Frequancy
        self.LblLog = Label(master, text="Data Log Rate (s)", font=("Calibri",text+4))
        self.LblLog.place(x=dataX,y=dataY+60)
        logScale = Scale(master, from_=0, to=20, label = "Set to 0 for <1s Logging", font=("Calibri",text+2), length=150, tickinterval=5, orient=HORIZONTAL,)
        logScale.place(x=dataX,y=dataY+80)
        logScale.set(testDefault[4])
        #Calibration Checkbox
        checkPressure = tk.Checkbutton(master, text='Gauge Pressure',variable=var2, onvalue=1, offvalue=0)
        checkPressure.place(x=dataX,y=dataY+150)
        var2.set(int(testDefault[5]))
        
    #### Live Data ####
        datax = 550
        datay = 80
        #pressure
        self.dataHeading = Label(master, text="Live Data", font=("Calibri",text+10))
        self.dataHeading.place(x=datax+120,y=datay)
        self.psen0 = Label(master, text="KHCO3 Inlet: 0kPa", font=("Calibri",text+6))
        self.psen0.place(x=datax,y=datay+35)
        self.psen1 = Label(master, text="KHCO3 Outlet: 0kPa", font=("Calibri",text+6))
        self.psen1.place(x=datax,y=datay+70)
        self.psen2 = Label(master, text="CO2 Inlet: 0kPa", font=("Calibri",text+6))
        self.psen2.place(x=datax,y=datay+105)
        self.psen3 = Label(master, text="CO2 Outlet: 0kPa", font=("Calibri",text+6))
        self.psen3.place(x=datax,y=datay+140)
        #CO2 Flow
        self.flowRB = Label(master, text="CO2 Flow Rate: 0 SCCM", font=("Calibri",text+6))
        self.flowRB.place(x=datax+240,y=datay+35)
        #power
        self.power0 = Label(master, text="Current: 0 mA", font=("Calibri",text+6))
        self.power0.place(x=datax+240,y=datay+70)
        self.power1 = Label(master, text="Voltage: 0 V", font=("Calibri",text+6))
        self.power1.place(x=datax+240,y=datay+105)
        self.power2 = Label(master, text="Power: 0 mW", font=("Calibri",text+6))
        self.power2.place(x=datax+240,y=datay+140)
        
        salty = datay + 240
        self.imageHeading = Label(master, text="Salt Idenification", font=("Calibri",text+8))
        self.imageHeading.place(x=datax,y=salty)
        self.saltData = Label(master, text="Total Salt Area: 0 mm2", font=("Calibri",text+6))
        self.saltData.place(x=datax,y=salty+35)
        if not mac:
            self.img = Image.open(func.latestFile())
        self.img = Image.open("/home/pi/Carbon-Capture-Test-Bed/Images_Edited/20220329-141506_identified.jpg")
        self.imgW, self.imgH = self.img.size
        self.imgW = round(int(self.imgW)/2)
        self.imgH = round(int(self.imgH)/2)
        self.imgSmall = self.img.resize((self.imgW,self.imgH))
        self.imgSmall = ImageTk.PhotoImage(self.imgSmall)
        self.saltImage = Label(master,image=self.imgSmall)
        self.saltImage.place(x=datax,y=salty+70)

    #### Buttons ####
        btnX = setX+50
        btnY = setY+390
        self.BtnPreStart = Button(master, text="Start PreTest", command=lambda: self.preTest(), width=10, height=2, bg='#f7d240', activebackground='#f7a840', wraplength=100)
        self.BtnPreStart.place(x=btnX-55,y=btnY)
        self.BtnStart = Button(master, text="Start Test", command=lambda: self.validateTest(), width=10, height=2, bg='#DDDDDD', activebackground='#a6e89e', wraplength=100, state= DISABLED)
        self.BtnStart.place(x=btnX+55,y=btnY)
        self.BtnCancel = Button(master, text="Cancel Test", command=lambda: self.stopTest(), width=10, height=2, bg='#DDDDDD', activebackground='#ff5959', wraplength=100)
        self.BtnCancel.place(x=btnX,y=btnY+50)
        
        self.BtnDefault = Button(master, text="Save Test Default", command=lambda: self.saveTest())
        self.BtnDefault.place(x=20,y=20)

        self.BtnClose = Button(master, text="Close", command=lambda: self.close())
        self.BtnClose.place(x=10,y=580)

        self.BtnCalibrate = Button(master, text="Calibrate System", command=lambda: self.calibrate())
        self.BtnCalibrate.place(x=22,y=60)
        
        

################################## Main Program ###############################################################
    #Change Powersupply Label
    def lblChange(self):
        global radioVar
        radioVar = var1.get()
        if radioVar == 1:
            if debug:
                print("changing voltage")
            self.LblPower.config(text = "Set Voltage (V):")
        else:
            if debug:
                print("changing current")
            self.LblPower.config(text = "Set Current (A):")

    def calibrate(self):
        p1 = Popen(['python3','CalibrationUI.py'])
        p1.wait()
        
    #Save Test Default Values
    def saveTest(self):
        global testDefault, radioVar, logScale, var2
        testDefault = [0]*13
        try:
            testDefault[0] = float(EntFlow[0].get())
            testDefault[1] = float(radioVar)
            testDefault[2] = float(EntPower[0].get())
            testDefault[3] = float(EntTime[0].get())
            testDefault[4] = float(logScale.get()) #Logging Value
            testDefault[5] = float(var2.get()) #Calibration Setting
            testDefault[6] = float(EntFlowLim[0].get())
            testDefault[7] = float(EntCurrentLim[0].get())
            testDefault[8] = float(EntVoltLim[0].get())
            testDefault[9] = float(EntPressureLim[0].get())
            testDefault[10] = float(EntImageRate[0].get())
            testDefault[11] = testDefault[11]
            testDefault[12] = testDefault[12]
            print(testDefault)
            func.saveTestPreset(testDefault,False)
        except Exception as e:
            print(e)
            func.message("Warning","Save Test Settings Failed")

    #Kill Processes
    def killProcesses(self):
        global psen_script, image_script, multi, power_script, q, maini_pipe
        if debug:
            print("Killing")
        if 'psen_script' in globals():
            q.put_nowait((0,True)) #Send Shutdown Signal
            time.sleep(0.05)
            psen_script.terminate()
        if 'image_script' in globals():
            maini_pipe.send("stop")
            time.sleep(0.05)
            image_script.terminate()
            del image_script
        if 'power_script' in globals():
            power_script.terminate()
        if 'multi' in globals():
            q.put_nowait((0,True)) #Send Shutdown Signal
            time.sleep(0.5)
            multi.terminate() #Closes the Queue
        if not mac:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(17,GPIO.OUT)
            GPIO.setup(22,GPIO.OUT)
            GPIO.output(17, GPIO.LOW)
            GPIO.output(22, GPIO.LOW)
            func.setZero() #Uses tca outside mulitplexer to set DACs to zero (power and CO2)
        
    #closes window
    def close(self):
        if debug:
            print("closing")
        try:
            self.killProcesses()
            list_of_files = glob.glob('/home/pi/Carbon-Capture-Test-Bed/Images_Raw/*.jpg')
            list_of_files.sort(key=os.path.getctime)
            for file in list_of_files[:-1]:
                os.remove(file)
        except Exception as e:
            func.errorLog(e, "Close")
        finally:
            sys.exit(0)

    ### Estop Function ###
    def stopTest(self):
        global estop, testRunning, testDefault
        if not estop:
            estop = True
            self.killProcesses()
            testRunning = False
            self.BtnCancel.config(text="Reset Test", bg='#ff5959', activebackground='#FF0000')
            self.BtnPreStart.config(state= DISABLED, bg='#DDDDDD')
            self.BtnStart.config(text="Start Test",state= DISABLED, bg='#DDDDDD')
            EntFlow[0].delete(0,'end')
            EntPower[0].delete(0,'end')
            EntTime[0].delete(0,'end')
            EntFlow[0].insert(0,str(testDefault[0]))
            EntPower[0].insert(0,str(testDefault[2]))
            EntTime[0].insert(0,str(testDefault[3]))
        else:
            estop = False
            self.BtnCancel.config(text="Cancel Test", bg='#DDDDDD', activebackground='#ff5959')
            self.LblCountdown.config(text = "")
            self.BtnPreStart.config(text="Start PreTest", bg='#f7d240', state = NORMAL)
            self.BtnCalibrate.config(state=NORMAL)
            

### Start Pre Test procedure ###  #calibrate pressure sensors, start pump and gas flowing in cell, call 30 sec wait function
    def preTest(self):
        global multi, q
        limitList = [0]*4
        try:
            gasFlow = float(EntFlow[0].get()) #add similiar proportional control calcuations to powerValue
            if gasFlow > 131 or gasFlow < 0:
                func.message("Warning","Gas Flow Rate must not exceed 131 SCCM and must be a postive value")
                raise Exception("Gas Flow rate over 131")
            logRate = float(logScale.get()) #Logging Value
            calibrating = bool(var2.get()) #Calibration Setting
            limitList[0] = float(EntFlowLim[0].get())
            limitList[1] = float(EntCurrentLim[0].get())
            limitList[2] = float(EntVoltLim[0].get())
            limitList[3] = float(EntPressureLim[0].get())
            for i in limitList:
                if i < 0:
                    func.message("Error","Limit Values must be Postive")
                    raise Exception("Negative Values")
        except ValueError:
            func.message("Error","Please Enter Numbers Only")
        except Exception as e:
           print("Error in Numerical Entry: ", e)
           func.errorLog(e, "preTest")
        
        else: #only proceeds if test values pass muster
            if calibrating:
                #calibrationValue = 0
                calibrationValue = func.calibration()
            else:
                calibrationValue = 0

            self.BtnCalibrate.config(state=DISABLED)
            #Initialization of Multiplexer Process
            print("about to start Multi")
            q = Queue()
            multi_pipe, mainMulti_pipe = Pipe()
            multi = Process(target= muliplexer, args= (calibrationValue,logRate,limitList,q,multi_pipe,))
            multi.start()
            
            #Setting up GPIO Pins for Relays
            #Start Gas Flow and Pump once calibration is complete
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(22,GPIO.OUT)
            GPIO.output(22, GPIO.HIGH) #turning on Pump

            gasFlowNorm = gasFlow*5/200/3.28 #convert to percent fraction
            q.put_nowait((4,gasFlowNorm)) #send inital gas flow values
            #print("Sending Gas Flow", gasFlow)
            
            start = time.time()
            self.preTestCountDown(preTestWait) #Start 30sec preTest loop *** make gobal value, not hardcoded
            self.preTestCheck(start) #Start checking loop, will shutdown system if test start delay is too long
            self.errorChecking(mainMulti_pipe) 
            # *** unnecessary if Auto Test start is okay, this version requires user input  

    def preTestCountDown(self, i):
        global estop
        if i > 0 and estop == False: #Countdown Started
            self.BtnPreStart.config(text = str(i))
            i -= 1
            self.testWait = root.after(1000, lambda: self.preTestCountDown(i))
        elif estop: #Cancled by Estop
            root.after_cancel(self.testWait)
            self.BtnPreStart.config(text = "PreTest Cancelled")
        else: #Completed Successfully
            root.after_cancel(self.testWait)
            self.BtnPreStart.config(text = "PreTest Complete", bg='#DDDDDD', state= DISABLED)
            self.BtnStart.config(state= NORMAL, bg = '#72d466')

    def preTestCheck(self, startTime):
        global estop, testRunning
        testCancelled = False
        if not testRunning and not estop and not testCancelled: 
            elaspedTime = time.time()-startTime
            if elaspedTime > preTestDelay: ## *** Change Time and message based on Joel Feedback
                self.stopTest()
                func.message("Error","Test not initated after %f s of PreTest. Test cancelled" %(preTestDelay))
                testCancelled = True
                func.errorLog("Test not started after PreTest (%0.1f s)" %(preTestDelay), "PreTest Check")
            self.testCheck = root.after(1000, lambda: self.preTestCheck(startTime))
        else:
            root.after_cancel(self.testCheck)
            

### Start Test ###      Starting actual program, initiating buffers, starting power delivery to Cell
    def validateTest(self):
        global psen_script, image_script, power_script, q, radioVar, testRunning, maini_pipe
        testRunning = True
        if debug:
            print("validating")
        try:
            testMin = float(EntTime[0].get())
            if testMin < 0:
                func.message("Warning","Test Duration must be Positive")
                raise Exception("Voltage above Max 24v")
            powerValue = float(EntPower[0].get())
            if powerValue > 24 or powerValue < 0:
                func.message("Warning","Voltage cannot not exceed 24V and must be a Postive Value")
                raise Exception("Voltage above Max 24v")
            if radioVar == 2:
                func.message("Warning","Current Control not Currently Enabled")
                raise Exception("Current Selected")
            repeatRate = round(float(EntImageRate[0].get()))*1000
            if repeatRate < 1000:
                func.message("Warning","Image Capture rate must be greater than 1 second and an interger value")
                raise Exception("Value must be greater than 1")
        except ValueError:
            func.message("Error","Please Enter Numbers Only")
        except Exception as e:
            print("Numerical Entry Error:", e)
            func.errorLog(e, 'ValidateTest')
        else:
            self.BtnStart.config(text="Test Running", state=DISABLED)
            #1 means voltage
            if radioVar == 1: ### *** Remove hardcoded numbers, add calibration function
                powerNormValue = ((powerValue)*0.0383) + 0.0825 #*** use calibration fucntion Calculated Calibration Curve (y=0.0386x + 0.0797)
            #2 means current
            if radioVar == 2:
                powerNormValue = powerValue*5/20/3.28  #Current 0-20A Proportial 5v, percentage value for DAC 0-3.28v
            powerTuple = (radioVar,powerNormValue) #combining volt or current selection and Desired Value

            #Turn on Power Supply
            q.put_nowait((2,powerTuple))

            #Turn on LEDs
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(17,GPIO.OUT)
            GPIO.output(17, GPIO.HIGH) 

            #Initiallize pressure sensor process
            psen_pipe, mainp_pipe = Pipe()
            psen_script = Process(target= start_psensor, args= (psen_pipe,q,))
            psen_script.start()

            #Initiallize power sensor process
            power_pipe, mainpower_pipe = Pipe()
            power_script = Process(target= power_log, args= (power_pipe,q,))
            power_script.start()

            #Initiallize Image Capture Process
            image_pipe, maini_pipe = Pipe()
            image_script = Process(target= start_imageCapture, args= (image_pipe,testDefault[11]))
            image_script.start()

            #Call repeating functions
            self.button_countdown(int(testMin*60))
            self.pressure_sensor(psen_pipe, mainp_pipe,int(testMin*60))
            self.power_sensor(power_pipe,mainpower_pipe)
            self.image_capture(image_pipe, maini_pipe, repeatRate)

### Repeating Functions ###
    def button_countdown(self,i):
        global estop, countdown
        if debug:
            print("countdown")
        
        if i > 0 and estop == False:
            self.LblCountdown.config(text = str(i))
            i -= 1
            countdown = root.after(1000, lambda: self.button_countdown(i))
        elif estop:
            self.LblCountdown.config(text = "Test Cancelled")
            root.after_cancel(countdown)
        else:
            self.LblCountdown.config(text = "Test Ended")
            self.stopTest()
            root.after_cancel(countdown)

    def pressure_sensor(self, psen_pipe, mainp_pipe, testSec):
        global estop
        if debug:
            print("Pressure Sensor")

        if not estop:
            pressureList = [0]*4
            while mainp_pipe.poll(): #empty Pressure Sensor Pipe
                pressureList= mainp_pipe.recv()
            self.pressure_0 = round(pressureList[0],3) #round all pressure values to 3 Decimals
            self.pressure_1 = round(pressureList[1],3)
            self.pressure_2 = round(pressureList[2],3)
            self.pressure_3 = round(pressureList[3],3)
            #self.graphing(self.pressure_0,self.pressure_1,self.pressure_2,self.pressure_3, testSec)

            self.psen0.config(text = "KHCO3 Inlet: "+str(self.pressure_0)+"kPa") #Update the pressure sensor labels on UI
            self.psen1.config(text = "KHCO3 Outlet: "+str(self.pressure_1)+"kPa")
            self.psen2.config(text = "CO2 Inlet: "+str(self.pressure_2)+"kPa")
            self.psen3.config(text = "CO2 Outlet: "+str(self.pressure_3)+"kPa")
            pressure_sensor = root.after(1000, lambda: self.pressure_sensor(psen_pipe, mainp_pipe,testSec))
        else:
            root.after_cancel(self.pressure_sensor)

    def power_sensor(self, power_pipe, mainpower_pipe):
        global estop
        if debug:
            print("Power Sensor")
        if not estop:
            powerList = [0]*4
            while mainpower_pipe.poll(): #Empty power pipe
                powerList= mainpower_pipe.recv()
            self.power_0 = round(powerList[0],3)
            self.power_1 = round(powerList[1],3)
            self.power_2 = round(powerList[2],3)
            self.flow_RB = round(powerList[3],3)

            self.power0.config(text = "Current: "+str(self.power_0)+" mA") #Update Lables
            self.power1.config(text = "Voltage: "+str(self.power_1)+" V")
            self.power2.config(text = "Power: "+str(self.power_2)+" mW")
            self.flowRB.config(text = "CO2 Flow Rate: "+str(self.power_2)+" SCCM")
            power_sensor = root.after(1000, lambda: self.power_sensor(power_pipe, mainpower_pipe))
        else:
            root.after_cancel(self.pressure_sensor)

    def image_capture(self, image_pipe, maini_pipe, repeatRate):
        global estop
        if debug:
            print("Image Capture Starting")

        pipeContents = []
        if not estop:
            while maini_pipe.poll():    #Empty pipe 
                pipeContents.append(maini_pipe.recv())
            for i in pipeContents:      # Check pipe contents for salt area from background process
                if type(i) == float:
                    self.saltArea = round(i,3)
                    
            maini_pipe.send("run") #Send Run signal to image capture processes 
            self.saltData.config(text = "Total Salt Area: %.3fmm2"%self.saltArea)
            try:
                self.img = Image.open(func.latestFile())
                self.imgW, self.imgH = self.img.size
                self.imgW = round(int(self.imgW)/2)
                self.imgH = round(int(self.imgH)/2)
                self.imgSmall = self.img.resize((self.imgW,self.imgH))
                self.imgSmall = ImageTk.PhotoImage(self.imgSmall)
                self.saltImage.config(image=self.imgSmall)
            except Exception as e:
                func.errorLog(e, "Image Capture")
            image_capture = root.after(repeatRate, lambda: self.image_capture(image_pipe, maini_pipe, repeatRate))
        else:
            maini_pipe.send("stop")
            time.sleep(0.5)
            root.after_cancel(self.image_capture)

    def errorChecking(self, mainMulti_pipe):
        if not estop:
            while mainMulti_pipe.poll():
                self.errorTuple = mainMulti_pipe.recv()
            if self.errorTuple[0]:
                self.stopTest()
                if self.errorTuple[1] == 1:
                    func.message("Error","Test was Ended Due to CO2 Flow Rate measured over Limit")
                    func.errorLog("Test was Ended Due to CO2 Flow Rate measured over Limit", "Error Checking")
                if self.errorTuple[1] == 2:
                    func.message("Error","Test was Ended Due to Current measured over Limit")
                    func.errorLog("Test was Ended Due to Current measured over Limit", "Error Checking")
                if self.errorTuple[1] == 3:
                    func.message("Error","Test was Ended Due to Voltage measured over Limit")
                    func.errorLog("Test was Ended Due to Voltage measured over Limit", "Error Checking")
                if self.errorTuple[1] == 4:
                    func.message("Error","Test was Ended Due to Pressure Flux measured over Limit")
                    func.errorLog("Test was Ended Due to Pressure Flux measured over Limit", "Error Checking")    
            errorChecking = root.after(500, lambda: self.errorChecking(mainMulti_pipe))
        else:
            self.errorTuple=(False,0)
            root.after_cancel(self.errorChecking)    

root = Tk()
my_gui = controls(root)
root.mainloop()
