import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class evalPoints(object):
	def __init__(self, points):
		# termination criteria
		self.points = points

	def lineAnalysis(self):
		# Determines the best fit of a set of 3 points, with the center point
		dataMean = np.mean(self.points,axis=0)
		uu, dd, vv = np.linalg.svd(self.points-dataMean)
		lineVect = vv[0]
		SSres = 0
		SStot = 0
		for v in self.points:
			point2line = np.linalg.norm(np.cross(lineVect,v-dataMean))
			SSres = SSres+point2line*point2line
			SStot = SStot+np.linalg.norm(v-dataMean)*np.linalg.norm(v-dataMean)
		Rsquare = 1-SSres/SStot
		return lineVect, dataMean, Rsquare

	def circleAnalysis(self):
		# Determine the radius and center of a circle

		#setting the points
		A = self.points[0]
		B = self.points[1]
		C = self.points[2]
		# Lengths of sides opposite to parent point, ex. Point A is opposite to side a
		a = np.linalg.norm(C - B)
		b = np.linalg.norm(C - A)
		c = np.linalg.norm(B - A)

		# Radius (r) equation of Circumcircle of a Triangle
		s = (a + b + c) / 2
		r = a * b * c / 4 / np.sqrt(s * (s - a) * (s - b) * (s - c))

		# location of circle center (cc) using circumcenter barcyntric coordinated
		b1 = a * a * (b * b + c * c - a * a)
		b2 = b * b * (a * a + c * c - b * b)
		b3 = c * c * (a * a + b * b - c * c)
		cc = np.column_stack((A, B, C)).dot(np.hstack((b1, b2, b3)))
		cc /= b1 + b2 + b3

		#Getting normal vector for circle
		normalVector = np.cross(A-C, B-C)
		normalVector /= np.linalg.norm(normalVector)

		#calculating the angle of the plane to the x, y plane
		normalXY = [0, 0, 1] #normal vecor to x,y plane
		theta = np.arccos(np.dot(normalVector, normalXY))

		return r, cc, normalVector, theta

	def evaluate(self):
		circ_r, circ_cent, circ_axis, theta = self.circleAnalysis()
		line_vect, line_cent, line_Rs = self.lineAnalysis()

		if line_Rs > 0.99:
			isRotary = 0
			centerPoint = line_cent
			axisVect = line_vect

		else:
			isRotary = 1
			centerPoint = circ_cent
			axisVect = circ_axis

		return isRotary, centerPoint, axisVect

	def plotPoints(self):
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		printPoints = np.array(self.points)
		minP = np.amin(printPoints)
		maxP = np.amax(printPoints)
		ax.scatter(printPoints[:,0],-1*printPoints[:,1],printPoints[:,2],zdir = 'y')

		# ax.set_xlim3d(minP-100,maxP+100)
		# ax.set_ylim3d(minP-100,maxP+100)
		# ax.set_zlim3d(0,maxP+100)
		ax.set_xlim3d(-100,100)
		ax.set_ylim3d(0,1000)
		ax.set_zlim3d(-100,100)


		fig.show()

def plotAll(evals):
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	for evalu in evals:
		printPoints = np.array(evalu.points)
		ax.scatter(printPoints[:, 0], -1 * printPoints[:, 1], printPoints[:, 2], zdir='y')

	ax.set_xlim3d(-200, 200)
	ax.set_ylim3d(500, 2000)
	ax.set_zlim3d(-200, 200)

	fig.show()
