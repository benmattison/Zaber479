import numpy as np

vectors = np.array([[1,2,3],[2,4,6],[3,6,9]])
vectors = vectors + np.random.normal(size=vectors.shape) * 0.05


def lineAnalysis(vectors):
	dataMean = vectors.mean(axis=0)
	uu, dd, vv = np.linalg.svd(vectors-dataMean)
	lineVect = vv[0]
	error = 0
	for v in vectors:
		point2line = np.linalg.norm(np.cross(lineVect,v-dataMean))
		error = error+point2line
	return vv[0], dataMean, error

print(lineAnalysis(vectors))