import cv2

cap = cv2.VideoCapture(3)

#photo number
i = 0

# number of photos
p = 10


while True:

    ret, frame = cap.read()
    cv2.imshow('img', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.imwrite('StereoCalibration/StereoRight_%d.jpg' % i, frame)
        i = i + 1

    if i == p:
        break


cap.release()
cv2.destroyAllWindows()
