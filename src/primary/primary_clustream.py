from .core import CluStream
from .primary_generic import PrimaryGeneric
class PrimaryCluStream(PrimaryGeneric):
	BATCH_DTYPE="float64"
	def __init__(self,*args,window_range,microkernels,kernel_radius,**kwargs):
		super().__init__(*args,batch_size=microkernels,**kwargs)
		self.model=CluStream(
			m=microkernels,
			t=kernel_radius,
			h=self.stream.lines if window_range==None else window_range
		)
		self.clustream_is_initted=False
		
	def preproc(self,batch): 
		if self.clustream_is_initted:
			self.model.partial_fit(batch)
		else:
			# these were in __init__
			#init_points = self.stream.peek() if peek else self.stream.pop()
			# init_points=self.stream.pop()
			init_points=batch
			print("initing clustream...")
			self.model.init_offline(init_points,seed=self.seed)
			self.clustream_is_initted=True

		return self.model.get_partial_cluster_centers()