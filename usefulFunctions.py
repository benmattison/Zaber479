import cv2
import sys
import os
import json

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
	answered = False
	while not answered:
		answer = raw_input(prompt)
		if answer in answerList:
			return answer
		print "Invalid response!"

def print_wait(message):
	response = raw_input(message+"\n [Press ENTER to continue or Q+ENTER to quit]").lower()
	if 'q' in response:
		print "exiting"
		sys.exit()

def saveToJson(fpath, dataDict):
	try:
		with open(fpath, 'w') as f:
			json.dump(dataDict, f)
			f.close()
	except Exception as e:
		print e
		return False
	return True

def readJson(fpath):
	with open(fpath, 'r') as f:
		params = json.load(f)
		return params

def find_cameras():
	cam_list = []
	for cam_int in range(6):
		cam = cv2.VideoCapture(cam_int)
		if cam.isOpened():
			cam_list.append(cam_int)
	return cam_list