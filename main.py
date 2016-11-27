import usefulFunctions as us
# import zaberCommands as zc
import evaluatePoints as ev
import stereoTracking as st
import robotFunctions as rb
import calibrateCameras as cb
import zaberCommands as zc

# The main function called for our software. There should not be a lot of code in here, most stuff should be done in other code.

# Welcome the user, get them to press enter to continue or allow them to quit.
welcomeMess = "Welcome to Gus, Dylan, and Ben's automatic robot analysis. For information on how to use the program, please see README.txt"
us.print_wait(welcomeMess)

EXIT_FLAG = False

# To add a state, add it to the dict and also include it in the prompt so users can know it is an option.
states = {"init" : 1, "main" : 2, "quit" : 3}
prompt = "What would you like to do? [1: Initialize, 2: Skip Initialization, 3: Quit]"

settingsPath = "settings.json"

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

		Lcam_int, Rcam_int = cb.select_cameras(camList)
		userSettings["Lcam"] = Lcam_int
		userSettings["Rcam"] = Rcam_int

		# Have the user select if they want to do a camera calibration or not. If not, load a default calibration.
		calPath = cb.find_calibration()

		if not calPath:
			us.print_wait("No calibration file selected. You will need to take pictures.")
			saveFolder = raw_input("Please enter a name for the folder containing the images: ")
			if not saveFolder:
				saveFolder = "tempPhotos"
			us.print_wait("When the calibration pattern is in both frames, press 'p' to capture images")
			photoPath = cb.saveCaliPhotos(Lcam_int, Rcam_int, saveFolder)
			# Might as well give the calibration the same name as the folder of photos it comes from.
			calName = saveFolder
			calPath = cb.calibrateFromPics([9,6],photoPath,calName)
			calConstants = cb.loadCalibration(calPath)
		userSettings["calPath"] = calPath

		us.saveToJson(settingsPath, userSettings)

		startState = "main"

	if startState == states["main"]:
		userSettings = us.readJson(settingsPath)
		Lcam_int = userSettings["Lcam"]
		Rcam_int = userSettings["Rcam"]
		calConstants = cb.loadCalibration(userSettings["calPath"])

		# Identify COM ports, find the stages.
		ser,port = zc.check_serial_ports()
		devices,numDevices = zc.initialize_zaber_serial(port,maxDevices=10)


		# Begin tracking end effector. At this point, all stages should be at 'home' position
		sqSize = 37.67
		track = st.StereoTracker(calFile,sqSize)  # initialize stereo tracker
		track.initializeCameras(Lcam_int, Rcam_int)

		# Move stage 1 twice and save motion points.
		microSteps=200000
		x = [0,0,0]
		y = [0,0,0]
		z = [0,0,0]
		points = {}
		for i in range(0,numDevices-1):
			devices[i].move_rel(microSteps)
			x[0],y[0],z[0] = track.trackBall('pink')
			devices[i].move_rel(microSteps)
			x[1],y[1],z[1] = track.trackBall('pink')
			devices[i].move_rel(microSteps)
			x[2],y[2],z[2] = track.trackBall('pink')
			points[i] = (x,y,z)


		# Evaluate the motion from those points.


		# ...

		# Determine the hierarchy of rotary stages

		# Output useful data about the axes of motion of the devices, including transformation matrices between stages.