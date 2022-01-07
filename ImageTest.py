import cv2
from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.resolution = (2592, 1944)
print("Start Camera")
camera.start_preview()
camera.brightness = 40
camera.contrast = 50
#for i in range(0,80):
#    camera.annotate_text = "Brightness: " +str(i)
#    camera.contrast = i
#    sleep(.5)
    
#camera.annotate_text = "10 seconds:"
#input("enter when finished")
sleep(60)
try:
    camera.capture("/home/pi/Desktop/testnew.jpg")
except:
    print("error")

camera.stop_preview()




#imageFile = "/home/pi/Desktop/image.jpg"
#image = cv2.imread(imageFile)
#cv2.imshow("1", image)
#cv2.waitKey(0)