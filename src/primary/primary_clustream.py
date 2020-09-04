from .core import CluStream
from .primary_generic import PrimaryGeneric
class PrimaryCluStream(PrimaryGeneric):
	BATCH_DTYPE="float64"
	def __init__(self,*args,clustream_seed,window_range,microkernels,kernel_radius,**kwargs):
		super().__init__(*args,batch_size=microkernels,**kwargs)
		self.model=CluStream(m=microkernels,t=kernel_radius,h=window_range)
		#init_points = self.stream.peek() if peek else self.stream.pop()
		init_points=self.stream.pop()
		print("initing clustream...")
		self.model.init_offline(init_points,seed=clustream_seed)

	def preproc(self,batch): 
		self.model.partial_fit(batch)
		return self.model.get_partial_cluster_centers()