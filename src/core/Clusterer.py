# from sklearn.cluster import Birch as ClustererAlgo
from sklearn.metrics import silhouette_score
from multiprocessing.dummy import Pool
import numpy as np
#drawer clusterer
def maximize_silhouette(iterator):
	"""
	maximize clusterer score, minimizes it's k

	Args:
		iterator : iterator of tupples of score,clusterer
	"""
	score=-float("inf")
	k=float("inf")
	ans=None
	for x,clusterer in iterator:
		if x>score:
			score=x
			ans=clusterer
			k=clusterer.k
		elif x==score: #colision
			if clusterer.k <= k:
				score=x
				ans=clusterer
				k=clusterer.k
	return score,ans


class Clusterer:
	"""
	Creates various Clusterer Objects and manages it's silhouette for each batch

	Args:
		algorithm (Clusterer class): clusterer algorithm to use
		kappa (ndarray): kappa set
		result_mode (string): {labels,centroids} mode to store the best results
	Attributes:
		best_clusterers (dict): dict that maps the best batch_index,k -> labels or centroids
	"""

	def __init__(self,algorithm,kappa,result_mode):
		self.algorithm=algorithm
		self.pool=Pool()
		self.__RESULT_FUNCTION={
			"labels":	lambda shelve:shelve.clusterer.labels_.astype(np.uint8).copy(),
			"centroids":lambda shelve:shelve.clusterer.cluster_centers_.astype(np.float64).copy()
		}[result_mode]
		self.drawer=[Shelve(self.algorithm,k) for k in kappa]
		self.best_clusterers=dict()
		self.batch_index=0

	def __handler(arg):
		clusterer,batch=arg
		clusterer.add(batch)
		score=clusterer.get_score(batch)
		print(f"{clusterer.k:2}, {score:.3f}")
		return score,clusterer
	
	def add_and_get_best_score(self,batch):
		"""
		Add batch to all clusterer and returns the k,silhouette of the best k
		
		Args:
			batch (ndarray):
		Returns:
			(k,silhouette)
		"""
		score,best=maximize_silhouette(
			self.pool.imap_unordered(
				Clusterer.__handler,((clusterer,batch) for clusterer in self.drawer)
			)
		)
		self.best_clusterers[(self.batch_index,best.k)]=self.__RESULT_FUNCTION(best)
		self.batch_index+=1
		return best.k,score

	def get_result(self,batch_index,k):
		"""
		Returns best label or centroid for given batch_index and k or None if not found
		
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
		if "partial_fit" in dir(self.clusterer):
			self.add=self.add_online
		else:
			self.add=self.add_offline

	def add_online(self,batch):
		self.clusterer.partial_fit(batch)

	def add_offline(self,batch):
		self.clusterer.fit(batch)

	def get_score(self,batch):
		try:
			return silhouette_score(batch,self.clusterer.labels_)
		except ValueError: #all values in labels are identical
			self.clusterer.labels_[-1]+=1
			try:
				ans=silhouette_score(batch,self.clusterer.labels_)
			except Exception:
				self.clusterer.labels_[-1]-=1
				print("ERROR COMPUTING SILHOUETTE, RETURNING -1")
				return -1
			self.clusterer.labels_[-1]-=1
			return ans
