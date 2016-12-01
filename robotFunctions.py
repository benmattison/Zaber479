import numpy as np
import sys
import sympy as sp

class robot(object)
	def __init__(self, origin, z0):
		self.origin = center1
		self.origins = [self.origin]
		# This should be a normalized vector in space
		self.z0 = z0/np.linalg.norm(z0)
		self.Zaxes = [self.z0]

		# Need to create a set of orthonormal vectors for the origin.
		arb = [0.0,0.0,1.0] # An arbitrary vector
		# To avoid uncertainty, avoid an arbitrary vector that is close to parallel with z0.
		if np.dot(z0, arb) > 0.99:
			arb = [0.0,1.0,0.0]

		# Find x0 using the cross product.
		x0 = np.cross(self.z0, arb);
		self.x0 = x0/np.linalg.norm(x0) # normalize it
		self.Xaxes = [self.x0]

		self.y0 = np.cross(self.x0, self.z0) # This will automatically be normalized
		self.Yaxes = [self.y0]

		self.numJoints = 0

	def add_joint(c, z, isRotary = True):
		# make sure z is normalized
		z /= np.linalg.norm(z)
		# Easiest one to add
		self.Zaxes.append(z)
		# Find the parameters that relate this joint to the last joint
		[c, x, d, theta, r, alpha] = calcParams(self.origins(-1), self.Zaxes(-1), self.Xaxes(-1),c,z)
		self.origins.append(c)
		self.Xaxes.append(x)
		self.Yaxes.append(np.cross(x,z))

		# Use symbolic math to allow us to make the transfoamrtion matrices editable later when we know joint values.
		j = sp.symbols('j'+str(len(self.numJoints)))

		# Only one degree of freedom per joint
		if isRotary:
			theta = theta+j
		else:
			d = d+j

		# These are the standard 4x4 transformation matrices based on DH conventions
		T1 = np.array([[np.cos(theta), -1.0*np.sin(theta), 0, 0],[np.sin(theta), np.cos(theta), 0, 0],[0, 0, 1, d],[0, 0, 0, 1]])
		T2 = np.array([[1,0,0,r],[0, np.cos(alpha), -1.0*np.sin(alpha), 0],[0, np.sin(alpha), np.cos(alpha), 0],[0, 0, 0, 1]])

		self.T  *= T1*T2

		self.numJoints += 1



	def calcParams(c1,z1,x1,c2,z2):
		# This array makes the equations for the shortest distance (perpendicular) between 2 lines into linear algebra
		A = np.array([[np.dot(z1,z1), -1.0*np.dot(z1,z2)],[np.dot(z1,z2), -1.0*np.dot(z2,z2)]])
		# A*d=b
		b = np.array([-1.0*np.dot(z1,c1-c2), -1.0*np.dot(z2,c1-c2)])

		# if the lines are parallel, A will be singular
		if np.linalg.cond(A) > sys.float_info.epsilon:
			print("the lines are parallel, we will use the point closest to c1")
			s = -1.0*np.dot(z2,c2-c1)/np.dot(z2,z2)
			[d1,d2] = np.array([0, s])
		else:
			b = np.array([np.dot(z1,c1-c2)*-1.0, np.dot(z2,c1-c2)*-1.0])
			print("b", b)
			[d1,d2] = np.linalg.solve(A,b)

		# Move the joint origin to the new point that is at the common normal
		c2 = c2+d2*z2
		# This is a DH parameter
		d = d1

		L = c2+z2*param[1]-(c1+z1*param[0]) # This is the vector of the common normal
		# This is a DH parameter
		r = np.linalg.norm(L)
		# points from 
		if r>0:
			x2 = L/r
		else: # if the joints have the same origin
			x2 = x1

		# This is a DH parameter
		theta = np.arccos(dot(x1,x2)) # This may have to be reversed, theta goes from old x to new x.

		# This is a DH parameter
		alpha = np.arccos(dot(z1,z2))


		return [c2, x2, d, theta, r, alpha]

	def calcEndEffPos(joint_params):
		if length(joint_params)
