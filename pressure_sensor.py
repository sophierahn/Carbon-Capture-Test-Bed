import time
#from adafruit_blinka.board.dragonboard_410c import I2C0_SCL
import board
import adafruit_mprls
import spidev
#from busio import I2C

i2c = board.I2C()

# Simplest use, connect to default over I2C
mpr = adafruit_mprls.MPRLS(i2c, psi_min=0, psi_max=25)

while True:
   print((mpr.pressure,))
   time.sleep(1)

# spi = spidev.SpiDev()
# spi.open(0,0)
# spi.max_speed_hz = 400000
# to_send = [0xAA, 0x00, 0x00]
# spi.xfer(to_send)
# print(spi.readbytes(8))
# to_send = [0xF0, 0x00, 0x00, 0x00]
# spi.xfer(to_send)
# time.sleep(2)
# print(spi.readbytes(24))