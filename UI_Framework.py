import sys
import time
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import Canvas
from PIL import ImageTk, Image, ImageFile
from random import randint
import matplotlib
from matplotlib import pylab
from numpy import False_
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from pylab import plot, show, figure, xlabel, ylabel, draw, pause, ion, close
import os
import glob
import csv
from datetime import datetime
from datetime import timedelta
from multiprocessing import Process, Pipe, Queue
import func
#import subprocess

#Using *** to indicate Changes should be made in future


#set true to view UI not on RPI
mac = False
if not mac:
    from pressure_sensor import start_psensor
    from detect_bright_spots import start_imageCapture
    from mulitplexer import muliplexer
    from power_sensor import power_log
    import RPi.GPIO as GPIO


    #If running on pi, this is to mount CSV flashdrive, giving us a folder to send data to
    #sdc1 is a potential flashdrive name, may not be true for the pi
    #Check and adjust using lsblk on the command line, it should be the same name every time
    #I'd love to make this more dynamic than a hardcoded file name but idk how to do that rn
    #The name of the device should be sdXY where X is any letter and Y any digit
    #This doesn't need to be done in a specific process bc it's interacting with the OS
    #subprocess.run(["udisksctl",  "mount",  "-b",  "/dev/sdc1"])


ImageFile.LOAD_TRUNCATED_IMAGES = True

EntFlow = [None]*1
EntPower = [None]*1
EntTime = [None]*1
EntPump = [None]*1

estop = False
graph = False
countdown = None
debug = False
testRunning = False

class controls:
    global radioVar, var, estop, countdown, testDefault, graph, testRunning
    testDefault = func.loadTestPresets()

    def __init__(self, master):
        self.master = master
        #Define Window
        master.title("Carbon Capture Control")
        master.geometry('1000x630') #Set Size of GUI window (WxH)
        master.lift()
        #self.canvas = Canvas(master, width=1000, height=630)
        #self.canvas.pack()
        #master.attributes('-topmost',True)
        #RPI settings
        text = 6
        setX = 90
        setY = 130
        entX = 190

        #Mac Settings
        #text = 10
        #setX = 70
        #setY = 100
        #entX = 160

        #### Data variables ####
        self.pressure = float(0)
        self.saltArea = float(0)
        # self.canvas.create_line(1,1,1,255, width = 3, fill="#666666")

        #Master Title
        self.lblTitle = Label(master, text="MEA Cell Controls", font=("Calibri",text+14))
        self.lblTitle.place(x=400,y=10)


    #### Settings Titles ####
        self.TitlFlow = Label(master, text="Flow Controller", font=("Calibri",text+8))
        self.TitlFlow.place(x=setX,y=setY+100)
        self.TitlPower = Label(master, text="Power Supply", font=("Calibri",text+8))
        self.TitlPower.place(x=setX,y=setY+200)
        #Countdown Timer
        self.LblTimer = Label(master, text="Remaining Time:", font=("Calibri",text+6))
        self.LblTimer.place(x=setX,y=setY-50)
        self.LblCountdown = Label(master, text="", font=("Calibri",text+6))
        self.LblCountdown.place(x=setX+140,y=setY-50)

    #### Settings Controls ####
        def only_numbers(char):
            if char.isdigit() or char == ".":
                return True
            else:
                return False
        validation = root.register(only_numbers)


        #Pump controls
        # EntPump[0] = Entry(master, width=5, justify=RIGHT, validate="key", validatecommand=(validation, '%S'))
        # self.LblPump = Label(master, text="Flow Rate:", font=("Calibri",text+4))
        # EntPump[0].place(x=entX,y=setY+30)
        # EntPump[0].insert(0,testDefault[0])#Set Default
        # self.LblPump.place(x=setX,y=setY+30)

        #Flow Controller controls
        EntFlow[0] = Entry(master, width=5, justify=RIGHT, validate="key", validatecommand=(validation, '%S'))
        self.LblFlow = Label(master, text="Flow Rate:", font=("Calibri",text+4))
        EntFlow[0].place(x=entX,y=setY+130)
        EntFlow[0].insert(0,testDefault[0])#Set Default
        self.LblFlow.place(x=setX,y=setY+130)

        #Power supply controls
        EntPower[0] = Entry(master, width=5, justify=RIGHT, validate="key", validatecommand=(validation, '%S'))
        self.LblPower = Label(master, text="Set Voltage:    ", font=("Calibri",text+4))
        EntPower[0].place(x=entX,y=setY+280)
        EntPower[0].insert(0,testDefault[2])#Set Default
        self.LblPower.place(x=setX,y=setY+280)
        global var #power supply Radio Buttons
        var = IntVar()
        self.radPowerV = Radiobutton(master, text="Voltage Control", variable=var, value=1, command=lambda: self.lblChange())
        self.radPowerC = Radiobutton(master, text="Current Control", variable=var, value=2, command=lambda: self.lblChange())
        self.radPowerV.place(x=setX,y=setY+230)
        self.radPowerC.place(x=setX,y=setY+250)
        var.set(testDefault[1])

        #Test Duration
        EntTime[0] = Entry(master, width=5, justify=RIGHT, validate="key", validatecommand=(validation, '%S'))
        self.LblTime = Label(master, text="Test Duration:", font=("Calibri",text+6))
        EntTime[0].place(x=entX,y=setY+340)
        EntTime[0].insert(0,testDefault[3])#Set Default
        self.LblTime.place(x=setX-20,y=setY+340)

        datax = 600
        datay = 80
    #### Data ####
        #pressure
        self.dataHeading = Label(master, text="Live Data", font=("Calibri",text+8))
        self.dataHeading.place(x=datax+100,y=datay)
        self.psen0 = Label(master, text="Inlet 1: 0kPa", font=("Calibri",text+6))
        self.psen0.place(x=datax,y=datay+35)
        self.psen1 = Label(master, text="Outlet 1: 0kPa", font=("Calibri",text+6))
        self.psen1.place(x=datax+170,y=datay+35)
        self.psen2 = Label(master, text="Inlet 2: 0kPa", font=("Calibri",text+6))
        self.psen2.place(x=datax,y=datay+70)
        self.psen3 = Label(master, text="Outlet 2: 0kPa", font=("Calibri",text+6))
        self.psen3.place(x=datax+170,y=datay+70)
        #power
        self.power0 = Label(master, text="Current: 0 mA", font=("Calibri",text+6))
        self.power0.place(x=datax-50,y=datay+105)
        self.power1 = Label(master, text="Voltage: 0 V", font=("Calibri",text+6))
        self.power1.place(x=datax+110,y=datay+105)
        self.power2 = Label(master, text="Power: 0 mW", font=("Calibri",text+6))
        self.power2.place(x=datax+250,y=datay+105)

        salty = datay + 160
        if not mac:
            self.imageHeading = Label(master, text="Salt Idenification", font=("Calibri",text+8))
            self.imageHeading.place(x=datax,y=salty)
            self.saltData = Label(master, text="Total Salt Area: 0 mm2", font=("Calibri",text+6))
            self.saltData.place(x=datax,y=salty+35)
            self.img = Image.open("/home/pi/Carbon-Capture-Test-Bed/test.jpg")
            self.imgW, self.imgH = self.img.size
            self.imgW = round(int(self.imgW)/10)
            self.imgH = round(int(self.imgH)/10)
            self.imgSmall = self.img.resize((self.imgW,self.imgH))
            self.imgSmall = ImageTk.PhotoImage(self.imgSmall)
            self.saltImage = Label(master,image=self.imgSmall)
            self.saltImage.place(x=datax,y=salty+70)

    #### Buttons ####
        btnX = setX+50
        btnY = setY+390
        print(btnY, setY)
        self.BtnPreStart = Button(master, text="Start PreTest", command=lambda: self.preTest(), width=10, height=2, bg='#DDDDDD', activebackground='#f7a840', wraplength=100)
        self.BtnPreStart.place(x=btnX-55,y=btnY)
        self.BtnStart = Button(master, text="Start Test", command=lambda: self.validateTest(), width=10, height=2, bg='#DDDDDD', activebackground='#72d466', wraplength=100, state= DISABLED)
        self.BtnStart.place(x=btnX+55,y=btnY)
        self.BtnCancel = Button(master, text="Cancel Test", command=lambda: self.stopTest(), width=10, height=2, bg='#DDDDDD', activebackground='#ff5959', wraplength=100)
        self.BtnCancel.place(x=btnX,y=btnY+50)
        # self.BtnPurge = Button(master, text="Purge Cell", command=lambda: self.validateTest(), width=10, height=2, bg='#DDDDDD', activebackground='#32CD32', wraplength=100)
        # self.BtnPurge.place(x=btnX+130,y=btnY+20)
        self.BtnDefault = Button(master, text="Save Test Default", command=lambda: self.saveTest())
        self.BtnDefault.place(x=20,y=20)

        self.BtnClose = Button(master, text="Close", command=lambda: self.close())
        self.BtnClose.place(x=10,y=580)


    #Change Powersupply Label
    def lblChange(self):
        global radioVar
        radioVar = var.get()
        if radioVar == 1:
            if debug:
                print("changing voltage")
            self.LblPower.config(text = "Set Voltage:")
        else:
            if debug:
                print("changing current")
            self.LblPower.config(text = "Set Current:")

    #Save Test Default Values
    def saveTest(self):
        global testDefault, radioVar
        try:
            testDefault[0] = float(EntFlow[0].get())
            testDefault[1] = float(radioVar)
            testDefault[2] = float(EntPower[0].get())
            testDefault[3] = float(EntTime[0].get())
            print(testDefault)
        except:
            func.message("Warning","Numerical Entry Invalid")

    #Kill Processes
    def killProcesses(self):
        global psen_script, image_script, multi, power_script, q
        if debug:
            print("Killing")
        if 'psen_script' in globals():
            q.put_nowait((3,True))
            time.sleep(0.05)
            psen_script.terminate()
        if 'image_script' in globals():
            image_script.terminate()
        if 'power_script' in globals():
            power_script.terminate()
        if 'multi' in globals():
            q.put_nowait((3,True))
            time.sleep(0.05)
            multi.terminate()
        if not mac:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(17,GPIO.OUT)
            GPIO.setup(21,GPIO.OUT)
            GPIO.output(17, GPIO.LOW)
            GPIO.output(21, GPIO.LOW)
        
    #closes window
    def close(self):
        if debug:
            print("closing")
        self.killProcesses()
        sys.exit(0)

    ##Estop Function //Need to add a reset fuctionality to change estop back to false so tests can be restarted
    def stopTest(self):
        global estop, testRunning, testDefault
        if not estop:
            self.killProcesses()
            estop = True
            testRunning = False
            self.BtnCancel.config(text="Reset Test", bg='#ff5959', activebackground='#FF0000')
            self.BtnPreStart.config(state= DISABLED)
            self.BtnStart.config(state= DISABLED)
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
            self.BtnPreStart.config(text="Start PreTest", state = NORMAL)

    #Start Pre Test procedure: start pump and gas flowing in cell, call 30 sec wait function
    def preTest(self):
        global multi, q
        try:
            testFreq = 1 #decimal of full speed *** need to make this user adjustable
            gasFlow = float(EntFlow[0].get()) #add similiar proportional control calcuations to powerValue
        except:
           func.message("Warning","Numerical Entry Invalid")
           testFreq = 1 #this one might be unneccessary, I'm not sure
        else:
            #### *** Make a button to let a user indicate this as true or false
            calibrating = False  
            #if calibrating:
                #calibrateStatus = 1
            #else:
                #calibrateStatus = 0
            
            
            #Initialization of Multiplexer Process
            q = Queue()
            multi = Process(target= muliplexer, args= (calibrating,testFreq,q,))
            multi.start()
            #Setting up GPIO Pins for Relays
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(17,GPIO.OUT)
        
            #keeps checking for end of calibration signal
            #while calibrateStatus = 1:
                ##Checking queue for calibration flag
                #while not q.empty():
                    #try:
                        #queueDump.append(q.get_nowait())
                    #except:
                        #pass
             
                ##Checking each tuple at a time from the queue
                #for i in queueDump:
                    #if i[0] == 0:
                        #q.put_nowait((0,i[1])) #pressure sensor data
                   # if i[0] == 1:
                    #    q.put_nowait((1,i[1])) #power sensor Data
                    #if i[0] == 2:
                    #    q.put_nowait((2,i[1])) #DAC instructions
                    #if i[0] == 3:
                    #    shutoff = i[1]  #shutoff command
                    #    q.put_nowait((3,shutoff))
                    #if i[0] == 4:
                    #    calibrateStatus = i[1]
                    #    #I don't think it needs to be put back, it's been recieved
            
            
            
            #Start Gas Flow and Pump once calibration is complete
            #q.put_nowait((3,gasFlow)) #send inital gas flow values
            GPIO.output(17, GPIO.HIGH) #turning on Pump
            
            start = time.time()
            self.preTestCountDown(10) #Start 30sec preTest loop *** make gobal value, not hardcoded
            self.preTestCheck(start) #Start checking loop, will shutdown system if test start delay is too long
            # *** unnecessary if Auto Test start is okay, this version requires user input

    def preTestCountDown(self, i):
        global estop
        if i > 0 and estop == False:
            self.BtnPreStart.config(text = str(i))
            i -= 1
            self.testWait = root.after(1000, lambda: self.preTestCountDown(i))
        elif estop: #cancled by Estop
            root.after_cancel(self.testWait)
            self.BtnPreStart.config(text = "PreTest Cancelled")
        else: #Completed Successfully
            root.after_cancel(self.testWait)
            self.BtnPreStart.config(text = "PreTest Complete", state= DISABLED)
            self.BtnStart.config(state= NORMAL)

    def preTestCheck(self, startTime):
        global estop, testRunning
        testCancelled = False
        if not testRunning and not estop and not testCancelled:
            elaspedTime = time.time()-startTime
            print(elaspedTime)
            if elaspedTime > 60:
                self.stopTest()
                func.message("Error","Test not initated after 2 min of PreTest. Test cancelled")
                testCancelled = True
            self.testCheck = root.after(1000, lambda: self.preTestCheck(startTime))
        else:
            root.after_cancel(self.testCheck)

    #Starting actual program, initiating buffers, starting power delivery to Cell
    def validateTest(self):
        global psen_script, image_script, power_script, q, radioVar, testRunning
        testRunning = True
        valid = False
        if debug:
            print("validating")
        try:
            testMin = float(EntTime[0].get())
            powerValue = float(EntPower[0].get())
        except:
           func.message("Warning","Numerical Entry Invalid")
        else:
            
            #1 means voltage?
            if radioVar == 1: ### *** Remove hardcoded numbers, add calibration function
                    powerNormValue = (powerValue*0.0386) - 0.0203 #Calculated Calibration Curve (y=0.0386x - 0.0203)
            #2 means current?
            if radioVar == 2:
                powerNormValue = powerValue*5/20/3.28  #Current 0-20A Proportial 5v, percentage value for DAC 0-3.28v
            powerTuple = (radioVar,powerNormValue) #combining volt or current selection and Desired Value

            #send inital set values
            # q.put_nowait((2,powerTuple))

            #Initiallize pressure sensor process
            psen_pipe, mainp_pipe = Pipe()
            psen_script = Process(target= start_psensor, args= (psen_pipe,q,))
            psen_script.start()

            #Initiallize power sensor process
            power_pipe, mainpower_pipe = Pipe()
            power_script = Process(target= power_log, args= (power_pipe,q,))
            power_script.start()

            #Initiallize Image Capture Process
            # image_pipe, maini_pipe = Pipe()
            # image_script = Process(target= start_imageCapture, args= (image_pipe,))
            # image_script.start()
            # maini_pipe.send(False)s
            #Turn on LEDs
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(21,GPIO.OUT)
            GPIO.output(21,GPIO.HIGH)

            #Call repeating functions
            self.button_countdown(int(testMin*60))
            self.pressure_sensor(psen_pipe, mainp_pipe,int(testMin*60))
            self.power_sensor(power_pipe,mainpower_pipe)
            #self.image_capture(image_pipe, maini_pipe)

    def button_countdown(self,i):
        if debug:
            print("countdown")
        global estop, countdown
        if i > 0 and estop == False:
            self.LblCountdown.config(text = str(i))
            i -= 1
            countdown = root.after(1000, lambda: self.button_countdown(i))
        elif estop:
            root.after_cancel(countdown)
            self.LblCountdown.config(text = "Test Cancelled")
        else:
            self.LblCountdown.config(text = "Test Ended")
            self.stopTest()

    def pressure_sensor(self, psen_pipe, mainp_pipe, testSec):
        global estop
        if debug:
            print("Pressure Sensor")
            print("the main pipe poll comes back: ",mainp_pipe.poll())
        if not estop:
            pressureList = [0]*4
            while mainp_pipe.poll():
                pressureList= mainp_pipe.recv()
            #print(pressureList)
            self.pressure_0 = round(pressureList[0],3)
            self.pressure_1 = round(pressureList[1],3)
            self.pressure_2 = round(pressureList[2],3)
            self.pressure_3 = round(pressureList[3],3)

            self.graphing(self.pressure_0,self.pressure_1,self.pressure_2,self.pressure_3, testSec)

            self.psen0.config(text = "Inlet 1: "+str(self.pressure_0)+"kPa")
            self.psen1.config(text = "Outlet 1: "+str(self.pressure_1)+"kPa")
            self.psen2.config(text = "Inlet 2: "+str(self.pressure_2)+"kPa")
            self.psen3.config(text = "Outlet 2: "+str(self.pressure_3)+"kPa")
            pressure_sensor = root.after(1000, lambda: self.pressure_sensor(psen_pipe, mainp_pipe,testSec))
        else:
            root.after_cancel(self.pressure_sensor)

    def power_sensor(self, power_pipe, mainpower_pipe):
        global estop
        if debug:
            print("Pressure Sensor")
            print("the main pipe poll comes back: ",mainpower_pipe.poll())
        if not estop:
            powerList = [0]*3
            while mainpower_pipe.poll():
                powerList= mainpower_pipe.recv()
            self.power_0 = round(powerList[0],3)
            self.power_1 = round(powerList[1],3)
            self.power_2 = round(powerList[2],3)

            self.power0.config(text = "Current: "+str(self.power_0)+" mA")
            self.power1.config(text = "Voltage: "+str(self.power_1)+" V")
            self.power2.config(text = "Power: "+str(self.power_2)+" mW")
            power_sensor = root.after(1000, lambda: self.power_sensor(power_pipe, mainpower_pipe))
        else:
            root.after_cancel(self.pressure_sensor)

    def image_capture(self, image_pipe, maini_pipe):
        global estop
        if debug:
            print("Image Capture Salt Area")
            print("the main pipe poll comes back: ",maini_pipe.poll())
        if not estop:
            while maini_pipe.poll():
                self.saltArea = round(maini_pipe.recv(),3)
            #print(self.saltArea)
            #testing
            self.saltData.config(text = "Total Salt Area: %fmm2"%self.saltArea)
            self.img = Image.open(func.latestFile())
            self.imgW, self.imgH = self.img.size
            self.imgW = round(int(self.imgW)/4)
            self.imgH = round(int(self.imgH)/4)
            self.imgSmall = self.img.resize((self.imgW,self.imgH))
            self.imgSmall = ImageTk.PhotoImage(self.imgSmall)
            self.saltImage.config(image=self.imgSmall)
            image_capture = root.after(1000, lambda: self.image_capture(image_pipe, maini_pipe))
        else:
            root.after_cancel(self.image_capture)

    def graphing(self, press0, press1, press2, press3, testSec):
        global graph, estop
        while graph and not estop:
            press_0 = []
            press_1 = []
            press_2 = []
            press_3 = []

            plt.ion()
            plt.clf()
            index = list(range(0,testSec+1))
            press_0.append(press0)
            press_1.append(press1)
            press_2.append(press2)
            press_3.append(press3)

            l = len(press_0)
            plt.plot(index[0:l],press_0)
            plt.plot(index[0:l],press_1)
            plt.plot(index[0:l],press_2)
            plt.plot(index[0:l],press_3)
            scroll = index[0:l]
            if scroll[-1]>10:
                press_0.pop(0)
                press_1.pop(1)
                press_2.pop(2)
                press_3.pop(3)
                index.pop(0)
                plt.xlim([index[-10], index[-1]])
            else:
                plt.xlim([0, 10])
            plt.ylim([0, 100])
            plt.show
            plt.pause(0.05)

root = Tk()
my_gui = controls(root)
root.mainloop()
