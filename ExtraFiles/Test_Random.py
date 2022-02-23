#Test.py
import time

start = time.time()
count = 10
while count > 0:
    time.sleep(0.5)
    end = time.time()
    print(end - start)
    count -= 1