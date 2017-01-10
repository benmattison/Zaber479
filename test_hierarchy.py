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

	print "Finding COM ports..."
	# Identify COM ports, find the stages.
	port = zc.check_serial_ports()
	print "Initializing stages..."
	devices, numDevices = zc.initialize_zaber_serial(port, maxDevices=10)

	# Begin tracking end effector. At this point, all stages should be at 'home' position
	sqSize = userSettings["chessboardSquareSize"]
	track = st.StereoTracker(calConstants, sqSize)  # initialize stereo tracker
	track.initializeCameras(Lcam_int, Rcam_int, Lcam_exposure=-5, Rcam_exposure=-4, fps=30)

	return devices, numDevices, track


def get_device_points(track,devices,numDevices):
	device_points = []
	for i in range(numDevices):
		#print i
		points = rt.move_track_home(track, devices, i)
		device_points.append(points)
		print ""
		print "Tracked points for device " + str(i) + ": "
		print points
		time.sleep(2)
	return device_points


if __name__ == '__main__':

	settingsPath = "settingsLogi.json"

	devices, numDevices, track = init_devices_track_from_settings(settingsPath)

	print ""
	print "Align cameras so full robotic range of motion is in both views and press Q+ENTER"
	track.showMask('pink')
	print ""
	print "Starting tracking..."

	# Get initial data homing after every track
	device_points = get_device_points(track,devices,numDevices)

	#print ""
	#print "All tracked points: "
	#print device_points

	print ""
	evals = []
	rotary = []
	radii = []

	i = 0
	for points in device_points:
		evaluation = ev.evalPoints(points)

		evals.append(evaluation)

		isRotary, center, axis, radius, stepSize1k = evaluation.evaluate()
		rotary.append(isRotary)
		radii.append(radius)
		print "Details for device " + str(i) + ":"
		print("Rotary?", isRotary)
		print("Center Point", center)
		print("Axis", axis)
		print("Radius (mm)",radius)
		print("mm per 1000 steps", stepSize1k)
		print ""
		i+=1

	# Basic hierarchy algorithm starts now
	test_steps = 500000
	tolerance = 10 # in mm

	for i in range(numDevices):
		# different test for each rotary stage
		if rotary[i] == 1:
			print "Determining hierarchy for rotary stage " + str(i) + '...'
			print "Original radius of this stage motion is: "
			print radii[i]
			print ""
			for j in range(numDevices):
				# Don't try moving the test device
				print "Checking whether device " + str(j) + " is above or below device " + str(i) + "..."
				if j == i:
					print "They are the same stage"
					print ""
					continue
				devices[j].move_rel(test_steps)
				time.sleep(2)
				new_points = rt.move_track_home(track,devices,i)
				new_eval = ev.evalPoints(new_points)
				_, _, _, new_radius, _ = new_eval.evaluate()
				devices[j].home()
				time.sleep(2)

				print "New radius of the motion was: "
				print new_radius
				print ""
				# Check if radius changed
				if (abs(new_radius-radii[i]) > tolerance):
					print("Device " + str(j) + " is above device " + str(i) + " in the hierarchy")
				else:
					print("Device " + str(j) + " is below device " + str(i) + " in the hierarchy")
				print ""
				#TODO: Implement a stack/list to sort devices


	print "Finished checking hierarchy"

	us.print_wait("Continue...")
	track.close()