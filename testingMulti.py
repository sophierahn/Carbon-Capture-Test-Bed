import board
import adafruit_tca9548a
import adafruit_mprls
import time

i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)
mpr_1 = adafruit_mprls.MPRLS(tca[1], psi_min=0, psi_max=25)

count = 10

while count > 0:
    pressure = mpr_1.pressure
    print (pressure)
    count -= 1
    time.sleep(1)

