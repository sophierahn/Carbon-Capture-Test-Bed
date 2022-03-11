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
### Functionality Notes ####

### To Do ###
#Time the function speed
##I don't think we could move faster unless we restructured
#Add option for lower frequency


def muliplexer(calibrationValue,testFreq,limitList,q):
    queueDump = []
    powerList = [0]*3
    pressureList = [0]*4
    powerLevel = (0,0)
    shutoff = False
    data = False
    firstTime = True #used to start data logging once the power supply receives a value
    next = 0
   
    print("Opening I2C bus")
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)
    mpr_0 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25) # *** update TCA indexes with new pi setup
    mpr_1 = adafruit_mprls.MPRLS(tca[5], psi_min=0, psi_max=25)
    mpr_2 = adafruit_mprls.MPRLS(tca[6], psi_min=0, psi_max=25)
    mpr_3 = adafruit_mprls.MPRLS(tca[7], psi_min=0, psi_max=25)
    energy = adafruit_ina260.INA260(tca[4])
    #dac_1 = adafruit_mcp4725.MCP4725(tca[3], address=0x60)
    dac_2 = adafruit_mcp4725.MCP4725(tca[2], address=0x60)
    #adc = ADS.ADS1015(tca[0])
    #chanADC = AnalogIn(adc, ADS.P0)
    
    ### Checking polling type ###
    if testFreq > 0:
        intermittent = True
    else:
        intermittent = False
    
    ### Initalize Data File, When pretest is started  ***this will create blank files if the pretest is cancled -> move to func and use firstTime?
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
       
        ### Checking queue Data, acting or putting back
        #print("reading Queue")
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
            
        
        ### Normal Opperation ###
        ##Collecting Data and Writing to lists
        #print("reading pressure sensors")
        p0 = mpr_0.pressure - calibrationValue
        p1 = mpr_1.pressure - calibrationValue
        p2 = mpr_2.pressure - calibrationValue
        p3 = mpr_3.pressure - calibrationValue
        pressureList = [p0,p1,p2,p3]

        #gasRB = chanADC.voltage #Add proportional conversion to pressure from voltage *** add to pressure or power list 

        #pressureList = [random.randint(5,10), p1, random.randint(5,10), random.randint(5,10)]
        powerList = [energy.current, energy.voltage, energy.power]

    ### Error Checking ### *** add pressure fluxuation 
        # if energy.current > currentLimit or energy.voltage > voltLimit:
        #     #shutoff = True ### *** sending shutoff signal from here means pressure and power dont have a chance to shutdown
        #     multi_pipe.send(True) 

        #Writing Pressure and Power data to the Queue
        q.put_nowait((3,pressureList))
        #q.put_nowait((1,powerList))
    
        #Writing data to DACs
        ### *** add switching system to select current vs volt control
        dac_2.normalized_value = powerLevel[1]
    
        queueDump = [] #reseting the local queue list
        
        #Logging, intermitant or direct
        data = False
        now = time.time()
        if data:
            datalist = pressureList + powerList
            if intermittent and now > next:
                pwriter.writerow(datalist) #writing data to csv
                next = time.time() + testFreq
            else:
                pwriter.writerow(datalist) #writing data to csv

        
    
    ### After ShutOff ###
    print("Mulit Closed")
    #dac_1.normalized_value = 0 #Setting Dacs to Zero at Shutoff Command
    dac_2.normalized_value = 0
    pfile.close() #Closing CSV file
    q.close()
    q.join_thread()

