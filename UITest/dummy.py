import numpy as np
import math
import time
from multiprocessing import Process, Pipe, Queue
import random

def fillarray(dum_pipe):
    dumdata = [0]
    x = 0
    while x < 1000:
        data = random.randint(0,9)
        dumdata.append(data)
        x = x + 1
    while x > 1:
        data2 = dumdata[x]
        #print(data2)
        dum_pipe.send(data2)
        time.sleep(0.1)
        x = x - 1


if __name__ == '__main__':
    fillarray()