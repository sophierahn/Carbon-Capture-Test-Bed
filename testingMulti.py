import board
import adafruit_tca9548a
import adafruit_mprls
import time
import RPi.GPIO as GPIO
import adafruit_ina260
import adafruit_mcp4725
import func

pressure = [0]*4
electricity = [0]*3


i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)
#mpr_0 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25)
mpr_1 = adafruit_mprls.MPRLS(tca[1], psi_min=0, psi_max=25)
#mpr_2 = adafruit_mprls.MPRLS(tca[2], psi_min=0, psi_max=25)
mpr_3 = adafruit_mprls.MPRLS(tca[3], psi_min=0, psi_max=25)
#energy = adafruit_ina260.INA260(tca[4])
dac = adafruit_mcp4725.MCP4725(tca[5], address=0x60)



GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)

print(func.loadTestPresets())
func.saveTestPreset([0,2,3,4])
print(func.loadTestPresets())
#while count <= 10:
    #GPIO.output(17, GPIO.HIGH)
#     pressure[0] = round(mpr_0.pressure,3)
#     pressure[1] = round(mpr_1.pressure,3)
#     pressure[2] = round(mpr_2.pressure,3)
#     pressure[3] = round(mpr_3.pressure,3)
#     print (pressure)
    #r = 1
    #setValue = 1748
    #aim = 1.4
powerValue = 0
print("Starting")
while powerValue <= 10:

    #powerNormValue = powerValue*5/32.2/3.28
    #dac.raw_value = 3877
    #time.sleep(1)
    #elec = [energy.current, energy.voltage, energy.power]
    #print(elec[1])
    powerNormValue = (powerValue*0.0386) + 0.0797
    print(powerValue, powerNormValue)
    dac.normalized_value = powerNormValue
    #GPIO.output(17, GPIO.HIGH)
    #x = input()
    #r = elec[1]/aim
    #print (r)
    #time.sleep(4)
    #elec = [energy.current, energy.voltage, energy.power]
    #print(elec[1], elec[0], elec[2])
    #GPIO.output(17, GPIO.LOW)
    #x = input()
    time.sleep(3)
    powerValue +=1
    #count -= 1

dac.normalized_value = 0
#dac.raw_value = 0
 

#GPIO.output(17, GPIO.LOW) 


  

