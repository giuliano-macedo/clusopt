from .slave_generic import SlaveGeneric
from sklearn.cluster import MiniBatchKMeans
from functools import partial

class SlaveMiniBatch(SlaveGeneric):
	BATCH_DTYPE="float32"
	RESULT_MODE="labels"
	def __init__(self,*args,batch_size,**kwargs):
		super().__init__(*args,**kwargs)
		self.batch_size=batch_size
		self.ALGORITHM=partial(
			MiniBatchKMeans,
			random_state=self.seed,
			batch_size=self.batch_size,
			n_init=1
		)
