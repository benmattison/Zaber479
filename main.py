import usefulFunctions as us
import pickle
import sys

# The main function called for our software. There should not be a lot of code in here, most stuff should be done in other code.

# Welcome the user, get them to press enter to continue or allow them to quit.
welcomeMess = "Welcome to Gus, Dylan, and Ben's automatic robot analysis. For information on how to use the program, please see README.txt"
us.print_wait(welcomeMess)

# Initiate cameras
camList = us.find_cameras()
if len(camList) < 2:
	us.print_wait("There are not enough cameras detected on this system.")
	sys.exit()

# Have the user select if they want to do a camera calibration or not. If not, load a default calibration.
calFile = find_calibration()

if calFile:
	calConstants = pickle.load(calFile)
else:
# certain = False
# while not certain:
# 	answer = us.get_bool("\nWould you like to calibrate the cameras?")
# 	action = {True:"perform camera calibration",False:"skip camera calibration and use default parameters"}[answer]
# 	certain = us.get_bool("\nAre you srue you want to "+action+"?")
# if answer:
# 	us.dumFunc("calibrateCameras")
	us.dumFunc("calibrateCameras")


# For calibration, have markers on the screen that identify where the pattern should go. Automatically take pictures when it is there.
# Save the calibration data to a readable file.

# Identify COM ports, find the stages.

# Begin tracking end effector

# Move stage 1 twice and save motion points.
# Evaluate the motion from those points.

# ...

# Determine the heirarchy of rotary stages

# Output useful data about the axes of motion of the devices, including transformation matrices between stages.