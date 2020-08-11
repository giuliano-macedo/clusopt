from .core import Streamkm
from .master_generic import MasterGeneric
import numpy as np
class MasterStreamkm(MasterGeneric):
	BATCH_DTYPE="float64"
	def __init__(self,*args,coreset_size,length,streamkm_seed,**kwargs):
		super().__init__(*args,batch_size=coreset_size,**kwargs)
		self.model=Streamkm(length=length,coresetsize=coreset_size,seed=streamkm_seed)

	def preproc(self,batch): 
		self.model.batch_online_cluster(batch)
		ans=self.model.get_streaming_coreset_centers()
		if np.isinf(ans).any():
			#too much duplicates causes streamkm to return -inf's
			raise ArithmeticError()
		return ans
		