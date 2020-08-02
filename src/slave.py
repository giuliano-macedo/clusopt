#!/usr/bin/env python3
"""
slave.py
====================================
The slave node
"""
from core.utils import Silhouette;Silhouette #force compile
from network import ClientSocket,PAYID
from argparse import ArgumentParser
from collections import namedtuple
import numpy as np
import logging
		
class Slave:
	"""
	Args:
		batch_size (int) : size of the chunks that the dataset will be splitted
		kappa (ndarray) : K's to test
		seed (int): seed to use
		repetitions (int): number of repetitions
		ghost (int or None) : if not None, enable ghost mode when batch index equals itself
		disk_cache (int or None) : enable disk cache with max memory size equal to itself
		distance_matrix_method (str) : distance matrix algorithm to use
		batch_size (int): length of each batch
	Attributes:
		
	"""
	def __init__(self,server,kappa,seed,repetitions,ghost,disk_cache,distance_matrix_method,batch_size):
		self.server=server
		self.kappa=kappa
		self.seed=seed
		self.repetitions=repetitions
		self.ghost=ghost
		self.disk_cache=disk_cache
		self.distance_matrix_method=distance_matrix_method
		self.batch_size=batch_size

	def run(self,server):
		"""
		main method, run slave's node algorithm
		"""
		pass

def get_args():
	parser=ArgumentParser()
	parser.add_argument("master_addr",help="address of the master")
	parser.add_argument('-v','--verbose', action='store_true',help="enbale verbose")
	parser.add_argument('-g','--ghost', type=int,help="enable ghost mode in batch index TIME",metavar="TIME")
	parser.add_argument('-c','--disk-cache', type=int,help="use disk cache, keeping max of BATCHES in memory",metavar="BATCHES")
	args=parser.parse_args()
	if args.verbose:
		logging.basicConfig(format='[%(levelname)s]%(message)s',level=logging.DEBUG)
	return args
def main(server,opts):
	print(f"Connected to {server.ip}")
	config=server.recv(PAYID.pickle).obj
	config=namedtuple('Config', sorted(config))(**config) #dict -> namedtuple
	print("algorithm:",config.algorithm)
	print("seed,repetitions:",config.seed,config.repetitions)
	print("distance matrix method:",config.distance_matrix_method)
	print("batch_size",config.batch_size)
	print("kappa:",config.kappa)
	print("kappa length:",len(config.kappa))
	print("kappa sum:",sum(config.kappa))
	print(f"kappa variance: {np.var(config.kappa):.2f}")
	slave_args=dict(
		server=server,
		kappa=config.kappa,
		seed=config.seed,
		repetitions=config.repetitions,
		distance_matrix_method=config.distance_matrix_method,
		batch_size=config.batch_size
		**opts
	)

	if config.algorithm=="minibatch":
		from slave_algorithms import SlaveMiniBatch as SlaveAlgorithm
		slave_args={**slave_args,**{
			"batch_size":config.batch_size
		}}
	elif config.algorithm=="clustream":
		from slave_algorithms import SlaveCluStream as SlaveAlgorithm
		# slave_args={**slave_args,**{
			
		# }}
	elif config.algorithm=="streamkm":
		from slave_algorithms import SlaveStreamkm as SlaveAlgorithm
		# slave_args={**slave_args,**{
			
		# }}
	else:
		raise RuntimeError("Unexpected error")
	slave=SlaveAlgorithm(**slave_args)
	slave.run()
	print("done")

if __name__=="__main__":
	
	args=get_args()
	try:
		server=ClientSocket(args.master_addr,3523)
	except ConnectionRefusedError:
		print("Error connecting to",args.master_addr)
		exit(-1)
	opts=vars(args)
	
	#not needed in Server class
	del(opts["master_addr"])
	del(opts["verbose"])

	main(server,opts)
	
	
