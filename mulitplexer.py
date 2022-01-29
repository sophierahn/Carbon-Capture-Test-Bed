import board
import adafruit_tca9548a
import adafruit_mprls


def muliplexer(q):
    queueDump = []
    #powerReceived = []
    pressure = [0]*4
    shutoff = False
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)
    mpr_1 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25)
    mpr_2 = adafruit_mprls.MPRLS(tca[1], psi_min=0, psi_max=25)

    while not shutoff:
        while not q.empty():
            try:
                queueDump.append(q.get_nowait())
            except:
                pass
        for i in queueDump:
            if i[0] == 0:
                q.put_nowait((0,i[1]))
            #if i[0] == 1:
            #    powerReceived.append(i[1])
            if i[0] == 2:
                shutoff = i[1]
                q.put_nowait((2,shutoff))
        pressure[0] = mpr_1.pressure
        pressure[1] = mpr_2.pressure
        q.put_nowait((0,pressure))
        queueDump = []
    
    print("Mulit Closed")
    #print("Power: ", powerReceived)
    q.close()

