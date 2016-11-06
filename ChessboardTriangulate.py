
# SCRIPT TO TEST IF TRIANGULATE POINTS WORKS FOR CHESSBOARD CORNERS

import numpy as np
import pickle
import cv2
import glob

# Get pre-calibrated camera setup
mypath = "CalibrationPhotos/"
infile = open(mypath + "arbitrary_stereo_calibration_Nov2.pickle", "rb")
datathings = pickle.load(infile)
M1, M2, d1, d2, R, T, E, F, dims, T_real = datathings

print(M1)
print('')
print(M2)
print('')
print(T_real)
print('')

# Stereo Rectify to get projection matrices
flags = 0
flags |= cv2.CALIB_ZERO_DISPARITY
R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(M1, d1, M2, d2, dims, R, T_real, alpha=-1, flags = flags)

print(R)
print('')
print(R1)
print('')
print(R2)
print('')
print(P1)
print('')
print(P2)
print('')

print(P2[0,3]/P1[0,0])
print('')

# Modify P2 to not just be a translation in x
#P2[:,3]=np.transpose(T_real*P1[0,0])

print(P2)
print('')


# Image a and b are before and after moving the chessboard laterally ~20cm
imageLa = glob.glob("CalibrationPhotos/Nov2Ben/test2a_L.png")
imageLb = glob.glob("CalibrationPhotos/Nov2Ben/test2b_L.png")
imageRa = glob.glob("CalibrationPhotos/Nov2Ben/test2a_R.png")
imageRb = glob.glob("CalibrationPhotos/Nov2Ben/test2b_R.png")

# Read in OpenCV
frameLa = cv2.imread(imageLa[0])
frameRa = cv2.imread(imageRa[0])
frameLb = cv2.imread(imageLb[0])
frameRb = cv2.imread(imageRb[0])

# Convert to grayscale
grayLa = cv2.cvtColor(frameLa, cv2.COLOR_BGR2GRAY)
grayRa = cv2.cvtColor(frameRa, cv2.COLOR_BGR2GRAY)
grayLb = cv2.cvtColor(frameLb, cv2.COLOR_BGR2GRAY)
grayRb = cv2.cvtColor(frameRb, cv2.COLOR_BGR2GRAY)

# Get image points (corners)
retLa, cornersLa = cv2.findChessboardCorners(grayLa, (9, 6), None)
retRa, cornersRa = cv2.findChessboardCorners(grayRa, (9, 6), None)
retLb, cornersLb = cv2.findChessboardCorners(grayLb, (9, 6), None)
retRb, cornersRb = cv2.findChessboardCorners(grayRb, (9, 6), None)

# Get world points
worldPointsA = cv2.triangulatePoints(P1,P2,cornersLa,cornersRa)
worldPointsB = cv2.triangulatePoints(P1,P2,cornersLb,cornersRb)

# Scale to x,y,z cartesian
worldPointsA /= worldPointsA[3]
worldPointsB /= worldPointsB[3]
worldPointsA = worldPointsA[:3]
worldPointsB = worldPointsB[:3]

# Find distances points moved
distances = np.linalg.norm(worldPointsA-worldPointsB,axis=0)

print(distances)
