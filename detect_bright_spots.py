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


global xPos, yPos, area
xPos = []
yPos = []
area = 0

# construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True,
# 	help="path to the image file")
# args = vars(ap.parse_args())


# load the image, convert it to grayscale, and blur it
image = cv2.imread("/home/pi/Desktop/testnew.jpg")
h = image.shape[0]
w = image.shape[1]
print(h, w)
#cropping Image
image = image[round(h/2-400):round(h/2+900), round(w/2-600):round(w/2+600)]
h = image.shape[0]
w = image.shape[1]
hSmall = round(h/2)
wSmall = round(w/2)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (11, 11), 0)
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

threshSmall = cv2.resize(thresh, (hSmall, wSmall))
cv2.imshow("2", threshSmall)
cv2.waitKey(0)

# perform a connected component analysis on the thresholded
# image, then initialize a mask to store only the "large"
# components neighbors=8,
labels = measure.label(thresh, background=0)
mask = np.zeros(thresh.shape, dtype="uint8")
print(image.shape[0], image.shape[1])
# loop over the unique components
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
	#if numPixels > 300:
	mask = cv2.add(mask, labelMask)

# find the contours in the mask, then sort them from left to
# right
cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
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
		xPos.append(round(cX*scaleFactor,4))
		yPos.append(round(cY*scaleFactor,4))
		#newArea = math.pi*(scaleFactor*radius)**2
		area += math.pi*(scaleFactor*radius)**2
		#print(newArea)

	#print("X:"+ str(cX) + " Y:" + str(cY) + " Radius:" + str(radius))
	cv2.circle(image, (int(cX), int(cY)), int(radius),
		(0, 0, 255), 3)
	cv2.putText(image, "#{}".format(i + 1), (x, y - 15),
		cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

# show the output image
threshSmall = cv2.resize(image, (hSmall, wSmall))
cv2.imshow("Image", threshSmall)
print (area)
#print (xPos)
cv2.imwrite("Test_image.jpg", image)
cv2.waitKey(0)