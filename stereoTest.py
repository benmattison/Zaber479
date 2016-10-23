import cv2
from matplotlib import pyplot as plt
import numpy as np

capR = cv2.VideoCapture(1)
capL = cv2.VideoCapture(2)

while True:

    retR, frameR = capR.read()
    retL, frameL = capL.read()

    grayImgR = cv2.cvtColor(frameR, cv2.COLOR_BGR2GRAY)
    grayImgL = cv2.cvtColor(frameL, cv2.COLOR_BGR2GRAY)

    cv2.imshow('right',grayImgR)
    cv2.imshow('left',grayImgL)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break



# This is the resizing ratio. Increasing length and height by r=2.
r = 4
# The dimensions of the new image.
dim = (int(grayImgR.shape[1] * r), int(grayImgR.shape[0] * r)) 
# perform the actual resizing of the image using bilinear interpolation
grayImgR = cv2.resize(grayImgR, dim, interpolation = cv2.INTER_LINEAR)
grayImgL = cv2.resize(grayImgL, dim, interpolation = cv2.INTER_LINEAR)

# stereo = cv2.StereoBM_create()
# stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
stereo = cv2.StereoSGBM_create(1, 16, 15)

disparity = stereo.compute(grayImgL, grayImgR)
# cv2.imshow('disparity',disparity)
plt.imshow(disparity,'gray')
plt.show()



capR.release()
capL.release()
cv2.destroyAllWindows()