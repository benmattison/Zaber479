import cv2


saveLocation = 'CalibrationPhotos/MinoruCalibration/'

def rescale(image, ratio): # Resize an image using linear interpolation
	if ratio == 1:
		return image
	dim = (int(image.shape[1] * ratio), int(image.shape[0] * ratio))
	rescaled = cv2.resize(image, dim, interpolation = cv2.INTER_LINEAR)
	return rescaled

exposure = -5
fps = 5
Lcam = cv2.VideoCapture(1)
Rcam = cv2.VideoCapture(2)
for camera in [Lcam, Rcam]:
	camera.set(15,exposure)
	camera.set(5,fps)


# Logi1exposure = 0

# Lcam.set(15,Logi1exposure)
# Rcam.set(15,exposure)
# Lcam.set(5,fps)
# Rcam.set(5,fps)

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
		LcapL = rescale(capL, 4)
		LcapR = rescale(capR, 4)
		cv2.imwrite(saveLocation+'Stereo%d_L.png'%i, LcapL)
		cv2.imwrite(saveLocation+'Stereo%d_R.png'%i, LcapR)
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
