
from .primary_generic import PrimaryGeneric
from sklearn.cluster import MiniBatchKMeans
class PrimaryMiniBatchSplit(PrimaryGeneric):
	BATCH_DTYPE="float64"
	def __init__(self,*args,microclusters,**kwargs):
		super().__init__(*args,batch_size=microclusters,**kwargs)
		
		self.model=MiniBatchKMeans(
			n_clusters=microclusters,
			batch_size=self.chunk_size,
			compute_labels=False,
			init_size=self.chunk_size,
			random_state=self.seed
		)

	def preproc(self,batch): 
		# for i in range(4000//100):
		# 	l=i*100
		# 	h=(i+1)*100
		# 	self.model.partial_fit(batch[l:h])
		self.model.partial_fit(batch)
		return self.model.cluster_centers_