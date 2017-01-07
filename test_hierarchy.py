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


def init_devices_track_from_settings(settingsPath):
	if not os.path.isfile(settingsPath):
		print settingsPath + " could not be located"

	userSettings = us.readJson(settingsPath)
	Lcam_int = userSettings["Lcam"]
	Rcam_int = userSettings["Rcam"]
	calConstants = cb.loadCalibration(userSettings["calPath"])
	if calConstants is None:
		print "Calibration settings at " + userSettings["calPath"] + " could not be found."

	# Identify COM ports, find the stages.
	port = zc.check_serial_ports()
	devices, numDevices = zc.initialize_zaber_serial(port, maxDevices=10)

	# Begin tracking end effector. At this point, all stages should be at 'home' position
	sqSize = userSettings["chessboardSquareSize"]
	track = st.StereoTracker(calConstants, sqSize)  # initialize stereo tracker
	track.initializeCameras(Lcam_int, Rcam_int, Lcam_exposure=-4, Rcam_exposure=-4, fps=30)

	return devices, numDevices, track


def get_device_points(track,devices,numDevices):
	device_points = []
	for i in range(numDevices):
		print i
		device_points.append(rt.move_track_home(track, devices, i))
		time.sleep(2)
	return device_points


if __name__ == '__main__':

	settingsPath = "settingsLogi.json"

	devices, numDevices, track = init_devices_track_from_settings(settingsPath)

	print "Align cameras so full robotic range of motion is in both views and press Q+ENTER"
	track.showVideo()

	# Get initial data homing after every track
	device_points = get_device_points(track,devices,numDevices)

	print device_points

	evals = []
	rotary = []
	radii = []

	for points in device_points:
		evaluation = ev.evalPoints(points)

		evals.append(evaluation)

		isRotary, center, axis, radius, stepSize1k = evaluation.evaluate()
		rotary.append(isRotary)
		radii.append(radius)
		print("Rotary?", isRotary)
		print("Center Point", center)
		print("Axis", axis)
		print("Radius",radius)
		print("mm per 1000 steps", stepSize1k)

	# Basic hierarchy algorithm starts now
	test_steps = 500000
	tolerance = 10 # in mm

	for i in range(numDevices):
		# different test for each rotary stage
		if rotary[i] == 1:
			print("Original Radius", radii[i])
			for j in range(numDevices):
				# Don't try moving the test device
				if j == i:
					continue
				devices[j].move_rel(test_steps)
				new_points = rt.move_track_home(track,devices,i)
				new_eval = ev.evalPoints(new_points)
				_, _, _, new_radius, _ = new_eval.evaluate()
				devices[j].home()
				time.sleep(2)

				print("New Radius", new_radius)
				# Check if radius changed
				if (abs(new_radius-radii[i]) > tolerance):
					print("Device " + str(j) + " is above device " + str(i) + " in the hierarchy")
				else:
					print("Device " + str(j) + " is below device " + str(i) + " in the hierarchy")
				#TODO: Implement a stack/list to sort devices


	us.print_wait("Continue...")
	track.close()