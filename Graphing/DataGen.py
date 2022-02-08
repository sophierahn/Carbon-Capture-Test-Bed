#Random
import tkinter as tk
import random
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from time import sleep
import matplotlib.pyplot as plt
matplotlib.use("MacOSX")
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

root = tk()
count = 1
x = []
index = []
while count < 30:
    x.append(random.randint(0,100))
    index.append(count)
    
    #y = random.randint(0,100)
    plt.ion()
    plt.clf()
    plt.plot(index,x)
    length = len(x) 
    
    
    if index[-1]>10:
        x.pop(0)
        index.pop(0)
        print(x[-12:-1])
        print(index[-12:-1])
        plt.xlim([index[-10], index[-1]])
    else:
        plt.xlim([0, 10])

    # if index[-1]>12:
    #     x = x[-12:-1]
    #     index = index[-12:-1]
    plt.ylim([0, 100])
    plt.show
    alsdkf=input()
    count += 1
alsdkf=input()
print(length)