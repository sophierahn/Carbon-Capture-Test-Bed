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
import func
import glob
import os
from datetime import datetime
from multiprocessing import Process, Pipe, Queue


def start_imageCapture(image_pipe,q):
    global xPos, yPos, area
    xPos = []
    yPos = []
    area = 0
    debug = False

    # initalize camera, set exposure and attempt to capture image
    camera = PiCamera()
    camera.brightness = 50
    camera.contrast = 60
    camera.iso = 800
    #shutoff = image_pipe.recv()

    print("Starting Camera Loop")
    shutoff = False
    queueDump = []

    while not shutoff:
        for i in queueDump:
            if i[0] == 0:
                shutoff = i[1]  #shutoff command
                q.put_nowait((0,shutoff))
            if i[0] == 1:
                q.put_nowait((1,i[1]))
            if i[0] == 2:
                q.put_nowait((2,i[1]))
            if i[0] == 3:
                q.put_nowait((3,i[1])) #pressure sensor data
        fileID = datetime.now().strftime("%Y%m%d-%H%M%S")
        fileName = "/home/pi/Carbon-Capture-Test-Bed/Raw_Images/%s_salt.jpg" %(fileID)
        try:
            camera.capture(fileName)
        except:
            print("Error: Camera Capture Failed")
        else:
            # Look at image folder, load most recent file
            # * means all if need specific format then *.csv
            list_of_files = glob.glob('/home/pi/Carbon-Capture-Test-Bed/Raw_Images/*.jpg')
            latest_file = max(list_of_files, key=os.path.getctime)
            image = cv2.imread(latest_file)
            h = image.shape[0]
            w = image.shape[1]

            if debug:
                print(h, w)

            # cropping Image
            image = image[round(h/2-400):round(h/2+900),round(w/2-600):round(w/2+600)]
            h = image.shape[0]
            w = image.shape[1]
            hSmall = round(h/2)
            wSmall = round(w/2)

            # convert it to grayscale, and blur it
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (11, 11), 0)

            if debug:
                threshSmall = cv2.resize(gray, (hSmall, wSmall))
                cv2.imshow("gray", threshSmall)
                cv2.waitKey(0)

            # threshold the image to reveal light regions in the
            # blurred image
            ####### change colour cut off to fine tune #####
            thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)[1]

            # perform a series of erosions and dilations to remove
            # any small blobs of noise from the thresholded image
            thresh = cv2.erode(thresh, None, iterations=2)
            thresh = cv2.dilate(thresh, None, iterations=4)

            if debug:
                threshSmall = cv2.resize(thresh, (hSmall, wSmall))
                cv2.imshow("2", threshSmall)
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
                #numPixels = cv2.countNonZero(labelMask)

                # if the number of pixels in the component is sufficiently
                # large, then add it to our mask of "large blobs"
                # if numPixels > 300:
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
                        scaleFactor = (math.sqrt(200)/2)/radius
                    else:
                        xPos.append(round(cX*scaleFactor, 4))
                        yPos.append(round(cY*scaleFactor, 4))
                        # newArea = math.pi*(scaleFactor*radius)**2
                        area += math.pi*(scaleFactor*radius)**2
                        # print(newArea)

                    # print("X:"+ str(cX) + " Y:" + str(cY) + " Radius:" + str(radius))
                    cv2.circle(image, (int(cX), int(cY)), int(radius),
                        (0, 0, 255), 3)
                    cv2.putText(image, "#{}".format(i + 1), (x, y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

                # show the output image
                if debug:
                    threshSmall = cv2.resize(image, (hSmall, wSmall))
                    cv2.imshow("Image", threshSmall)
                    cv2.waitKey(0)
                    print(area)

                fileID = datetime.now().strftime("%Y%m%d-%H%M%S")
                fileName = "/home/pi/Carbon-Capture-Test-Bed/Edited_Images/%s_identified.jpg" % (fileID)
                cv2.imwrite(fileName, image)
                image_pipe.send(area)
            else:
                #fileID = datetime.now().strftime("%Y%m%d-%H%M%S")
                #fileName = "/home/pi/Carbon-Capture-Test-Bed/Edited_Images/%s_identified.jpg" % (fileID)
                cv2.imwrite(fileName, gray)
                image_pipe.send(area)
            print("Image Completed")
            sleep(10)
            queueDump = []

    print("Image Closed")
    image_pipe.close()