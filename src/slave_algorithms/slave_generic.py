from slave import Slave
from core import Clusterer
from network import Payload,PAYID
class SlaveGeneric(Slave):
	BATCH_DTYPE=None #{float32,float64}
	RESULT_MODE=None #{labels,centroids}
	ALGORITHM=None #sklearn clusterer

	def __init__(self,*args,batch_size,**kwargs):
		super().__init__(*args,**kwargs)
		self.__BATCH_PAYID={
			"float32":PAYID.compressed_float32_matrix,
			"float64":PAYID.compressed_float64_matrix,
		}[self.BATCH_DTYPE]

		self.__RESULT_PAYID={
			"labels":PAYID.uint8_vector,
			"centroids":PAYID.float64_matrix
		}[self.RESULT_MODE]
		self.batch_size=batch_size
	
	def run(self):
		clusterer=Clusterer(self.ALGORITHM,self.kappa,self.RESULT_MODE)
		#---------------------------------------------------------------------------------
		#for every payload calc sil_score
		bc=0
		while True:
			pay=self.server.recv(self.__BATCH_PAYID,PAYID.end)
			if pay.id==PAYID.end:
				print(f"ended with {bc}")
				break
			k,sil=clusterer.add_and_get_best_score(pay.obj)
			self.server.send(Payload(PAYID.silhouette,(bc,k,sil)))
			print(f"i am finished with t={bc}")
			bc+=1
		self.server.send(Payload(PAYID.end))
		#---------------------------------------------------------------------------------
		#check if is winner for some k and t
		while True:
			pay=self.server.recv(PAYID.results_req,PAYID.end)
			if pay.id==PAYID.end:
				break
			batch_index,k=pay.obj
			print(f"i am the winner for batch_index={batch_index} and k={k}")
			result=clusterer.get_result(batch_index,k)
			if result is None:
				self.server.send(Payload(PAYID.err))
				print(*clusterer.best_clusterers.items(),sep="\n")
				print("-"*48)
				raise RuntimeError(f"Requested batch_index,k not found ({pay.obj}), values available {list(clusterer.best_clusterers.keys())}")
			self.server.send(Payload(self.__RESULT_PAYID,result))