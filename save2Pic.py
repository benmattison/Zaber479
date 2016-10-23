import cv2

exposure = -6
fps = 5
Lcam = cv2.VideoCapture(0)
Rcam = cv2.VideoCapture(1)
#for camera in [Lcam, Rcam]:
#	camera.set(15,exposure)
#	camera.set(5,fps)

#photo number
i = 0

# number of photos
p = 10

L = True
done = False

while True:
	for camera in [Lcam, Rcam]:
		# Switching between cameras, easy to label image outputs.
		if L:
			camSide = 'L'
		else:
			camSide = 'R'

		(grabbed, frame) = camera.read()
		cv2.imshow('img'+camSide,frame)

		key = cv2.waitKey(1)

		if key == ord('p'):
			cv2.imwrite('StereoCalibration/Stereo%d_'%i+camSide+'.png', frame)
			cv2.imwrite('StereoCalibration/Stereo%d_other.png' % i, lastFrame)
			i = i + 1
			if i == p:
				done = True
				break	
		elif key == ord('q'):
			done = True
			break

		if L:
			L = False
		else:
			L = True
		lastFrame = frame
	if done:
		break


Lcam.release()
Rcam.release()
cv2.destroyAllWindows()
