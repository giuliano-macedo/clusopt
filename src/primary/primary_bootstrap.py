import numpy as np
from utils import Timer
from network import Ship,ServerSocket,PAYID,Payload
from math import ceil

class PrimaryBootstrap:
	"""
	Args:
		algorithm (str): the algorithm to use
		stream (core.Stream): Dataset stream
		number_nodes (int): number of remote nodes to connect
		seed (int): seed to use in the replicas
		repetitions (int): number of times to repeat replica algorithm
		lower_threshold (int): lower threshold for kappas set generation
		kappas_method (function): kappas set builder function
		remote_nodes (str): path to the file that contains the ip for all remote replicas
	Attributes:
		stream (str):
		number_nodes (int):
		lower_threshold (int):
		kappas_method (function):
		kappas (ndarray):kappa set for each replica
		replicas (list): list of connected replicas
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

		self.total_batches=ceil(self.stream.lines/self.stream.chunk_size)
		self.replicas=set()
		#t -> msock
		self.ship=Ship(self.number_nodes,remote_nodes)
		self.overall_timer=Timer()
	
	def accept_handler(self,msock):
		"""
		Helper method to accept some socket based on the protocol.
		adds msock to replicas list
		
		Args:
			msock (network.Socket): socket to be added.
		"""
		self.replicas.add(msock)
		print(f"replica {msock.ip} connected")

	def send_to_all_replicas(self,payid,*args):
		for replica in self.replicas:
			replica.send(Payload(payid,*args))

	def run(self,**json_opts):
		"""
		Run primary's node initialization and send extra json_opts to replicas

		Args:
			**json_opts : extra json options to send to replicas 
		"""
		#connect remote nodes
		for msock in self.ship.get_node_sockets():
			self.accept_handler(msock)
		#---------------------------------------------------------------------------------
		#connect local nodes
		server=ServerSocket(3523)
		print("waiting for replicas, press [CTRL+C] to stop waiting")
		try:
			while True:
				self.accept_handler(server.accept()) #no nedd to be multithread
		except KeyboardInterrupt:
			pass
		print(end="\r")
		assert len(self.replicas)!=0,"no replicas connected"
		self.kappas=self.kappas_method(len(self.replicas),self.lower_threshold)
		for replica,kappa in zip(self.replicas,self.kappas):
			replica.send(Payload(PAYID.pickle,{**{
				"algorithm":self.algorithm,
				"kappa":kappa,
				"seed":self.seed,
				"repetitions":self.repetitions,
				"distance_matrix_method":self.distance_matrix_method,
				"batch_size":self.batch_size
			},**json_opts}))

	def __del__(self):
		print("closing everything")
		for replica in self.replicas:
			replica.close()