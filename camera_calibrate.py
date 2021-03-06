import numpy as np
import cv2
import glob

sqSize = [12,10]
winSize = (11,11)

def rescale(image, ratio): # Resize an image using linear interpolation
	if ratio == 1:
		return image
	dim = (int(image.shape[1] * ratio), int(image.shape[0] * ratio))
	rescaled = cv2.resize(image, dim, interpolation = cv2.INTER_LINEAR)
	return rescaled

class StereoCalibration(object):
	def __init__(self, filepath, squareSize):
		# termination criteria
		self.criteria = (cv2.TERM_CRITERIA_EPS +
						 cv2.TERM_CRITERIA_MAX_ITER, 30, 0.0001)
		self.criteria_cal = (cv2.TERM_CRITERIA_EPS +
							 cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)
		self.sqSize = squareSize

		# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
		self.objp = np.zeros((self.sqSize[0]*self.sqSize[1], 3), np.float32)
		self.objp[:, :2] = np.mgrid[0:self.sqSize[0], 0:self.sqSize[1]].T.reshape(-1, 2)

		# Arrays to store object points and image points from all the images.
		self.objpoints = []  # 3d point in real world space
		self.imgpoints_l = []  # 2d points in image plane.
		self.imgpoints_r = []  # 2d points in image plane.

		self.cal_path = filepath
		self.read_images(self.cal_path)

	def read_images(self, cal_path):
		images_right = glob.glob(cal_path + '*_R*')
		images_left = glob.glob(cal_path + '*_L*')
		images_left.sort()
		images_right.sort()

		if not images_right:
			print('cant find images')

		for i, fname in enumerate(images_right):
			img_l = cv2.imread(images_left[i])
			img_r = cv2.imread(images_right[i])

			gray_l = cv2.cvtColor(img_l, cv2.COLOR_BGR2GRAY)
			gray_r = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)

			# Find the chess board corners
			ret_l, corners_l = cv2.findChessboardCorners(gray_l, (self.sqSize[0], self.sqSize[1]))
			ret_r, corners_r = cv2.findChessboardCorners(gray_r, (self.sqSize[0], self.sqSize[1]))

			# If found, add object points, image points (after refining them)
			self.objpoints.append(self.objp)

			if ret_l is True:
				rt = cv2.cornerSubPix(gray_l, corners_l, winSize,
									  (-1, -1), self.criteria)
				self.imgpoints_l.append(corners_l)

				# Draw and display the corners
				ret_l = cv2.drawChessboardCorners(img_l, (self.sqSize[0], self.sqSize[1]),
												  corners_l, ret_l)
				cv2.imshow(images_left[i], img_l)
				cv2.waitKey(20)
			else:
				print("couldn't find chessboard corners")

			if ret_r is True:
				rt = cv2.cornerSubPix(gray_r, corners_r, winSize,
									  (-1, -1), self.criteria)
				self.imgpoints_r.append(corners_r)

				# Draw and display the corners
				ret_r = cv2.drawChessboardCorners(img_r, (self.sqSize[0], self.sqSize[1]),
												  corners_r, ret_r)
				cv2.imshow(images_right[i], img_r)
				cv2.waitKey(20)
				
			img_shape = gray_l.shape[::-1]

		# Use this if you want to see the pictures with chessboards for a while.
		key = cv2.waitKey(0)

		rt, self.M1, self.d1, self.r1, self.t1 = cv2.calibrateCamera( \
			self.objpoints, self.imgpoints_l, img_shape, None, None)
		rt, self.M2, self.d2, self.r2, self.t2 = cv2.calibrateCamera( \
			self.objpoints, self.imgpoints_r, img_shape, None, None)

		self.camera_model = self.stereo_calibrate(img_shape)

	def stereo_calibrate(self, dims):
		flags = 0
		# flags |= cv2.CALIB_FIX_INTRINSIC
		# # flags |= cv2.CALIB_FIX_PRINCIPAL_POINT
		# flags |= cv2.CALIB_USE_INTRINSIC_GUESS
		# flags |= cv2.CALIB_FIX_FOCAL_LENGTH
		# # flags |= cv2.CALIB_FIX_ASPECT_RATIO
		# flags |= cv2.CALIB_ZERO_TANGENT_DIST
		# # flags |= cv2.CALIB_RATIONAL_MODEL
		# # flags |= cv2.CALIB_SAME_FOCAL_LENGTH
		# # flags |= cv2.CALIB_FIX_K3
		# # flags |= cv2.CALIB_FIX_K4
		# # flags |= cv2.CALIB_FIX_K5

		stereocalib_criteria = (cv2.TERM_CRITERIA_MAX_ITER +
								cv2.TERM_CRITERIA_EPS, 100, 1e-5)
		ret, M1, d1, M2, d2, R, T, E, F = cv2.stereoCalibrate(
			self.objpoints, self.imgpoints_l,
			self.imgpoints_r, imageSize = dims, cameraMatrix1 = self.M1, distCoeffs1 = self.d1, cameraMatrix2 = self.M2,
			distCoeffs2 = self.d2, criteria=stereocalib_criteria, flags=flags)

		print('Intrinsic_mtx_1', M1)
		print('dist_1', d1)
		print('Intrinsic_mtx_2', M2)
		print('dist_2', d2)
		print('R', R)
		print('T', T)
		print('E', E)
		print('F', F)
		print('dims',dims)

		# for i in range(len(self.r1)):
		#     print("--- pose[", i+1, "] ---")
		#     self.ext1, _ = cv2.Rodrigues(self.r1[i])
		#     self.ext2, _ = cv2.Rodrigues(self.r2[i])
		#     print('Ext1', self.ext1)
		#     print('Ext2', self.ext2)

		print('')

		camera_model = dict([('M1', M1), ('M2', M2), ('dist1', d1),
							('dist2', d2), ('rvecs1', self.r1),
							('rvecs2', self.r2), ('R', R), ('T', T),
							('E', E), ('F', F),('dims',dims)])

		cv2.destroyAllWindows()
		return camera_model
