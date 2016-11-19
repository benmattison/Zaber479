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