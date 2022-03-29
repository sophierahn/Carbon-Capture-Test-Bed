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


def muliplexer(calibrationValue,testFreq,limitList,q, multi_pipe):
    queueDump = []
    powerList = [0]*4
    pressureList = [0]*4
    powerLevel = (0,0)
    gasFlow = 0
    shutoff = False
    data = False
    firstTime = True #used to start data logging once the power supply receives a value
    next = 0
   
    print("Opening I2C bus")
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)
    mpr_0 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25) 
    mpr_1 = adafruit_mprls.MPRLS(tca[5], psi_min=0, psi_max=25)
    mpr_2 = adafruit_mprls.MPRLS(tca[6], psi_min=0, psi_max=25)
    mpr_3 = adafruit_mprls.MPRLS(tca[7], psi_min=0, psi_max=25)
    energy = adafruit_ina260.INA260(tca[4]) 
    dac_1 = adafruit_mcp4725.MCP4725(tca[3], address=0x60)#to the power supply
    dac_2 = adafruit_mcp4725.MCP4725(tca[2], address=0x60) #to the flow controller
    adc = ADS.ADS1015(tca[1])
    chan = AnalogIn(adc, ADS.P0, ADS.P1)
 
    #dac_1.normalized_value = powerLevel[1]
    
    ### Checking polling type ###
    if testFreq > 0:
        intermittent = True
    else:
        intermittent = False
    
    ### Initalize Data File, When pretest is started  ***this will create blank files if the pretest is cancled -> move to func and use firstTime?
    # now = datetime.now()
    # current= now.strftime("%m_%d_%Y_%H_%M_%S")
    # pfilename = "./data/" +"Sensor_data_" + current +".csv"
    # pfile = open(pfilename, "w") #creating pressure sensor data csv with current date and time
    # pwriter = csv.writer(pfile)
    # pwriter.writerow(['Elapsed Time', 'KHCO3 In (kPa)' , 'KHCO3 Out (kPa)', 'CO2 In (kPa)', 'CO2 Out (kPa)', 'Current (mA)', 'Voltage (V)', 'Power (mW)', 'CO2 Flow Rate (SCCM)'])
    #start = time.time()

    while not shutoff:
        while not q.empty():
            try:
                queueDump.append(q.get_nowait())
            except:
                pass
       
        ### Checking queue Data, acting or putting back
        for i in queueDump:
            if i[0] == 0:
                shutoff = i[1]  #shutoff command
                q.put_nowait((0,shutoff))
            if i[0] == 1:
                q.put_nowait((1,i[1])) #power sensor Data
            if i[0] == 2:
                powerLevel = i[1]  #power supply DAC
                print(powerLevel[1])
                if firstTime: #start data logging when the actual test starts
                    data = True
                    pwriter, pfile, start = func.startFile()
                    firstTime = False
            if i[0] == 3:
                q.put_nowait((3,i[1])) #pressure sensor data
            if i[0] == 4:
                gasFlow = i[1] #CO2 Flow Rate
            
        
    ### Normal Opperation ###
        # Collecting Data and Writing to lists
        p0 = mpr_0.pressure - calibrationValue
        p1 = mpr_1.pressure - calibrationValue
        #p1 = random.randint(950,970)
        p2 = mpr_2.pressure - calibrationValue
        p3 = mpr_3.pressure - calibrationValue
        pressureList = [p0,p1,p2,p3]
        pressureAve = (p0+p1+p2+p3)/4
        flowRB = chan.voltage*40 
        powerList = [energy.current, energy.voltage, energy.power,flowRB]
        #pressureList = [random.randint(5,10), p1, random.randint(5,10), random.randint(5,10)]
       
        #Writing Pressure and Power data to the Queue
        q.put_nowait((3,pressureList))
        q.put_nowait((1,powerList))
    
        #Writing data to DACs
        dac_1.normalized_value = powerLevel[1]
        dac_2.normalized_value = gasFlow
        
    

        ### Error Checking ### 
        #Legend:
        # msg = 1, C02 overflow
        # msg = 2, current over
        # msg = 3, voltage over
        # msg = 4, pressure over

        if flowRB > limitList[0]:  
            #print("what!!!",flowRB, limitList)      #CO2 Flow Rate Check
            multi_pipe.send((True,1)) 
        if powerList[0] > limitList[1]: #Current Check
            #print("why?",powerList) 
            multi_pipe.send((True,2)) 
        if powerList[1] > limitList[2]: #Voltage Check
            multi_pipe.send((True,3))
        if pressureAve > limitList[3]:  #Pressure Sensor Check
            multi_pipe.send((True,4)) 

        queueDump = [] #reseting the local queue list
        
        #Logging, intermitant or direct
        #data = False #*** Remove
        now = time.time()
        if data:
            elapsed = round(time.time()-start,2)
            datalist = [elapsed]+pressureList+powerList
            if intermittent and now > next:
                pwriter.writerow(datalist) #writing data to csv
                next = time.time() + testFreq
            else:
                pwriter.writerow(datalist) #writing data to csv

    ### After ShutOff ###
    print("Mulit Closed")
    dac_1.normalized_value = 0 #Setting DACs to Zero at Shutoff 
    dac_2.normalized_value = 0
   
    q.close()
    try:
        pfile.close() #Closing CSV file
        q.join_thread()
    except Exception as e:
        func.errorLog(e, "Multiplexer")

