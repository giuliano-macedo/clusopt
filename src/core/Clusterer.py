import numpy as np
from sklearn.cluster import MiniBatchKMeans
# from sklearn.cluster import Birch as ClustererAlgo
from sklearn.metrics import silhouette_score
from multiprocessing.dummy import Pool
#drawer clusterer
class Clusterer:
	def __add_shelve(self,k):
		c=Shelve(k,self.batch_size)
		self.drawer.append(c)

	def __init__(self,kappa,batch_size=None):
		self.batch_size=batch_size
		self.pool=Pool()
		self.drawer=[]
		for k in kappa:
			self.__add_shelve(k)

	def __handler(arg):
		self,clusterer,batch=arg
		clusterer.add(batch)
		return clusterer.k,clusterer.get_score(batch)
	def add_and_get_score(self,batch):
		return self.pool.imap_unordered(Clusterer.__handler,((self,c,batch,) for c in self.drawer))

class Shelve:
	def __init__(self,k,batch_size=None):
		self.k=k
		self.clusterer=MiniBatchKMeans(
			n_clusters=k,
			batch_size=batch_size
		)
		self.batch_size=batch_size
		self.labels=np.empty(0)
	def add(self,batch):
		self.clusterer.partial_fit(batch)
		if not self.labels.any():
			self.labels=self.clusterer.labels_.astype(np.uint8)
			return
		n=len(self.labels)
		self.labels.resize((n+len(self.clusterer.labels_.astype(np.uint8))))
		self.labels[n:]=self.clusterer.labels_
	def get_score(self,batch):
		l=len(batch)
		try:
			return silhouette_score(batch,self.labels[-l:])
		except ValueError: #all values in labels are identical
			self.labels[-1]+=1
			try:
				ans=silhouette_score(batch,self.labels[-l:])
			except Exception:
				self.labels[-1]-=1
				print("ERROR COMPUTING SILHOUETTE, RETURNING -1")
				return -1
			self.labels[-1]-=1
			return ans
