import cv2
import pickle
# Import some open source code
from camera_calibrate import StereoCalibration

# Perform calibration of the two cameras from a set of photos.
cal = StereoCalibration('CalibrationPhotos/DualLogi/')
# Extract calibration information (matrices)\
# Intrinsic Camera Matrices
M1 = cal.camera_model.get('M1')
M2 = cal.camera_model.get('M2')
# Distortion Matrixes
d1 = cal.camera_model.get('d1')
d2 = cal.camera_model.get('d2')
R = cal.camera_model.get('R') # Relative rotation matrix between first and second
T = cal.camera_model.get('T') # Relative translation vector between first and second
E = cal.camera_model.get('E') # Essential matrix
F = cal.camera_model.get('F') # Fundamental metrix
dims = cal.camera_model.get('dims')

sqr_size = 0.02365  # 14.25mm length of the printed calibration squares
T_real = T*sqr_size

# Save in CalibrationPhotos folder
mypath = "CalibrationPhotos/"

# Change file name based on calibraion setup
calibrationName = "DualLogi"

datathings = (M1, M2, d1, d2, R, T, E, F, dims, T_real)
outf = open(mypath + "arbitrary_stereo_calibration_" + calibrationName + ".pickle", "wb")
pickle.dump(datathings, outf)