import cv2

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

def find_cameras():
	for cam_int in 