import numpy as np
from sklearn.cluster import MiniBatchKMeans as ClustererAlgo
# from sklearn.cluster import Birch as ClustererAlgo
from sklearn.metrics import silhouette_score
from multiprocessing.dummy import Pool
from math import sqrt,ceil
#drawer clusterer
class Clusterer:
	def __add_shelve(self,k):
		c=Shelve(k,self.batch_size)
		self.drawer.append(c)

	def __init__(self,kc,kci,batch_size=None):
		self.kc=kc
		self.kci=kci
		self.batch_size=batch_size
		self.pool=Pool()
		self.drawer=[]
		self.__add_shelve(self.kc)

		maxn=ceil(sqrt(batch_size))
		for k in range(self.drawer[-1].k+self.kci,maxn+1,self.kci):
			# print(f"[KMEANS] CREATING k={k}")
			self.__add_shelve(k)
		# print(f"for k in range({self.drawer[-1].k+self.kci},{maxn+1},{self.kci}):")

	def __handler(arg):
		self,clusterer,batch=arg
		clusterer.add(batch)
		return clusterer.k,clusterer.get_score(batch)
	def add_and_get_score(self,batch):
		return self.pool.imap_unordered(Clusterer.__handler,((self,c,batch,) for c in self.drawer))

class Shelve:
	def __init__(self,k,batch_size=None):
		self.k=k
		self.clusterer=ClustererAlgo(
			n_clusters=k,
			# batch_size=batch_size
			)
		self.batch_size=batch_size
		self.labels=np.empty(0)
	def add(self,batch):
		self.clusterer.partial_fit(batch)
		if not self.labels.any():
			self.labels=self.clusterer.labels_
			return
		n=len(self.labels)
		self.labels.resize((n+len(self.clusterer.labels_)))
		self.labels[n:]=self.clusterer.labels_
	def get_score(self,datapoints):
		return silhouette_score(datapoints[-self.batch_size:],self.labels[-self.batch_size:])
