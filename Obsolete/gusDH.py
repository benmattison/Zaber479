import numpy as np
import sys

# # These lines are skew
# c1 = np.array([1,1,0])
# z1 = np.array([-1,0,0])
# c2 = np.array([0,0,1])
# z2 = np.array([1,1,0])

# # These lines intersect
# c1 = np.array([1,1,0])
# z1 = np.array([0,0,1])
# c2 = np.array([0,0,1])
# z2 = np.array([1,1,0])

# These lines are parallel
c1 = np.array([1,1,0])
z1 = np.array([0,0,1])
c2 = np.array([0,1,1])
z2 = np.array([0,0,-3])

A = np.array([[np.dot(z1,z1), -1.0*np.dot(z1,z2)],[np.dot(z1,z2), -1.0*np.dot(z2,z2)]])

print("A", A)

# if the lines are parallel, A will be singular
if np.linalg.cond(A) > sys.float_info.epsilon:
	print("the lines are parallel, we will use the point closest to c1")
	s = -1.0*np.dot(z2,c2-c1)/np.dot(z2,z2)
	param = np.array([0, s])
else:
	b = np.array([np.dot(z1,c1-c2)*-1.0, np.dot(z2,c1-c2)*-1.0])
	print("b", b)
	param = np.linalg.solve(A,b)

print("s,t", param)

L3 = c1+z1*param[0]-(c2+z2*param[1])
print("L3", L3)

print("L1 intersection", c1+z1*param[0])
print("L2 intersection", c2+z2*param[1])