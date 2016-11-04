# import the necessary packages
import numpy as np
import cv2


# Maximum horizontal angle of the camera frame of view.
th_max = 22.5
# camera separation distance (mm)
d_sep = 60

# an assortment of upper and lower bounds for the different colors we use in HSV.
greenLower = (45, 86, 30)
greenUpper = (80, 255, 255)
pinkLower = (145, 0, 180)
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
exposure = -20
fps = 5
# grab the reference to the webcams
Lcam = cv2.VideoCapture(1)
Rcam = cv2.VideoCapture(2)
for camera in [Lcam, Rcam]:
	camera.set(15,exposure) # 15 is the code for exposure
	camera.set(5,fps) # 5 is the code for FPS
	camera.set(12,4) # 12 is code for saturation
	print "Camera Properties"
	print camera.get(10)
	print camera.get(11)
	print camera.get(12)
	print camera.get(13)
	print camera.get(14)
	print camera.get(15)
	print ''


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



while True:

	retL,capL = Lcam.read()
	retR,capR = Rcam.read()

	# Going to scale up by this ratio for better analysis
	scaleR = 4
	# Perform the actual resizing of the image using bilinear interpolation
	capL_orig = capL
	capR_orig = capR
	capL = rescale(capL_orig, scaleR)
	capR = rescale(capR_orig, scaleR)

	(maskL, hsvL) = filterColor(capL, lower, upper)
	(maskR, hsvR) = filterColor(capR, lower, upper)

	cv2.imshow('maskL', rescale(maskL, 1.0 / scaleR))
	cv2.imshow('maskR', rescale(maskR, 1.0 / scaleR))

	cntsL = cv2.findContours(maskL.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
	cntsR = cv2.findContours(maskR.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
	centerL = None
	centerR = None

	# only proceed if at least one contour was found
	if len(cntsL)>0 and len(cntsR)>0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		cL = max(cntsL, key=cv2.contourArea)
		print len(cL)
		((xL, yL), (d1, d2), angle) = cv2.fitEllipse(cL)
		radiusL = (d1+d2)/4
		ML = cv2.moments(cL)
		centerL = (int(ML["m10"] / ML["m00"]), int(ML["m01"] / ML["m00"]))

		# only proceed if the radius meets a minimum size
		if radiusL > minRad:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(capL, (int(xL), int(yL)), int(radiusL),
					   (0, 255, 255), 2)
			cv2.circle(capL, centerL, 5, (0, 0, 255), -1)

		# Repeat for Right side
		cR = max(cntsR, key=cv2.contourArea)
		((xR, yR), (d1, d2), angle) = cv2.fitEllipse(cR)
		radiusR = (d1+d2)/4
		MR = cv2.moments(cR)
		centerL = (int(ML["m10"] / ML["m00"]), int(ML["m01"] / ML["m00"]))

		if radiusR > minRad:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(capR, (int(xR), int(yR)), int(radiusR),
					   (0, 255, 255), 2)
			cv2.circle(capR, centerR, 5, (0, 0, 255), -1)

	capL = rescale(capL, 1.0 / scaleR)
	capR = rescale(capR, 1.0 / scaleR)

	cv2.imshow("FrameL", capL)
	cv2.imshow("FrameR", capR)

	key = cv2.waitKey(10)

	if key == ord("q"):
		break


# cleanup the camera and close any open windows
Lcam.release()
Rcam.release()
cv2.destroyAllWindows()