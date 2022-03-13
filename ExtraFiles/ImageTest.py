import cv2
from picamera import PiCamera
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)
GPIO.output(17, GPIO.HIGH)
camera = PiCamera()
camera.resolution = (3280,2464)
print("Start Camera")
#camera.start_preview()
camera.brightness = 50
camera.contrast = 60
camera.iso = 800
#print(camera.exposure_time)
# for i in range(20,100):
#     camera.annotate_text = "Brightness: " +str(i)
#     camera.brightness = i
#     sleep(.5)
    
#camera.annotate_text = "10 seconds:"
#input("enter when finished")
sleep(1)
try:
    camera.capture("/home/pi/Carbon-Capture-Test-Bed/testnew2.jpg")
except:
    print("error")

image = cv2.imread("/home/pi/Carbon-Capture-Test-Bed/testnew2.jpg")
h = image.shape[0]
w = image.shape[1]
# image = image[round(h/2-400):round(h/2+900),round(w/2-600):round(w/2+600)]
# h = image.shape[0]
# w = image.shape[1]
hSmall = round(h/2)
wSmall = round(w/2)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)[1]

threshSmall = cv2.resize(thresh, (hSmall, wSmall))
cv2.imshow("gray", threshSmall)
cv2.waitKey(0)
#camera.stop_preview()
GPIO.output(17, GPIO.LOW)



#imageFile = "/home/pi/Desktop/image.jpg"
#image = cv2.imread(imageFile)
#cv2.imshow("1", image)
#cv2.waitKey(0)