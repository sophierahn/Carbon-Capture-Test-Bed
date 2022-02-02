#Pressure sensor logging fuction 

def power_log (power_pipe, q):
    shutoff = False
    #dataCheck = []
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
                q.put_nowait((0,i[1]))
            if i[0] == 1:
                power = i[1]
                power_pipe.send(power)
            if i[0] == 2:
                shutoff = i[1]
                q.put_nowait((2,shutoff))
        queueDump = []
    print("Power Closed")
    #print("Pressure:",dataCheck[-10:-1])
    power_pipe.close()
