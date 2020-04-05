import os
from sklearn.cluster import KMeans
try:
	from .clustream import CluStream as CluStream_
except ImportError:
	backup=os.getcwd()
	print("compiling CluStream")
	os.chdir(os.path.join(os.path.dirname(__file__),"src"))
	os.system("make")
	os.chdir("..")
	try:
		from .clustream import CluStream as CluStream_
	except ImportError:
		raise ImportError("Something went wrong in the compilation")
	os.chdir(backup)

class CluStream(CluStream_):
	def init_offline(self,init_points,seed=0,n_init=1):
		"""
		initialize microclusters using kmeans++

		Args:
			init_points (ndarray): points to initialize
			seed (int): 
			n_init (init): number of kmeans runs
		"""
		cluster_centers=KMeans(
			n_clusters=self.m,
			init="k-means++",
			random_state=seed,
			n_init=n_init
		).fit(init_points).cluster_centers_
		self.init_kernels_offline(cluster_centers,init_points)