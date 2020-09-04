from .core import Streamkm
from .primary_generic import PrimaryGeneric
class PrimaryStreamkm(PrimaryGeneric):
	BATCH_DTYPE="float64"
	def __init__(self,*args,coreset_size,length,streamkm_seed,**kwargs):
		super().__init__(*args,batch_size=coreset_size,**kwargs)
		self.model=Streamkm(length=length,coresetsize=coreset_size,seed=streamkm_seed)

	def preproc(self,batch): 
		self.model.partial_fit(batch)
		return self.model.get_partial_cluster_centers()
		