from primary.core import CluStream,Streamkm
from sklearn.cluster import KMeans,MiniBatchKMeans

from abc import ABC,abstractmethod

class StaticGeneric(ABC):

	# batch_size and NAME members are abstract

	@abstractmethod
	def partial_fit(self,chunk):pass

	@abstractmethod
	def get_partial_cluster_centers(self):pass

	@abstractmethod
	#should return (center,labels)
	def get_final_cluster_centers(self)->tuple:pass

class StaticClustream(StaticGeneric):
	NAME="clustream"

	def __init__(self,seed,k,window_range,microclusters,kernel_radius):
		self.batch_size=microclusters
		self.model=CluStream(
			h=window_range,
			m=microclusters,
			t=kernel_radius
		)
		self.seed=seed
		self.initted=False
		self.macro_model=KMeans(
			init="k-means++",
	 		random_state=self.seed,
	 		n_clusters=k,
	 	)

	def partial_fit(self,chunk):
		if self.initted:
			self.model.partial_fit(chunk)
		else:
			self.model.init_offline(chunk,self.seed)
			self.initted=True
		self.__micro_clusters=self.model.get_kernel_centers()
		self.__macro_labels=self.macro_model.fit_predict(self.__micro_clusters)
		self.__macro_clusters=self.macro_model.cluster_centers_

	def get_partial_cluster_centers(self):
		return self.__micro_clusters

	def get_final_cluster_centers(self):
		return self.__macro_clusters,self.__macro_labels

class StaticStreamkm(StaticGeneric):
	NAME="streamkm"
	def __init__(self,seed,k,coresetsize,length):
		self.batch_size=coresetsize
		self.model=Streamkm(
			coresetsize=coresetsize,
			length=length,
			seed=seed
		)
		self.seed=seed
		self.macro_model=KMeans(
			init="k-means++",
	 		random_state=self.seed,
	 		n_clusters=k,
	 	)

	def partial_fit(self,chunk):
		self.model.partial_fit(chunk)
		self.__coresets=self.model.get_streaming_coreset_centers()

		self.__macro_labels=self.macro_model.fit_predict(self.__coresets)
		self.__macro_clusters=self.macro_model.cluster_centers_

	def get_partial_cluster_centers(self):
		return self.__coresets

	def get_final_cluster_centers(self):
		return self.__macro_clusters,self.__macro_labels

class StaticMinibatch(StaticGeneric):
	NAME="minibatch"
	def __init__(self,seed,k,chunk_size):
		self.batch_size=chunk_size
		self.model=MiniBatchKMeans(
			batch_size=chunk_size,
			n_clusters=k,
			compute_labels=True
		)

	def partial_fit(self,chunk):
		self.model.partial_fit(chunk)

	def get_partial_cluster_centers(self):
		return self.model.cluster_centers_

	def get_final_cluster_centers(self):
		return self.model.cluster_centers_,self.model.labels_


class StaticMinibatchSplit(StaticGeneric):
	NAME="minibatchsplit"
	def __init__(self,seed,k,chunk_size,microclusters):
		self.batch_size=microclusters
		self.model=MiniBatchKMeans(
			batch_size=chunk_size,
			n_clusters=microclusters,
			compute_labels=False
		)
		self.seed=seed
		self.macro_model=KMeans(
			init="k-means++",
	 		random_state=self.seed,
	 		n_clusters=k,
	 	)

	def partial_fit(self,chunk):
		self.model.partial_fit(chunk)
		self.__micro_clusters=self.model.cluster_centers_

		self.__macro_labels=self.macro_model.fit_predict(self.__micro_clusters)
		self.__macro_clusters=self.macro_model.cluster_centers_

	def get_partial_cluster_centers(self):
		return self.__micro_clusters

	def get_final_cluster_centers(self):
		return self.__macro_clusters,self.__macro_labels