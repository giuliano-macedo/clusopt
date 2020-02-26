# from sklearn.cluster import Birch as ClustererAlgo
from sklearn.metrics import silhouette_score
from multiprocessing.dummy import Pool
import numpy as np
#drawer clusterer
class Clusterer:
	"""
	Creates various Clusterer Objects and manages it's silhouette for each batch

	Args:
		algorithm (Clusterer class): clusterer algorithm to use
		kappa (ndarray): kappa set
	Attributes:
		best_clusterers (dict): dict that maps the best batch_index,k -> label
	"""

	def __init__(self,algorithm,kappa):
		self.algorithm=algorithm
		self.pool=Pool()
		self.drawer=[Shelve(self.algorithm,k) for k in kappa]
		self.best_clusterers=dict()
		self.batch_index=0

	def __handler(arg):
		clusterer,batch=arg
		clusterer.add(batch)
		score=clusterer.get_score(batch)
		print(f"{clusterer.k:2}, {score:.2f}")
		return clusterer,score
	
	def add_and_get_best_score(self,batch):
		"""
		Add batch to all clusterer and returns the k,silhouette of the best k
		
		Args:
			batch (ndarray):
		Returns:
			(k,silhouette)
		"""
		best,score=min(
			self.pool.imap_unordered(
				Clusterer.__handler,((clusterer,batch) for clusterer in self.drawer)
			),
			key=lambda t:t[1] #sil
		)
		self.best_clusterers[(self.batch_index,best.k)]=best.labels.copy()
		self.batch_index+=1
		return best.k,score

	def get_best_label(self,batch_index,k):
		"""
		Returns best label for given batch_index and k or None if not found
		
		Args:
			batch_index (int):
			k (int):

		Returns:
			(ndarray or None)
		"""
		return self.best_clusterers.get((batch_index,k),None)



class Shelve:
	def __init__(self,algorithm,k):
		self.k=k
		self.clusterer=algorithm(n_clusters=k)
	def add(self,batch):
		self.clusterer.partial_fit(batch)
		self.labels=self.clusterer.labels_.astype(np.uint8)
	def get_score(self,batch):
		try:
			return silhouette_score(batch,self.labels)
		except ValueError: #all values in labels are identical
			self.labels[-1]+=1
			try:
				ans=silhouette_score(batch,self.labels)
			except Exception:
				self.labels[-1]-=1
				print("ERROR COMPUTING SILHOUETTE, RETURNING -1")
				return -1
			self.labels[-1]-=1
			return ans
