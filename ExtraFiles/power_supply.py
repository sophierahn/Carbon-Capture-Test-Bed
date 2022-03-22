#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:        D2A.py
# Purpose:     PWM driver for an AtoD application
#
# Author:      paulv
#
# Created:     24-10-2015
# Copyright:   (c) paulv 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)    # set GPIO 25 as output for the PWM signal
D2A = GPIO.PWM(12, 1000)    # create object D2A for PWM on port 25 at 1KHz
D2A.start(0)                # start the PWM with a 0 percent duty cycle (off)

try:

    while True:
        dutycycleS = input('Enter a duty cycle percentage from 0-100 : ')
        dutycycle = int(dutycycleS)
        print("Duty Cycle is : {0}%".format(dutycycle))
        D2A.ChangeDutyCycle(dutycycle)
        sleep(5)

except (KeyboardInterrupt, ValueError, Exception) as e:
    print(e)
    D2A.stop()     # stop the PWM output
    GPIO.cleanup() # clean up GPIO on CTRL+C exit


def main():
    pass

if __name__ == '__main__':
    main()