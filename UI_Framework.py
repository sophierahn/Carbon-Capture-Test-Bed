import sys
import time
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import Canvas
from random import randint
import matplotlib
from matplotlib import pylab
from numpy import False_
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from pylab import plot, show, figure, xlabel, ylabel, draw, pause, ion, close
import os
import csv
from datetime import datetime
from datetime import timedelta
from multiprocessing import Process, Pipe, Queue
import func
from pressure_sensor import start_psensor

EntFlow = [None]*1
EntPower = [None]*1
EntTime = [None]*1
EntPump = [None]*1

estop = False
countdown = None
debug = True

class controls:
    global radioVar, var, estop, countdown, testDefault
    testDefault = [0,0,0,3]

    def __init__(self, master):
        self.master = master
        master.title("Carbon Capture Control")
        master.geometry('1000x630') #Set Size of GUI window (WxH)
        master.lift()
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
       
        # self.canvas = Canvas(master, bg="#f2f2f2")
        # self.canvas.place(x=MVP+10, y=50)
        # self.canvas.create_line(1,1,1,255, width = 3, fill="#666666")    

        #Master Title
        self.lblTitle = Label(master, text="MEA Cell Controls", font=("Calibri",text+14))
        self.lblTitle.pack(side=TOP)

        
    #### Settings Titles ####
        self.TitlPump = Label(master, text="Pump Controls", font=("Calibri",text+8))
        self.TitlPump.place(x=setX,y=setY)
        self.TitlFlow = Label(master, text="Flow Controller", font=("Calibri",text+8))
        self.TitlFlow.place(x=setX,y=setY+100)
        self.TitlPower = Label(master, text="Power Supply", font=("Calibri",text+8))
        self.TitlPower.place(x=setX,y=setY+200)

        self.LblTimer = Label(master, text="Remaining Time:", font=("Calibri",text+6))
        self.LblTimer.place(x=setX+300,y=setY-50)
        self.LblCountdown = Label(master, text="", font=("Calibri",text+6))
        self.LblCountdown.place(x=setX+460,y=setY-50)

    #### Settings Controls ####
        def only_numbers(char):
            if char.isdigit() or char == ".":
                return True
            else:
                return False
        validation = root.register(only_numbers)
        

        #Pump controls
        EntPump[0] = Entry(master, width=5, justify=RIGHT, validate="key", validatecommand=(validation, '%S'))
        self.LblPump = Label(master, text="Flow Rate:", font=("Calibri",text+4))
        EntPump[0].place(x=entX,y=setY+30)
        EntPump[0].insert(0,testDefault[0])#Set Default
        self.LblPump.place(x=setX,y=setY+30)

        #Flow Controller controls
        EntFlow[0] = Entry(master, width=5, justify=RIGHT, validate="key", validatecommand=(validation, '%S'))
        self.LblFlow = Label(master, text="Flow Rate:", font=("Calibri",text+4))
        EntFlow[0].place(x=entX,y=setY+130)
        EntFlow[0].insert(0,testDefault[1])#Set Default
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
        var.set(1)

        #Test Duration
        EntTime[0] = Entry(master, width=5, justify=RIGHT, validate="key", validatecommand=(validation, '%S'))
        self.LblTime = Label(master, text="Test Duration:", font=("Calibri",text+6))
        EntTime[0].place(x=entX,y=setY+340)
        EntTime[0].insert(0,testDefault[3])#Set Default
        self.LblTime.place(x=setX-20,y=setY+340)

    #### Buttons ####
        btnX = setX+50
        btnY = setY+400
        self.BtnStart = Button(master, text="Start Test", command=lambda: self.validateTest(), width=10, height=2, bg='#DDDDDD', activebackground='#32CD32', wraplength=100)
        self.BtnStart.place(x=btnX,y=btnY)
        self.BtnCancel = Button(master, text="Cancel Test", command=lambda: self.stopTest(), width=10, height=2, bg='#DDDDDD', activebackground='#32CD32', wraplength=100)
        self.BtnCancel.place(x=btnX,y=btnY+50)
        self.BtnPurge = Button(master, text="Purge Cell", command=lambda: self.validateTest(), width=10, height=2, bg='#DDDDDD', activebackground='#32CD32', wraplength=100)
        self.BtnPurge.place(x=btnX+130,y=btnY+20)
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
        global testDefault
        try:
            testDefault[0] = float(EntPump[0].get())
            testDefault[1] = float(EntFlow[0].get())
            testDefault[2] = float(EntPower[0].get())
            testDefault[3] = float(EntTime[0].get())
            print(testDefault)
        except:
            func.Missatge("Warning","Numerical Entry Invalid")

    #closes window
    def close(self):
        if debug:
            print("closing")
        global psen_script
        if 'psen_script' in globals():

            psen_script.kill()
        sys.exit(0)
    
    ##Estop Function //Need to add a reset fuctionality to change estop back to false so tests can be restarted
    def stopTest(self): 
        global estop, psen_script
        if not estop:
            estop = True
            if 'psen_script' in globals():
                psen_script.kill()
            self.BtnCancel.config(text="Reset", bg='#FF0000', activebackground='#FF0000')
            EntFlow[0].delete(0,'end')
            EntPump[0].delete(0,'end')
            EntPower[0].delete(0,'end')
            EntTime[0].delete(0,'end')
            EntFlow[0].insert(0,str(testDefault[0]))
            EntPump[0].insert(0,testDefault[1])
            EntPower[0].insert(0,testDefault[2])
            EntTime[0].insert(0,testDefault[3])
        else:
            estop = False
            self.BtnCancel.config(text="Cancel Test", bg='#DDDDDD', activebackground='#32CD32')
            self.LblCountdown.config(text = "")

    #start of test program, validating all varibles
    def validateTest(self):
        if debug:
            print("validating")
        global psen_script
        try:
            gasFlow = float(EntFlow[0].get())
            liquidFlow = float(EntPump[0].get())
            testMin = float(EntTime[0].get())
            powerVC = float(EntPower[0].get())
        except:
           func.Missatge("Warning","Numerical Entry Invalid")
        
        #Initiallize pressure sensor process
        psen_pipe, mainp_pipe = Pipe()
        psen_script = Process(target= start_psensor, args= (psen_pipe,))
        psen_script.start()  
        mainp_pipe.send(False)

        #Initiallize Image Capture Process
        image_pipe, maini_pipe = Pipe()
        image_script = Process(target= start_imageCapture, args= (image_pipe,))
        image_script.start()  
        maini_pipe.send(False)

        #Call repeating functions
        self.button_countdown(int(testMin*60))
        self.pressure_sensor(psen_pipe, mainp_pipe)
        self.image_capture(image_pipe, maini_pipe)

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

    def pressure_sensor(self, psen_pipe, mainp_pipe):
        global estop
        if debug:
            print("Pressure Sensor")
        if not estop:
            print("the main pipe poll comes back: ",mainp_pipe.poll()) 
            while mainp_pipe.poll():
                self.pressure = mainp_pipe.recv()
            print(self.pressure)
            pressure_sensor = root.after(1000, lambda: self.pressure_sensor(psen_pipe, mainp_pipe))
        else:
            root.after_cancel(pressure_sensor)

    def image_capture(self, image_pipe, maini_pipe):
        global estop
        if debug:
            print("Image Capture Salt Area")
        saltArea = float(0)
        if not estop:
            print("the main pipe poll comes back: ",maini_pipe.poll()) 
            while maini_pipe.poll():
                saltArea = maini_pipe.recv()
            print(saltArea)
            pressure_sensor = root.after(1000, lambda: self.image_capture(image_pipe, maini_pipe))
        else:
            root.after_cancel(image_capture)
        

root = Tk()
my_gui = controls(root)  
root.mainloop()