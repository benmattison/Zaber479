import numpy as np
import cv2
import glob

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7 * 9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:7].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.


images = glob.glob('StereoCalibration/Left/*.jpg')

for fname in images:

    #read image from StereoCalibration folder
    img = cv2.imread(fname)
    # Convert to gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #find chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, (9, 7), None)
    #showing if it read the picture properly
    print(ret)

    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners)


# Calibrate camera
ret, cameraMatrix, distCoeffs, rvecs, tvecs, = cv2.calibrateCamera(objpoints,imgpoints,gray.shape[::-1],None,None)

# Get new camera matrix
img = cv2.imread('StereoCalibration/Left/StereoLeft_0.jpg')
h,w = img.shape[:2]
newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix,distCoeffs,(w,h),1,(w,h))

# Undistort
undistorted = cv2.undistort(img, cameraMatrix, distCoeffs, None, newCameraMatrix)

#crop image, needs tweeking
#x,y,w,h = roi
#undistorted = undistorted[y:y+h, x:x+h]

#write undistorted test image
cv2.imwrite('StereoCalibration/Left/randomPicCali.jpg',undistorted)
