import board
import adafruit_tca9548a
import adafruit_mprls
import adafruit_ina260
import adafruit_mcp4725
import csv
from datetime import datetime
import subprocess
import random
import math
import time
import func

### Functionality Notes ###
#The purpose of multiplexer is to poll sensors and activate actuators
#It collects data directly from the sensors at a frequency matching the run time of the script
#It saves this data to a CSV uniquely time stamped
#It checks the contents of the queue, differentiating between shut off, actuators, and sensors based on ID
#It puts sensor data back immediately without interacting with it - presumably thats old data anyway
#It enacts actuator instructions
#It saves the shutoff status, which will allow for graceful shutdown in the case of shutdown - which we like
#It writes new sensor data to the queue, it will appear after previously placed data
# ^^this could be space for frequency control, right now we're spitting data as fast as we can
### Functionality Notes ####

### To Do ###
#Time the function speed
##I don't think we could move faster unless we restructured
#Add option for lower frequency


def muliplexer(calibrating, testFreq,q):
    queueDump = []
    powerList = [0]*3
    pressureList = [0]*4
    powerLevel = (0,0)
    shutoff = False
    data = False
    firstTime = True #used to start data logging once power supply receives a value
    sampleTime = True #used with frequency variance
    calibrationSamples = 500 # probably higher?
    calibrationList =[]
    calibrationValue = 0 #so that if we skip calibration, we see absolute results
    calibrateStatus = 1 #bc we want to hop into calibration mode at startup
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)
    #mpr_0 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25)
    mpr_1 = adafruit_mprls.MPRLS(tca[1], psi_min=0, psi_max=25)
    #mpr_2 = adafruit_mprls.MPRLS(tca[2], psi_min=0, psi_max=25)
    mpr_3 = adafruit_mprls.MPRLS(tca[3], psi_min=0, psi_max=25)
    energy = adafruit_ina260.INA260(tca[4])
    dac_1 = adafruit_mcp4725.MCP4725(tca[5], address=0x60)
    #dac_2 = adafruit_mcp4725.MCP4725(tca[6], address=0x60)
    
    ### Checking polling type ###
    if testFreq > 0:
        intermittent = True
    else:
        intermittent = False
    
    ### Initalize Data File, When pretest is initated 
    now = datetime.now()
    current= now.strftime("%m_%d_%Y_%H_%M_%S")
    pfilename = "./data/" +"Pressure_sensor_data_" + current +".csv"
    pfile = open(pfilename, "w") #creating pressure sensor data csv with current date and time
    pwriter = csv.writer(pfile)
    pwriter.writerow(['0' , '1', '2', '3', 'current', 'voltage', 'power'])


    while not shutoff:
        while not q.empty():
            try:
                queueDump.append(q.get_nowait())
            except:
                pass
        #Checking each tuple at a time from the queue
        for i in queueDump:
            if i[0] == 0:
                shutoff = i[1]  #shutoff command
                q.put_nowait((0,shutoff))
            if i[0] == 1:
                q.put_nowait((1,i[1])) #power sensor Data
            if i[0] == 2:
                powerLevel = i[1]  #power supply DAC
                if firstTime: #start data logging when the actual test starts
                    data = True
                    firstTime = False
            if i[0] == 3:
                q.put_nowait((3,i[1])) #pressure sensor data
            if i[0] == 4:
                q.put_nowait((4,i[1])) #calibration status
        
        ### Calibration ###
        if calibrating:
            q.put_nowait((4,calibrateStatus))
            while len(calibrationList) <= calibrationSamples:
                #calibrationList.append(mpr_0.pressure)
                calibrationList.append(mpr_1.pressure)
                #calibrationList.append(mpr_2.pressure)
                calibrationList.append(mpr_3.pressure)
            
            #to eliminate individual sensor drift
            sum = sum(calibrationList)
            calibrationValue = sum/calibrationSamples
            func.saveTestPreset([calibrationValue],True) #Write Calibration value to Test Preset File
            calibrating = False 
            calibrateStatus = 0
            q.put_nowait((4,calibrateStatus)) #tells the main program to contiune
        
        ### Normal Opperation ###
        else: 
        #either we've finished calibration or we skipped it
            #Collecting Data and Writing to lists
            #p0 = mpr_0.pressure - calibrationValue
            p1 = mpr_1.pressure - calibrationValue
            #p2 = mpr_2.pressure - calibrationValue
            p3 = mpr_3.pressure - calibrationValue
            #pressureList = [p0,p1,p2,p3]
            pressureList = [random.randint(5,10), p1, random.randint(5,10), p3]
            powerList = [energy.current, energy.voltage, energy.power]

            #Writing Pressure and Power data to the Queue
            q.put_nowait((0,pressureList))
            q.put_nowait((1,powerList))
        
            #Writing data to DACs
            ### *** add switching system to select current vs volt control
            #dac_1.normalized_value = powerLevel[1]
            
            queueDump = [] #reseting the local queue list
            
            #Logging, intermitant or direct
            now = time.time()
            if data:
                if intermittent and now > next:
                    pwriter.writerow(pressureList) #writing data to csv
                    lastWritten = time.time()
                    next = lastWritten + testFreq
                else:
                    pwriter.writerow(pressureList) #writing data to csv

        
    
    ### After ShutOff ###
    print("Mulit Closed")
    dac_1.normalized_value = 0 #Setting Dacs to Zero at Shutoff Command
    pfile.close() #Closing CSV file
    q.close()
    q.join_thread()

