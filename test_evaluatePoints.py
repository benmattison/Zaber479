import evaluatePoints as ev
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cv2
import pickle


lineVectors = np.array([[1,2,3],[2,4,6],[3,6,9]])
circleVectors = np.array([[0,0,0],[2,0,0],[2,2,2]])

infile = open('pathPoints.pickle', 'rb')
pathPoints = pickle.load(infile)

vectors = pathPoints

print vectors

# vectors = vectors + np.random.normal(size=vectors.shape) * 0.05

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(vectors[0],vectors[1],vectors[2])

fig.show()

x = raw_input('press enter:\n')

ev = ev.evalPoints(vectors)

# print ev.lineAnalysis()
# print ev.circleAnalysis()
isRotary, center, axis = ev.evaluateArbitrary()
print("Rotary?", isRotary)
print("Center Point", center)
print("Axis", axis)