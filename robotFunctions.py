import numpy as np
import sys
import sympy as sp

class robot(object):
	def __init__(self, origin, z0):
		# Make sure they are inputting Numpy arrays.
		if type(origin).__module__ != np.__name__:
			print(type(origin).__module__)
			print(np.__name__)
			print(type(origin).__module__ == np.__name__)
			raise ValueError("origin must be a Numpy array")
		if type(z0).__module__ != np.__name__:
			raise ValueError("z0 must be a Numpy array")

		self.origin = origin
		self.origins = [self.origin]
		# This should be a normalized vector in space
		self.z0 = z0/np.linalg.norm(z0)
		self.Zaxes = [self.z0]

		# Need to create a set of orthonormal vectors for the origin.
		arb = np.array([0.0,0.0,1.0]) # An arbitrary vector
		# To avoid uncertainty, avoid an arbitrary vector that is close to parallel with z0.
		if np.dot(z0, arb) > 0.99:
			arb = ([0.0,1.0,0.0])

		# Find x0 using the cross product.
		x0 = np.cross(arb, self.z0);
		self.x0 = x0/np.linalg.norm(x0) # normalize it
		self.Xaxes = [self.x0]

		self.y0 = np.cross(self.z0, self.x0) # This will automatically be normalized
		self.Yaxes = [self.y0]

		self.numJoints = 0
		self.j_vars = []
		self.T = np.identity(4)

	def add_joint(self, c, z, isRotary = True):
		# make sure z is normalized
		print np.linalg.norm(z)
		z = z/np.linalg.norm(z)
		# Easiest one to add
		self.Zaxes.append(z)
		# Find the parameters that relate this joint to the last joint
		c, x, d, theta, r, alpha = self.calcParams(self.origins[-1], self.Zaxes[-1], self.Xaxes[-1],c,z)
		self.origins.append(c)
		self.Xaxes.append(x)
		self.Yaxes.append(np.cross(z,x))

		# Use symbolic math to allow us to make the transfoamrtion matrices editable later when we know joint values.
		j = sp.symbols('j'+str(self.numJoints))

		self.j_vars.append(j)

		# Only one degree of freedom per joint
		if isRotary:
			theta = theta+j
		else:
			d = d+j

		# These are the standard 4x4 transformation matrices based on DH conventions
		T1 = sp.Matrix([[sp.cos(theta), -1.0*sp.sin(theta), 0, 0],[sp.sin(theta), sp.cos(theta), 0, 0],[0, 0, 1, d],[0, 0, 0, 1]])
		print T1
		T2 = sp.Matrix([[1,0,0,r],[0, sp.cos(alpha), -1.0*sp.sin(alpha), 0],[0, sp.sin(alpha), sp.cos(alpha), 0],[0, 0, 0, 1]])
		print T2

		print T1*T2
		print self.T*T1

		self.T  = self.T*T1*T2

		self.numJoints += 1



	def calcParams(self,c1,z1,x1,c2,z2):
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

		L = c2+z2*d2-(c1+z1*d1) # This is the vector of the common normal
		# This is a DH parameter
		r = np.linalg.norm(L)
		# points from 
		if r>0:
			x2 = L/r
		else: # if the joints have the same origin
			x2 = x1

		# This is a DH parameter
		theta = np.arccos(np.dot(x1,x2)) # This may have to be reversed, theta goes from old x to new x.

		# This is a DH parameter
		alpha = np.arccos(np.dot(z1,z2))


		return c2, x2, d, theta, r, alpha

	def calcEndEffPos(self, joint_params):
		if len(joint_params) == self.numJoints:
			subvars = [(self.j_vars[i], joint_params[i]) for i in range(self.numJoints)]
			Treal = self.T.subs(subvars)
			print("Treal", Treal)
			return Treal
		else:
			print("Not enough information")
