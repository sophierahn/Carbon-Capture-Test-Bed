#Pressure sensor logging fuction 

def start_psensor(psen_pipe, q):
    shutoff = False
    queueDump = []
    pressure = [0]*4

    while not shutoff:
        while not q.empty():
            try:
                queueDump.append(q.get_nowait())
            except:
                pass
        for i in queueDump:
            if i[0] == 0:
                shutoff = i[1]  #shutoff command
                q.put_nowait((0,shutoff))
            if i[0] == 1:
                q.put_nowait((1,i[1])) #power sensor Data
            if i[0] == 2:
                q.put_nowait((2,i[1]))
            if i[0] == 3:
                pressure = i[1]
                psen_pipe.send(pressure) #pressure sensor data
            if i[0] == 4:
                q.put_nowait((4,i[1])) #calibration status
        
        queueDump = []
    print("Pressure Closed")
    psen_pipe.close()


