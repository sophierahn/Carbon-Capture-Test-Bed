from tkinter import *
import tkinter as tk
from time import sleep
#import RPi.GPIO as GPIO
import sys

def Missatge(cap,msg):
    lmsg = len(msg)/50+1
    tkmsg = tk.Toplevel()
    tkmsg.wm_title("%s"%str(cap))
    tkmsg.geometry('500x%s'% str(50*int(lmsg)+50))
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

