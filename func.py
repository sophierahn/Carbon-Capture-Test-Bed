from tkinter import *
import tkinter as tk
from time import sleep
#import RPi.GPIO as GPIO
import sys
import glob
import os
from datetime import datetime
import time
import csv

mac = True

if not mac:
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
        list_of_files = glob.glob('/home/pi/Carbon-Capture-Test-Bed/Images_Edited/*.jpg')
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
        if count <= 11:
            testDefault[count] = float(i[colon:])
        else:
            testDefault[count] = float(i[colon:])
        count += 1
    return testDefault

def saveTestPreset(testDefault,calibrate):
    if calibrate:
        with open('TestPreset.txt', 'a') as file:
            newString = "Calibrated Atmospheric Pressure: %f" %(testDefault[0])
            file.write(str(newString))
    else:
        with open('TestPreset.txt', 'w') as file:
            newString = "Flow Rate (ml/min): %f \n\
            Power Select (1-Voltage, 2-Current): %f \n\
            Power Value (v or A): %f \n\
            Test Durration (min): %f \n\
            Data Log Rate (0=As fast as possible): %f \n\
            Calibration Setting (0=absolute, 1=gauge): %f \n\
            Flow Limit: %f \n\
            Current Limit: %f \n\
            Voltage Limit: %f\n\
            Pressure Limit: %f\n\
            Image Capture Rate: %f\n\
            Image Calibration (mm/pixel): %f\n\
            Power Line: %f\n\
            Capture Images: %f" % (testDefault[0], testDefault[1], testDefault[2], testDefault[3], testDefault[4], testDefault[5], testDefault[6],testDefault[7],testDefault[8],testDefault[9],testDefault[10],testDefault[11],testDefault[12],testDefault[13])
            file.write(str(newString))

def calibration(): 
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)
    mpr_0 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25) # *** update TCA indexes with new pi setup
    mpr_1 = adafruit_mprls.MPRLS(tca[5], psi_min=0, psi_max=25)
    mpr_2 = adafruit_mprls.MPRLS(tca[6], psi_min=0, psi_max=25)
    mpr_3 = adafruit_mprls.MPRLS(tca[7], psi_min=0, psi_max=25)
    calibrationList = []
    calibrationSamples = 500 # ***change value as needed

    while len(calibrationList) <= calibrationSamples:
        calibrationList.append(mpr_0.pressure)
        calibrationList.append(mpr_1.pressure)
        calibrationList.append(mpr_2.pressure)
        calibrationList.append(mpr_3.pressure)
    
    #to eliminate individual sensor drift
    caliSum = sum(calibrationList)
    print(caliSum)
    calibrationValue = caliSum/len(calibrationList)
    #saveTestPreset([calibrationValue],True) #Write Calibration value to Test Preset File
    return(calibrationValue)

def setZero():
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)
    dac_1 = adafruit_mcp4725.MCP4725(tca[2], address=0x60)
    dac_2 = adafruit_mcp4725.MCP4725(tca[3], address=0x60)
    dac_1.normalized_value = 0
    dac_2.normalized_value = 0

def startFile(fileName):
    pfilename = "/media/pi/Lexar/CO2_System_Sensor_Data/" + fileName + ".csv"
    pfile = open(pfilename, "w") #creating pressure sensor data csv with current date and time
    pwriter = csv.writer(pfile)
    pwriter.writerow(['Elapsed Time', 'KHCO3 In (kPa)' , 'KHCO3 Out (kPa)', 'CO2 In (kPa)', 'CO2 Out (kPa)', 'Current (mA)', 'Voltage (V)', 'Power (mW)', 'CO2 Flow Rate (SCCM)'])
    start = time.time()
    return (pwriter, pfile, start)

def errorLog(error, location):
    with open('ErrorLog.txt', 'a') as file:
        now = datetime.now()
        current= now.strftime("%m/%d/%Y-%H:%M:%S")
        newString = "\n"+current + ": "+ str(location)+ " - " +str(error)
        file.write(newString)