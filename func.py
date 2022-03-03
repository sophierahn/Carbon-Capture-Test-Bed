from tkinter import *
import tkinter as tk
from time import sleep
#import RPi.GPIO as GPIO
import sys
import glob
import os

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
        