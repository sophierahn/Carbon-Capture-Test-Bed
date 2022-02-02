import board
import adafruit_tca9548a
import adafruit_mprls
import adafruit_ina260


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
        pressure[0] = round(mpr_0.pressure,3)
        pressure[1] = round(mpr_1.pressure,3)
        pressure[2] = round(mpr_2.pressure,3)
        pressure[3] = round(mpr_3.pressure,3)
        powerList = [energy.current, energy.voltage, energy.power]
        q.put_nowait((0,pressure))
        q.put_nowait((1,powerList))
        queueDump = []
    
    print("Mulit Closed")
    #print("Power: ", powerReceived)
    q.close()

