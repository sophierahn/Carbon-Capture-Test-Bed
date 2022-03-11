import board
import adafruit_tca9548a
import adafruit_mprls
import time
import RPi.GPIO as GPIO
import adafruit_ina260
import adafruit_mcp4725
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import func
from adafruit_ads1x15.analog_in import AnalogIn

pressure = [0]*4
electricity = [0]*3

i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)
mpr_0 = adafruit_mprls.MPRLS(tca[5], psi_min=0, psi_max=25)
mpr_1 = adafruit_mprls.MPRLS(tca[6], psi_min=0, psi_max=25)
mpr_2 = adafruit_mprls.MPRLS(tca[7], psi_min=0, psi_max=25)
mpr_3 = adafruit_mprls.MPRLS(tca[0], psi_min=0, psi_max=25)
#energy = adafruit_ina260.INA260(tca[3])
dac = adafruit_mcp4725.MCP4725(tca[2], address=0x60)
#adc = ADS.ADS1015(tca[1])
#chanADC = AnalogIn(adc, ADS.P0)



#GPIO.setmode(GPIO.BCM)


# Create single-ended input on channel 0
#chan = AnalogIn(adc, ADS.P0)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)




#pump
#GPIO.setup(22,GPIO.OUT)

#DAC
#GPIO.setup(17,GPIO.OUT)

# print(func.loadTestPresets())
# func.saveTestPreset([0,2,3,4])
# print(func.loadTestPresets())
#count = 0
#while count <= 10:

    #GPIO.output(22, GPIO.HIGH)
    #pressure[0] = round(mpr_1.pressure,3)
    #pressure[1] = round(mpr_3.pressure,3)
    #pressure[2] = round(mpr_2.pressure,3)
#    pressure[3] = round(mpr_3.pressure,3)
    #print (pressure)
    #time.sleep(2)
    #print(chanADC.value, chanADC.voltage)
    #GPIO.output(22, GPIO.LOW)
    #count = count +1
    #r = 1
    #setValue = 1748
    #aim = 1.4
#now = time.time()
#value = func.calibration()
#print(value, now, now-time.time())
powerValue = 0
print("Starting")
#print("{:>5}\t{:>5}".format('raw', 'v'))
while powerValue <= 10:

    #powerNormValue = powerValue*5/32.2/3.28
    #dac.raw_value = 3877
    #time.sleep(1)
    #elec = [energy.current, energy.voltage, energy.power]
    #print(elec[1])
    #dac.normalized_value = powerValue
    

    #print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
    powerNormValue = (powerValue*0.0386) + 0.0797
    dac.normalized_value = powerNormValue
    pressure[0] = round(mpr_1.pressure,3)
    pressure[1] = round(mpr_1.pressure,3)
    pressure[2] = round(mpr_2.pressure,3)
    pressure[3] = round(mpr_3.pressure,3)
    print (pressure)
    print(func.calibration())
    time.sleep(1)


    #gasRB = chanADC.voltage
    #print(gasRB)
    #GPIO.output(17, GPIO.HIGH)
    #x = input()
    #r = elec[1]/aim
    #print (r)
    #time.sleep(1)
    #elec = [energy.current, energy.voltage, energy.power]
    #print(elec[1], elec[0], elec[2])
    #GPIO.output(17, GPIO.LOW)
    #x = input()
    #time.sleep(3)
    powerValue +=1
    #count -= 1

dac.normalized_value = 0
#dac.raw_value = 0
 

#GPIO.output(17, GPIO.LOW) 


  

