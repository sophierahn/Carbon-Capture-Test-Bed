#Pressure sensor logging fuction 

def start_psensor(psen_pipe, q):
    shutoff = False
    #dataCheck = []
    queueDump = []
    pressure = 11

    while not shutoff:
        while not q.empty():
            try:
                queueDump.append(q.get_nowait())
            except:
                pass
        for i in queueDump:
            if i[0] == 0:
                pressure = i[1]
                psen_pipe.send(pressure)
                #dataCheck.append(pressure)
            #if i[0] == 1:
            #   q.put_nowait((1,i[1]))
            if i[0] == 2:
                shutoff = i[1]
                q.put_nowait((2,shutoff))
        queueDump = []
    print("Pressure Closed")
    #print("Pressure:",dataCheck[-10:-1])
    psen_pipe.close()





# import time
# import board
# import adafruit_mprls
# from multiprocessing import Process, Pipe, Queue

# def start_psensor(psen_pipe):
#     i2c = board.I2C()
#     mpr = adafruit_mprls.MPRLS(i2c, psi_min=0, psi_max=25)
#     shutoff = psen_pipe.recv()
#     #print("The main loop told me shutoff is")
#     #print(shutoff)
#     while (not shutoff):
#         pressure = mpr.pressure
#         #print("The pressure sensor says")
#         #print(pressure)
#         psen_pipe.send(pressure)
#     print("closing sensor end pipe")
#     psen_pipe.close()
    #this close function isn't currently relevant bc i cant send
    #a shut off signal from the main code
    #hopefully we can adjust that to be the case

#def poll_psensor(i2c, mpr, p_pipe):
    #pressure = mpr.pressure
    #p_pipe.send(pressure)





#while True:
   #print((mpr.pressure,))
   #time.sleep(1)

