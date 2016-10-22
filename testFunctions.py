import cv2

cap = cv2.VideoCapture(2)

#photo number
i = 0

# number of photos
p = 10


while True:

	ret, frame = cap.read()
	cv2.imshow('img', frame)

	# # resize the frame, blur it, and convert it to the HSV
	# # color space
	blurred = cv2.GaussianBlur(frame, (21,21), 0)
	cv2.imshow('blurred', blurred)

	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	pinkLower = (140, 50, 180)
	pinkUpper = (170, 255, 255)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, pinkLower, pinkUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

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
