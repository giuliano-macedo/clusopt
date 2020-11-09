from multiprocessing.dummy import Pool
import numpy as np
from . import DistanceMatrixAlgorithm
from clusopt_core.metrics import Silhouette
#drawer clusterer
def maximize_silhouette(iterator):
	"""
	maximize clusterer score, minimizes it's k when there is a draw

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
		elif x==score and clusterer.k <= k: #colision
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
		distance_matrix_method (str) : distance matrix algorithm to use
		batch_size (int): length of each batch
	Attributes:
		best_clusterers (dict): dict that maps the best batch_index,k -> labels or centroids
	"""

	def __init__(self,algorithm,kappa,distance_matrix_method,batch_size):
		self.algorithm=algorithm
		self.distance_matrix_algorithm=DistanceMatrixAlgorithm(
			method=distance_matrix_method,
			max_size=batch_size
		)
		self.pool=Pool()
		self.drawer=[Shelve(self.algorithm,k) for k in kappa]
		self.best_clusterers=dict()
		self.batch_index=0

	def __handler(arg):
		clusterer,batch,dist_matrix=arg
		clusterer.add(batch)
		score=clusterer.get_score(dist_matrix)
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
		dist_matrix=self.distance_matrix_algorithm.compute(batch)
		score,best=maximize_silhouette(
			self.pool.imap_unordered(
				Clusterer.__handler,((clusterer,batch,dist_matrix) for clusterer in self.drawer)
			)
		)
		self.distance_matrix_algorithm.clean()
		best_cluster_center=best.clusterer.cluster_centers_.astype(np.float64).copy()
		self.best_clusterers[(self.batch_index,best.k)]=best_cluster_center
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
		self.silhouette=Silhouette(n_clusters=k)
		if "partial_fit" in dir(self.clusterer):
			self.add=self.add_online
		else:
			self.add=self.add_offline

	def add_online(self,batch):
		self.clusterer.partial_fit(batch)

	def add_offline(self,batch):
		self.clusterer.fit(batch)

	def get_score(self,dist_matrix):
		try:
			return self.silhouette.get_score(dist_matrix,self.clusterer.labels_)
		except IndexError: # number of labels != dist_matrix number of rows/columns
			n=len(self.clusterer.labels_)
			dist_matrix=dist_matrix[:n,:n]
			return self.silhouette.get_score(dist_matrix,self.clusterer.labels_)
