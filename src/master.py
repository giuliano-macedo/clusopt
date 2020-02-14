#!/usr/bin/env python3
"""
master.py
====================================
The master node
"""
import numpy as np
from args import parse_args
from kappas import get_kappas
from utils import Timer
from network import Ship,ServerSocket,PAYID,Payload

class Master:
	"""
	Args:
		algorithm (str): the algorithm to use
		input (str): URI of the dataset
		number_nodes (int): number of remote nodes to connect
		lower_threshold (int): lower threshold for kappa set generation
		remote_nodes (str): path to the file that contains the ip for all remote slaves
	Attributes:
		input (str):
		number_nodes (int):
		lower_threshold (int):
		kappas (ndarray):kappa set for each slave
		slaves (list): list of connected slaves
		ship (midsc.network.Ship): ship object containing the number of nodes necessary
		overall_timer (midsc.Timer): Timer object for overall runtime
	"""


	def __init__(self,algorithm,_input,number_nodes,lower_threshold,remote_nodes):
		self.algorithm=algorithm
		self.input=_input
		self.number_nodes=number_nodes
		self.lower_threshold=lower_threshold
		self.kappas=np.empty(0)

		self.slaves=set()
		#t -> msock
		self.ship=Ship(self.number_nodes,remote_nodes)
		self.overall_timer=Timer()
	
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
		self.kappas=get_kappas(len(self.slaves),self.lower_threshold)
		for slave,kappa in zip(self.slaves,self.kappas):
			slave.send(Payload(PAYID.json,{**{
				"algorithm":self.algorithm,
				"kappa":kappa
			},**json_opts}))

if __name__=="__main__":
	args=parse_args()
	master_args={
		"algorithm":args.algorithm,
		"_input":args.input,
		"number_nodes":args.number_nodes,
		"lower_threshold":args.lower_threshold,
		"remote_nodes":args.remote_nodes
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
			"kernel_radius":args.kernel_radius
		}}
	elif args.algorithm=="streamkm":
		from master_algorithms import MasterStreamkm as MasterAlgorithm
		master_args={**master_args,**{
			"coreset_size":args.coreset_size,
			"length":args.length
		}}
	master=MasterAlgorithm(**master_args)
	master.run()
	