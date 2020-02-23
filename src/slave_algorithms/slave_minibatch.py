from slave import Slave
from core import Clusterer
from network import Payload,PAYID
class SlaveMiniBatch(Slave):
	def __init__(self,*args,batch_size,**kwargs):
		super().__init__(*args,**kwargs)
		self.batch_size=batch_size
	
	def run(self):
		clusterer=Clusterer(self.kappa)
		#---------------------------------------------------------------------------------
		#for every payload calc sil_score
		bc=0
		while True:
			pay=self.server.recv(PAYID.compressed_float32_matrix,PAYID.end)
			if pay.id==PAYID.end:
				print(f"ended with {bc}")
				break
			for k,sil in clusterer.add_and_get_score(pay.obj):
				self.server.send(Payload(PAYID.silhouette,(bc,k,sil)))
			print(f"i am finished with t={bc}")
			bc+=1
		self.server.send(Payload(PAYID.end))
		#---------------------------------------------------------------------------------
		#check if is winner for some k and t
		while True:
			pay=self.server.recv(PAYID.labels_req,PAYID.end)
			if pay.id==PAYID.labels_req:
				t,k=pay.obj
				print(f"i am the winner for t={t} and k={k}")
				winner_shelve=next((shelve for shelve in clusterer.drawer if shelve.k==k),None) #TODO O(N) but not that slow
				if winner_shelve==None:
					self.server.send(Payload(PAYID.err))
					raise RuntimeError(f"Requested k not found ({pay.obj}) ks available {[o.k for o in clusterer.drawer]}")
				tbatch_size=t*self.batch_size
				tbatch_size_plus=(t+1)*self.batch_size
				self.server.send(Payload(PAYID.uint8_vector,winner_shelve.labels[tbatch_size:tbatch_size_plus]))
			elif pay.id==PAYID.end:
				break