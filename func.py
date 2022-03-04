from tkinter import *
import tkinter as tk
from time import sleep
#import RPi.GPIO as GPIO
import sys
import glob
import os
import board
import adafruit_tca9548a
import adafruit_mprls
import adafruit_ina260
import adafruit_mcp4725
import math


def message(cap,msg):
    lmsg = len(msg)/50+1
    tkmsg = tk.Toplevel()
    tkmsg.wm_title("%s"%str(cap))
    height = str(50*int(lmsg)+50)
    tkmsg.geometry('500x%s+200+200'%height)
    Lmsg = Label(tkmsg,text="%s"%msg,wraplength=450)
    #Lmsg.place(x=25,y=10)
    Lmsg.pack(pady=20)
    btnok=Button(tkmsg, command=lambda:tkmsg.destroy(), text="Ok", width=6, height=1)
    btnok.pack()
    #btnok.place(x=230,y=80)

def isfloat(x):
    try:
        a =float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    try:
        a =int(x)
    except ValueError:
        return False
    else:
        return True

def latestFile():
        list_of_files = glob.glob('/home/pi/Carbon-Capture-Test-Bed/Edited_Images/*.jpg')
        #print(type(list_of_files), len(list_of_files))
        return max(list_of_files, key=os.path.getctime)

def loadTestPresets():
    with open('TestPreset.txt', 'r') as file:
        lines = file.readlines()
        testDefault = []
        for line in lines:
            testDefault.append(line.strip())
    count = 0
    for i in testDefault:
        colon = int(i.find(':')+2)
        testDefault[count] = i[colon:]
        count += 1
    return testDefault

def saveTestPreset(testDefault,calibrate):
        if calibrate:
            with open('TestPreset.txt', 'a') as file:
                newString = "Calibrated Atmospheric Pressure: %d" %(testDefault[0])
                file.write(str(newString))
        else:
            with open('TestPreset.txt', 'w') as file:
                newString = "Flow Rate (ml/min): %d \nPower Select (1-Voltage, 2-Current): %d \
                    \nPower Value (v or A): %d \nTest Durration (min): %d \nBreak" % (testDefault[0], testDefault[1],testDefault[2], testDefault[3])
                file.write(str(newString))

def calibration():
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)
    #mpr_0 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25)
    mpr_1 = adafruit_mprls.MPRLS(tca[1], psi_min=0, psi_max=25)
    #mpr_2 = adafruit_mprls.MPRLS(tca[2], psi_min=0, psi_max=25)
    mpr_3 = adafruit_mprls.MPRLS(tca[3], psi_min=0, psi_max=25)
    calibrationList = []
    calibrationSamples = 500

    while len(calibrationList) <= calibrationSamples:
        #calibrationList.append(mpr_0.pressure)
        calibrationList.append(mpr_1.pressure)
        #calibrationList.append(mpr_2.pressure)
        calibrationList.append(mpr_3.pressure)
    
    #to eliminate individual sensor drift
    caliSum = sum(calibrationList)
    calibrationValue = caliSum/calibrationSamples
    saveTestPreset([calibrationValue],True) #Write Calibration value to Test Preset File
    return(calibrationValue)
    #tells the main program to contiune