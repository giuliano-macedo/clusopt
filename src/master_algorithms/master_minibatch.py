from master import Master
from core import Bucket
from network import PAYID
from threading import Thread
import pandas
import zlib
from utils import save_to_csv
class MasterMiniBatch(Master):
	"""
	Args:
		batch_size (int) : size of the chunks that the dataset will be splitted
	Attributes:
		winners (list): contains sockets winner for each bach index
		bucket (list): contains each time, silhouete, and socket for each batch index
	"""
	def __init__(self,*args,batch_size):
		super().__init__(*args)
		self.batch_size=batch_size
		self.bucket=Bucket(self.batch_size)
		self.winners={}
	
	def accept_handler(self,msock):
		"""
		Helper method to accept some socket based on the protocol.
		adds msock to slaves list
		
		Args:
			msock (network.Socket): socket to be added.
		"""
		self.slaves.add(msock)
		print(f"slave {msock.ip} connected")
	
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
		msock.send(Payload(PAYID.datapoints,(batch,compressed)))
	def run(self):
		super().run()
		self.overall_timer.start()
		#send increment
		for slave in self.slaves:
			slave.send(Payload(PAYID.k_coeficient_inc,len(self.slaves)))
		#---------------------------------------------------------------------------------
		#start silhoete receiver threads
		sil_threads=[]
		for i,slave in enumerate(self.slaves):
			t=Thread(
				name=f"silhoete-{i}",
				target=Master.silhoete_recv_handler,
				args=(self,slave,)
			)
			sil_threads.append(t)
			t.start()
		#---------------------------------------------------------------------------------
		#start replicator sender threads
		repl_threads=[]
		for i,batch in enumerate(pandas.read_csv(config.input,chunksize=config.batch_size,dtype=np.float32)):
			print(f"t={i} sending {len(batch.values)} points")
			compressed=zlib.compress(batch.values.tobytes(),level=1)
			for j,slave in enumerate(self.slaves):
				t=Thread(
					name=f"Replicator-{i,j}",
					target=Master.replicator_send_handler,
					args=(self,slave,batch.values,compressed)
				)
				repl_threads.append(t)
				t.start()
		tmax=i
		#join sends
		for t in repl_threads:
			t.join()
		#---------------------------------------------------------------------------------
		#send end payload
		for slave in self.slaves:
			slave.send(Payload(PAYID.end))
		#---------------------------------------------------------------------------------
		#join recvs
		for t in sil_threads:
			t.join()
		#---------------------------------------------------------------------------------
		#determine winners and request labels
		if len(self.winners)!=tmax+1:
			logging.warning(f"Didn't recieve all t callbacks {len(self.winners),tmax+1}")
		winner_label=[]
		for t,winner in enumerate(self.winners.values()):
			print(f"requesting labels for {winner.msock} on k={winner.k} and time={t}")
			winner.msock.send(Payload(PAYID.labels_req,(t,winner.k)))
			labels=winner.msock.recv(PAYID.labels).obj
			print(f"got labels {labels[:30]}...")
			winner_label+=list(labels) #TODO probably slow
		#---------------------------------------------------------------------------------
		#log everything
		t=self.overall_timer.stop()
		print("saving overall.csv...")
		save_to_csv("overall.csv","%i,%e",[[t,winner.sil]],header="time,silhouette")
		print("saving buckets.csv...")
		self.bucket.save_logs("buckets.csv")
		print("saving labels.csv...")
		np.savetxt("labels.csv", np.asarray(winner_label), delimiter=",",fmt="%u")
		#---------------------------------------------------------------------------------
		#send end payload to everyone
		for slave in self.slaves:
			slave.send(Payload(PAYID.end))
		#---------------------------------------------------------------------------------
		#close everything
		print("closing everything")
		for slave in self.slaves:
			slave.close()