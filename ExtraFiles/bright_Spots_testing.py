# USAGE
# python detect_bright_spots.py --image images/lights_01.png

# import the necessary packages
from imutils import contours
from skimage import measure
import numpy as np
import argparse
import imutils
import cv2
import math
from picamera import PiCamera
from time import sleep
#import func
import glob
import os
from datetime import datetime
from multiprocessing import Process, Pipe, Queue
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)
GPIO.output(17, GPIO.HIGH)

global xPos, yPos, area
xPos = []
yPos = []
area = 0
debug = True

# initalize camera, set exposure and attempt to capture image
camera = PiCamera()
camera.resolution = (3280,2464)
camera.rotation = 180
camera.brightness = 40
camera.contrast = 80
camera.iso = 300
#shutoff = image_pipe.recv()
time.sleep(2)
print("Starting Camera Loop")
shutoff = False
queueDump = []


    
#fileID = datetime.now().strftime("%Y%m%d-%H%M%S")
fileName = "/home/pi/Carbon-Capture-Test-Bed/testnew2.jpg"
try:
    camera.capture("/home/pi/Carbon-Capture-Test-Bed/testnew2.jpg")
except:
    print("Error: Camera Capture Failed")
else:
    # Look at image folder, load most recent file
    # * means all if need specific format then *.csv
    #list_of_files = glob.glob('/home/pi/Carbon-Capture-Test-Bed/Raw_Images/*.jpg')
    #latest_file = max(list_of_files, key=os.path.getctime)
    image = cv2.imread("/home/pi/Carbon-Capture-Test-Bed/testnew2.jpg")
    h = image.shape[0]
    w = image.shape[1]

    if debug:
        print(h, w)
        

    # cropping Image
    image = image[round(h/2-600):round(h/2+400),round(w/2-500):round(w/2+500)]
    h = image.shape[0]
    w = image.shape[1]
    hSmall = round(h/2)
    wSmall = round(w/2)
    imageSmall = cv2.resize(image, (hSmall, wSmall))
    print(imageSmall.shape[:2])


    pts = np.array([[0,400], [260, 260], [400, 0], 
                    [1000, 0], [1000, 600], [670, 720],
                    [550, 1000], [0, 1000]],
                np.int32)
    pts = pts.reshape((-1, 1, 2))
    mask = np.zeros(image.shape[:2], dtype="uint8")
    cv2.fillPoly(mask, [pts], 255)
    masked = cv2.bitwise_and(image, image, mask=mask)
 


    # convert it to grayscale, and blur it
    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)

    if debug:
        threshSmall = cv2.resize(gray, (hSmall, wSmall))
        imageSmall = cv2.resize(image, (hSmall, wSmall))
        cv2.imshow("image", imageSmall)
        cv2.waitKey(0)
        cv2.imshow("gray", threshSmall)
        cv2.imwrite("grayscale.jpg", gray)
        cv2.imwrite("blankImage.jpg", image)
        cv2.waitKey(0)
        

    # threshold the image to reveal light regions in the
    # blurred image
    ####### change colour cut off to fine tune #####
    thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)[1]

    # perform a series of erosions and dilations to remove
    # any small blobs of noise from the thresholded image
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=4)

    if debug:
        threshSmall = cv2.resize(thresh, (hSmall, wSmall))
        cv2.imshow("2", threshSmall)
        cv2.imwrite("threshhold.jpg", thresh)
        cv2.waitKey(0)

    # perform a connected component analysis on the thresholded
    # image, then initialize a mask to store only the "large"
    # components neighbors=8,
    labels = measure.label(thresh, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")
    # print(image.shape[0], image.shape[1])
    # loop over the unique components
    count = 0
    for label in np.unique(labels):
        # if this is the background label, ignore it
        if label == 0:
            continue

        # otherwise, construct the label mask and count the
        # number of pixels
        labelMask = np.zeros(thresh.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)

        # if the number of pixels in the component is sufficiently
        # large, then add it to our mask of "large blobs"
        if numPixels > 100:
            mask = cv2.add(mask, labelMask)
            count += 1
    #print(count)

    # find the contours in the mask, then sort them from left to
    # right
    area = 0
    if count != 0:
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = contours.sort_contours(cnts)[0]

        # loop over the contours
        for (i, c) in enumerate(cnts):
            # draw the bright spot on the image
            (x, y, w, h) = cv2.boundingRect(c)
            ((cX, cY), radius) = cv2.minEnclosingCircle(c)
            if i == 0:
                scaleFactor = 0.024035
            else:
                xPos.append(round(cX*scaleFactor, 4))
                yPos.append(round(cY*scaleFactor, 4))
                # newArea = math.pi*(scaleFactor*radius)**2
                area += math.pi*(scaleFactor*radius)**2
                # print(newArea)
            
            #gray_2 = cv2.cvtColor(image, cv2.COLO)
            # print("X:"+ str(cX) + " Y:" + str(cY) + " Radius:" + str(radius))
            cv2.circle(masked, (int(cX), int(cY)), int(radius),
                (255, 0, 0), 5)
            cv2.putText(masked, "#{}".format(i + 1), (x, y - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

        # show the output image
        if debug:
            threshSmall = cv2.resize(masked, (hSmall, wSmall))
            cv2.imshow("Image", threshSmall)
            cv2.waitKey(0)
            print(area)

        fileID = datetime.now().strftime("%H%M%S")
        fileName = "/home/pi/Carbon-Capture-Test-Bed/Images_Edited/%s_Testing.jpg" % (fileID)
        cv2.imwrite("final.jpg", masked)
        
    else:
        #fileID = datetime.now().strftime("%Y%m%d-%H%M%S")
        #fileName = "/home/pi/Carbon-Capture-Test-Bed/Edited_Images/%s_identified.jpg" % (fileID)
        cv2.imwrite(fileName, gray)
        
    print("Image Completed")
    #sleep(10)
    shutoff = True
    queueDump = []
    GPIO.output(17, GPIO.LOW)

    print("Image Closed")

    
    