import cv2
import glob
import argparse
import numpy as np

class Save1Pic(object):
	def __init__(self,savePath,numPics,camIndex,rescaleSize):
		self.saveLocation = savePath
		self.maxPic = numPics
		self.rescaleSize = rescaleSize

		self.cam = cv2.VideoCapture(camIndex)

		self.setParams(self.cam)

		self.main()

	def rescale(self, image, ratio):  # Resize an image using linear interpolation
		if ratio == 1:
			return image
		dim = (int(image.shape[1] * ratio), int(image.shape[0] * ratio))
		rescaled = cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR)
		return rescaled

	def setParams(self, camera):
		EXPOSURE_PARAM = 15
		FPS_PARAM = 5

		exposure = -5
		fps = 5

		camera.set(EXPOSURE_PARAM, exposure)
		camera.set(FPS_PARAM, fps)

	def main(self):
		i = 0
		done = False

		while True:
			ret, frame = self.cam.read()
			cv2.imshow('img', frame)

			key = cv2.waitKey(1)
			if key == ord('p'):
				cv2.imwrite(self.saveLocation+'Pic_%d.jpg' % i, frame)
				i = i + 1
				if i == self.maxPic:
					done = True
			elif key == ord('q'):
				done = True

			if done:
				break

		self.cam.release()
		cv2.destroyAllWindows()
		return


class Save2Pic(object):
	def __init__(self,savePath,numPics,leftCamIndex,rightCamIndex,rescaleSize):
		self.saveLocation = savePath
		self.maxPic =  numPics
		self.rescaleSize = rescaleSize

		self.Lcam = cv2.VideoCapture(leftCamIndex)
		self.Rcam = cv2.VideoCapture(rightCamIndex)

		Save1Pic.setParams(self.Lcam)
		Save1Pic.setParams(self.Rcam)

		self.main()

	def main(self):
		i = 0
		done = False

		while True:
			retL, capL = self.Lcam.read()
			retR, capR = self.Rcam.read()

			cv2.imshow('imgL', capL)
			cv2.imshow('imgR', capR)

			key = cv2.waitKey(1)
			if key == ord('p'):
				LcapL = Save1Pic.rescale(capL, self.rescaleSize)
				LcapR = Save1Pic.rescale(capR, self.rescaleSize)
				cv2.imwrite(self.saveLocation+'Stereo%d_L.png'%i, LcapL)
				cv2.imwrite(self.saveLocation+'Stereo%d_R.png'%i, LcapR)
				i = i + 1
				if i == self.maxPic:
					done = True
			elif key == ord('q'):
				done = True

			if done:
				break

		self.Lcam.release()
		self.Rcam.release()
		cv2.destroyAllWindows()
		return
