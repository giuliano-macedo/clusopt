from .master_generic import MasterGeneric
class MasterMiniBatch(MasterGeneric):
	BATCH_DTYPE="float32"

	def __init__(self,*args,**kwargs):
		super().__init__(*args,batch_size=None,**kwargs)

	def preproc(self,batch): 
		return batch