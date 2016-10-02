import cv2
from matplotlib import pyplot as plt
import numpy as np

cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

while True:

    ret, frame = cap.read()
    ret2, frame2 = cap2.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    cv2.imshow('logitech',frame)
    cv2.imshow('webcam',frame2)

    stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
    disparity = stereo.compute(gray, gray2)
    cv2.imshow('disparity',disparity)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break