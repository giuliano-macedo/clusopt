from .core import CluStream
from .master_generic import MasterGeneric
class MasterCluStream(MasterGeneric):
	BATCH_DTYPE="float64"
	RESULT_MODE="centroids"
	def __init__(self,*args,clustream_seed,window_range,microkernels,kernel_radius,**kwargs):
		super().__init__(*args,batch_size=microkernels,**kwargs)
		self.model=CluStream(m=microkernels,t=kernel_radius,h=window_range)
		#init_points = self.stream.peek() if peek else self.stream.pop()
		init_points=self.stream.pop()
		print("initing clustream...")
		self.model.init_offline(init_points,seed=clustream_seed)

	def preproc(self,batch): 
		self.model.batch_online_cluster(batch)
		return self.model.get_kernel_centers()