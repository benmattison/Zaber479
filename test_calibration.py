import stereoTracking as st
import cv2
import usefulFunctions as us
import calibrateCameras as cb

settingsPath = 'settingsLogi.json'
userSettings = us.readJson(settingsPath)
calConstants = cb.loadCalibration(userSettings["calPath"])
sqSize = userSettings["chessboardSquareSize"]

track = st.StereoTracker(calConstants, sqSize)  # initialize stereo tracker

picturePath = "C:\UBC\5th Year\ENPH479\Code\Zaber479\CalibrationPhotos\Logitech_EpsiodeV_smallSquares"

