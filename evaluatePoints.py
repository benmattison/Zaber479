import numpy as np
import scipy


class evalPoints(object):
	def __init__(self, points):
		# termination criteria
		self.points = points

	def lineAnalysis(self):
		# Determines the best fit of a set of 3 points, with the center point
		dataMean = self.points.mean(axis=0)
		uu, dd, vv = np.linalg.svd(self.points-dataMean)
		lineVect = vv[0]
		error = 0
		for v in self.points:
			point2line = np.linalg.norm(np.cross(lineVect,v-dataMean))
			error = error+point2line
		avgError = error/length(self.points)
		return vv[0], dataMean, avgError

	def circleAnalysis(self):
