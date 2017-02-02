import usefulFunctions as us
import evaluatePoints as ev
import stereoTracking as st
import robotFunctions as rb
import calibrateCameras as cb
import zaberCommands as zc
import os
import time
import numpy as np
import test_runTests as rt
import Tkinter as tk

if __name__ == '__main__':

	settingsPath = "settingsLogi.json"

	if not os.path.isfile(settingsPath):
		print settingsPath + " could not be located"

	userSettings = us.readJson(settingsPath)
	Lcam_int = userSettings["Lcam"]
	Rcam_int = userSettings["Rcam"]
	calConstants = cb.loadCalibration(userSettings["calPath"])
	if calConstants is None:
		print "Calibration settings at " + userSettings["calPath"] + " could not be found."

	# Begin tracking end effector. At this point, all stages should be at 'home' position
	sqSize = userSettings["chessboardSquareSize"]
	track = st.StereoTracker(calConstants, sqSize)  # initialize stereo tracker
	track.initializeCameras(Lcam_int, Rcam_int, Lcam_exposure=-5, Rcam_exposure=-5, fps=30)

	print ""
	print "Align cameras so full robotic range of motion is in both views and press Q+ENTER"
	track.showMaskTune('pink')
	print ""
	print "Starting tracking..."

	track.close()