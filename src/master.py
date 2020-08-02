#!/usr/bin/env python3
"""
master.py
====================================
The master node
"""
import numpy as np
from args import parse_args
from utils import Timer
from network import Ship,ServerSocket,PAYID,Payload
import os
from core import Stream

class Master:
	"""
	Args:
		algorithm (str): the algorithm to use
		stream (core.Stream): Dataset stream
		number_nodes (int): number of remote nodes to connect
		seed (int): seed to use in the slaves
		repetitions (int): number of times to repeat slave algorithm
		lower_threshold (int): lower threshold for kappas set generation
		kappas_method (function): kappas set builder function
		remote_nodes (str): path to the file that contains the ip for all remote slaves
	Attributes:
		stream (str):
		number_nodes (int):
		lower_threshold (int):
		kappas_method (function):
		kappas (ndarray):kappa set for each slave
		slaves (list): list of connected slaves
		ship (midsc.network.Ship): ship object containing the number of nodes necessary
		overall_timer (midsc.Timer): Timer object for overall runtime
	"""


	def __init__(self,
			algorithm,
			stream,
			number_nodes,
			seed,
			repetitions,
			lower_threshold,
			kappas_method,
			remote_nodes,
			distance_matrix_method
		):
		self.algorithm=algorithm
		self.stream=stream
		self.number_nodes=number_nodes
		self.seed=seed
		self.repetitions=repetitions
		self.lower_threshold=lower_threshold
		self.kappas_method=kappas_method
		self.kappas=np.empty(0)
		self.distance_matrix_method=distance_matrix_method

		self.slaves=set()
		#t -> msock
		self.ship=Ship(self.number_nodes,remote_nodes)
		self.overall_timer=Timer()
	
	def accept_handler(self,msock):
		"""
		Helper method to accept some socket based on the protocol.
		adds msock to slaves list
		
		Args:
			msock (network.Socket): socket to be added.
		"""
		self.slaves.add(msock)
		print(f"slave {msock.ip} connected")

	def send_to_all_slaves(self,payid,*args):
		for slave in self.slaves:
			slave.send(Payload(payid,*args))

	def run(self,**json_opts):
		"""
		Run master's node initialization and send extra json_opts to slaves

		Args:
			**json_opts : extra json options to send to slaves 
		"""
		#connect remote nodes
		for msock in self.ship.get_node_sockets():
			self.accept_handler(msock)
		#---------------------------------------------------------------------------------
		#connect local nodes
		server=ServerSocket(3523)
		print("waiting for slaves, press [CTRL+C] to stop waiting")
		try:
			while True:
				self.accept_handler(server.accept()) #no nedd to be multithread
		except KeyboardInterrupt:
			pass
		print(end="\r")
		assert len(self.slaves)!=0,"no slaves connected"
		self.kappas=self.kappas_method(len(self.slaves),self.lower_threshold)
		for slave,kappa in zip(self.slaves,self.kappas):
			slave.send(Payload(PAYID.json,{**{
				"algorithm":self.algorithm,
				"kappa":kappa,
				"seed":self.seed,
				"repetitions":self.repetitions,
				"distance_matrix_method":self.distance_matrix_method,
				"batch_size":self.batch_size
			},**json_opts}))

	def __del__(self):
		print("closing everything")
		for slave in self.slaves:
			slave.close()

def create_results_dir():
	path="./results"
	if os.path.exists(path) and not os.path.isdir(path):
		raise RuntimeError(f"{os.getcwd()}/results is not a directory")
	elif not os.path.exists(path):
		os.mkdir(path)

if __name__=="__main__":
	args=parse_args()
	create_results_dir()
	master_args={
		"algorithm":args.algorithm,
		"number_nodes":args.number_nodes,
		"seed":args.seed,
		"repetitions":args.repetitions,
		"lower_threshold":args.lower_threshold,
		"remote_nodes":args.remote_nodes,
		"distance_matrix_method":args.distance_matrix_method
	}
	if args.algorithm=="minibatch":
		from master_algorithms import MasterMiniBatch as MasterAlgorithm
		master_args={**master_args,**{
			"batch_size":args.batch_size
		}}
	elif args.algorithm=="clustream":
		from master_algorithms import MasterCluStream as MasterAlgorithm
		master_args={**master_args,**{
			"window_range":args.window_range,
			"microkernels":args.microclusters,
			"kernel_radius":args.kernel_radius,
			"clustream_seed":args.clustream_seed
		}}
	elif args.algorithm=="streamkm":
		from master_algorithms import MasterStreamkm as MasterAlgorithm
		master_args={**master_args,**{
			"coreset_size":args.coreset_size,
			"length":args.length,
			"streamkm_seed":args.streamkm_seed
		}}
	else:
		raise RuntimeError("unexpected error")
	if args.kappas_method=="gauss":
		from kappas import get_kappas_gauss as get_kappas
	elif args.kappas_method=="v1":
		from kappas import get_kappas_v1 as get_kappas
	elif args.kappas_method=="v2":
		from kappas import get_kappas_v2 as get_kappas
	elif args.kappas_method=="random":
		from kappas import get_kappas_random as get_kappas
	else:
		raise RuntimeError("unexpected error")
	master_args["kappas_method"]=get_kappas
	master_args["stream"]=Stream(args.input,args.chunk_size,MasterAlgorithm.BATCH_DTYPE)
	master=MasterAlgorithm(**master_args)
	master.run()
	