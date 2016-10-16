import cv2

cap = cv2.VideoCapture(2)

#photo number
i = 0

# number of photos
p = 10


while True:

	ret, frame = cap.read()
	cv2.imshow('img', frame)

	key = cv2.waitKey(5)

	if key == ord('p'):
		cv2.imwrite('StereoCalibration/StereoRight_%d.jpg' % i, frame)
		i = i + 1
		if i == p:
			break
	elif key == ord('q'):
		break


cap.release()
cv2.destroyAllWindows()
