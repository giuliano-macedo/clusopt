from slave import Slave
from sklearn.cluster import MiniBatchKMeans
from functools import partial
from core import Clusterer
from network import Payload,PAYID
class SlaveMiniBatch(Slave):
	def __init__(self,*args,batch_size,**kwargs):
		super().__init__(*args,**kwargs)
		self.batch_size=batch_size
	
	def run(self):
		clusterer=Clusterer(partial(MiniBatchKMeans,batch_size=self.batch_size),self.kappa)
		#---------------------------------------------------------------------------------
		#for every payload calc sil_score
		bc=0
		while True:
			pay=self.server.recv(PAYID.compressed_float32_matrix,PAYID.end)
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
			pay=self.server.recv(PAYID.labels_req,PAYID.end)
			if pay.id==PAYID.end:
				break
			batch_index,k=pay.obj
			print(f"i am the winner for batch_index={batch_index} and k={k}")
			labels=clusterer.get_best_label(batch_index,k)
			if labels is None:
				self.server.send(Payload(PAYID.err))
				print(*clusterer.best_clusterers.items(),sep="\n")
				print("-"*48)
				raise RuntimeError(f"Requested batch_index,k not found ({pay.obj}), values available {list(clusterer.best_clusterers.keys())}")
			self.server.send(Payload(PAYID.uint8_vector,labels))