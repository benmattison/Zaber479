import numpy as np
import cv2

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6 * 9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.

cap = cv2.VideoCapture(0)

count = 0;

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    #cv2.imwrite('randomPic.jpg',frame)

    # Convert to gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

    cv2.imshow('img', frame)

    print(ret)

    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners)
        #cv2.imwrite('originalChessboard.jpg', frame)

        # Draw and display the corners
        cv2.drawChessboardCorners(frame, (9, 6), corners2, ret)
        cv2.imshow('img', frame)
        #cv2.imwrite('originalChessboardWithLines.jpg',frame)
        cv2.waitKey(500)
        #while True:
        #    if cv2.waitKey(1) & 0xFF == ord('q'):
        #        break
        count=count+1;
        if count == 30:
            break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
print(objpoints)
print(imgpoints)

# Calibrate camera
ret, cameraMatrix, distCoeffs, rvecs, tvecs, = cv2.calibrateCamera(objpoints,imgpoints,gray.shape[::-1],None,None)

print(cameraMatrix)
print(distCoeffs)
print(rvecs)
print(tvecs)

# Get new camera matrix
img = cv2.imread('randomPic.jpg')
img2 = cv2.imread('OGrandomPic.jpg')
h,w = img.shape[:2]
h2,w2 = img.shape[:2]
newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix,distCoeffs,(w,h),1,(w,h))
newCameraMatrix2, roi2 = cv2.getOptimalNewCameraMatrix(cameraMatrix,distCoeffs,(w2,h2),1,(w2,h2))

# Undistort
undistorted = cv2.undistort(img, cameraMatrix, distCoeffs, None, newCameraMatrix)
undistorted2 = cv2.undistort(img2, cameraMatrix, distCoeffs, None, newCameraMatrix2)
#undistorted = cv2.undistort(img, cameraMatrix, distCoeffs, None, None)

#x,y,w,h = roi
#undistorted = undistorted[y:y+h, x:x+h]
cv2.imwrite('randomPicCali.jpg',undistorted)
cv2.imwrite('OGrandomPicCali.jpg',undistorted2)
