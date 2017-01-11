import stereoTracking as st
import usefulFunctions as us
import calibrateCameras as cb

settingsPath = "settingsLogi.json"
userSettings = us.readJson(settingsPath)
Lcam_int = userSettings["Lcam"]
Rcam_int = userSettings["Rcam"]
calConstants = cb.loadCalibration(userSettings["calPath"])

print calConstants
calConstants[8]=(1280,720)

sqSize = userSettings["chessboardSquareSize"]
track = st.StereoTracker(calConstants, sqSize)  # initialize stereo tracker
track.initializeCameras(Lcam_int, Rcam_int, Lcam_exposure=-5, Rcam_exposure=-5, fps=30)

track.showVideo()
track.showMask('pink')

track.close()