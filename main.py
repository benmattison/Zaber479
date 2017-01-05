import usefulFunctions as us
# import zaberCommands as zc
import evaluatePoints as ev
import stereoTracking as st
import robotFunctions as rb
import calibrateCameras as cb
import zaberCommands as zc
import os
import test_runTests as rt

# The main function called for our software. There should not be a lot of code in here, most stuff should be done in other code.

# Welcome the user, get them to press enter to continue or allow them to quit.
welcomeMess = "Welcome to Gus, Dylan, and Ben's automatic robot analysis. For information on how to use the program, please see README.txt"
us.print_wait(welcomeMess)

EXIT_FLAG = False

# To add a state, add it to the dict and also include it in the prompt so users can know it is an option.
states = {"init" : 1, "main" : 2, "quit" : 3}
prompt = "What would you like to do? [1: Initialize, 2: Skip Initialization, 3: Quit]"

settingsPath = "settingsLogi.json"

while not EXIT_FLAG:
	startState = int(us.get_answer(prompt, [str(val) for val in states.values()]))

	if startState == states["quit"]:
		EXIT_FLAG = True
		continue

	elif startState == states["init"]:
		# this dict will hold the user settings until they are saved.
		userSettings = {}
		# Initiate cameras
		camList = us.find_cameras()

		if len(camList) < 2:
			us.print_wait("There are not enough cameras detected on this system. Please attach cameras and restart the program.")
			# sys.exit()
		elif len(camList) == 2:
			us.print_wait("Stereo cameras detected. Continue to initialize cameras.")
		else:
			us.print_wait("Multiple cameras detected. You will need to select which cameras are which.")

		Lcam_int, Rcam_int = cb.select_cameras(camList, exposure = -1, fps = 30)
		userSettings["Lcam"] = Lcam_int
		userSettings["Rcam"] = Rcam_int

		# Have the user select if they want to do a camera calibration or not. If not, load a default calibration.
		calPath = cb.find_calibration()
		sqSize = 37.67
		chessboardSize = [9,6]

		if not calPath:
			us.print_wait("No calibration file selected. You will need to take pictures.")
			saveFolder = raw_input("Please enter a name for the folder containing the images: ")
			if not saveFolder:
				saveFolder = "tempPhotos"
			us.print_wait("When the calibration pattern is in both frames, press 'p' to capture images")
			photoPath = cb.saveCaliPhotos(Lcam_int, Rcam_int, saveFolder)
			# Might as well give the calibration the same name as the folder of photos it comes from.
			calName = saveFolder

			calPath = cb.calibrateFromPics(chessboardSize,photoPath,calName)
			calConstants = cb.loadCalibration(calPath)
		userSettings["calPath"] = calPath
		userSettings["chessboardSquareSize"] = sqSize

		us.saveToJson(settingsPath, userSettings)

		startState = "main"

	if startState == states["main"]:
		if not os.path.isfile(settingsPath):
			print "Settings.json could not be located"
			continue

		userSettings = us.readJson(settingsPath)
		Lcam_int = userSettings["Lcam"]
		Rcam_int = userSettings["Rcam"]
		calConstants = cb.loadCalibration(userSettings["calPath"])
		if calConstants is None:
			print "Calibration settings at "+userSettings["calPath"]+" could not be found."
			continue

		# Identify COM ports, find the stages.
		ser,port = zc.check_serial_ports()
		devices, numDevices = zc.initialize_zaber_serial(port,maxDevices=10)


		# Begin tracking end effector. At this point, all stages should be at 'home' position
		sqSize = userSettings["chessboardSquareSize"]
		track = st.StereoTracker(calConstants,sqSize)  # initialize stereo tracker
		track.initializeCameras(Lcam_int, Rcam_int,exposure=-4,fps=30)

		# Have user align cameras
		print "Align cameras so full robotic range of motion is in both views"
		track.showVideo()

		# Move stages and save motion points.
		device_points = []
		for i in range(numDevices):
			print i
			device_points.append(rt.move_track_home(track, devices, i))

		print device_points

		# Evaluate the motion from those points.
		for points in device_points:
			evaluation = ev.evalPoints(points)

			print evaluation.lineAnalysis()
			print evaluation.circleAnalysis()
			isRotary, center, axis = evaluation.evaluate()
			print("Rotary?", isRotary)
			print("Center Point", center)
			print("Axis", axis)

			evaluation.plotPoints()
			us.print_wait("Continue...")

		track.close()

		# Determine the hierarchy of rotary stages

		# Output useful data about the axes of motion of the devices, including transformation matrices between stages.