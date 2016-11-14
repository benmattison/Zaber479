import cv2
import pickle
# Import some open source code
from camera_calibrate import StereoCalibration

# Perform calibration of the two cameras from a set of photos.
cal = StereoCalibration('CalibrationPhotos/MinoruCalibrationXL/',[6,9])

# Extract calibration information (matrices)
# Intrinsic Camera Matrices
M1 = cal.camera_model.get('M1')
M2 = cal.camera_model.get('M2')
# Distortion Matrixes
d1 = cal.camera_model.get('dist1')
d2 = cal.camera_model.get('dist2')

R = cal.camera_model.get('R') # Relative rotation matrix between first and second
T = cal.camera_model.get('T') # Relative translation vector between first and second
E = cal.camera_model.get('E') # Essential matrix
F = cal.camera_model.get('F') # Fundamental metrix
dims = cal.camera_model.get('dims')

# Change file name based on calibraion setup
calibrationName = "MinoruXL"

datathings = (M1, M2, d1, d2, R, T, E, F, dims)
outf = open('CalibrationPhotos/arbitrary_stereo_calibration_' + calibrationName + '.pickle', 'wb')
pickle.dump(datathings, outf)