import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Data for three points
A = np.array([2.0, 1.5, 0.0])
B = np.array([6.0, 4.5, 0.0])
C = np.array([11.75, 6.25, 0.0])

#Lengths of sides opposite to parent point. Point A is opposite side a
a = np.linalg.norm(C - B)
b = np.linalg.norm(C - A)
c = np.linalg.norm(B - A)

#Radius equation of Circumcircle of a Triangle
s = (a + b + c) / 2
R = a*b*c / 4 / np.sqrt(s * (s - a) * (s - b) * (s - c))

#location of circle using circumcenter barcyntric coordinated
b1 = a*a * (b*b + c*c - a*a)
b2 = b*b * (a*a + c*c - b*b)
b3 = c*c * (a*a + b*b - c*c)
P = np.column_stack((A, B, C)).dot(np.hstack((b1, b2, b3)))
P /= b1 + b2 + b3

print(R)
print(P)
