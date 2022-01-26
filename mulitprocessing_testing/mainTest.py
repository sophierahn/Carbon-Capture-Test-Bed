#Testing
from multiprocessing import Process, Pipe, Queue
#import Queue
from time import sleep
from mulitplexer_test import muliplexer
from pressure_test import pressureStore


powerLevel = [20,30,40,50,60,70,80,90,100,110,120,130,140,150]
index = 0
count = 10

#Multiplexer
q = Queue()
multi = Process(target= muliplexer, args= (q,))
multi.start()

#Power Supply
psen_pipe, mainp_pipe = Pipe()
psen_script = Process(target= pressureStore, args= (psen_pipe,q))
psen_script.start()  

pressure = 22

while count > 0:
    while mainp_pipe.poll():
        pressure = mainp_pipe.recv()
    print("pressure =", pressure)
    q.put_nowait((1,powerLevel[index]))

    if pressure%5 == 0:
        q.put_nowait((2,True))
        sleep(1)
        multi.terminate()
        psen_script.terminate()
        break

    index += 1
    count -= 1
    sleep(1)

q.put_nowait((2,True))
sleep(1)
multi.terminate()
psen_script.terminate()










