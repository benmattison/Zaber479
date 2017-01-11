# Import python packages
import numpy as np
import cv2
import pickle
# Import some open source code
import calibrateCameras as cb
# Import our own code
import evaluatePoints


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
	if ratio == 1:
		return image
	dim = (int(image.shape[1] * ratio), int(image.shape[0] * ratio))
	rescaled = cv2.resize(image, dim, interpolation = cv2.INTER_LINEAR)
	return rescaled


# Based on code from http://www.morethantechnical.com/2012/01/04/simple-triangulation-with-opencv-from-harley-zisserman-w-code/
# Implements Hartley's algorithms.
def linearTriangulate(P1, P2, point1, point2, w1 = 1, w2 = 1):
	A = np.array([[point1[0]*P1[2,0]-P1[0,0], point1[0]*P1[2,1]-P1[0,1], point1[0]*P1[2,2]-P1[0,2]], \
		[point1[1]*P1[2,0]-P1[1,0], point1[1]*P1[2,1]-P1[1,1], point1[1]*P1[2,2]-P1[1,2]], \
		[point2[0]*P2[2,0]-P2[0,0], point2[0]*P2[2,1]-P2[0,1], point2[0]*P2[2,2]-P2[0,2]], \
		[point2[1]*P2[2,0]-P2[1,0], point2[1]*P2[2,1]-P2[1,1], point2[1]*P2[2,2]-P2[1,2]]])
	A[:2,:] = A[:2,:]/w1
	A[3:,:] = A[3:,:]/w2
	B = np.array([point1[0]*P1[2,3]-P1[0,3], point1[1]*P1[2,3]-P1[1,3], \
		point2[0]*P2[2,3]-P2[0,3], point2[1]*P2[2,3]-P2[1,3]])
	B = -B
	B[:2] = B[:2]/w1
	B[3:] = B[3:]/w2
	X = np.linalg.lstsq(A,B)
	X = X[0]
	X = np.append(X,1.0)
	return X


def iterTriangulate(P1, P2, point1, point2):
	EPSILON = 1e-8
	w1, w2 = 1, 1

	maxIterations = 10

	for i in range(maxIterations):
		X = linearTriangulate(P1, P2, point1, point2, w1, w2)

		w1_new = np.dot(P1[2],X)
		w2_new = np.dot(P2[2],X)

		if max([abs(w1-w1_new), abs(w2-w2_new)]) < EPSILON:
			break

		w1 = w1_new
		w2 = w2_new

	return X


def getHSVBounds(**kwargs):

	# Default is pink
	lower = (145, 0, 180)
	upper = (160, 255, 255)

	for key in kwargs:
		if key == 'hsv':
			if kwargs[key] == 'green':
				lower = (45, 86, 30)
				upper = (80, 255, 255)
			elif kwargs[key] == 'pink':
				lower = (140, 0, 0)
				upper = (255, 255, 255)
			elif kwargs[key] == 'blue':
				lower = (115, 100, 70)
				upper = (125, 255, 255)

	return lower, upper


class StereoTracker(object):
	def __init__(self,calConstants,sqSize):
		#print len(calConstants)
		[self.M1, self.M2, self.d1, self.d2, self.R, self.T, self.E, self.F, self.dims] = calConstants
		flags = 0
		flags |= cv2.CALIB_ZERO_DISPARITY
		self.R1, self.R2, self.P1, self.P2, self.Q, self.roi1, self.roi2 = cv2.stereoRectify(self.M1, self.d1, self.M2, self.d2, self.dims, self.R, self.T, alpha=-1, flags=flags)
		self.sqSize = sqSize
		#print("R1",self.R1)
		#print("R2",self.R2)

	def initializeCameras(self,Lcam_index,Rcam_index,Lcam_exposure=-4,Rcam_exposure=-4,fps=30):
		self.Lcam = cv2.VideoCapture(Lcam_index)
		self.Rcam = cv2.VideoCapture(Rcam_index)

		# # Defaults for Minoru
		# exposure = -11
		# fps = 5
		# # Adjust if needed
		# for key in kwargs:
		# 	if key == 'exposure':
		# 		exposure = kwargs[key]
		# 	elif key == 'fps':
		# 		fps = kwargs[key]

		self.Lcam.set(cv2.CAP_PROP_EXPOSURE, Lcam_exposure)
		self.Rcam.set(cv2.CAP_PROP_EXPOSURE, Rcam_exposure)


		for camera in [self.Lcam, self.Rcam]:
			#camera.set(cv2.CAP_PROP_AUTO_EXPOSURE,1)
			#camera.set(cv2.CAP_PROP_EXPOSURE, exposure)
			camera.set(cv2.CAP_PROP_FPS, fps)
			#camera.set(cv2.CAP_PROP_FORMAT,cv2.CV_8UC3)
			camera.set(cv2.CAP_PROP_FRAME_WIDTH,self.dims[0])
			camera.set(cv2.CAP_PROP_FRAME_HEIGHT,self.dims[1])
			camera.set(cv2.CAP_PROP_GAIN,1.0)
			camera.set(cv2.CAP_PROP_BRIGHTNESS,1.0)
			print camera.get(cv2.CAP_PROP_BRIGHTNESS)
			print camera.get(cv2.CAP_PROP_CONTRAST)
			print camera.get(cv2.CAP_PROP_GAIN)


	def showVideo(self):
		while True:
			# retR, capR = self.Rcam.read()
			# retL, capL = self.Lcam.read()
			retR = self.Rcam.grab()
			retL = self.Lcam.grab()
			if retR and retL:
				retR, capR = self.Rcam.retrieve()
				retL, capL = self.Lcam.retrieve()

				cv2.imshow('Rcam',capR)
				cv2.imshow('Lcam',capL)

			key = cv2.waitKey(1)
			if key == ord('q'):
				break

	def showMask(self, colour):
		lower, upper = getHSVBounds(hsv=colour)
		while True:
			# retR, capR = self.Rcam.read()
			# retL, capL = self.Lcam.read()
			retR = self.Rcam.grab()
			retL = self.Lcam.grab()
			if retR and retL:
				retR, capR = self.Rcam.retrieve()
				retL, capL = self.Lcam.retrieve()
				maskL, hsvL = filterColor(capL, lower, upper)
				maskR, hsvR = filterColor(capR, lower, upper)

				cv2.imshow('Rcam_mask',maskR)
				cv2.imshow('Lcam_mask',maskL)

			key = cv2.waitKey(1)
			if key == ord('q'):
				break

	def showFrame(self):
		retR = self.Rcam.grab()
		retL = self.Lcam.grab()
		if retR and retL:
			retR, capR = self.Rcam.retrieve()
			retL, capL = self.Lcam.retrieve()

			cv2.imshow('Rcam',capR)
			cv2.imshow('Lcam',capL)

	def trackBall(self,colour): # Returns the world coordinates [x, y, z] of the tracking ball
		lower, upper = getHSVBounds(hsv=colour)

		retL, capL = self.Lcam.read()
		retR, capR = self.Rcam.read()

		maskL, hsvL = filterColor(capL, lower, upper)
		maskR, hsvR = filterColor(capR, lower, upper)

		cntsL = cv2.findContours(maskL.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
		cntsR = cv2.findContours(maskR.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

		if len(cntsL) < 1 or len(cntsR) < 1: # No contours found
			return None

		cL = max(cntsL, key=cv2.contourArea)
		cR = max(cntsR, key=cv2.contourArea)

		((xL, yL), (d1, d2), angle) = cv2.fitEllipse(cL)

		((xR, yR), (d1, d2), angle) = cv2.fitEllipse(cR)

		worldPoints = iterTriangulate(self.P1, self.P2, (xL, yL), (xR, yR))
		#worldPoints = cv2.triangulatePoints(self.P1, self.P2, np.array([xL, yL]), np.array([xR, yR]))
		worldPoints /= worldPoints[3]

		worldPoints = worldPoints[:3]
		worldPoints *= self.sqSize  # Size of the large calibration squares

		xReal = worldPoints[0]
		yReal = worldPoints[1]
		zReal = worldPoints[2]

		return [xReal, yReal, zReal]

	def close(self):
		self.Lcam.release()
		self.Rcam.release()
		cv2.destroyAllWindows()

if __name__ == '__main__':

	sqr_size = 37.67  # 14.25mm, 19.25mm, 23.65mm, 37.67mm length of the printed calibration squares
	# T_real = T*sqr_size

	# mypath = "CalibrationPhotos/"
	# infile = open(mypath + 'arbitrary_stereo_calibration_MinoruXL.pickle', 'rb')
	# datathings = pickle.load(infile)

	calPath = "CalibrationPhotos/calibration_gusTest.json"
	datathings = cb.loadCalibration(calPath)
	M1, M2, d1, d2, R, T, E, F, dims = datathings
	print datathings

	print('T', T)
	print('T*sqr', T*sqr_size)

	flags = 0
	flags |= cv2.CALIB_ZERO_DISPARITY

	R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(M1, d1, M2, d2, dims, R, T, alpha=-1, flags = flags)
	print('R1', R1)
	print('R2', R2)
	print('P1', P1)
	print('P2', P2)
	print('Q', Q)
	print('roi1', roi1)
	print('roi2', roi2)

	# an assortment of upper and lower bounds for the different colors we use in HSV.
	greenLower = (45, 86, 30)
	greenUpper = (100, 255, 255)
	pinkLower = (145, 0, 180)
	pinkUpper = (160, 255, 255)
	blueLower = (115,100,70)
	blueUpper = (125,255,255)

	# Choose the ones you want to use.
	lower = greenLower
	upper = greenUpper

	# the minimum radius of a blob to detect it.
	minRad = 5

	# initialized these variables so that we can print them no matter what
	((xL, yL), radiusL) = ((0,0),0)
	((xR, yR), radiusR) = ((0,0),0)
	(xReal, yReal, zReal) = (0,0,0)

	Lcam = cv2.VideoCapture(1)
	Rcam = cv2.VideoCapture(2)
	minoruExposure = -4
	Logi2exposure = -6
	Logi1exposure = 0
	fps = 5

	for camera in [Lcam, Rcam]:
		camera.set(15,minoruExposure)
		camera.set(5,fps)

	# Lcam.set(15,Logi1exposure)
	# Rcam.set(15,Logi2exposure)
	# Lcam.set(5,fps)
	# Rcam.set(5,fps)

	pathPoints = []


	while True:

		retL,capL = Lcam.read()
		retR,capR = Rcam.read()

		key = cv2.waitKey(10)

		if key == ord("q"):
			break

		# Going to scale up by this ratio for better analysis
		if key == ord("c"):
			scaleR = 1
			bigPicFlag = 1
		else:
			scaleR = 1
			bigPicFlag = 0

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

		imgCenter = (int(0.5*capL.shape[1]),int(0.5*capL.shape[0]))
		cv2.circle(capL, imgCenter, 20, (0, 255, 0), 3)
		cv2.circle(capR, imgCenter, 20, (0, 255, 0), 3)

		# only proceed if at least one contour was found
		if len(cntsL)>0 and len(cntsR)>0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			cL = max(cntsL, key=cv2.contourArea)
			cR = max(cntsR, key=cv2.contourArea)
			if len(cL) < 10 or len(cR) < 10:
				continue
			((xL, yL), (d1, d2), angle) = cv2.fitEllipse(cL)
			radiusL = (d1+d2)/4
			ML = cv2.moments(cL)
			centerL = (int(ML["m10"] / ML["m00"]), int(ML["m01"] / ML["m00"]))

			# only proceed if the radius meets a minimum size
			if radiusL > minRad:
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				cv2.circle(capL, (int(xL), int(yL)), int(radiusL),(0, 255, 255), 2)
				cv2.circle(capL, centerL, 5, (0, 0, 255), -1)

			# Repeat for Right side
			((xR, yR), (d1, d2), angle) = cv2.fitEllipse(cR)
			radiusR = (d1+d2)/4
			MR = cv2.moments(cR)
			centerL = (int(ML["m10"] / ML["m00"]), int(ML["m01"] / ML["m00"]))

			if radiusR > minRad:
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				cv2.circle(capR, (int(xR), int(yR)), int(radiusR),(0, 255, 255), 2)
				cv2.circle(capR, centerR, 5, (0, 0, 255), -1)

		if key == ord("c"):

			# Find coordinates in 3D space using the triangulatePoints function for the centers of the circles
			# worldPoints1 = cv2.triangulatePoints(P1,P2,(xL,yL),(xR,yR))
			worldPoints = iterTriangulate(P1,P2,(xL,yL),(xR,yR))
			worldPoints /= worldPoints[3]
			# print('worldPoints1:', worldPoints1)

			worldPoints = worldPoints[:3]
			worldPoints *= sqr_size # Size of the large calibration squares

			print('worldPoints:', worldPoints)

			# Scale by 4th homogeneous coordinate (Not sure about this actually)
			xReal = worldPoints[0]
			yReal = worldPoints[1]
			zReal = worldPoints[2]

			if not pathPoints:
				pathPoints = [worldPoints]
				print len(pathPoints)
			else:
				pathPoints.append(worldPoints)
				print len(pathPoints)

			print('')

			if len(pathPoints) == 3:
				outfile = open("pathPoints.pickle", "wb")
				pickle.dump(pathPoints, outfile)

				Ev = evaluatePoints.evalPoints(pathPoints)
				print Ev.evaluate()
				Ev.plotPoints()

		capL = rescale(capL, 1.0 / scaleR)
		capR = rescale(capR, 1.0 / scaleR)

		cv2.imshow("FrameL", capL)
		cv2.imshow("FrameR", capR)


	# cleanup the camera and close any open windows
	Lcam.release()
	Rcam.release()
	cv2.destroyAllWindows()