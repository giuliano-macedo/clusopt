from .primary_generic import PrimaryGeneric
class PrimaryMiniBatch(PrimaryGeneric):
	BATCH_DTYPE="float32"

	def __init__(self,*args,**kwargs):
		super().__init__(*args,batch_size=None,**kwargs)

	def preproc(self,batch): 
		return batch