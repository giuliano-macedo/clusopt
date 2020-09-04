from .replica_generic import ReplicaGeneric
from sklearn.cluster import MiniBatchKMeans
from functools import partial

class ReplicaMiniBatch(ReplicaGeneric):
	BATCH_DTYPE="float32"
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.ALGORITHM=partial(
			MiniBatchKMeans,
			random_state=self.seed,
			batch_size=self.batch_size,
			n_init=self.repetitions
		)
