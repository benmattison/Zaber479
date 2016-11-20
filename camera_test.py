import stereo_tracking as st
import usefulFunctions as us
import cv2

sqSize = 37.67
mypath = "CalibrationPhotos/"
calFile = open(mypath + 'arbitrary_stereo_calibration_MinoruXL.pickle', 'rb')
track = st.StereoTracker(calFile,sqSize)  # initialize stereo tracker

# Initiate cameras
camList = us.find_cameras()
if len(camList) < 2:
	us.print_wait("There are not enough cameras detected on this system.")
	# sys.exit()
elif len(camList) == 2:
	us.print_wait("Stereo cameras detected. Continue to initialize cameras.")
else:
	us.print_wait("Multiple cameras detected. You will need to select which cameras are which.")

print(camList)

Lcam_int, Rcam_int = us.select_cameras(camList)

track.initializeCameras(Lcam_int, Rcam_int)

while True:
    track.showVideo()

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# cam = cv2.VideoCapture(1)
# cam.set(cv2.CAP_PROP_FORMAT,cv2.CV_8UC1)
# cam.set(cv2.CAP_PROP_FPS,5)
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
# cam.set(cv2.CAP_PROP_FRAME_WIDTH,320)
# while True:
#     ret = cam.grab()
#     if ret:
#         retR, capR = cam.retrieve()
#         retL, capL = cam.retrieve()
#
#     cv2.imshow('Rcam', capR)
#     cv2.imshow('Lcam', capL)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break