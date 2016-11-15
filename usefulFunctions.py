import cv2
import sys
import os
import fnmatch

def dumFunc(funcName):
	# dummy function, doesn't do anything.
	print("Doing "+funcName)

def get_bool(prompt):
	while True:
		try:
			answer = raw_input(prompt+" (y or n)")
			return {'y':True,'n':False}[answer]
		except KeyError:
			print "Invalid input please enter 'y' or 'n'!"

def get_answer(prompt, answerList):
	choiceStr = "("
	for answer in answerList:
		choiceStr += answer+", "
	choiceStr += ")"
	answered = False
	while not answered:
		answer = raw_input(prompt+choiceStr)
		if answer in answerList:
			return answer
		print "Invalid response!"

def print_wait(message):
	response = raw_input(message+"\n [Press ENTER to continue or Q+ENTER to quit]").lower()
	if 'q' in response:
		print "exiting"
		sys.exit()

def find_calibration():
	directory = 'Calibration'
	if not os.path.exists(directory):
		makeFolder = get_bool("Cannot find the calibration folder, do you want to create one?")
		if makeFolder:
			os.makedirs(directory)
			return None
	else:
		for file in os.listdir(directory):
			if fnmatch.fnmatch(file, 'calibration*.pickle'):
				usePickle = get_bool("Found calibration file "+file+"\nDo you want to use this?")
				if usePickle:
					return file
	return None


def find_cameras():
	cam_list = []
	for cam_int in range(6):
		cam = cv2.VideoCapture(cam_int)
		if cam.isOpened():
			cam_list.append(cam_int)
	return cam_list


