import cv2

exposure = -6
fps = 5
Lcam = cv2.VideoCapture(2)
Rcam = cv2.VideoCapture(1)
# for camera in [Lcam, Rcam]:
# 	camera.set(15,exposure)
# 	camera.set(5,fps)
Logi1exposure = -8
Lcam.set(15,Logi1exposure)
Rcam.set(15,exposure)
Lcam.set(5,fps)
Rcam.set(5,fps)

#photo number
i = 0

# number of photos
p = 10

L = True
done = False

while True:
	retL, capL = Lcam.read()
	retR, capR = Rcam.read()

	cv2.imshow('imgL',capL)
	cv2.imshow('imgR',capR)

	key = cv2.waitKey(1)

	if key == ord('p'):
		cv2.imwrite('CalibrationPhotos/DualLogi/Stereo%d_L.png'%i, capL)
		cv2.imwrite('CalibrationPhotos/DualLogi/Stereo%d_R.png'%i, capR)
		i = i + 1
		if i == p:
			done = True	
	elif key == ord('q'):
		done = True

	if done:
		break

Lcam.release()
Rcam.release()
cv2.destroyAllWindows()
