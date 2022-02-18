#Random
import tkinter as tk
import random
import matplotlib
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
#from matplotlib.figure import Figure
from time import sleep
import matplotlib.pyplot as plt
import board
import adafruit_tca9548a
import adafruit_mprls
matplotlib.use("TkAgg")
LARGE_FONT= ("Verdana", 12)
#style.use("ggplot")


# def data():
#     count = 1
#     x = []
#     # y = []
#     while count < 100:
#         x.append(random.randint(0,100))
#         #y = random.randint(0,100)
#         plt.ion()
#         plt.clf
#         plt.plot(x)
#         plt.show
#         sleep(1)
#         count += 1
#     return (x)

# plt.ion()
#datax = data()
# print(datax)
# plt.plot(datax)
# plt.show
# x = input()

i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)
mpr_0 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25)
mpr_1 = adafruit_mprls.MPRLS(tca[1], psi_min=0, psi_max=25)
mpr_2 = adafruit_mprls.MPRLS(tca[2], psi_min=0, psi_max=25)
mpr_3 = adafruit_mprls.MPRLS(tca[3], psi_min=0, psi_max=25)

#root = tk()
count = 1
x = []
y = []
w = []
z = []
index = []
while count < 30:

    pressure0 = mpr_0.pressure
    pressure1 = mpr_1.pressure 
    pressure2 = mpr_2.pressure 
    pressure3 = mpr_3.pressure   
    x.append(pressure0)
    y.append(pressure1)
    w.append(pressure2)
    z.append(pressure3)
    #x.append(random.randint(950,1000))
    index.append(count)
    
    #y = random.randint(0,100)
    plt.ion()
    plt.clf()

    plt.plot(index,x)
    plt.plot(index,y)
    plt.plot(index,w)
    plt.plot(index,z)
    length = len(x) 
    
    
    if index[-1]>10:
        x.pop(0)
        y.pop(0)
        w.pop(0)
        z.pop(0)
        index.pop(0)
        print(x[-12:-1])
        print(index[-12:-1])
        plt.xlim([index[-10], index[-1]])
    else:
        plt.xlim([0, 10])

    # if index[-1]>12:
    #     x = x[-12:-1]
    #     index = index[-12:-1]
    plt.ylim([973, 977])
    plt.show
    #if count == 1:
        #alsdkf=input()
    plt.pause(.5)
    count += 1
alsdkf=input()
#print(length)