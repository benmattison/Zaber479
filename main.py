import usefulFunctions as us
import zaberCommands as zc
import evaluatePoints as ev
import stereo_tracking as st
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
	# sys.exit()
elif len(camList) == 2:
	us.print_wait("Stereo cameras detected. Continue to initialize cameras.")
else:
	us.print_wait("Multiple cameras detected. You will need to select which cameras are which.")

Lcam_int, Rcam_int = us.select_cameras(camList)

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