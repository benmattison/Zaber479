# USAGE
# python object_movement.py --video object_tracking_example.mp4
# python object_movement.py

# import the necessary packages
from collections import deque
import numpy as np
import cv2


# Maximum horizontal angle of the camera frame of view.
th_max = 22.5
# camera separation distance (mm)
d_sep = 60

# an assortment of upper and lower bounds for the different colors we use in HSV.
greenLower = (45, 86, 30)
greenUpper = (80, 255, 255)
pinkLower = (140, 50, 180)
pinkUpper = (170, 255, 255)
blueLower = (115,100,70)
blueUpper = (125,255,255)
# Choose the ones you want to use.
lower = pinkLower
upper = pinkUpper

# the minimum radius of a blob to detect it.
minRad = 5

# initialized these variables so that we can print them no matter what
((x, y), radius) = ((0,0),0)

# if we have uniform camera settings the color matching should work better
# we should also explore some of the other .set options like hue.
exposure = -6
fps = 5
# grab the reference to the webcams
Lcam = cv2.VideoCapture(1)
Rcam = cv2.VideoCapture(2)
for camera in [Lcam, Rcam]:
	camera.set(15,exposure)
	camera.set(5,fps)

# Keeps track of the last 10 points for averaging.
lastPoints = np.zeros((10,2,3),dtype=np.float)
lastPointsInd = 0 # index to iterate through


L = True # First we will look at the left camera.

# Initialize some variables, ignore this until later.
th = [1,1]
(zreal,xreal,yreal) = (0.0,0.0,0.0)
pathPoints = []
breakloop = False

def rescale(image, ratio): # Resize an image using linear interpolation
	dim = (int(image.shape[1] * ratio), int(image.shape[0] * ratio))
	rescaled = cv2.resize(image, dim, interpolation = cv2.INTER_LINEAR)
	return rescaled

def filterColor(image, lowerHSV, upperHSV): # Filter out a certain set of colors from an image
	# # resize the frame, blur it, and convert it to the HSV
	# # color space
	blurred = cv2.GaussianBlur(image, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, lowerHSV, upperHSV)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	return mask, hsv



# keep recording indefiniely
while True:
	# Switch between cameras
	for camera in [Lcam, Rcam]:
		# Switching between cameras, easy to label image outputs.
		if L:
			camSide = 'L'
		else:
			camSide = 'R'

		# grab the current frame
		(grabbed, frame) = camera.read()
		
		# Going to scale up by this ratio for better analysis
		scaleR = 4
		# Perform the actual resizing of the image using bilinear interpolation
		frame_orig = frame
		frame = rescale(frame_orig, scaleR)

		(mask, hsv) = filterColor(frame,lower,upper)

		cv2.imshow('mask'+camSide, rescale(mask,1.0/scaleR))

		# find contours in the mask and initialize the current
		# (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
		center = None

		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

			# only proceed if the radius meets a minimum size
			if radius > minRad:
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				cv2.circle(frame, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(frame, center, 5, (0, 0, 255), -1)

		# THIS NEEDS TO BE CALIBRATED BETTER
		# C = observed radius (pixels) * actual distance (mm)
		# TODO: Find this by accurate measurement.
		C = 52000
		# This is a rough distance estimate from radius. We can do better with stereo and compare to this.
		if radius>0:
			dist_r = C/radius
		else: 
			dist_r = 0

		# make x and y relative to origin (center)
		(xframe,yframe) = (int(x),int(y))
		(x,y) = (x-frame.shape[1]/2,y-frame.shape[0]/2)

		lastPoints[lastPointsInd,int(L)] = [x,y,radius]

		averages = lastPoints.mean(axis=0)
		(xav,yav,radav) = averages[int(L)]
		avxav = np.mean(averages[:,0])

		# maximum horixontal pixels
		w_max = frame.shape[1]/2
		# maximum vertical pixels
		h_max = frame.shape[0]/2

		th[L] = xav/w_max*th_max

		triangle = (90-th[1], 90+th[0], th[1]-th[0])

		# a is the distance from the left camera
		a = np.sin(np.deg2rad(triangle[0]))*d_sep/np.sin(np.deg2rad(triangle[2]))
		# b is the distance from the right camera
		b = np.sin(np.deg2rad(triangle[1]))*d_sep/np.sin(np.deg2rad(triangle[2]))

		dist_stereo = b*np.sin(np.deg2rad(triangle[0]))

		if not L:
			zreal = dist_stereo*np.cos(np.deg2rad(np.mean(th)))
			xreal = dist_stereo*np.sin(np.deg2rad(np.mean(th)))
			yreal = -xreal*yav/avxav

		# Scale down the frame again for displaying.
		frame = rescale(frame,1.0/scaleR)

		cv2.putText(frame, "d_r: {}, d_stereo: {:4.2f}, (x, y, z): ({},{},{})".format(int(dist_r),
			dist_stereo,int(xreal),int(yreal),int(zreal)),
			(10, 20), cv2.FONT_HERSHEY_SIMPLEX,
			0.65, (0, 0, 255), 2)

		cv2.putText(frame, "X: {}, Y: {}, dia: {}".format(int(xav), int(yav), int(2*radav)),
			(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
			0.65, (0, 0, 255), 2)

		# show the frame to our screen and increment the frame counter
		cv2.imshow("Frame"+camSide, frame)

		# Switching between cameras, easy to label image outputs.
		if L:
			L = False
		else:
			L = True
			# Iterate through the history.
			lastPointsInd = lastPointsInd+1;
			if lastPointsInd==lastPoints.shape[0]:
				lastPointsInd = 0

		key = cv2.waitKey(2)
		# if the 'c' key is pressed, display the hsv values at the center of the ball
		if key == ord("c"):
			# print(hsv.shape[0],hsv.shape[1])
			# print(xframe,yframe)
			print hsv[yframe,xframe,:]
			print hsv[yframe+10,xframe+10,:]
			print hsv[yframe-10,xframe-10,:]
		# take coordinates if 'p' is pressed
		if key == ord("p"):
			if not pathPoints:
				pathPoints = [[xreal,yreal,zreal]]
				print pathPoints
			else:
				pathPoints.append([xreal,yreal,zreal])
				path = np.array(pathPoints[len(pathPoints)-1])-np.array(pathPoints[len(pathPoints)-2])
				print path

		# if the 'q' key is pressed, stop the loop
		if key == ord("q"):
			breakloop = True
			break
	if breakloop:
		break


# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()