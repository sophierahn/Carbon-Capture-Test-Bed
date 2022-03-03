#Pressure sensor logging fuction 

def power_log (power_pipe, q):
    shutoff = False
    queueDump = []
    power = [0]*3

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
                power = i[1]
                power_pipe.send(power) #power sensor Data
            if i[0] == 2:
                q.put_nowait((2,i[1]))
            if i[0] == 3:
                q.put_nowait((3,i[1])) #pressure sensor data
            if i[0] == 4:
                q.put_nowait((4,i[1])) #calibration status
        
        queueDump = []
        
    print("Power Closed")
    power_pipe.close()
