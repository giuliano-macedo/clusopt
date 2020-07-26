from core.utils import DistanceTable
from sklearn.metrics import pairwise_distances
class DistanceMatrixAlgorithm:
	__available_algs={"custom","sklearn"}
	def __init__(self,method,max_size):
		"""
		Swithces matrix distances computation methods

		Args:
			method (str): name of the method
			max_size (str): to set matrix as max_size X max_size
		"""
		assert(method in DistanceMatrixAlgorithm.__available_algs)
		getattr(self,method+"_setup")(max_size)
		self.compute=getattr(self,method+"_compute")

	def compute(self,batch):
		"""will be overloaded by corresponding alg"""
		pass

	def sklearn_setup(self,max_size):pass

	def custom_setup(self,max_size):
		self.dist_table=DistanceTable(max_size=max_size)

	def sklearn_compute(self,batch):
		return pairwise_distances(batch,n_jobs=1) #n_jobs>1 gets slower

	def custom_compute(self,batch):
		return self.dist_table.compute(batch)
