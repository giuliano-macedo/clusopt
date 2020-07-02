from master import Master
from core import Bucket
from network import PAYID,Payload
import numpy as np
import logging
from threading import Thread
from queue import Queue
from pandas import read_csv
import json
import zlib
from utils import save_to_csv

class Replicator(Thread):
	"""
	Thread responsible for sending compressed batches to each slave in synchronized
	new threads
	"""
	def __init__(self,slaves,payid):
		super().__init__(name="Replicator")
		self.slaves=slaves
		self.payid=payid
		self.__queue=Queue() #maybe cache

	def send_handler(payid,msock,shape,compressed):
		"""
		Send to a slaves the current chunk
		
		Args:
			payid (Payload.Id) : data network id
			msock (network.Socket): socket to send data.
			shape (tuple): batch's number of lines and columns
			compressed (bytes): compressed batch data
		"""
		msock.send(Payload(payid,(shape,compressed)))

	def run(self):
		i=0
		threads=[None for _ in self.slaves]
		while True:
			should_stop,shape,compressed = self.__queue.get()
			if should_stop:break
			print(f"t={i} sending {shape[0]} points")
			for j,slave in enumerate(self.slaves):
				thread=Thread(
					name=f"Replicator.send_handler-{i,j}",
					target=Replicator.send_handler,
					args=(self.payid,slave,shape,compressed)
				)
				threads[j]=thread
				thread.start()
			for thread in threads:
				thread.join()
			i+=1

	def add_job(self,shape,compressed):
		self.__queue.put((False,shape,compressed))

	def join(self):
		self.__queue.put((True,None,None))		
		super().join()

class MasterGeneric(Master):
	"""
	Args:
		batch_size (int) : size of the chunks that the dataset will be splitted
	Attributes:
		winners (list): contains sockets winner for each bach index
		bucket (Bucket): contains each time, silhouete, and socket for each batch index
		stream (iterator): iterator of the data stream
		BATCH_DTYPE (str): defines the type of the data stream {float32,float64}
		RESULT_MODE (str): defines the type of results {labels,centroids}
	"""
	
	BATCH_DTYPE=None #{float32,float64}
	RESULT_MODE=None #{labels,centroids}
	def preproc(self,batch):
		"""
		Function pre process batches before sending it to slaves

		Args:
			batch (np.ndarray):
		Returns:
			(np.ndarray)
		"""
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
		replicator=Replicator(self.slaves,self.__BATCH_PAYID)
		replicator.start()
		for i,chunk in enumerate(self.stream):
			batch=self.preproc(chunk.values)
			compressed=zlib.compress(batch.tobytes(),level=1)
			batch_shape=batch.shape
			replicator.add_job(batch_shape,compressed)
			del(batch)
		tmax=i
		
		replicator.join()
		
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