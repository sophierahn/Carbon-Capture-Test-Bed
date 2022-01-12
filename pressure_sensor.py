import time
import board
import adafruit_mprls
from multiprocessing import Process, Pipe, Queue

def start_psensor(psen_pipe):
    i2c = board.I2C()
    mpr = adafruit_mprls.MPRLS(i2c, psi_min=0, psi_max=25)
    shutoff = psen_pipe.recv()
    #print("The main loop told me shutoff is")
    #print(shutoff)
    while (not shutoff):
        pressure = mpr.pressure
        #print("The pressure sensor says")
        #print(pressure)
        psen_pipe.send(pressure)
    print("closing sensor end pipe")
    psen_pipe.close()
    #this close function isn't currently relevant bc i cant send
    #a shut off signal from the main code
    #hopefully we can adjust that to be the case

#def poll_psensor(i2c, mpr, p_pipe):
    #pressure = mpr.pressure
    #p_pipe.send(pressure)





#while True:
   #print((mpr.pressure,))
   #time.sleep(1)

