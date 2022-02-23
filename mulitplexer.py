import board
import adafruit_tca9548a
import adafruit_mprls
import adafruit_ina260
import adafruit_mcp4725
import csv
from datetime import datetime
import subprocess


def muliplexer(q):
    queueDump = []
    powerList = [0]*3
    pressureList = [0]*4
    shutoff = False
    data = True
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)
    mpr_0 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25)
    mpr_1 = adafruit_mprls.MPRLS(tca[1], psi_min=0, psi_max=25)
    mpr_2 = adafruit_mprls.MPRLS(tca[2], psi_min=0, psi_max=25)
    mpr_3 = adafruit_mprls.MPRLS(tca[3], psi_min=0, psi_max=25)
    energy = adafruit_ina260.INA260(tca[4])
    dac_1 = adafruit_mcp4725.MCP4725(tca[5], address=0x60)
    #dac_2 = adafruit_mcp4725.MCP4725(tca[6], address=0x60)

    if data:
        now = datetime.now()
        current= now.strftime("%m_%d_%Y_%H_%M_%S")
        pfilename = "./data/" +"Pressure_sensor_data_" + current +".csv"

        #args = ["echo ","test ",">>",pfilename]
        #subprocess.run(["echo ","test ",">>",pfilename]) 

        #creating pressure sensor data csv with current date and time
        pfile = open(pfilename, "w")
        pwriter = csv.writer(pfile)
        pwriter.writerow(['0' , '1', '2', '3', 'current', 'voltage', 'power'])

    while not shutoff:
        while not q.empty():
            try:
                queueDump.append(q.get_nowait())
            except:
                pass
        for i in queueDump:
            if i[0] == 0:
                q.put_nowait((0,i[1])) #pressure sensor data
            if i[0] == 1:
                q.put_nowait((1,i[1])) #power sensor Data
            if i[0] == 2:
                powerLevel = i[1]  #power supply DAC
            if i[0] == 3:
                shutoff = i[1]  #shutoff command
                q.put_nowait((3,shutoff))

        #Collecting Data and Writing to lists
        pressureList = [mpr_0.pressure, mpr_1.pressure, mpr_2.pressure, mpr_3.pressure]
        powerList = [energy.current, energy.voltage, energy.power]

        #Writing data to the Queue
        q.put_nowait((0,pressureList))
        q.put_nowait((1,powerList))
        queueDump = [] #reseting the local queue list

        #Writing data to DACs
        ### *** add switching system to select current vs volt control
        #dac_1.normalized_value = powerLevel[1]

        if data:
            pwriter.writerow(pressureList) #writing data to csv

        
    
    #Shutoff Command recieved
    print("Mulit Closed")
    dac_1.normalized_value = 0 #Setting Dacs to Zero at Shutoff Command
    if data:
        pfile.close() #Closing CSV file
    q.close()
    q.join_thread()

