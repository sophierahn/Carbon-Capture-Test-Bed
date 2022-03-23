import board
import adafruit_tca9548a
import adafruit_mprls
import adafruit_ina260
import adafruit_mcp4725
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import csv
from datetime import datetime
import subprocess
import random
import math
import numpy as np
from scipy.optimize import curve_fit
import time


### Functionality Notes ###
#This is made to create a more accurate calibration curve for the power supply
#it was made by ripping apart multiplexer
#goodjob making mulitplexer bronwyn

def powerCalibrator():
    currentList = []
    voltageList = []
    powerList = []
    powerLevel = np.arange(0,1,0.01).tolist()
    print("testing at the intervals of: ")
    print(powerLevel)

    def objective(x, a, b, c):
        return a * x + b

   
    print("Opening I2C bus")
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)
    energy = adafruit_ina260.INA260(tca[4]) 
    dac_1 = adafruit_mcp4725.MCP4725(tca[3], address=0x60)#to the power supply
 
    #dac_1.normalized_value = powerLevel[1]
    

    now = datetime.now()
    current= now.strftime("%m_%d_%Y_%H_%M_%S")
    pfilename = "./data/" +"Power_Supply_Calibration_Data_" + current +".csv"
    pfile = open(pfilename, "w") #creating pressure sensor data csv with current date and time
    pwriter = csv.writer(pfile)
    pwriter.writerow([ 'Power Level', 'current', 'voltage', 'power'])

    x = 0
    y = int(0)

    for x in powerLevel:
        dac_1.normalized_value = powerLevel[y]
        time.sleep(3)
        currentList.append(energy.current)
        voltageList.append(energy.voltage)
        print(x)
        powerList.append(energy.power)
        y = y + int(1)

  
    voltrela, voltsmt = curve_fit(objective, powerLevel, voltageList)
    currentrela, currsmt = curve_fit(objective, powerLevel, currentList)
    powerrela, powersmt = curve_fit(objective, powerLevel, powerList)
    
    print(voltrela)
    print(currentrela)
    print(powerrela)



    #Logging, intermitant or direct
    data = True #*** Remove
    now = time.time()
    y = int(0)
    if data:
        for x in powerLevel:
            print(type(y))
            current = currentList[y]
            voltage = voltageList[y]
            power = powerList[y]
            powerlevel = powerLevel[y]
            pwriter.writerow([powerlevel, current, voltage, power]) #writing data to csv
            y = y + int(1)

    ### After ShutOff ###
    print("Mulit Closed")
    dac_1.normalized_value = 0 #Setting DACs to Zero at Shutoff 
    
    pfile.close() #Closing CSV file






powerCalibrator()