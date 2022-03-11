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

# def graphing(self, press0, press1, press2, press3, testSec): ### Not currently in Use, Last thing to fix, maybe dont bother
#         global graph, estop
#         while graph and not estop:
#             press_0 = []
#             press_1 = []
#             press_2 = []
#             press_3 = []

#             plt.ion()
#             plt.clf()
#             index = list(range(0,testSec+1))
#             press_0.append(press0)
#             press_1.append(press1)
#             press_2.append(press2)
#             press_3.append(press3)

#             l = len(press_0)
#             plt.plot(index[0:l],press_0)
#             plt.plot(index[0:l],press_1)
#             plt.plot(index[0:l],press_2)
#             plt.plot(index[0:l],press_3)
#             scroll = index[0:l]
#             if scroll[-1]>10:
#                 press_0.pop(0)
#                 press_1.pop(1)
#                 press_2.pop(2)
#                 press_3.pop(3)
#                 index.pop(0)
#                 plt.xlim([index[-10], index[-1]])
#             else:
#                 plt.xlim([0, 10])
#             plt.ylim([0, 100])
#             plt.show
#             plt.pause(0.05)