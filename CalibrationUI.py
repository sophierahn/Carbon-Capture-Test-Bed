#Calibration UI

import sys
import tkinter as tk
from tkinter import *
from tkinter import Canvas
import func
from ImageScaleCalibration import imageScaleCalibration


global scaleFactor, powerLine
testDefault = func.loadTestPresets()
scaleFactor = testDefault[11]
powerLine = testDefault[12]

text = 4
master = tk.Tk()
master.title("CO2 Calibration UI")
master.geometry('600x300+150+150') #Set Size of GUI window (WxH)

lblTitle = Label(master, text="Calibration Panel", font=("Calibri",text+16))
lblTitle.place(x=200,y=5)
lblInstructImageTitle = Label(master, text="Image Scale Calibration", font=("Calibri",text+8))
lblInstructImageTitle.place(x=10,y=40)
lblInstructImage = Label(master, text="Please Place the calibration block on the\ncenter of the cell window", font=("Calibri",text+4),justify="left")
lblInstructImage.place(x=10,y=60)
lblScale = Label(master, text="Scale Factor: ", font=("Calibri",text+6),justify="left")
lblScale.place(x=10,y=100)
imageButton = Button(master, text="Calibrate Image Scale", command=lambda: runImageCalibration(), width=20, height=2, bg='#DDDDDD', activebackground='#f7a840', wraplength=100)
imageButton.place(x=30,y=140)

lblInstructPowerTitle = Label(master, text="Power Supply Calibration", font=("Calibri",text+8))
lblInstructPowerTitle.place(x=300,y=40)
lblInstructPower = Label(master, text="Ensure the Power supply is turned on\nand power leads are disconnected from the cell", font=("Calibri",text+4),justify="left")
lblInstructPower.place(x=300,y=60)
lblPowerCurve = Label(master, text="Power Curve: ", font=("Calibri",text+6),justify="left")
lblPowerCurve.place(x=300,y=100)
powerButton = Button(master, text="Calibrate Power Control", command=lambda: runPowerCalibration(), width=20, height=2, bg='#DDDDDD', activebackground='#f7a840', wraplength=100)
powerButton.place(x=330,y=140)

BtnClose = Button(master, text="Close", command=lambda: close())
BtnClose.place(x=10,y=270)

def runImageCalibration():
    global scaleFactor
    imageButton.config(text="Running")
    #scaleFactor = 40
    scaleFactor = imageScaleCalibration()
    lblScale.config(text="Scale Factor: %.3f" %(scaleFactor))
    imageButton.config(text="Completed")

def runPowerCalibration():
    global powerLine
    func.message("Warning","This process will cycle the Power supply up to 24 Volts. Please ensure the cell is not engerized and the power leads are safe\n\nThe process will start when you hit Okay")
    powerButton.config(text="Running")
    powerLine = 0.0912
    #powerLine = powerCalibrator()
    lblPowerCurve.config(text=powerLine)
    powerButton.config(text="Completed")

def saveTest():
    global powerLine, scaleFactor
    testDefault = func.loadTestPresets()
    testDefault[11] = scaleFactor
    testDefault[12] = powerLine
    print(testDefault)
    func.saveTestPreset(testDefault,False)
       
def close():
    saveTest()
    sys.exit(0)

master.mainloop()

