import usefulFunctions as us
import evaluatePoints as ev
import stereoTracking as st
import robotFunctions as rb
import calibrateCameras as cb
import zaberCommands as zc
import os
import time
import numpy as np


def move_track_home(track, devices, device_int, num_moves = 2, num_steps = 300000):
	points = []
	points.append(track.trackBall('pink')) # take pic/points at home position
	for i in range(num_moves):
		while track.trackBall('pink') is None:
			print "Ball not located in both cameras... re-align cameras and press Q+ENTER"
			# This error basically just means the entire tracking is messed up...
			track.showVideo()
		devices[device_int].move_rel(num_steps)
		points.append(track.trackBall('pink'))
		time.sleep(2)
	devices[device_int].home()
	return np.array(points)

if __name__ == '__main__':

	settingsPath = "settingsLogiBen.json"

	if not os.path.isfile(settingsPath):
		print settingsPath+" could not be located"

	userSettings = us.readJson(settingsPath)
	Lcam_int = userSettings["Lcam"]
	Rcam_int = userSettings["Rcam"]
	calConstants = cb.loadCalibration(userSettings["calPath"])
	if calConstants is None:
		print "Calibration settings at "+userSettings["calPath"]+" could not be found."

	# Identify COM ports, find the stages.
	port = zc.check_serial_ports()
	devices, numDevices = zc.initialize_zaber_serial(port,maxDevices=10)

	# Begin tracking end effector. At this point, all stages should be at 'home' position
	sqSize = userSettings["chessboardSquareSize"]
	track = st.StereoTracker(calConstants,sqSize)  # initialize stereo tracker
	track.initializeCameras(Lcam_int, Rcam_int,exposure=-4,fps=30)
	print "Align cameras so full robotic range of motion is in both views and press Q+ENTER"
	track.showVideo()

	device_points = []
	for i in range(numDevices):
		print i
		device_points.append(move_track_home(track, devices, i))
		time.sleep(2)

	print device_points

	evals = []

	for points in device_points:
		evaluation = ev.evalPoints(points)

		evals.append(evaluation)

		# print evaluation.lineAnalysis()
		# print evaluation.circleAnalysis()
		isRotary, center, axis = evaluation.evaluate()
		print("Rotary?", isRotary)
		print("Center Point", center)
		print("Axis", axis)

		evaluation.plotPoints()
		us.print_wait("Continue...")

	ev.plotAll(evals)
	us.print_wait("Continue...")
	track.close()