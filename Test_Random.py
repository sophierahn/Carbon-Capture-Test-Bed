
# #import bright_Spots_testing
# import func
# from imutils import contours
# from skimage import measure
# import numpy as np
# import argparse
# import imutils
# import cv2
# import math
# import glob
# import os

# debug = True

# # image = cv2.imread("/Users/bronwynerb/Carbon-Capture-Test-Bed/ExtraFiles/IMG_5103.jpg")
# # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# # blurred = cv2.GaussianBlur(gray, (11, 11), 0)

# # if debug:
# #     #threshSmall = cv2.resize(gray, (hSmall, wSmall))
# #     cv2.imshow("gray", blurred)
# #     cv2.waitKey(0)
# # thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]

# # # perform a series of erosions and dilations to remove
# # # any small blobs of noise from the thresholded image
# # thresh = cv2.erode(thresh, None, iterations=2)
# # thresh = cv2.dilate(thresh, None, iterations=4)

# # if debug:
# #     #threshSmall = cv2.resize(thresh, (hSmall, wSmall))
# #     cv2.imshow("2", thresh)
# #     cv2.waitKey(0)
# list_of_files = glob.glob('/Users/bronwynerb/Desktop/To Be Deleted/*')
# list_of_files.sort(key=os.path.getmtime)

# print(list_of_files[:-1], type(list_of_files))
# for file in list_of_files[:-1]:
#     os.remove(file)

from picamera import PiCamera
from time import sleep
from fractions import Fraction

# Force sensor mode 3 (the long exposure mode), set
# the framerate to 1/6fps, the shutter speed to 6s,
# and ISO to 800 (for maximum gain)
camera = PiCamera(
    resolution=(1280, 720),
    framerate=Fraction(1, 6),
    sensor_mode=3)
camera.shutter_speed = 6000000
camera.iso = 800
# Give the camera a good long time to set gains and
# measure AWB (you may wish to use fixed AWB instead)
sleep(30)
camera.exposure_mode = 'off'
# Finally, capture an image with a 6s exposure. Due
# to mode switching on the still port, this will take
# longer than 6 seconds
camera.capture('dark.jpg')
    
    

