import numpy as np
from sympy import *


class TransformationMatrix(object):
    def __init__(self, z_vector):
        self.z_vector = z_vector


    #This function is used to find an arbitry vector that is perpendicular
    # to a given vector.
    def perpendicular_vector(self,z_vector):

        if (z_vector.x) == 0 and (z_vector.y) == 0:
            if (z_vector.z) == 0:
                # Zvector is Vector(0, 0, 0)
                raise ValueError('zero vector')

            # zvector is Vector(0, 0, z_vector.z)
            # return xvector (0, z_vector.z, 0)
            return (0, z_vector.z, 0)

        return (-z_vector.y, z_vector.x, 0)



    #This function checks to see if to lines intersect
    # Equations of lines are represented by a point and a scalar multiplied by a vector
    # eg. z0 = z_0 + t*z0_vector
    # eg. z1 = z_1 + s*z1_vector
    # The lines intersect if there is a s and t that satisfy the linear system
    # if the lines intersect return the point of intersection if not return false
    def point_of_intersection(self, z0_vector, z_0, z1_vector, z_1):

        # solving for coefficients of two parametrized lines if they satisfy linear system then lines intersect
        M = Matrix([[z0_vector[0], -z1_vector[0], -z_0[0] + z_1[0]], [z0_vector[1], -z1_vector[1], -z_0[1] + z_1[1]]])

        RREF = M.rref()[0]
        t = RREF[0,2]
        s = RREF[1,2]

        # if the equation is satisfied the point of intersection is such that z0 = z1
        if (z_0 + t*z0_vector) == (z_1 + s*z1_vector):
            return (z_0 + t*z0_vector)

        else:
           return False




    # An equation of a plane is described by its normal vector represented by ax + by + cz + d = 0
    # This function finds the equation of a plane of the common perpendicular between two lines and the original line
    # This is computed by finding the common perpendicular and taking the determiniant of the point in line 1,
    # vector1, and common perpendicular ie cross product(vector1 X vector2)
    #
    #   | (x-O1[0])  (y-O1[1])  (z-O1[2])  |
    #   | vector1[0] vector1[1] vector1[2] |  = 0
    #   |  cross[0]   cross[1]   cross[2]  |
    #
    # This determinant will give you the coefficients for equaiton of the plane
    def equation_of_plane_common_perpendicular(self, vector1, O1, vector2, O2):

        cross_product = np.cross(vector1,vector2)

        a = cross_product[0]
        b = cross_product[1]
        c = cross_product[2]
        #note the negative because (x - O1) ect.
        d = - (cross_product[0] * O1[0] + cross_product[1] * O1[1] + cross_product[2] * O1[2])

        return a, b, c, d

    # This function determines the equation of the orthonormal line
    # between to lines
    # 3 cases: 1- lines intersect
    #          2- lines are parallel
    #          3- lines do not intersect and are not parallel
    def orthonormal_line(self, z0_vector, z_0, z1_vector, z_1):

        # Calculating the cross product between two vectors gives orthogonal
        # vector to both vectors.
        # Check to see if z1_vector is already orthogonal if it is set ortho_vector = z1_vector
        ortho_vector = np.cross(z0_vector, z1_vector)

        if np.any(ortho_vector) == False:
            ortho_vector = z1_vector

        # Case 1 Lines intersect , set origin to be z_0 and vector to be ortho_vector
        intersection_point = point_of_intersection(z0_vector, z_0, z1_vector, z_1)
        if intersection_point!= False:







