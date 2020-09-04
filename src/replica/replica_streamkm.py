from .replica_generic import ReplicaGeneric
from sklearn.cluster import KMeans
from functools import partial

class ReplicaStreamkm(ReplicaGeneric):
	BATCH_DTYPE="float64"
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.ALGORITHM=partial(
			KMeans,
			random_state=self.seed,
			init="k-means++",
			n_init=self.repetitions
		)