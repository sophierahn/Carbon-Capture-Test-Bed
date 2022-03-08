#Test.py
import time
import tkinter as tk
from tkinter import *

window = tk.Tk()
window.title("test of scrolledtext and INSERT method")
window.geometry('350x200')

txt = Entry(window,width=10,justify= RIGHT)
txt.insert(tk.INSERT,'3.785')
txt.grid(column=0,row=0)

window.mainloop() 