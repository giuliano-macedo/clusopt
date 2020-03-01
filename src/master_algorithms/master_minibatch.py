from .master_generic import MasterGeneric
class MasterMiniBatch(MasterGeneric):
	BATCH_DTYPE="float32"
	RESULT_MODE="labels" 
	def preproc(self,batch): 
		return batch