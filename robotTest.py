import numpy as np
import robotFunctions as rb

c0 = np.array([0,0,0])
z0 = np.array([0,0,1])

robo1 = rb.robot(c0,z0)

print robo1.x0
print robo1.y0

robo1.add_joint(c0,z0,True)

print robo1.T

print robo1.calcEndEffPos([np.pi])