import random
from time import sleep

def pressureStore(psen_pipe,q):
    shutoff = False
    dataCheck = []
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
                dataCheck.append(pressure)
            if i[0] == 1:
                q.put_nowait((1,i[1]))
            if i[0] == 2:
                shutoff = i[1]
                q.put_nowait((2,shutoff))
        queueDump = []
    print("Pressure Closed")
    print("Pressure:",dataCheck[-10:-1])
    psen_pipe.close()
           