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
		self.clean=getattr(self,method+"_clean")

	def compute(self,batch):
		"""will be overloaded by corresponding alg"""
		pass

	def sklearn_setup(self,max_size):pass

	def custom_setup(self,max_size):
		self.dist_table=DistanceTable(max_size=max_size)

	def sklearn_compute(self,batch):
		self.last_ans=pairwise_distances(batch,n_jobs=1) #n_jobs>1 gets slower
		return self.last_ans

	def custom_compute(self,batch):
		if batch.shape[0]!=self.dist_table.table.shape[0]:
			print("counter measure triggered")
			return DistanceTable(max_size=batch.shape[0]).compute(batch)
		return self.dist_table.compute(batch)

	def sklearn_clean(self):
		del(self.last_ans) 

	def custom_clean(self):pass #don't delete the matrix, it will be used next time
