from .core import Streamkm
from .master_generic import MasterGeneric
class MasterStreamkm(MasterGeneric):
	BATCH_DTYPE="float64"
	RESULT_MODE="centroids"
	def __init__(self,*args,coreset_size,length,streamkm_seed,**kwargs):
		super().__init__(*args,batch_size=coreset_size,**kwargs)
		self.model=Streamkm(length=length,coresetsize=coreset_size,seed=streamkm_seed)

	def preproc(self,batch): 
		self.model.batch_online_cluster(batch)
		return self.model.get_streaming_coreset_centers()
		