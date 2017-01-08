import cv2
import glob
import argparse
import numpy as np
import os


def createFolder(location):
	if not (location.endswith('/') or location.endswith('\\')):
		location = location + '/'
	if not os.path.exists(location):
		os.makedirs(location)


def setParams(camera, exposure = -4, fps = 30, img_height = 640, img_width = 480):
	camera.set(cv2.CAP_PROP_EXPOSURE, exposure)
	camera.set(cv2.CAP_PROP_FPS, fps)
	camera.set(cv2.CAP_PROP_FRAME_HEIGHT, img_height)
	camera.set(cv2.CAP_PROP_FRAME_WIDTH, img_width)


def rescale(image, ratio):  # Resize an image using linear interpolation
	if ratio == 1:
		return image
	dim = (int(image.shape[1] * ratio), int(image.shape[0] * ratio))
	rescaled = cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR)
	return rescaled


class Save1Pic(object):
	def __init__(self,savePath,numPics,camIndex,rescaleSize):
		self.saveLocation = savePath
		createFolder(self.saveLocation)
		self.maxPic = numPics
		self.rescaleSize = rescaleSize

		self.cam = cv2.VideoCapture(camIndex)

		setParams(self.cam)

		self.main()

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
	def __init__(self,savePath,numPics,leftCamIndex,rightCamIndex,rescaleSize,displayPattern=False,chessBoardSize=[9,6],img_height=640,img_width=480,fps=30,exposure=-4):
		self.saveLocation = savePath
		createFolder(self.saveLocation)
		self.maxPic = numPics
		self.rescaleSize = rescaleSize

		self.Lcam = cv2.VideoCapture(leftCamIndex)
		self.Rcam = cv2.VideoCapture(rightCamIndex)

		self.fps = fps
		self.img_height = img_height
		self.img_width = img_width
		self.exposure = exposure

		setParams(self.Lcam,exposure=self.exposure,img_width=self.img_width,img_height=self.img_height,fps=self.fps)
		setParams(self.Rcam,exposure=self.exposure,img_width=self.img_width,img_height=self.img_height,fps=self.fps)

		self.main(displayPattern=displayPattern, patSize=chessBoardSize)

	def main(self, displayPattern = False, patSize = [9,6]):
		i = 0
		done = False

		while True:
			retL, capL = self.Lcam.read()
			retR, capR = self.Rcam.read()

			capLorig = capL.copy()
			capRorig = capR.copy()

			# Useful to display the chessboard pattern
			if displayPattern:
				# criteria = (cv2.TERM_CRITERIA_MAX_ITER, 4)
				criteria = (cv2.TERM_CRITERIA_MAX_ITER +
								cv2.TERM_CRITERIA_EPS, 4, 1e-5)
				winSize = (11,11)

				gray_l = cv2.cvtColor(capL, cv2.COLOR_BGR2GRAY)
				gray_r = cv2.cvtColor(capR, cv2.COLOR_BGR2GRAY)

				# Find the chess board corners
				hasCorners_L, corners_l = cv2.findChessboardCorners(gray_l, (patSize[0], patSize[1]))
				if hasCorners_L:
					hasCorners_R, corners_r = cv2.findChessboardCorners(gray_r, (patSize[0], patSize[1]))
				else:
					hasCorners_R = False

				if hasCorners_L is True:
					rt = cv2.cornerSubPix(gray_l, corners_l, winSize, (-1, -1), criteria)
					# Draw and display the corners
					cv2.drawChessboardCorners(capL, (patSize[0], patSize[1]),
													  corners_l, hasCorners_L)


				if hasCorners_R is True:
					rt = cv2.cornerSubPix(gray_r, corners_r, winSize, (-1, -1), criteria)
					# Draw and display the corners
					cv2.drawChessboardCorners(capR, (patSize[0], patSize[1]),
													  corners_r, hasCorners_R)	
			else: # if we aren't checking for corners, assume they are there.
				hasCorners_R = True
				hasCorners_L = True		

			if retL:
				cv2.imshow('imgL', capL)
			if retR:
				cv2.imshow('imgR', capR)

			key = cv2.waitKey(20)
			if key == ord('w'):
				cv2.imshow('origL', capLorig)
				cv2.waitKey(0)
			if key == ord('p'):
				if not (hasCorners_R and hasCorners_L):
					print('Chessboard pattern not found in both images. No picture saved.')
				else: 
					LcapL = rescale(capLorig, self.rescaleSize)
					LcapR = rescale(capRorig, self.rescaleSize)
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
