import random
from time import sleep


def muliplexer(q):
    queueDump = []
    powerReceived = []
    shutoff = False
    while not shutoff:
        #print("mulit:",q.empty())
        while not q.empty():
            try:
                queueDump.append(q.get_nowait())
            except:
                pass
        for i in queueDump:
            if i[0] == 0:
                q.put_nowait((0,i[1]))
            if i[0] == 1:
                powerReceived.append(i[1])
            if i[0] == 2:
                shutoff = i[1]
                #print("Mulit Shutting off")
                q.put_nowait((2,shutoff))
        pressure = random.randint(800,900)
        q.put_nowait((0,pressure))
        queueDump = []
        #sleep(.1)
    
    print("Mulit Closed")
    print("Power: ", powerReceived)
    q.close()

