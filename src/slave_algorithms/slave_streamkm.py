from .slave_generic import SlaveGeneric
from sklearn.cluster import KMeans
from functools import partial

class SlaveStreamkm(SlaveGeneric):
	BATCH_DTYPE="float64"
	RESULT_MODE="centroids"
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.ALGORITHM=partial(
			KMeans,
			random_state=self.seed,
			init="k-means++",
			n_init=1
		)