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
        # Determine the radius and center of a circle

        #setting the points
        A = self.points.points1
        B = self.points.points2
        C = self.points.points3
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
	    normalvector = np.cross(a, b)

        return r cc normalvector



