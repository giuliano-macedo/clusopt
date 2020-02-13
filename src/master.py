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
from network import Ship,ServerSocket

class Master:
	"""
	Args:
		input (str): URI of the dataset
		number_nodes (int): number of remote nodes to connect
		lower_threshold (int): lower threshold for kappa set generation
	Attributes:
		input (str):
		number_nodes (int):
		lower_threshold (int):
		kappas (ndarray):kappa set for each slave
		slaves (list): list of connected slaves
		ship (midsc.network.Ship): ship object containing the number of nodes necessary
		overall_timer (midsc.Timer): Timer object for overall runtime
	"""


	def __init__(self,_input,number_nodes,lower_threshold):
		self.input=_input
		self.number_nodes=number_nodes
		self.lower_threshold=lower_threshold
		self.kappas=np.empty(0)

		self.slaves=set()
		#t -> msock
		self.ship=Ship(self.number_nodes)
		self.overall_timer=Timer()
		

	def run(self):
		"""
		main method, run master's node algorithm
		"""
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
	