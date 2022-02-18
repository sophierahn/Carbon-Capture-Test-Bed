import board
import adafruit_tca9548a
import adafruit_mprls
import time
import RPi.GPIO as GPIO
import adafruit_ina260
import adafruit_mcp4725

pressure = [0]*4
electricity = [0]*3


i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)
mpr_0 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25)
mpr_1 = adafruit_mprls.MPRLS(tca[1], psi_min=0, psi_max=25)
mpr_2 = adafruit_mprls.MPRLS(tca[2], psi_min=0, psi_max=25)
mpr_3 = adafruit_mprls.MPRLS(tca[3], psi_min=0, psi_max=25)
energy = adafruit_ina260.INA260(tca[4])
dac = adafruit_mcp4725.MCP4725(tca[5], address=0x60)



count = 10

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)

while count <= 10:
    #GPIO.output(17, GPIO.HIGH)
#     pressure[0] = round(mpr_0.pressure,3)
#     pressure[1] = round(mpr_1.pressure,3)
#     pressure[2] = round(mpr_2.pressure,3)
#     pressure[3] = round(mpr_3.pressure,3)
#     print (pressure)
    #r = 1
    #setValue = 1748
    #aim = 1.4

#while r > 1.01 or r < 0.99:
    #dac.raw_value = 3877
    #time.sleep(1)
    #elec = [energy.current, energy.voltage, energy.power]
    #print(elec[1])
    #dac.normalized_value = 0.946826238
    #GPIO.output(17, GPIO.HIGH)
    #x = input()
    #r = elec[1]/aim
    #print (r)
    #time.sleep(4)
    #elec = [energy.current, energy.voltage, energy.power]
    #print(elec[1])
    GPIO.output(17, GPIO.LOW)
    #x = input()
    # time.sleep(1)
    count += 1

#dac.normalized_value = 0
dac.raw_value = 0
 

#GPIO.output(17, GPIO.LOW) 


  

