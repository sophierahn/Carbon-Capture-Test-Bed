#!/usr/bin/python3

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
import func


def imageScaleCalibration():
    global xPos, yPos, area
    xPos = []
    yPos = []
    area = 0
    debug = True

    # Turn on LEDs
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(17,GPIO.OUT)
    GPIO.output(17, GPIO.HIGH)

    # Initalize camera, set exposure and attempt to capture image
    camera = PiCamera()
    camera.resolution = (3280,2464)
    camera.rotation = 180
    camera.brightness = 40
    camera.contrast = 80
    camera.iso = 300
    time.sleep(2)
    
    fileName = "/home/pi/Carbon-Capture-Test-Bed/ExtraFiles/CalibrationImage.jpg"
    try:
        camera.capture(fileName)
    except:
        print("Error: Camera Capture Failed")
        func.message("Error","Camera Capture Failed")
    else:
        image = cv2.imread(fileName)
        h = image.shape[0]
        w = image.shape[1]
            
        # Cropping Image
        image = image[round(h/2-600):round(h/2+400),round(w/2-500):round(w/2+500)]
        h = image.shape[0]
        w = image.shape[1]
        hSmall = round(h/2)
        wSmall = round(w/2)

        # Apply a mask to cut off connectors in the corners
        pts = np.array([[0,400], [250, 240], [400, 0], 
                        [1000, 0], [1000, 600], [730, 750],
                        [600, 1000], [0, 1000]],
                    np.int32)
        pts = pts.reshape((-1, 1, 2))
        mask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.fillPoly(mask, [pts], 255)
        masked = cv2.bitwise_and(image, image, mask=mask)

        # convert it to grayscale
        gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
        
####### change colour cut off to fine tune ###### threshold the image to reveal light regions in the
        thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)[1]
###### Fine Tune Here #####

        # perform a series of erosions and dilations to remove
        # any small blobs of noise from the thresholded image
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=4)

        # perform a connected component analysis on the thresholded
        # image, then initialize a mask to store only the "large"
        # components neighbors=8,
        labels = measure.label(thresh, background=0)
        mask = np.zeros(thresh.shape, dtype="uint8")
        # loop over the unique components
        count = 0
        for label in np.unique(labels):
            # if this is the background label, ignore it
            if label == 0:
                continue

            # otherwise, construct the label mask and count the number of pixels
            labelMask = np.zeros(thresh.shape, dtype="uint8")
            labelMask[labels == label] = 255
            numPixels = cv2.countNonZero(labelMask)

            # Only looking for one very large blog, the calibration block in the center
            if numPixels > 1000:
                mask = cv2.add(mask, labelMask)
                count += 1

        # find the contours in the mask, then sort them from left to right
        area = 0
        if count != 0:
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            cnts = contours.sort_contours(cnts)[0]

            # loop over the contours
            for (i, c) in enumerate(cnts):
                # draw the Circle around the bright spots on the image
                (x, y, w, h) = cv2.boundingRect(c)
                ((cX, cY), radius) = cv2.minEnclosingCircle(c)
                if i == 0:
                    scaleFactor = (math.sqrt(200)/2)/radius
                    print("Scale: ",scaleFactor)
                #Circle    
                cv2.circle(image, (int(cX), int(cY)), int(radius),(255, 0, 0), 5)
                #Text
                cv2.putText(image, "#{}".format(i + 1), (x, y - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

            # show the output image
            if debug:
                finalSmall = cv2.resize(image, (hSmall, wSmall))
                threshSmall = cv2.resize(thresh, (hSmall, wSmall))
                imageSmall = cv2.resize(image, (hSmall, wSmall))
                cv2.imshow("Image", imageSmall)
                cv2.imshow("Thresholded", threshSmall)
                cv2.imshow("Identified", finalSmall)
                cv2.waitKey(0)
        
            fileName = "/home/pi/Carbon-Capture-Test-Bed/ExtraFiles/CalibrationImage_Identified.jpg"
            cv2.imwrite(fileName, image)
            
        else:
            print("No Contour Found")
            func.message("Error","Calibration Block Not Found")
            
        print("Calibration Completed")
        GPIO.output(17, GPIO.LOW)
        return(scaleFactor)



    
    