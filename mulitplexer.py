import board
import adafruit_tca9548a
import adafruit_mprls
import adafruit_ina260
import adafruit_mcp4725
#import csv
#from datetime import datetime


def muliplexer(q):
    queueDump = []
    powerList = [0]*3
    pressure = [0]*4
    shutoff = False
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)
    mpr_0 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25)
    mpr_1 = adafruit_mprls.MPRLS(tca[1], psi_min=0, psi_max=25)
    mpr_2 = adafruit_mprls.MPRLS(tca[2], psi_min=0, psi_max=25)
    mpr_3 = adafruit_mprls.MPRLS(tca[3], psi_min=0, psi_max=25)
    energy = adafruit_ina260.INA260(tca[4])
    dac = adafruit_mcp4725.MCP4725(tca[5], address=0x60)

    #To be used with file indexing
    #now = datetime.now()
    #current= now.strftime("%m/%d/%Y, %H:%M:%S")

    #creating pressure sensor data csv with current date and time
    #pfilename = "path/to/folder/on/usb/flashdrive" +"Pressure_sensor_data " + current
    #pfile = open('%s.csv' %pfilename, 'w')
    #pwriter = csv.writer(pfile)
    #pwriter.writerow(' ', '0' , '1', '2', '3', 'current', 'voltage', 'power')


    while not shutoff:
        while not q.empty():
            try:
                queueDump.append(q.get_nowait())
            except:
                pass
        for i in queueDump:
            if i[0] == 0:
                q.put_nowait((0,i[1]))
            if i[0] == 1:
                q.put_nowait((1,i[1]))
            if i[0] == 2:
                shutoff = i[1]  
                q.put_nowait((2,shutoff))

        #Writing data to lists
        pressure[0] = mpr_0.pressure  
        pressure[1] = mpr_1.pressure
        pressure[2] = mpr_2.pressure
        pressure[3] = mpr_3.pressure
        powerList = [energy.current, energy.voltage, energy.power]

        #writing data to csvs
        #pwriter.writerow(pressure, powerList)

        q.put_nowait((0,pressure))
        q.put_nowait((1,powerList))
        queueDump = []
    

    print("Mulit Closed")
    #print("Power: ", powerReceived)

    #closing pressure sensor file
    #pfile.close()


    q.close()

