from master import Master
from core import Bucket
from network import PAYID,Payload
import numpy as np
import logging
from threading import Thread
from pandas import read_csv
import json
import zlib
from utils import save_to_csv
class MasterGeneric(Master):
	"""
	Args:
		batch_size (int) : size of the chunks that the dataset will be splitted
	Attributes:
		winners (list): contains sockets winner for each bach index
		bucket (list): contains each time, silhouete, and socket for each batch index
	"""
	
	BATCH_DTYPE=None #{float32,float64}
	RESULT_MODE=None #{labels,centroids}
	def preproc(self,batch): #iterator
		pass
	

	def __init__(self,*args,batch_size,**kwargs):
		super().__init__(*args,**kwargs)
		self.batch_size=batch_size
		self.bucket=None
		self.winners={}
		self.stream=read_csv(
			self.input,
			chunksize=self.batch_size,
			header=None,
			dtype={
				"float32":np.float32,
				"float64":np.float64
			}[self.BATCH_DTYPE]
		)
		
		self.__BATCH_PAYID={
			"float32":PAYID.compressed_float32_matrix,
			"float64":PAYID.compressed_float64_matrix,
		}[self.BATCH_DTYPE]

		self.__RESULT_PAYID={
			"labels":PAYID.uint8_vector,
			"centroids":PAYID.float64_matrix
		}[self.RESULT_MODE]
	
	def silhoete_recv_handler(self,msock):
		"""
		Helper method to recv each batch silhouete.
		updates bucket list and winners list
		
		Args:
			msock (network.Socket): socket to recv data.
		"""
		while True:
			pay=msock.recv(PAYID.end,PAYID.silhouette)
			if pay.id==PAYID.end:
				break
			# t is the batch_counter
			t,k,sil=pay.obj
			print(msock.ip,t,k,round(sil,3))
			isfull=self.bucket.add(t,k,sil,msock)
			if isfull:
				bucket_winner=self.bucket.get(t)
				print(f"winner on t={t} {bucket_winner}")
				self.winners[t]=bucket_winner

	def replicator_send_handler(self,msock,batch,compressed):
		"""
		Send to all slaves the current chunk
		
		Args:
			msock (network.Socket): socket to send data.
			batch (np.ndarray): dataset chunk
			compressed (bytes): compressed batch data
		"""
		msock.send(Payload(self.__BATCH_PAYID,(batch,compressed)))

	def run(self):
		super().run(batch_size=self.batch_size)
		self.overall_timer.start()
		self.bucket=Bucket(len(self.slaves))
		#---------------------------------------------------------------------------------
		#start silhoete receiver threads
		sil_threads=[]
		for i,slave in enumerate(self.slaves):
			t=Thread(
				name=f"Silhoete-{i}",
				target=MasterGeneric.silhoete_recv_handler,
				args=(self,slave)
			)
			sil_threads.append(t)
			t.start()
		#---------------------------------------------------------------------------------
		#start replicator sender threads
		repl_threads=[]
		for i,batch in enumerate(self.preproc(self.stream)):
			print(f"t={i} sending {len(batch.values)} points")
			compressed=zlib.compress(batch.values.tobytes(),level=1)
			for j,slave in enumerate(self.slaves):
				t=Thread(
					name=f"Replicator-{i,j}",
					target=MasterGeneric.replicator_send_handler,
					args=(self,slave,batch.values,compressed)
				)
				repl_threads.append(t)
				t.start()
		tmax=i
		#join sends
		for t in repl_threads:
			t.join()
		self.send_to_all_slaves(PAYID.end)
		#---------------------------------------------------------------------------------
		#join recvs
		for t in sil_threads:
			t.join()
		#---------------------------------------------------------------------------------
		#determine winners and request labels
		if len(self.winners)!=tmax+1:
			logging.warning(f"Didn't recieve all t callbacks {len(self.winners),tmax+1}")
		winner_results=[]
		for t,winner in enumerate(self.winners.values()):
			print(f"requesting results for {winner.msock} on k={winner.k} and time={t}")
			winner.msock.send(Payload(PAYID.results_req,(t,winner.k)))
			result=winner.msock.recv(self.__RESULT_PAYID).obj
			winner_results.append(result.tolist())
		#---------------------------------------------------------------------------------
		#log everything
		t=self.overall_timer.stop()
		print("saving overall.csv...")
		save_to_csv("overall.csv","%i,%e",[[t,winner.sil]],header="time,silhouette")
		print("saving buckets.csv...")
		self.bucket.save_logs("buckets.csv")
		print("saving results.json...")
		with open("results.json","w") as f:
			json.dump(winner_results,f)
		self.send_to_all_slaves(PAYID.end)