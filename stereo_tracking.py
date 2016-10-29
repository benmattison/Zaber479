# Import python packages
import numpy as np
import cv2
import pickle
# Import some open source code
from camera_calibrate import StereoCalibration

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

def rescale(image, ratio): # Resize an image using linear interpolation
	dim = (int(image.shape[1] * ratio), int(image.shape[0] * ratio))
	rescaled = cv2.resize(image, dim, interpolation = cv2.INTER_LINEAR)
	return rescaled

# # Perform calibration of the two cameras from a set of photos.
# cal = StereoCalibration('CalibrationPhotos/DualLogi/')
# # Extract calibration information (matrices)\
# # Intrinsic Camera Matrices
# M1 = cal.camera_model.get('M1')
# M2 = cal.camera_model.get('M2')
# # Distortion Matrixes
# d1 = cal.camera_model.get('d1')
# d2 = cal.camera_model.get('d2')
# R = cal.camera_model.get('R') # Relative rotation matrix between first and second
# T = cal.camera_model.get('T') # Relative translation vector between first and second
# E = cal.camera_model.get('E') # Essential matrix
# F = cal.camera_model.get('F') # Fundamental metrix
# dims = cal.camera_model.get('dims')

# sqr_size = 0.01425  # 14.25mm length of the printed calibration squares
# T_real = T*sqr_size

mypath = "CalibrationPhotos/"
infile = open(mypath + "arbitrary_stereo_calibration_DualLogi.pickle", "rb")
datathings = pickle.load(infile)
M1, M2, d1, d2, R, T, E, F, dims, T_real = datathings

print('T real',T_real)
print('')

R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(M1, d1, M2, d2, dims, R, T_real)

print('R1',R1)
print('R2',R2)
print('P1',P1)
print('P2',P2)

# an assortment of upper and lower bounds for the different colors we use in HSV.
greenLower = (45, 86, 30)
greenUpper = (80, 255, 255)
pinkLower = (105, 60, 60)
pinkUpper = (170, 255, 255)
blueLower = (115,100,70)
blueUpper = (125,255,255)

# Choose the ones you want to use.
lower = pinkLower
upper = pinkUpper

# the minimum radius of a blob to detect it.
minRad = 5

# initialized these variables so that we can print them no matter what
((xL, yL), radiusL) = ((0,0),0)
((xR, yR), radiusR) = ((0,0),0)
(xReal, yReal, zReal) = (0,0,0)

Lcam = cv2.VideoCapture(1)
Rcam = cv2.VideoCapture(0)
# for camera in [Lcam, Rcam]:
# 	camera.set(15,exposure)
# 	camera.set(5,fps)
Logi2exposure = -6
fps = 5
Logi1exposure = 0
Lcam.set(15,Logi1exposure)
Rcam.set(15,Logi2exposure)
Lcam.set(5,fps)
Rcam.set(5,fps)


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
		((xL, yL), radiusL) = cv2.minEnclosingCircle(cL)
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
		((xR, yR), radiusR) = cv2.minEnclosingCircle(cR)
		MR = cv2.moments(cR)
		centerL = (int(ML["m10"] / ML["m00"]), int(ML["m01"] / ML["m00"]))

		if radiusR > minRad:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(capR, (int(xR), int(yR)), int(radiusR),
					   (0, 255, 255), 2)
			cv2.circle(capR, centerR, 5, (0, 0, 255), -1)

	# Find coordinates in 3D space using the triangulatePoints function for the centers of the circles
	worldPoints = cv2.triangulatePoints(P1,P2,(xL,yL),(xR,yR))
	worldPoints /= worldPoints[3]
	worldPoints = worldPoints[:3]

	# Scale by 4th homogeneous coordinate (Not sure about this actually)
	xReal = worldPoints[0]
	yReal = worldPoints[1]
	zReal = worldPoints[2]

	key = cv2.waitKey(10)

	if key == ord("c"):
		if not pathPoints:
			pathPoints = [worldPoints]
			print length(worldPoints)
		else:
			pathPoints.append(worldPoints)
			print length(worldPoints)
		print('worldPoints:', worldPoints)
		print('')

		if length(pathPoints) == 3:
			outfile = open("pathPoints.pickle", "wb")
			pickle.dump(pathPoints, outf)

	capL = rescale(capL, 1.0 / scaleR)
	capR = rescale(capR, 1.0 / scaleR)

	cv2.imshow("FrameL", capL)
	cv2.imshow("FrameR", capR)

	if key == ord("q"):
		break


# cleanup the camera and close any open windows
Lcam.release()
Rcam.release()
cv2.destroyAllWindows()