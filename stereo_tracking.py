import numpy as np
import cv2
import glob
import argparse

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

cal = StereoCalibration('C:/UBC/5th Year/ENPH479/Code/Zaber479/LogitechCalibration/')

M1 = cal.camera_model.get('M1')
M2 = cal.camera_model.get('M2')
d1 = cal.camera_model.get('d1')
d2 = cal.camera_model.get('d2')
R = cal.camera_model.get('R')
T = cal.camera_model.get('T')
E = cal.camera_model.get('E')
F = cal.camera_model.get('F')
dims = cal.camera_model.get('dims')

sqr_size = 0.01425  # 14.25mm

T_real = T*sqr_size

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
pinkLower = (130, 50, 180)
pinkUpper = (210, 255, 255)
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

# The Logitech camera responded really poorly to the exposure so I left it at default for now
exposure = -6
fps = 5
# grab the reference to the webcams
Lcam = cv2.VideoCapture(0)
Rcam = cv2.VideoCapture(1)
#for camera in [Lcam, Rcam]:
#    camera.set(15, exposure)
#    camera.set(5, fps)

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

    # Scale by 4th homogeneous coordinate (Not sure about this actually)
    xReal = worldPoints[0]/worldPoints[3]
    yReal = worldPoints[1]/worldPoints[3]
    zReal = worldPoints[2]/worldPoints[3]

    print('xReal:', xReal)
    print('yReal:', yReal)
    print('zReal:', zReal)

    capL = rescale(capL, 1.0 / scaleR)
    capR = rescale(capR, 1.0 / scaleR)

    cv2.imshow("FrameL", capL)
    cv2.imshow("FrameR", capR)

    key = cv2.waitKey(100)
    if key == ord("q"):
        break


# cleanup the camera and close any open windows
Lcam.release()
Rcam.release()
cv2.destroyAllWindows()