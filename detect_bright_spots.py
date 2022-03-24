# USAGE
# python detect_bright_spots.py --image images/lights_01.png

# import the necessary packages
from xmlrpc.client import Boolean
from imutils import contours
from skimage import measure
import numpy as np
import argparse
import imutils
import cv2
import math

#from sympy import true
from picamera import PiCamera
import time 
import func
import glob
import os
from datetime import datetime
from multiprocessing import Process, Pipe, Queue
import csv
from datetime import datetime


def start_imageCapture(image_pipe,scaleFactor):
    global xPos, yPos, area, radiusList
    xPos = []
    yPos = []
    radiusList = []
    area = 0
    debug = False

    # initalize camera, set exposure and attempt to capture image
    camera = PiCamera()
    camera.resolution = (3280,2464)
    camera.brightness = 40
    camera.contrast = 80
    camera.iso = 700
    time.sleep(2)
    #shutoff = image_pipe.recv()

    print("Starting Camera Loop")
    shutoff = False
    queueDump = []
    data = True

    if data:
        now = datetime.now()
        current= now.strftime("%m_%d_%Y_%H_%M_%S")
        pfilename1 = "./data/" +"Image_Data" + current +".csv"
        pfile1 = open(pfilename1, "w") #creating Image data csv with current date and time
        pwriter1 = csv.writer(pfile1)
        pwriter1.writerow(['Time' , 'Cumulative Area', '# of Detected Areas'])

        pfilename2 = "./data/" +"X_Y_Data" + current +".csv"
        pfile2 = open(pfilename2, "w") #creating Image data csv with current date and time
        pwriter2 = csv.writer(pfile2)
        now = time.time()
        

    while not shutoff:
        pipeContents = []

        while image_pipe.poll(): #Empty pipe 
                pipeContents.append(image_pipe.recv())

        for i in pipeContents:
            if type(i) == float:
                image_pipe.send(i)
            if type(i) == str:
                runStatus = i

        if runStatus == "run":
            fileID = datetime.now().strftime("%Y%m%d-%H%M%S")
            fileName = "/home/pi/Carbon-Capture-Test-Bed/Images_Raw/%s_salt.jpg" %(fileID)
            try:
                camera.capture(fileName)
            except:
                print("Error: Camera Capture Failed")
            else:
                # Look at image folder, load most recent file
                # * means all if need specific format then *.csv
                list_of_files = glob.glob('/home/pi/Carbon-Capture-Test-Bed/Images_Raw/*.jpg')
                elapsed = time.time()-now
                pwriter2.writerow([elapsed , 'X Postion', 'Y Postion', 'Radius'])
                latest_file = max(list_of_files, key=os.path.getctime)
                image = cv2.imread(latest_file)
                h = image.shape[0]
                w = image.shape[1]

                if debug:
                    print(h, w)

                # cropping Image
                image = image[round(h/2-400):round(h/2+600),round(w/2-500):round(w/2+500)]
                h = image.shape[0]
                w = image.shape[1]
                hSmall = round(h/2)
                wSmall = round(w/2)

                #Masking the connectors out of the image
                pts = np.array([[0,400], [240, 240], [400, 0], # *** points of the polygon, may need to fine tune 
                                [1000, 0], [1000, 600], [730, 750],
                                [600, 1000], [0, 1000]],
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
                    cv2.imshow("gray", threshSmall)
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
                    cv2.waitKey(0)

                # perform a connected component analysis on the thresholded image, then initialize a mask to store only the "large"
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

                    # otherwise, construct the label mask and count the number of pixels
                    labelMask = np.zeros(thresh.shape, dtype="uint8")
                    labelMask[labels == label] = 255
                    #numPixels = cv2.countNonZero(labelMask)

                    # (Not used) if the number of pixels in the component is sufficiently large, then add it to our mask of "large blobs"
                    # if numPixels > 300:
                    mask = cv2.add(mask, labelMask)
                    count += 1
                #print(count)

                # find the contours in the mask, then sort them from left to right
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
                        
                        #saving the x and y position, adding to the total error 
                        xPos.append(round(cX*scaleFactor, 4))
                        yPos.append(round(cY*scaleFactor, 4))
                        radiusList.append(round(radius*scaleFactor, 4))
                        area += math.pi*(scaleFactor*radius)**2
                        pwriter2.writerow(['' , xPos, yPos, radius])
                        
                        cv2.circle(image, (int(cX), int(cY)), int(radius),(0, 255, 0), 4)
                        cv2.putText(image, "#{}".format(i + 1), (x, y - 15),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

                    # show the output image
                    if debug:
                        threshSmall = cv2.resize(image, (hSmall, wSmall))
                        cv2.imshow("Image", threshSmall)
                        cv2.waitKey(0)
                        print(area)

                    fileID = datetime.now().strftime("%Y%m%d-%H%M%S")
                    fileName = "/home/pi/Carbon-Capture-Test-Bed/Images_Edited/%s_identified.jpg" % (fileID)
                    imageSmall = cv2.resize(image, (hSmall, wSmall),interpolation=cv2.INTER_AREA)
                    cv2.imwrite(fileName, imageSmall)
                    image_pipe.send(area)
                else:
                    image_pipe.send(area)

                #print("Image Completed")
                runStatus = "wait"
                pwriter2.writerow([''])
                if data:
                    datalist = [time.time(),area, count]
                    pwriter1.writerow(datalist) #writing data to csv
                    
               
        if runStatus == "stop":
            print("closing")
            shutoff = True
    
    print("Image Closed")
    image_pipe.close()