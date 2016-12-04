import usefulFunctions as us
import evaluatePoints as ev
import stereoTracking as st
import robotFunctions as rb
import calibrateCameras as cb
import zaberCommands as zc

settingsPath = "settings.json"

if not os.path.isfile(settingPath):
	print "Settings.json could not be located"

userSettings = us.readJson(settingsPath)
Lcam_int = userSettings["Lcam"]
Rcam_int = userSettings["Rcam"]
calConstants = cb.loadCalibration(userSettings["calPath"])
if calConstants is None:
	print "Calibration settings at "+userSettings["calPath"]+" could not be found."

# Identify COM ports, find the stages.
ser,port = zc.check_serial_ports()
devices, numDevices = zc.initialize_zaber_serial(port,maxDevices=10)

# Begin tracking end effector. At this point, all stages should be at 'home' position
sqSize = 37.67
track = st.StereoTracker(userSettings["calPath"],sqSize)  # initialize stereo tracker
track.initializeCameras(Lcam_int, Rcam_int)

def move_track_home(track, devices, device_int, num_moves = 3, num_steps = 200000):
	points = []
	for i in range(num_moves):
		points.append(track.trackBall('pink'))
		devices[device_int].move_rel(num_steps)
		time.sleep(2)
	devices[device_int].home()

device_points = []
for i in range(len(devices)):
	device_points.append(move_track_home(track, devices, i))

print device_points
