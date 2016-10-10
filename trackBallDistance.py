# USAGE
# python object_movement.py --video object_tracking_example.mp4
# python object_movement.py

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2


# Maximum horizontal angle of the camera frame of view.
# TODO: Test this.
th_max = 30
# Maximum vertical angle.
phi_max = 20
# camera separation distance (mm)
d_sep = 60

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=32,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space
# !!! Changed the color values to match my green pingpong balls
# greenLower = (45, 86, 30)
# greenUpper = (80, 255, 255)
pinkLower = (145, 86, 30)
pinkUpper = (180, 255, 255)
# lower_blue = np.array([100, 50, 35])
# upper_blue = np.array([140, 255, 100])

lower = pinkLower
upper = pinkUpper

# !!! Made the minimum detection radius smaller
minRad = 5

(dX, dY) = (0, 0)
direction = ""
# !!! Initialized these variables so that we can print them no matter what
((x, y), radius) = ((0,0),0)

# grab the reference to the webcams
Lcam = cv2.VideoCapture(2)
Rcam = cv2.VideoCapture(1)
L = 1

th = [1,1]
phi = [1,1]

# keep looping
while True:
	for camera in [Lcam, Rcam]:
		# Switching between cameras, easy to label image outputs.
		if L:
			camSide = 'L'
		else:
			camSide = 'R'

		# grab the current frame
		(grabbed, frame) = camera.read()

		# This is the resizing ratio. Increasing length and height by r=2.
		r = 4
		# The dimensions of the new image.
		dim = (int(frame.shape[1] * r), int(frame.shape[0] * r))
		 
		# perform the actual resizing of the image using bilinear interpolation
		frame_orig = frame
		frame = cv2.resize(frame_orig, dim, interpolation = cv2.INTER_LINEAR)

		# # resize the frame, blur it, and convert it to the HSV
		# # color space
		# frame = imutils.resize(frame, width=600)
		# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		# construct a mask for the color "green", then perform
		# a series of dilations and erosions to remove any small
		# blobs left in the mask
		mask = cv2.inRange(hsv, lower, upper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)

		cv2.imshow('mask'+camSide, mask)

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

		# show the movement deltas and the direction of movement on
		# the frame
		# !!! COMMENTED OUT: 
		# cv2.putText(frame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
		# 	0.65, (0, 0, 255), 3)
		# !!! Added the X, Y, and diameter display

		# THIS NEEDS TO BE CALIBRATED BETTER
		# C = observed radius (pixels) * actual distance (mm)
		# TODO: Find this by accurate measurement.
		C = 18000
		# This is a rough distance estimate from radius. We can do better with stereo and compare to this.
		if radius>0:
			dist_r = C/radius
		else: 
			dist_r = 0

		# make x and y relative to origin (center)
		(x,y) = (x-frame.shape[1]/2,y-frame.shape[0]/2)
		
		# Distance from the origin to the center of the ball.
		r_o = np.sqrt(x*x+y*y)

		# maximum horixontal pixels
		w_max = frame.shape[1]/2
		# maximum vertical pixels
		h_max = frame.shape[0]/2


		th[L] = x/w_max*th_max
		phi[L] = y/h_max*phi_max

		triangle = (90-th[1], 90+th[0], 180-th[0]+th[1])

		a = np.sin(np.deg2rad(triangle[0]))*d_sep/np.sin(np.deg2rad(triangle[2]))
		b = np.sin(np.deg2rad(triangle[1]))*d_sep/np.sin(np.deg2rad(triangle[2]))

		dist_stereo = np.sqrt(a*a+b*b)

		cv2.putText(frame, "dist_r: {}, dist_stereo: {}".format(int(dist_r), dist_stereo),
			(10, 20), cv2.FONT_HERSHEY_SIMPLEX,
			0.65, (0, 0, 255), 2)
		# cv2.putText(frame, "dx: {}, dy: {}".format(dX, dY),
		# 	(10, 20), cv2.FONT_HERSHEY_SIMPLEX,
		# 	0.65, (0, 0, 255), 2)
		cv2.putText(frame, "X: {}, Y: {}, r_0: {}, dia: {}".format(int(x), int(y), int(r_o), int(2*radius)),
			(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
			0.65, (0, 0, 255), 2)

		# show the frame to our screen and increment the frame counter
		cv2.imshow("Frame"+camSide, frame)

		# Switching between cameras, easy to label image outputs.
		if L:
			L = 0
		else:
			L = 1

	key = cv2.waitKey(1) & 0xFF
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()