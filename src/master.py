#!/usr/bin/env python3
"""
master.py
====================================
The master node
"""
from network import ServerSocket,Payload,Ship
from core import Bucket
from threading import Thread
from collections import namedtuple
import numpy as np
import pandas
import logging
import zlib
from args import parse_args
from utils import save_to_csv,Timer
from kappas import get_kappas

class Master:
	"""
	Args:
		number_nodes (int): number of remote nodes to connect
		input (str): URI of the dataset
		batch_size (int) : size of the chunks that the dataset will be splitted
	Attributes:
		slaves (list): list of connected slaves
		ship (midsc.network.Ship): ship object containing the number of nodes necessary
		overall_timer (midsc.Timer): Timer object for overall runtime
		winners (list): contains sockets winner for each bach index
		bucket (list): contains each time, silhouete, and socket for each batch index
	"""


	def __init__(self,**config):
		self.config=namedtuple("config",list(config.keys()))(*list(config.values()))
		self.slaves=set()
		#t -> msock
		self.winners={}
		self.bucket=Bucket(self.config.batch_size)
		self.ship=Ship(self.config.number_nodes)
		self.overall_timer=Timer()
	def accept_handler(self,msock):
		"""
		Helper method to accept some socket based on the protocol.
		adds msock to slaves list
		
		Args:
			msock (network.Socket): socket to be added.
		"""
		msock.send(Payload(Payload.Id.k_coeficient,len(self.slaves)+2))
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
			pay=msock.recv(Payload.Id.end,Payload.Id.silhouette)
			if pay.id==Payload.Id.end:
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
		msock.send(Payload(Payload.Id.datapoints,(batch,compressed)))
	def run(self):
		"""
		main method, run master's node algorithm
		"""
		config=self.config #ugly but whatever
		#---------------------------------------------------------------------------------
		#connect remote nodes
		for msock in self.ship.get_node_sockets():
			self.accept_handler(msock)
		#---------------------------------------------------------------------------------
		#connect local nodes
		server=ServerSocket(3523)
		print("waiting for slaves press [CTRL+C] to stop waiting")
		try:
			while True:
				self.accept_handler(server.accept()) #no nedd to be multithread
		except KeyboardInterrupt:
			pass
		print(end="\r")
		assert len(self.slaves)!=0,"no slaves connected"
		self.overall_timer.start()
		#---------------------------------------------------------------------------------
		#send increment
		for slave in self.slaves:
			slave.send(Payload(Payload.Id.k_coeficient_inc,len(self.slaves)))
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
			slave.send(Payload(Payload.Id.end))
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
			winner.msock.send(Payload(Payload.Id.labels_req,(t,winner.k)))
			labels=winner.msock.recv(Payload.Id.labels).obj
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
			slave.send(Payload(Payload.Id.end))
		#---------------------------------------------------------------------------------
		#close everything
		print("closing everything")
		for slave in self.slaves:
			slave.close()
		self.kappas=get_kappas(len(self.slaves),self.lower_threshold)

if __name__=="__main__":
	args=parse_args()
	master_args={
		"_input":args.input,
		"number_nodes":args.number_nodes,
		"lower_threshold":args.lower_threshold
	}
	if args.algorithm=="minibatch":
		from master_algorithms import MasterMiniBatch
		master_args={**master_args,**{
			"batch_size":args.batch_size
		}}
		master=MasterMiniBatch(**master_args)
	elif args.algorithm=="clustream":
		from master_algorithms import MasterCluStream
		master_args={**master_args,**{
			"window_range":args.window_range,
			"microkernels":args.microclusters,
			"kernel_radius":args.kernel_radius
		}}
		master=MasterCluStream(**master_args)
	elif args.algorithm=="streamkm":
		from master_algorithms import MasterStreamkm
		master_args={**master_args,**{
			"coreset_size":args.coreset_size,
			"length":args.length
		}}
		master=MasterStreamkm(**master_args)
	master.run()
	